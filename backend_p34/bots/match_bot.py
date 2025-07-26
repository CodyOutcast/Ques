import os
import json
import requests
import logging
from fastapi import APIRouter, HTTPException  # Changed to APIRouter
from pydantic import BaseModel
from dotenv import load_dotenv
from utils.db_utils import query_vector_db, get_user_infos, embed_text

load_dotenv()
router = APIRouter()  # Now a router
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
DEEPSEEK_URL = "https://api.deepseek.com/v1/chat/completions"

class MatchInput(BaseModel):
    query_paragraph: str

def extract_desired_tags_from_paragraph(paragraph):
    prompt = (
        f"Extract 1-5 desired feature tags from this description of project types: '{paragraph}'. "
        "Tags should be short phrases like 'AI projects', 'investors', 'good at coding', 'video editing'. "
        "Focus on the general transferable skills or project types or user types rather than specific technologies."
        "Include user/project types if mentioned. Output only a JSON list of tags, e.g., [\"tag1\", \"tag2\"]."
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
        tags = json.loads(content)
        if not (1 <= len(tags) <= 5):
            raise ValueError("Invalid tag count")
        return tags
    except Exception as e:
        logging.error(f"DeepSeek error: {e}")
        raise HTTPException(status_code=500, detail="Failed to extract tags")

@router.post("/summarize")  # Use router, no prefix
async def match_projects(input: MatchInput):
    tags = extract_desired_tags_from_paragraph(input.query_paragraph)
    tags_text = " ".join(tags)  # Concat for embedding
    
    # Embed locally
    query_vector = embed_text(tags_text)
    
    # Query VectorDB
    vector_ids = query_vector_db(query_vector, top_k=20)
    
    # Fetch user infos from PG
    user_infos = get_user_infos(vector_ids)
    
    return {"matches": user_infos}