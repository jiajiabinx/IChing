from fastapi import APIRouter, HTTPException, Request
from fastapi.templating import Jinja2Templates
from typing import Dict, List
from app import models, schemas
import json
import os
import anthropic
from app.routers import reference


router = APIRouter(
    prefix="/api/story",
    tags=["story"]
)
templates = Jinja2Templates(directory="templates")



@router.get("/gua")
async def tui_suan(payment_token: schemas.CompletedPayment) -> schemas.DisplayStory:
    check = models.check_payment(payment_token)
    if not check:
        raise HTTPException(status_code=400, detail="Payment not found")

    
    #get biography
    biography = await create_biography(payment_token)
    
    #find referennce
    wiki_references = models.get_random_wiki_references(3)
    wiki_references_str = json.dumps(wiki_references)
    
    client = anthropic.Anthropic(
        api_key=os.environ["CLAUDE_API_KEY"],
    )
    
    message = client.messages.create(
    model="claude-3-5-sonnet-20240620",
    max_tokens=1000,
    temperature=0,
    system="""Pretend that you are a historian and fortune teller. 
    You will be given a biography of a person. 
    You will use your vast knowledge of human history and pattern finding skills to write a short predictive story about their life.
    Pretend that the three historical figure and their stories are some of the most similar life trajectories to the person in question.
    You will use the biography to determine which three historical figures are most similar to the person in question.
    You will then use the biography to weave a short story using the life trajectories of the three historical figures.
    The story should be 1000 words or less.
    You do not need to respond with pleasantry. \n """,
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": biography
                },
                {
                    "type": "text",
                    "text": wiki_references_str
                }
            ]
        }
    ]
    )
    story_text = message.content[0].text
    #generate story
    display_story = models.insert_display_story(payment_token.transaction_id, story_text, wiki_references_str, "")
    return display_story

@router.put("/biography")
async def create_biography(payment_token: schemas.CompletedPayment) -> schemas.TempStory:
    user = models.get_user_by_id(payment_token.user_id)
    user_str = json.dumps(user)
    temp_story = models.insert_temp_story(payment_token.transaction_id, user_str)
    return temp_story

@router.get("/biography")
async def get_biography(story_id: int) -> schemas.TempStory:
    temp_story = models.get_temp_story(story_id)
    return temp_story


@router.get('/display')
async def get_story(story_id: int) -> schemas.DisplayStory:
    display_story = models.get_display_story(story_id)
    return display_story

