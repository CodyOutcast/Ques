# routers/recommendations.py
# Page 1: Recommendation/Home page - serves 20 most relevant cards for swiping

import os
import json
import logging
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from dotenv import load_dotenv
from sqlalchemy import text
from db_utils import query_vector_db, get_user_infos, embed_text, get_user_vector, get_user_history, get_random_unseen_users, SessionLocal
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

@router.get("/users")
async def get_recommendation_users(current_user: dict = Depends(get_current_user)):
    """
    Get 20 most relevant user profiles for the user to swipe on.
    Users are determined by similar vectors compared to this user's profile.
    Filters out users that have been seen before based on history.
    Uses progressive expansion strategy to ensure users are always available.
    """
    user_id = current_user["id"]
    
    try:
        logger.info(f"Getting recommendation users for user {user_id}")
        
        # Get user's vector from their profile
        user_vector = get_user_vector(user_id)
        if not user_vector:
            logger.warning(f"User vector not found for user {user_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="User vector not found. Please complete your profile first."
            )
        
        # Get user's history to filter out already seen users
        seen_user_ids = get_user_history(user_id)
        logger.info(f"User {user_id} has seen {len(seen_user_ids)} users previously")
        
        # Progressive search strategy: start with most similar, expand if needed
        target_users = 20
        max_attempts = 3
        search_sizes = [50, 150, 300]  # Progressively larger searches
        
        filtered_ids = []
        
        for attempt, search_size in enumerate(search_sizes):
            # Query vector DB for similar profiles
            similar_ids = query_vector_db(user_vector, top_k=search_size)
            
            # Filter out seen users and the user themselves
            filtered_ids = [id for id in similar_ids if id != str(user_id) and id not in seen_user_ids]
            
            logger.info(f"Attempt {attempt + 1}: Found {len(filtered_ids)} unseen users from top {search_size} similar profiles")
            
            # If we have enough users, break early
            if len(filtered_ids) >= target_users:
                break
                
            # If this is our last attempt and we still don't have enough, use fallback
            if attempt == max_attempts - 1 and len(filtered_ids) < target_users:
                logger.warning(f"User {user_id} has seen most similar profiles. Using fallback strategy.")
                fallback_ids = await get_fallback_cards(user_id, seen_user_ids, target_users - len(filtered_ids))
                filtered_ids.extend(fallback_ids)
                break
        
        # Take top 20 after filtering
        user_ids = filtered_ids[:target_users]
        
        if not user_ids:
            logger.info(f"No users available for user {user_id}")
            return {
                "users": [], 
                "message": "You've explored most available profiles! New users are joining daily - check back soon for fresh matches!"
            }
        
        # Get user infos for these users
        users = get_user_infos(user_ids)
        
        logger.info(f"Served {len(users)} users to user {user_id}")
        return {"users": users}
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error getting recommendation users for user {user_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get recommendation users. Please try again later."
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

@router.get("/cards")
async def get_recommendation_cards(current_user: dict = Depends(get_current_user)):
    """
    Get project cards for browsing based on card.json structure.
    Returns project cards with rich information including owner, collaborators, 
    media, and detailed project information for the card-based interface.
    """
    user_id = current_user["id"]
    
    try:
        logger.info(f"Getting project recommendation cards for user {user_id}")
        
        # Import here to avoid circular imports
        from dependencies.db import get_db
        from sqlalchemy.orm import Session
        from sqlalchemy import text
        
        # Get database session
        db_session = next(get_db())
        
        try:
            # Query for projects with their owners and related data
            query = text("""
                SELECT 
                    p.project_id,
                    p.short_description as title,
                    p.long_description as description,
                    p.status,
                    p.created_at,
                    p.start_time,
                    u.user_id as owner_id,
                    u.name as owner_name,
                    u.bio as owner_bio,
                    u.feature_tags as owner_tags,
                    COALESCE(
                        (SELECT COUNT(*) FROM user_projects up WHERE up.project_id = p.project_id), 
                        0
                    ) as collaborators_count
                FROM projects p
                LEFT JOIN user_projects up_owner ON p.project_id = up_owner.project_id
                LEFT JOIN users u ON up_owner.user_id = u.user_id
                WHERE p.status = 'ONGOING'
                ORDER BY p.created_at DESC
                LIMIT 20
            """)
            
            result = db_session.execute(query)
            rows = result.fetchall()
            
            # Transform to card format based on card.json
            cards = []
            for row in rows:
                # Get project tags (from tags table if associated)
                tag_query = text("""
                    SELECT t.tag_name 
                    FROM tags t 
                    WHERE t.is_active = true 
                    ORDER BY t.usage_count DESC 
                    LIMIT 3
                """)
                tag_result = db_session.execute(tag_query)
                project_tags = [tag[0] for tag in tag_result.fetchall()]
                
                # Get project media and links
                media_query = text("""
                    SELECT links, file_type 
                    FROM user_links 
                    WHERE user_id = :owner_id AND file_type IN ('media', 'cover')
                    LIMIT 5
                """)
                media_result = db_session.execute(media_query, {"owner_id": row.owner_id})
                media_files = media_result.fetchall()
                
                # Get project links
                link_query = text("""
                    SELECT links 
                    FROM user_links 
                    WHERE user_id = :owner_id AND file_type = 'website'
                    LIMIT 3
                """)
                link_result = db_session.execute(link_query, {"owner_id": row.owner_id})
                project_links = [link[0] for link in link_result.fetchall()]
                
                # Get collaborators info
                collab_query = text("""
                    SELECT u.name, u.bio
                    FROM user_projects up
                    JOIN users u ON up.user_id = u.user_id
                    WHERE up.project_id = :project_id AND up.user_id != :owner_id
                    LIMIT 3
                """)
                collab_result = db_session.execute(collab_query, {
                    "project_id": row.project_id, 
                    "owner_id": row.owner_id
                })
                collaborators_list = [
                    {
                        "name": collab[0], 
                        "role": "Collaborator", 
                        "avatar": f"https://api.dicebear.com/7.x/avataaars/svg?seed={collab[0]}"
                    } 
                    for collab in collab_result.fetchall()
                ]
                
                # Extract media URLs
                media_urls = []
                cover_url = None
                for media in media_files:
                    if media[1] == 'cover':
                        cover_url = media[0]
                    elif media[1] == 'media':
                        media_urls.append(media[0])
                
                # Build card structure matching card.json
                card = {
                    "id": row.project_id,
                    "title": row.title or "Untitled Project",
                    "description": row.description or row.title or "No description available",
                    "tags": project_tags,
                    "type": "project",
                    "cardStyle": "text-only",
                    "status": row.status.lower() if row.status else "ongoing",
                    "owner": {
                        "name": row.owner_name or "Anonymous",
                        "age": None,  # Would need to calculate from user data
                        "gender": None,  # Would need user profile data
                        "role": "Owner",
                        "distance": None,  # Would need location calculation
                        "avatar": f"https://api.dicebear.com/7.x/avataaars/svg?seed={row.owner_name}",
                        "tags": json.loads(row.owner_tags) if row.owner_tags else []
                    },
                    "collaborators": int(row.collaborators_count),
                    "collaboratorsList": collaborators_list,
                    "detailedDescription": row.description or "More details coming soon...",
                    "startTime": row.start_time.strftime("%B %Y") if row.start_time else "Recently",
                    "currentProgress": 40,  # Would need progress tracking
                    "content": row.description or "Project content...",
                    "purpose": "Building innovative solutions",  # Would need dedicated field
                    "lookingFor": {
                        "tags": ["Developer", "Designer", "Product Manager"],
                        "description": "Looking for passionate team members to join this project."
                    },
                    "links": project_links,
                    "media": media_urls,
                    "cover": cover_url or f"https://picsum.photos/400/300?random={row.project_id}",
                    "videoUrl": None,
                    "gradientBackground": f"bg-gradient-to-br from-violet-500 via-purple-500 to-indigo-600"
                }
                
                cards.append(card)
            
            logger.info(f"Served {len(cards)} project cards to user {user_id}")
            return {"cards": cards}
            
        finally:
            db_session.close()
            
    except Exception as e:
        logger.error(f"Error getting project cards for user {user_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get project cards. Please try again later."
        )
