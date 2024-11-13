from fastapi import APIRouter, HTTPException, Request
from fastapi.templating import Jinja2Templates
from typing import Dict, List
from app.routers import friends
from app import models,schemas


router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/sessions/{user_id}")
async def get_historical_sessions( user_id: int, response_model=List[schemas.HistoricalSession]):
    sessions = models.get_user_historical_sessions(user_id)
    return sessions


@router.get("/dashboard/{user_id}")
async def show_dashboard(request: Request, user_id: int):
    try:
        # Get user data
        user = models.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get user's friends
        user_friends = models.get_user_friends(user_id)
        print(user_friends)
        
        # Get discover friends (non-friends)
        discover_friends = await friends.discover_friends(user_id)
        
        # Get user's historical sessions
        user_history = await get_historical_sessions(user_id)
        
        return templates.TemplateResponse(
            "dashboard.html",
            {
                "request": request,
                "user": user,
                "friends": user_friends,
                "discover_friends": discover_friends,
                "user_history": user_history
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 