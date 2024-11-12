from fastapi import FastAPI, HTTPException, File, UploadFile, Form, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse
from typing import List, Optional
import uvicorn
from app import schemas, models


app = FastAPI()

# Set up Jinja2 templates
templates = Jinja2Templates(directory="templates")



@app.get("/")
async def serve_frontend(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.put("/api/users")
async def create_user(user: schemas.UserCreate) -> schemas.Users:
    user = models.insert_user(user.model_dump())
    return user

@app.post("/api/friends")
async def add_friend(friend: schemas.FriendCreate) -> schemas.Friend:
    try:
        friend = models.insert_friend(friend.user_id_left, friend.user_id_right)
        return friend
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/users/{user_id}/friends")
async def get_friends(user_id: int, response_model=List[schemas.Users]):
    friends = models.get_user_friends(user_id)
    return friends

@app.delete("/api/users/{user_id}")
async def delete_user(user_id: int):
    models.delete_user(user_id)
    return {"message": "User deleted successfully"}

@app.post("/api/orders")
async def create_order(order: schemas.OrderCreate):
    try:
        order_id = models.insert_order(order.user_id, order.amount)
        return {"message": "Order created successfully", "order_id": order_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/users/{user_id}/order_status")
async def check_order_status(user_id: int):
    has_order = models.check_user_order(user_id)
    return {"has_order": has_order}

@app.post("/api/orders/{order_id}/session")
async def create_session(order_id: int):
    try:
        session_id = models.create_session_for_order(order_id)
        return {"message": "Session created successfully", "session_id": session_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/payments")
async def record_payment(payment: schemas.PaidBy):
    try:
        models.record_payment(payment.user_id, payment.order_id, payment.session_id)
        return {"message": "Payment recorded successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)