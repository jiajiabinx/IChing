from fastapi import APIRouter, HTTPException
from app import models, schemas
from typing import List
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
    
    
@router.get("/{user_id}")
async def get_friends(user_id: int) -> List[schemas.Friend]:
    friends = models.get_user_friends(user_id)
    return friends


@router.get("/discover/{user_id}")
async def discover_friends(user_id: int) -> List[schemas.Users]:
    friends_ids = [friend[0] for friend in models.get_user_friends(user_id)]
    exclude_ids = friends_ids + [user_id]
    discover = models.get_random_users(exclude_ids)
    return discover