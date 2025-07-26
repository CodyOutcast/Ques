import os
import json
import requests
import logging
from fastapi import APIRouter, HTTPException  # Changed from FastAPI to APIRouter
from pydantic import BaseModel
from dotenv import load_dotenv
from utils.db_utils import store_user_tags, insert_to_vector_db

load_dotenv()
router = APIRouter()  # This is now a router, not a full app
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
DEEPSEEK_URL = "https://api.deepseek.com/v1/chat/completions"

class ProfileInput(BaseModel):
    user_id: int
    paragraph: str

def extract_tags_from_paragraph(paragraph):
    prompt = (
        f"Extract 1-5 feature tags from this paragraph: '{paragraph}'. "
        "Tags should be short phrases like 'investor', 'like coding', 'good at video editing'. "
        "Focus on the general transferable skills or project types or user types rather than specific technologies."
        "Include user types if mentioned. Output only a JSON list of tags, e.g., [\"tag1\", \"tag2\"]."
    )
    payload = {
        "model": "deepseek-chat", 
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.5
    }
    headers = {"Authorization": f"Bearer {DEEPSEEK_API_KEY}", "Content-Type": "application/json"}
    
    try:
        response = requests.post(DEEPSEEK_URL, json=payload, headers=headers)
        response.raise_for_status()
        content = response.json()['choices'][0]['message']['content']
        tags = json.loads(content)  # Expect JSON list
        if not (1 <= len(tags) <= 5):
            raise ValueError("Invalid tag count")
        return tags
    except Exception as e:
        logging.error(f"DeepSeek error: {e}")
        raise HTTPException(status_code=500, detail="Failed to extract tags")

@router.post("/summarize")  # Changed from @app.post to @router.post (no prefix needed here)
async def summarize_profile(input: ProfileInput):
    tags = extract_tags_from_paragraph(input.paragraph)
    tags_json = json.dumps(tags)  # For PG storage
    tags_text = " ".join(tags)  # Concat for VectorDB auto-embedding
    
    # Insert to VectorDB (auto-embeds)
    vector_id = insert_to_vector_db(tags_text, metadata={"user_id": input.user_id})
    
    # Store in PG
    store_user_tags(input.user_id, tags, vector_id)
    
    return {"tags": tags}