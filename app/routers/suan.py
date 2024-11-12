from fastapi import APIRouter, HTTPException
from typing import List
from app import models, schemas

router = APIRouter(
    prefix="/api/suan",
    tags=["suan"]
)

@router.post("/{user_id}")
async def suan(user_id: int, transaction: schemas.InitiatedTransaction):

    transaction_data = transaction.model_dump()
    user = models.get_user_by_id(user_id)
    references = models.yun_suan(user, 3)
    models.record_APICall(user,references,transaction_data)
    
    return {"message": "APICall recorded successfully"}



