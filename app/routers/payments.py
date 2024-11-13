from fastapi import APIRouter, HTTPException
from app import models, schemas

router = APIRouter(
    prefix="/api/payments",
    tags=["payments"]
)
    
@router.post("/confirm", response_model=schemas.CompletedPayment)
async def record_payment(payment: schemas.CompletedPayment):
    """
    Endpoint to confirm a payment. Creates a session and a CompletedPayment entry.
    """
    try:
        completed_payment = models.record_payment(payment.user_id, payment.order_id)
        return {"message": "Payment recorded successfully"}
    #or return completed_payment  
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))