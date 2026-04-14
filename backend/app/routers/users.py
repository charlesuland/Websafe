from fastapi import APIRouter, HTTPException, status
from app.dependencies import get_db
from app.models import User, Vendor
from fastapi import Depends
from pydantic import BaseModel, EmailStr
from sqlmodel import select
from app.auth import get_password_hash
from app.database import SessionLocal

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
    
    if prev_email:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with that email already exists"
        )
    
    if prev_username:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="That username is already taken"
        )



    hashed_pwd = get_password_hash(user_in.plain_password)
    #user_in.plain_password = hashed_pwd
    user_data = user_in.model_dump(exclude={"plain_password"})
    new_user = User(**user_data)
    new_user.hash_password = hashed_pwd
    new_user.stripe_customer_id = "test"
    db.add(new_user)
    db.commit()


    # automatically creates a vendor record for the user
    # router requires every user to have a vendor before it can make a project
    new_vendor = Vendor(
        business_name=new_user.username,
        email=new_user.email,
        owner=new_user.id,
        phone=new_user.phone,
        stripe_connect_id="",
        payouts_enabled=False,
        requirements_due_for_payment=""
    )
    db.add(new_vendor)
    db.commit()
    
    return {"message": "Account created successfully.", "username": new_user.username}