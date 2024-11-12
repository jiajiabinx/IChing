from fastapi import APIRouter, HTTPException
from app import models, schemas

router = APIRouter(
    prefix="/api/friends",
    tags=["friends"]
)

@router.post("/")
async def add_friend(friend: schemas.FriendCreate) -> schemas.Friend:
    try:
        friend = models.insert_friend(friend.user_id_left, friend.user_id_right)
        return friend
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) 