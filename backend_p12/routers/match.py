# routers/match.py
# Page 2: AI Search page - extract tags from user query and find similar projects/users

import os
import json
import requests
import logging
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from dotenv import load_dotenv
from db_utils import query_vector_db, get_user_infos, embed_text, get_user_history
from dependencies.auth import get_current_user

load_dotenv()
router = APIRouter()
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
DEEPSEEK_URL = "https://api.deepseek.com/v1/chat/completions"

class SearchInput(BaseModel):
    query: str  # User's description of what they're looking for

def extract_feature_tags_from_query(query):
    """
    Use DeepSeek API to extract 1-5 feature tags from user's search query.
    Focus on general transferable skills rather than specific expertise.
    """
    prompt = (
        f"Extract 1-5 feature tags from this user search query: '{query}'. "
        "The user is looking for projects to invest in, project ideas, or partners. "
        "Tags should be general transferable skills or interests like 'Investor', 'AI enthusiast', "
        "'good at coding', 'marketing expert', 'startup founder', etc. "
        "Focus on skills, roles, and general interests rather than specific technologies. "
        "Output only a JSON list of tags, e.g., [\"tag1\", \"tag2\"]."
    )
    
    payload = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3,
        "max_tokens": 100
    }
    headers = {"Authorization": f"Bearer {DEEPSEEK_API_KEY}", "Content-Type": "application/json"}
    
    try:
        response = requests.post(DEEPSEEK_URL, json=payload, headers=headers)
        response.raise_for_status()
        content = response.json()['choices'][0]['message']['content']
        
        # Clean the content and parse JSON
        content = content.strip()
        if content.startswith('```json'):
            content = content[7:]
        if content.endswith('```'):
            content = content[:-3]
        content = content.strip()
        
        tags = json.loads(content)
        if not isinstance(tags, list) or not (1 <= len(tags) <= 5):
            raise ValueError("Invalid tag format or count")
        return tags
        
    except Exception as e:
        logging.error(f"DeepSeek API error: {e}")
        raise HTTPException(status_code=500, detail="Failed to extract tags from query")

@router.post("/query")
async def ai_search(search_input: SearchInput, current_user: dict = Depends(get_current_user)):
    """
    AI Search endpoint for Page 2.
    Takes user's search query, extracts feature tags using DeepSeek API,
    and returns 20 most similar results from vector database.
    """
    user_id = current_user["id"]
    
    try:
        # Extract feature tags from the search query
        tags = extract_feature_tags_from_query(search_input.query)
        logging.info(f"Extracted tags for user {user_id}: {tags}")
        
        # Convert tags to text for embedding
        tags_text = " ".join(tags)
        
        # Embed the tags locally
        query_vector = embed_text(tags_text)
        
        # Get user's history to filter out already seen results
        seen_ids = get_user_history(user_id)
        
        # Query VectorDB for similar profiles/projects (get more to account for filtering)
        similar_ids = query_vector_db(query_vector, top_k=50)
        
        # Filter out seen results and the user themselves
        filtered_ids = [id for id in similar_ids if id != str(user_id) and id not in seen_ids]
        
        # Take top 20 after filtering
        result_ids = filtered_ids[:20]
        
        if not result_ids:
            return {
                "query": search_input.query,
                "extracted_tags": tags,
                "results": [],
                "message": "No new results found for your search. Try different keywords!"
            }
        
        # Fetch user/project infos from PostgreSQL
        results = get_user_infos(result_ids)
        
        logging.info(f"AI search by user {user_id} returned {len(results)} results")
        
        return {
            "query": search_input.query,
            "extracted_tags": tags,
            "results": results,
            "total_found": len(results)
        }
        
    except Exception as e:
        logging.error(f"Error in AI search for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Search failed")