from fastapi import APIRouter
from app.dependencies import get_db

router = APIRouter(prefix="/users", tags=["users"])

# to make a function user this format


@router.get("/")
async def read_user():
    return [{"username": "charlie"}]


@router.get("/{user_id}")
async def get_user(user_id: int):
    return [{"user": f"user1 + {user_id}"}]
