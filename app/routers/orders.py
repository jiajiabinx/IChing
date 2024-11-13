from fastapi import APIRouter, HTTPException
from app import models, schemas

router = APIRouter(
    prefix="/api/orders",
    tags=["orders"]
)

@router.post("/create_order", response_model=schemas.Order)
async def create_order(order: schemas.OrderCreate):
    try:
        created_order = models.insert_order(order.user_id, order.amount)
        return {"message": "Order created successfully", "order_id": created_order[0]}
    # or we could return the full order object with all fields, like return created_order
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))