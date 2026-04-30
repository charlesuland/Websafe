import secrets
import uuid
from jose import jwt, JWTError
from datetime import datetime, timezone, timedelta
from fastapi import HTTPException, Depends, APIRouter, status, Request, Response
from app.dependencies import (
    get_db,
    SECRET_KEY,
    ALGORITHM,
    TOKEN_ISSUER,
    ACCESS_COOKIE_NAME,
    REFRESH_COOKIE_NAME,
    CSRF_COOKIE_NAME,
    ACCESS_TOKEN_EXPIRES_MINUTES,
    REFRESH_TOKEN_EXPIRES_DAYS,
    COOKIE_SECURE,
    COOKIE_SAMESITE,
    validate_csrf,
)
from typing import Annotated, Optional
from sqlalchemy.orm import Session
from sqlmodel import select
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm
from app import models
from app.activity_log import log_and_commit_security_event
from slowapi import Limiter
from slowapi.util import get_remote_address
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="", tags=[""], dependencies=[], responses={404: {"description": "Not found"}}
)

pwd_context = CryptContext(schemes=["argon2"])

# Rate limiter for login attempts
limiter = Limiter(key_func=get_remote_address)


def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(plain_passowrd: str):
    return pwd_context.hash(plain_passowrd)


def create_jwt_token(*, user_id: int, token_type: str, expires_delta: timedelta, jti: str | None = None):
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "type": token_type,
        "iat": int(now.timestamp()),
        "exp": now + expires_delta,
        "iss": TOKEN_ISSUER,
    }
    if jti:
        payload["jti"] = jti
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def utcnow_naive() -> datetime:
    return datetime.utcnow()


def decode_jwt_token(token: str, expected_type: str):
    payload = jwt.decode(
        token,
        SECRET_KEY,
        algorithms=[ALGORITHM],
        issuer=TOKEN_ISSUER,
    )
    if payload.get("type") != expected_type:
        raise JWTError("Unexpected token type")
    return payload


def set_auth_cookies(response: Response, access_token: str, refresh_token: str, csrf_token: str):
    # Set access token cookie
    response.set_cookie(
        key=ACCESS_COOKIE_NAME,
        value=access_token,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite=COOKIE_SAMESITE,
        path="/",
        max_age=ACCESS_TOKEN_EXPIRES_MINUTES * 60,
    )

    # Set refresh token
    response.set_cookie(
        key=REFRESH_COOKIE_NAME,
        value=refresh_token,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite=COOKIE_SAMESITE,
        path="/",
        max_age=REFRESH_TOKEN_EXPIRES_DAYS * 24 * 60 * 60,
    )

    # Set CSRF token cookie
    response.set_cookie(
        key=CSRF_COOKIE_NAME,
        value=csrf_token,
        httponly=False,
        secure=COOKIE_SECURE,
        samesite=COOKIE_SAMESITE,
        path="/",
        max_age=REFRESH_TOKEN_EXPIRES_DAYS * 24 * 60 * 60,
    )


def clear_auth_cookies(response: Response):
    # Clear access token cookie
    response.delete_cookie(ACCESS_COOKIE_NAME, path="/")
    response.delete_cookie(REFRESH_COOKIE_NAME, path="/")
    response.delete_cookie(CSRF_COOKIE_NAME, path="/")

