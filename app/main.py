from fastapi import FastAPI, Request, Path, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
import random
from app.routers import users, friends, orders, payments
import app.models as models
import app.schemas as schemas
import asyncio
from typing import List

app = FastAPI()

# Set up Jinja2 templates
templates = Jinja2Templates(directory="templates")

HISTORICAL_FIGURES = [
    {
        "name": "Ada Lovelace",
        "years": "1815-1852",
        "description": "The world's first computer programmer, who wrote the first algorithm for Babbage's Analytical Engine."
    },
    {
        "name": "Nikola Tesla",
        "years": "1856-1943",
        "description": "Pioneer of modern electricity, known for his contributions to AC electrical systems."
    },
    {
        "name": "Marie Curie",
        "years": "1867-1934",
        "description": "First person to win Nobel Prizes in two sciences, discovered polonium and radium."
    },
    {
        "name": "Alan Turing",
        "years": "1912-1954",
        "description": "Father of computer science and artificial intelligence, broke the Enigma code."
    },
    {
        "name": "Grace Hopper",
        "years": "1906-1992",
        "description": "Pioneer of computer programming, developed the first compiler and COBOL language."
    }
]
# main file to just serve the frontend
@app.get("/")
async def serve_frontend(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})



@app.get("/confirm")
async def payment_confirmation(request: Request):
    return templates.TemplateResponse(
        "payment_confirm.html",
        {"request": request, "amount": 5.00}
    )
    
@app.post("/process")
async def process_payment(request: Request):
    # In a real application, you would process the payment here
    # For now, we'll just redirect to the story page
    return {"redirect_url": "/story"}

@app.get("/story")
async def show_story(request: Request):
    # Simulate some loading time (you can remove this in production)
    await asyncio.sleep(5)
    
    # Randomly select 3 historical figures
    selected_figures = random.sample(HISTORICAL_FIGURES, 3)
    return templates.TemplateResponse(
        "story.html",
        {
            "request": request,
            "figures": selected_figures
        }
    )

@app.get("/sessions/{user_id}")
async def get_historical_sessions( user_id: int, response_model=List[schemas.HistoricalSession]):
    sessions = models.get_user_historical_sessions(user_id)
    return sessions


# Include routers for the API
app.include_router(users.router)
app.include_router(friends.router)
app.include_router(orders.router)
app.include_router(payments.router)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)