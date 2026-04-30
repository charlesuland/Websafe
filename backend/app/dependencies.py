from app.database import SessionLocal

from typing import Annotated
from datetime import datetime, timezone
import os
import secrets
from jose import JWTError, jwt
from fastapi import HTTPException, status, Depends, Request
from pydantic import BaseModel
from app import models
from sqlalchemy.orm import Session
from sqlmodel import select
from app.schemas import User, TokenData
import boto3

ALGORITHM = "HS256"
SECRET_KEY = "asdf"
TOKEN_ISSUER = "websafe"
ACCESS_COOKIE_NAME = "access_token"
REFRESH_COOKIE_NAME = "refresh_token"
CSRF_COOKIE_NAME = "csrf_token"
CSRF_HEADER_NAME = "X-CSRF-Token"
ACCESS_TOKEN_EXPIRES_MINUTES = 15
REFRESH_TOKEN_EXPIRES_DAYS = 14
COOKIE_SECURE = os.getenv("COOKIE_SECURE", "false").lower() == "true"
COOKIE_SAMESITE = "lax"

s3_base_url = "https://websafe.s3.us-east-2.amazonaws.com/"


def get_s3_client():
    s3_client = boto3.resource("s3")

    return s3_client


async def upload_image_to_s3(
    file_bytes: bytes,
    file_key: str,
    content_type: str,
    s3_client
) -> str:
    """
    Upload image bytes to S3 and return the public URL.
    
    Args:
        file_bytes: The image file content as bytes
        file_key: The S3 key/path for the file
        content_type: MIME type of the file
        s3_client: Boto3 S3 resource client
    
    Returns:
        str: The public URL of the uploaded image
    """
    obj = s3_client.Object("websafe", file_key)
    obj.put(Body=file_bytes, ContentType=content_type)
    return f"{s3_base_url}{file_key}"

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_current_user(
    request: Request,
    db: Annotated[Session, Depends(get_db)],
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token = request.cookies.get(ACCESS_COOKIE_NAME)
    token_from_cookie = token is not None

    if not token:
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header.split(" ", 1)[1].strip()

    if not token:
        raise credentials_exception

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
            issuer=TOKEN_ISSUER,
        )
        token_type = payload.get("type")
        user_id = payload.get("sub")
        if token_type != "access" or user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    if token_from_cookie:
        validate_csrf(request)

    try:
        user = db.get(models.User, int(user_id))
    except (TypeError, ValueError):
        raise credentials_exception

    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: Annotated[models.User, Depends(get_current_user)],
):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def require_active_subscription(current_user=Depends(get_current_active_user), db=Depends(get_db)):
    subscription = db.execute(
        select(models.Subscription).where(
            models.Subscription.user_id == current_user.id,
            models.Subscription.current_period_end > datetime.utcnow()
        )
    ).scalar_one_or_none()
    if not subscription:
        raise HTTPException(status_code=403, detail="Active subscription required")
    return subscription


def validate_csrf(request: Request):
    if request.method.upper() in {"GET", "HEAD", "OPTIONS", "TRACE"}:
        return

    csrf_cookie = request.cookies.get(CSRF_COOKIE_NAME)
    csrf_header = request.headers.get(CSRF_HEADER_NAME)

    if not csrf_cookie or not csrf_header:
        raise HTTPException(status_code=403, detail="CSRF token missing")

    if not secrets.compare_digest(csrf_cookie, csrf_header):
        raise HTTPException(status_code=403, detail="CSRF token mismatch")
