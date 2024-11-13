from fastapi import APIRouter, HTTPException
from typing import List
from app import models, schemas

router = APIRouter(
    prefix="/api/users",
    tags=["users"]
)

@router.put("/", response_model=schemas.Users)
async def create_user(user: schemas.UserCreate) -> schemas.Users:
    try:
        created_user = models.insert_user(user.dict())
        return created_user
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{user_id}/friends", response_model=List[schemas.Users])
async def get_friends(user_id: int):
    try:
        friends = models.get_user_friends(user_id)
        return friends
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{user_id}")
async def delete_user(user_id: int):
    try:
        models.delete_user(user_id)
        return {"message": "User deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))