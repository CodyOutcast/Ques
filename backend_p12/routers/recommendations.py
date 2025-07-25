# routers/recommendations.py
# Page 1: Recommendation/Home page - serves 20 most relevant cards for swiping

import os
import json
import logging
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from dotenv import load_dotenv
from db_utils import query_vector_db, get_user_infos, embed_text, get_user_vector, get_user_history
from dependencies.auth import get_current_user

load_dotenv()
router = APIRouter()

class SwipeInput(BaseModel):
    card_id: int  # ID of the card being swiped
    is_like: bool  # True for like (swipe right), False for dislike (swipe left)

@router.get("/cards")
async def get_recommendation_cards(current_user: dict = Depends(get_current_user)):
    """
    Get 20 most relevant cards for the user to swipe on.
    Cards are determined by similar vectors compared to this user's profile.
    Filters out cards that have been used before based on history.
    """
    user_id = current_user["id"]
    
    try:
        # Get user's vector from their profile
        user_vector = get_user_vector(user_id)
        if not user_vector:
            raise HTTPException(status_code=404, detail="User vector not found. Please complete your profile first.")
        
        # Get user's history to filter out already seen cards
        seen_card_ids = get_user_history(user_id)
        
        # Query vector DB for similar profiles (top 50 to account for filtering)
        similar_ids = query_vector_db(user_vector, top_k=50)
        
        # Filter out seen cards and the user themselves
        filtered_ids = [id for id in similar_ids if id != str(user_id) and id not in seen_card_ids]
        
        # Take top 20 after filtering
        card_ids = filtered_ids[:20]
        
        if not card_ids:
            return {"cards": [], "message": "No new cards available. Check back later!"}
        
        # Get user infos for these cards
        cards = get_user_infos(card_ids)
        
        logging.info(f"Served {len(cards)} cards to user {user_id}")
        return {"cards": cards}
        
    except Exception as e:
        logging.error(f"Error getting recommendations for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get recommendations")

@router.post("/swipe")
async def handle_swipe(swipe: SwipeInput, current_user: dict = Depends(get_current_user)):
    """
    Handle user swipe action (like or dislike).
    Stores the action in the database so the card won't appear again.
    """
    user_id = current_user["id"]
    
    try:
        # Store the swipe action in likes table
        from db_utils import store_swipe_action
        store_swipe_action(
            liker_id=user_id,
            liked_item_id=swipe.card_id,
            liked_item_type="profile",
            is_like=swipe.is_like
        )
        
        action = "liked" if swipe.is_like else "disliked"
        logging.info(f"User {user_id} {action} card {swipe.card_id}")
        
        return {"message": f"Card {action} successfully", "card_id": swipe.card_id}
        
    except Exception as e:
        logging.error(f"Error handling swipe for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to process swipe")
