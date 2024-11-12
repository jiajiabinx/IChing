from fastapi import APIRouter, HTTPException
from typing import List
from app import models, schemas

router = APIRouter(
    prefix="/api/users",
    tags=["users"]
)

@router.put("/")
async def create_user(user: schemas.UserCreate) -> schemas.Users:
    user = models.insert_user(user.model_dump())
    return user

@router.get("/{user_id}/friends", response_model=List[schemas.Users])
async def get_friends(user_id: int):
    friends = models.get_user_friends(user_id)
    return friends

@router.delete("/{user_id}")
async def delete_user(user_id: int):
    models.delete_user(user_id)
    return {"message": "User deleted successfully"} 