# function to log security event in database
@router.post("/token")
@limiter.limit("5/minute")
async def login_for_access_token(
    request: Request,
    response: Response,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[Session, Depends(get_db)],
):
    # Support login by either username or email
    user = db.execute(
        select(models.User).where(
            (models.User.username == form_data.username) |
            (models.User.email == form_data.username)
        )
    ).scalar_one_or_none()
 
    # Always return a generic 401 regardless of whether the
    # username or password was wrong. 
    if not user or not verify_password(plain_password=form_data.password, hashed_password=user.hash_password):
        log_and_commit_security_event(
            db=db,
            user_id=getattr(user, "id", None),
            action="failed_login",
            request=request,
        )


        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
 
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    # Log login event
    log_and_commit_security_event(
        db=db,
        user_id=user.id,
        action="login",
        request=request,
    )

    access_token = create_jwt_token(
        user_id=user.id,
        token_type="access",
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRES_MINUTES),
    )

    refresh_jti = str(uuid.uuid4())
    refresh_token = create_jwt_token(
        user_id=user.id,
        token_type="refresh",
        expires_delta=timedelta(days=REFRESH_TOKEN_EXPIRES_DAYS),
        jti=refresh_jti,
    )
    csrf_token = secrets.token_urlsafe(32)

    db.add(
        models.RefreshSession(
            user_id=user.id,
            jti=refresh_jti,
            expires_at=utcnow_naive() + timedelta(days=REFRESH_TOKEN_EXPIRES_DAYS),
            user_agent=request.headers.get("user-agent"),
            ip_address=request.client.host if request.client else None,
        )
    )
    db.commit()

    set_auth_cookies(response, access_token, refresh_token, csrf_token)
    
    return {
        "status": "authenticated",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
        },
    }


@router.post("/auth/refresh")
async def refresh_tokens(request: Request, response: Response, db: Annotated[Session, Depends(get_db)]):
    validate_csrf(request)

    refresh_token = request.cookies.get(REFRESH_COOKIE_NAME)
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token missing")

    try:
        payload = decode_jwt_token(refresh_token, "refresh")
        user_id = int(payload["sub"])
        jti = payload["jti"]
    except (JWTError, KeyError, TypeError, ValueError):
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    session = db.query(models.RefreshSession).filter(models.RefreshSession.jti == jti).first()
    now = utcnow_naive()

    if not session or session.user_id != user_id or session.revoked_at is not None or session.expires_at <= now:
        raise HTTPException(status_code=401, detail="Refresh session invalid")

    session.revoked_at = now

    new_jti = str(uuid.uuid4())
    new_access_token = create_jwt_token(
        user_id=user_id,
        token_type="access",
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRES_MINUTES),
    )
    new_refresh_token = create_jwt_token(
        user_id=user_id,
        token_type="refresh",
        expires_delta=timedelta(days=REFRESH_TOKEN_EXPIRES_DAYS),
        jti=new_jti,
    )
    csrf_token = secrets.token_urlsafe(32)

    db.add(
        models.RefreshSession(
            user_id=user_id,
            jti=new_jti,
            expires_at=now + timedelta(days=REFRESH_TOKEN_EXPIRES_DAYS),
            user_agent=request.headers.get("user-agent"),
            ip_address=request.client.host if request.client else None,
        )
    )
    db.commit()

    set_auth_cookies(response, new_access_token, new_refresh_token, csrf_token)
    return {"status": "refreshed"}


@router.post("/auth/logout")
async def logout(request: Request, response: Response, db: Annotated[Session, Depends(get_db)]):
    validate_csrf(request)

    refresh_token = request.cookies.get(REFRESH_COOKIE_NAME)
    if refresh_token:
        try:
            payload = decode_jwt_token(refresh_token, "refresh")
            jti = payload.get("jti")
            if jti:
                session = db.query(models.RefreshSession).filter(models.RefreshSession.jti == jti).first()
                if session and session.revoked_at is None:
                    session.revoked_at = utcnow_naive()
                    db.commit()
        except JWTError:
            pass

    clear_auth_cookies(response)
    return {"status": "logged_out"}


@router.get("/auth/session")
async def get_session_status(request: Request, db: Annotated[Session, Depends(get_db)]):
    access_token = request.cookies.get(ACCESS_COOKIE_NAME)
    if not access_token:
        return {"authenticated": False}

    try:
        payload = decode_jwt_token(access_token, "access")
        user_id = int(payload["sub"])
    except (JWTError, KeyError, TypeError, ValueError):
        return {"authenticated": False}

    user = db.get(models.User, user_id)
    if not user or not user.is_active:
        return {"authenticated": False}

    return {
        "authenticated": True,
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
        },
    }
