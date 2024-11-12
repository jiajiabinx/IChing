from fastapi import APIRouter, HTTPException
from app import models, schemas

router = APIRouter(
    prefix="/api/orders",
    tags=["orders"]
)

@router.post("/")
async def create_order(order: schemas.OrderCreate):
    try:
        order_id = models.insert_order(order.user_id, order.amount)
        return {"message": "Order created successfully", "order_id": order_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{user_id}/order_status")
async def check_order_status(user_id: int):
    has_order = models.check_user_order(user_id)
    return {"has_order": has_order}

@router.post("/{order_id}/session")
async def create_session(order_id: int):
    try:
        session_id = models.create_session_for_order(order_id)
        return {"message": "Session created successfully", "session_id": session_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) 