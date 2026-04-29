from jose import jwt, JWTError
from datetime import datetime, timezone, timedelta
from fastapi import HTTPException, Depends, APIRouter, status, Request
from app.dependencies import get_db
from typing import Annotated, Optional
from sqlalchemy.orm import Session
from sqlmodel import select
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from app import models
from app.schemas import Token
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="", tags=[""], dependencies=[], responses={404: {"description": "Not found"}}
)

pwd_context = CryptContext(schemes=["argon2"])

SECRET_KEY = "asdf"
EXPIRES_IN_MINUTES = 30
ALGORITHM = "HS256"


def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(plain_passowrd: str):
    return pwd_context.hash(plain_passowrd)


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=30)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# function to log security event in database
def log_security_event(
    db: Session,
    user_id: Optional[int],
    action: str,
    request: Request,
    details: str | None = None,    
):
    event = models.SecurityLog(
        user_id=user_id,
        action=action,
        details=details or request.headers.get("user-agent"),
        ip_address= request.client.host 
            if request.client 
                else None,
    )
    db.add(event)
    db.commit()





@router.post("/token", response_model=Token)
async def login_for_access_token(
    request: Request,
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
        log_security_event(
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
    
    log_security_event(
        db=db,
        user_id=user.id,
        action="login",
        request=request,
    )
 
    access_token = create_access_token({"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}
