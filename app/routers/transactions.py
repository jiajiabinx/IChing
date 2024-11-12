from fastapi import APIRouter, HTTPException
from typing import List
from app import models, schemas

router = APIRouter(
    prefix="/api/transactions",
    tags=["transactions"]
)

@router.post("/APICall")
async def record_APICall(transaction: schemas.APICall):
    models.record_APICall(transaction.model_dump())
    return {"message": "APICall recorded successfully"}

@router.post("/SBERTCall")
async def record_SBERTCall(transaction: schemas.SBERTCall):
    models.record_SBERTCall(transaction.model_dump())
    return {"message": "SBERTCall recorded successfully"}

