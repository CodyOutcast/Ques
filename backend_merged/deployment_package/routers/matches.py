# routers/match.py
# Page 2: AI Search page - extract tags from user query and find similar projects/users

import os
import json
import requests
import logging
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from dotenv import load_dotenv
from dependencies.auth import get_current_user

# Try to import db_utils, handle gracefully if not available
try:
    from db_utils import query_vector_db, get_user_infos, embed_text, get_user_history, get_random_unseen_users
    DB_UTILS_AVAILABLE = True
except ImportError as e:
    logging.warning(f"db_utils not available: {e}")
    DB_UTILS_AVAILABLE = False

load_dotenv()
router = APIRouter()
logger = logging.getLogger(__name__)
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
DEEPSEEK_URL = "https://api.deepseek.com/v1/chat/completions"

class SearchInput(BaseModel):
    query: str  # User's description of what they're looking for

def extract_feature_tags_from_query(query):
    """
    Use DeepSeek API to extract 1-5 feature tags from user's search query.
    Focus on general transferable skills rather than specific expertise.
    """
    if not DEEPSEEK_API_KEY:
        logger.error("DeepSeek API key not configured")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="AI search service not configured"
        )
    
    try:
        logger.info(f"Extracting tags from query: {query[:100]}...")
        
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
            "temperature": 0.5,
            "max_tokens": 500
        }
        headers = {"Authorization": f"Bearer {DEEPSEEK_API_KEY}", "Content-Type": "application/json"}
        
        response = requests.post(DEEPSEEK_URL, json=payload, headers=headers, timeout=30)
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
            
        logger.info(f"Extracted tags: {tags}")
        return tags
        
    except requests.exceptions.RequestException as e:
        logger.error(f"DeepSeek API request error: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI search service temporarily unavailable"
        )
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse DeepSeek response: {e}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Invalid response from AI search service"
        )
    except Exception as e:
        logger.error(f"DeepSeek API error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to extract tags from query"
        )

async def get_search_fallback_results(user_id: int, seen_ids: list, needed_count: int):
    """
    Fallback strategy for AI search when user has seen most relevant profiles.
    Returns random unseen profiles to ensure search results are always available.
    """
    try:
        # Get random users that haven't been seen yet
        fallback_ids = get_random_unseen_users(user_id, seen_ids, needed_count)
        
        logging.info(f"Search fallback strategy provided {len(fallback_ids)} random unseen results for user {user_id}")
        return fallback_ids
        
    except Exception as e:
        logging.error(f"Error in search fallback strategy for user {user_id}: {e}")
        return []

@router.post("/query")
async def ai_search(search_input: SearchInput, current_user: dict = Depends(get_current_user)):
    """
    AI Search endpoint for Page 2.
    Takes user's search query, extracts feature tags using DeepSeek API,
    and returns 20 most similar results from vector database.
    Uses progressive expansion strategy to ensure results are always available.
    """
    user_id = current_user["id"]
    
    if not DB_UTILS_AVAILABLE:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Vector database services are currently unavailable"
        )
    
    try:
        logger.info(f"AI search for user {user_id}: {search_input.query[:100]}...")
        
        # Extract feature tags from the search query
        tags = extract_feature_tags_from_query(search_input.query)
        logging.info(f"Extracted tags for user {user_id}: {tags}")
        
        # Convert tags to text for embedding
        tags_text = " ".join(tags)
        
        # Embed the tags locally
        query_vector = embed_text(tags_text)
        
        # Get user's history to filter out already seen results
        seen_ids = get_user_history(user_id)
        
        # Progressive search strategy: start with most relevant, expand if needed
        target_results = 20
        max_attempts = 3
        search_sizes = [50, 150, 300]  # Progressively larger searches
        
        filtered_ids = []
        
        for attempt, search_size in enumerate(search_sizes):
            # Query VectorDB for similar profiles/projects
            similar_ids = query_vector_db(query_vector, top_k=search_size)
            
            # Filter out seen results and the user themselves
            filtered_ids = [id for id in similar_ids if id != str(user_id) and id not in seen_ids]
            
            logging.info(f"AI search attempt {attempt + 1}: Found {len(filtered_ids)} unseen results from top {search_size} similar profiles")
            
            # If we have enough results, break early
            if len(filtered_ids) >= target_results:
                break
                
            # If this is our last attempt and we still don't have enough, use fallback
            if attempt == max_attempts - 1 and len(filtered_ids) < target_results:
                logger.warning(f"AI search for user {user_id} has exhausted similar profiles. Using fallback strategy.")
                fallback_ids = await get_search_fallback_results(user_id, seen_ids, target_results - len(filtered_ids))
                filtered_ids.extend(fallback_ids)
                break
        
        # Take top 20 after filtering
        result_ids = filtered_ids[:target_results]
        
        if not result_ids:
            logger.info(f"No search results available for user {user_id}")
            return {
                "query": search_input.query,
                "extracted_tags": tags,
                "results": [],
                "message": "You've explored most profiles matching this search! Try different keywords or check back later for new users."
            }
        
        # Fetch user/project infos from PostgreSQL
        results = get_user_infos(result_ids)
        
        logger.info(f"AI search by user {user_id} returned {len(results)} results")
        
        return {
            "query": search_input.query,
            "extracted_tags": tags,
            "results": results,
            "total_found": len(results)
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions (from tag extraction)
        raise
    except Exception as e:
        logger.error(f"Error in AI search for user {user_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Search failed"
        )
