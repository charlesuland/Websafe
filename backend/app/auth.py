from jose import jwt, JWTError
from datetime import datetime, timezone, timedelta
from fastapi import HTTPException, Depends, APIRouter, status
from app.dependencies import get_db
from typing import Annotated
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from app import models
from app.schemas import Token

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


@router.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[Session, Depends(get_db)],
):
    user = db.query(models.User).filter(models.User.username == form_data.username)
    if not user or not verify_password(
        plain_password=form_data.password, hashed_password=user["hashed_password"]
    ):
        return HTTPException(status_code=401)
    access_token = create_access_token({"sub": user["username"]})
    return {"access_token": access_token, "token_type": "bearer"}
