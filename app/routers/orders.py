from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app import models, schemas

router = APIRouter(
    prefix="/api/orders",
    tags=["orders"]
)

class OrderResponse(BaseModel):
    redirect_url: str
    amount: int
    order_id: int


@router.post("/")
async def create_order(order: schemas.OrderCreate) -> OrderResponse:
    order = models.insert_order(order.amount)
    redirect_url = '/confirm'
    return OrderResponse(redirect_url=redirect_url, amount=order['amount'], order_id=order['order_id'])

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