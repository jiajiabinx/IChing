from fastapi import APIRouter, HTTPException
from typing import List
from app import models, schemas

router = APIRouter(
    prefix="/api/users",
    tags=["users"]
)

    

@router.get("/{user_id}", response_model=schemas.Users)
async def get_user(user_id: int) -> schemas.Users:
    try:
        user = models.get_user_by_id(user_id)
        if user and not user.get('display_name'):
            user['display_name'] = "Anonymous User " +user['user_id']
        return user
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/", response_model=schemas.Users)
async def create_user(user: schemas.UserCreate) -> schemas.Users:
    try:
        created_user = models.insert_user(user.dict())
        return created_user
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{user_id}", response_model=schemas.Users)
async def update_user(user: schemas.Users) -> schemas.Users:
    try:
        updated_user = models.update_user(user.model_dump())
        return updated_user
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{user_id}")
async def delete_user(user_id: int):
    try:
        models.delete_user(user_id)
        return {"message": "User deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))