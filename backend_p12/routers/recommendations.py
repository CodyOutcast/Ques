# routers/recommendations.py
# Page 1: Recommendation/Home page - serves 20 most relevant cards for swiping

import os
import json
import logging
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from dotenv import load_dotenv
from db_utils import query_vector_db, get_user_infos, embed_text, get_user_vector, get_user_history, get_random_unseen_users
from dependencies.auth import get_current_user

load_dotenv()
router = APIRouter()
logger = logging.getLogger(__name__)

class SwipeInput(BaseModel):
    card_id: int  # ID of the card being swiped
    is_like: bool  # True for like (swipe right), False for dislike (swipe left)

async def get_fallback_cards(user_id: int, seen_card_ids: list, needed_count: int):
    """
    Fallback strategy when user has seen most similar profiles.
    Returns random unseen profiles to ensure cards are always available.
    """
    try:
        # Get random users that haven't been seen yet
        fallback_ids = get_random_unseen_users(user_id, seen_card_ids, needed_count)
        
        logger.info(f"Fallback strategy provided {len(fallback_ids)} random unseen cards for user {user_id}")
        return fallback_ids
        
    except Exception as e:
        logging.error(f"Error in fallback strategy for user {user_id}: {e}")
        return []

@router.get("/cards")
async def get_recommendation_cards(current_user: dict = Depends(get_current_user)):
    """
    Get 20 most relevant cards for the user to swipe on.
    Cards are determined by similar vectors compared to this user's profile.
    Filters out cards that have been used before based on history.
    Uses progressive expansion strategy to ensure cards are always available.
    """
    user_id = current_user["id"]
    
    try:
        logger.info(f"Getting recommendation cards for user {user_id}")
        
        # Get user's vector from their profile
        user_vector = get_user_vector(user_id)
        if not user_vector:
            logger.warning(f"User vector not found for user {user_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="User vector not found. Please complete your profile first."
            )
        
        # Get user's history to filter out already seen cards
        seen_card_ids = get_user_history(user_id)
        logger.info(f"User {user_id} has seen {len(seen_card_ids)} cards previously")
        
        # Progressive search strategy: start with most similar, expand if needed
        target_cards = 20
        max_attempts = 3
        search_sizes = [50, 150, 300]  # Progressively larger searches
        
        filtered_ids = []
        
        for attempt, search_size in enumerate(search_sizes):
            # Query vector DB for similar profiles
            similar_ids = query_vector_db(user_vector, top_k=search_size)
            
            # Filter out seen cards and the user themselves
            filtered_ids = [id for id in similar_ids if id != str(user_id) and id not in seen_card_ids]
            
            logger.info(f"Attempt {attempt + 1}: Found {len(filtered_ids)} unseen cards from top {search_size} similar profiles")
            
            # If we have enough cards, break early
            if len(filtered_ids) >= target_cards:
                break
                
            # If this is our last attempt and we still don't have enough, use fallback
            if attempt == max_attempts - 1 and len(filtered_ids) < target_cards:
                logger.warning(f"User {user_id} has seen most similar profiles. Using fallback strategy.")
                fallback_ids = await get_fallback_cards(user_id, seen_card_ids, target_cards - len(filtered_ids))
                filtered_ids.extend(fallback_ids)
                break
        
        # Take top 20 after filtering
        card_ids = filtered_ids[:target_cards]
        
        if not card_ids:
            logger.info(f"No cards available for user {user_id}")
            return {
                "cards": [], 
                "message": "You've explored most available profiles! New users are joining daily - check back soon for fresh matches!"
            }
        
        # Get user infos for these cards
        cards = get_user_infos(card_ids)
        
        logger.info(f"Served {len(cards)} cards to user {user_id}")
        return {"cards": cards}
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error getting recommendation cards for user {user_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get recommendation cards. Please try again later."
        )
    except Exception as e:
        logger.error(f"Error getting recommendations for user {user_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get recommendations"
        )

@router.post("/swipe")
async def handle_swipe(swipe: SwipeInput, current_user: dict = Depends(get_current_user)):
    """
    Handle user swipe action (like or dislike).
    Stores the action in the database so the card won't appear again.
    """
    user_id = current_user["id"]
    
    try:
        logger.info(f"Processing swipe for user {user_id}: card {swipe.card_id}, like: {swipe.is_like}")
        
        # Store the swipe action in likes table
        from db_utils import store_swipe_action
        store_swipe_action(
            liker_id=user_id,
            liked_item_id=swipe.card_id,
            liked_item_type="profile",
            is_like=swipe.is_like
        )
        
        action = "liked" if swipe.is_like else "disliked"
        logger.info(f"User {user_id} {action} card {swipe.card_id}")
        
        return {"message": f"Card {action} successfully", "card_id": swipe.card_id}
        
    except Exception as e:
        logger.error(f"Error handling swipe for user {user_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process swipe"
        )
