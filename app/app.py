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
templates = Jinja2Templates(directory="build")


@app.get("/")
async def serve_frontend(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# @app.post("/api/submit_form")
# async def submit_form(
#     dob: str = Form(...),
#     pronouns: str = Form(...),
#     education: str = Form(...),
#     institutions: str = Form(...),
#     parents_professions: str = Form(...),
#     file: Optional[UploadFile] = File(None)
# ):
#     form_data = FormData(
#         dob=dob,
#         pronouns=pronouns,
#         education=education,
#         institutions=institutions,
#         parents_professions=parents_professions
#     )
    
#     # Here you would typically save the form_data to a database
#     print(f"Received form data: {form_data}")
    
#     if file:
#         # Here you would typically save the file to a storage system
#         print(f"Received file: {file.filename}")
    
#     return {"message": "Form submitted successfully"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)