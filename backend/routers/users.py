from fastapi import APIRouter

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

# to make a function user this format

@router.get("/")
async def read_user():
    return [{"username": "charlie"}]
