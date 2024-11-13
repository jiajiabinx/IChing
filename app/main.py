from fastapi import FastAPI, Request, Path, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
import random
from app.routers import users, friends, orders, payments, dashboard, auth
import app.models as models
import app.schemas as schemas
import asyncio
from typing import List

app = FastAPI()

base_url = "http://127.0.0.1:8000"

# Set up Jinja2 templates
templates = Jinja2Templates(directory="templates")
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this to your needs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/dashboard/{user_id}")
async def get_dashboard(request: Request, user_id: int):
    return templates.TemplateResponse(
            "dashboard.html",
            {
                "request": request,
                "user_id": user_id,
                "base_url": base_url 
            }
        )


@app.get("/sessions/{user_id}")
async def get_historical_sessions( user_id: int, response_model=List[schemas.HistoricalSession]):
    sessions = models.get_user_historical_sessions(user_id)
    return sessions

@app.get("/confirm")
async def confirm_order(request: Request):
    amount = request.query_params.get('amount')
    order_id = request.query_params.get('order_id')
    return templates.TemplateResponse(
        "payment_confirm.html",
        {"request": request, 
         "amount": amount, 
         "order_id": order_id,
         "base_url": base_url}
    )

# Include routers for the API
app.include_router(users.router)
app.include_router(friends.router)
app.include_router(orders.router)
app.include_router(payments.router)
app.include_router(dashboard.router)
app.include_router(auth.router)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)