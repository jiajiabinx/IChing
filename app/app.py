from fastapi import FastAPI, File, UploadFile, Form, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
from app import schemas, models
from app.database import SessionLocal


app = FastAPI()

# DB depdendency

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Mount the React build folder as a static directory
app.mount("/static", StaticFiles(directory="build/static"), name="static")

# Set up Jinja2 templates
templates = Jinja2Templates(directory="templates")


@app.get("/")
async def serve_frontend(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.put("/api/users")
async def create_user(user: schemas.Users, db: Session = Depends(get_db)):
    db_user = models.Users(**user.model_dump())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return {"message": "User created successfully"}



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)