from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
from app.routers import users, friends, orders, payments

app = FastAPI()

# Set up Jinja2 templates
templates = Jinja2Templates(directory="templates")

@app.get("/")
async def serve_frontend(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Include routers
app.include_router(users.router)
app.include_router(friends.router)
app.include_router(orders.router)
app.include_router(payments.router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)