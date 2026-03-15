from fastapi import APIRouter, HTTPException
from app.dependencies import get_db
from app.models import User
from fastapi import Depends
from pydantic import BaseModel, EmailStr
from sqlmodel import select
from app.auth import get_password_hash

router = APIRouter(prefix="/users", tags=["users"])

# to make a function user this format
i = 1


class UserIn(BaseModel):
    username: str
    email: EmailStr
    plain_password: str
    first_name: str
    last_name: str
    phone: str


@router.get("/")
async def read_user():
    return [{"username": "charlie"}]


@router.get("/{user_id}")
async def get_user(user_id: int):
    return [{"user": f"user1 + {user_id}"}]


@router.post("/add-user")
async def register_user(user_in: UserIn, db=Depends(get_db)):
    # see if there is already an email or username
    prev_email = (
        db.execute(select(User).where(User.email == user_in.email))
    ).scalar_one_or_none()
    prev_username = (
        db.execute(select(User).where(User.username == user_in.username))
        .scalars()
        .first()
    )
    if prev_username or prev_email:
        return HTTPException(status_code=401)

    hashed_pwd = get_password_hash(user_in.plain_password)
    user_in.plain_password = hashed_pwd
    user_data = user_in.model_dump(exclude={"plain_password"})
    new_user = User(**user_data)
    new_user.hash_password = hashed_pwd
    new_user.stripe_customer_id = "hello"
    db.add(new_user)
    db.commit()
    return user_in
