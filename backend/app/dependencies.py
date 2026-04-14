from app.database import SessionLocal

from typing import Annotated
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer
from fastapi import HTTPException, status, Depends
from pydantic import BaseModel
from app import models
from sqlalchemy.orm import Session
from app.schemas import User, TokenData
import boto3


# These dependencies are what the routes will pull from
# for ex., the functions will ask for a connection to the database; that comes from here

ALGORITHM = "HS256"
SECRET_KEY = "asdf"

s3_base_url = "https://websafe.s3.us-east-2.amazonaws.com/"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/token")


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
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[Session, Depends(get_db)],
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = (
        db.query(models.User)
        .filter(models.User.username == token_data.username)
        .first()
    )
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
