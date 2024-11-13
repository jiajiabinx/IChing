from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Dict
from app import models, schemas
from app.routers import users
from app.dependencies import templates

router = APIRouter(
)

class LoginForm(BaseModel):
    user_id: int

class SignupResponse(BaseModel):
    status: str
    user_id: int
    message: str

@router.get("/")
async def show_login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/login")
async def login(login_form: LoginForm):
    try:
        # Verify user exists
        user = await models.get_user_by_id(login_form.user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return {
            "status": "success",
            "redirect_url": f"/dashboard/{login_form.user_id}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/signup")
async def signup(sign_up_form: schemas.UserCreate) -> SignupResponse:
    try:
        user = await users.create_user(sign_up_form)        
        return SignupResponse(
            status="success",
            user_id=user['user_id'],
            message="User created successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
