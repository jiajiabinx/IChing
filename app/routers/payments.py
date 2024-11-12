from fastapi import APIRouter, HTTPException
from app import models, schemas

router = APIRouter(
    prefix="/api/payments",
    tags=["payments"]
)

@router.post("/")
async def record_payment(payment: schemas.CompletedPayment):
    try:
        models.record_payment(payment.user_id, payment.order_id, payment.session_id)
        return {"message": "Payment recorded successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) 