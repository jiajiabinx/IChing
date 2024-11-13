from fastapi import APIRouter, HTTPException, Request
from fastapi.templating import Jinja2Templates
from typing import Dict, List
from app import models, schemas
import json
import os
import anthropic
from app.routers import reference
from app.dependencies import templates


router = APIRouter(
    prefix="/api/story",
    tags=["story"]
)

@router.post('/yunsuan')
async def yun_suan(payment_token: schemas.CompletedPayment) -> schemas.TempStory:
    check = models.check_payment(payment_token.user_id, 
                                 payment_token.session_id, 
                                 payment_token.order_id)
    if not check:
        raise HTTPException(status_code=400, detail="Payment not found")
    #get biography
    corpus = await create_biography(payment_token)
    
    #find referennce
    #do a fake sbert call
    sbert_call = models.record_sbert_call(corpus)
    wiki_references = models.get_random_wiki_references(3)
    wiki_reference_ids = [r.wiki_page_id for r in wiki_references]
    
    #record identified relationships
    identified_relationships = models.record_identified_relationships(corpus.story_id, wiki_reference_ids)
    
    #record referred relationship
    referred_relationships = models.record_referred_relationship(corpus.story_id, sbert_call.transaction_id)
    return corpus

@router.post("/tuisuan")
async def tui_suan(payment_token: schemas.CompletedPayment) -> schemas.DisplayStory:
    check = models.check_payment(payment_token.user_id, 
                                 payment_token.session_id, 
                                 payment_token.order_id)
    if not check:
        raise HTTPException(status_code=400, detail="Payment not found")

    wiki_references = models.get_identified_references_by_session_id(payment_token.session_id)
    biography = await get_biography(wiki_references[0].story_id)
    wiki_references = [schemas.WikiReference(**r) for r in wiki_references]
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
    temp_story = models.insert_temp_story(user_str)
    return temp_story

@router.get("/biography")
async def get_biography(story_id: int) -> schemas.TempStory:
    temp_story = models.get_temp_story(story_id)
    return temp_story



