"""
Vector-based Project Card Recommendations Router
Provides personalized project recommendations based on user similarity
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from dependencies.db import get_db
from dependencies.auth import get_current_user
from models.users import User
from services.vector_recommendations import VectorRecommendationService

router = APIRouter(prefix="/api/v1/recommendations", tags=["Vector Recommendations"])
logger = logging.getLogger(__name__)

@router.get("/project-cards")
async def get_recommended_project_cards(
    limit: int = Query(20, ge=1, le=50, description="Number of cards to return"),
    exclude_own: bool = Query(True, description="Exclude user's own projects"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get personalized project card recommendations based on user's vector similarity
    
    This endpoint uses vector embeddings to find projects that match the user's
    interests, skills, and profile characteristics.
    """
    try:
        user_id = current_user.user_id
        logger.info(f"Getting {limit} recommended project cards for user {user_id}")
        
        # Get vector-based recommendations
        project_cards = VectorRecommendationService.get_recommended_projects_for_user(
            user_id=user_id,
            limit=limit,
            exclude_own_projects=exclude_own
        )
        
        logger.info(f"Found {len(project_cards)} recommended cards for user {user_id}")
        
        return {
            "user_id": user_id,
            "total_cards": len(project_cards),
            "cards": project_cards,
            "recommendation_method": "vector_similarity",
            "limit": limit
        }
        
    except Exception as e:
        logger.error(f"Error getting recommendations for user {current_user.user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get recommendations"
        )

@router.post("/update-user-vector")
async def update_user_vector(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update current user's vector in the vector database
    
    This should be called when user updates their profile, tags, or bio
    to ensure recommendations stay accurate.
    """
    try:
        user_id = current_user.user_id
        logger.info(f"Updating vector for user {user_id}")
        
        # Update user's vector
        vector_id = VectorRecommendationService.update_user_vector(db, user_id)
        
        if vector_id:
            logger.info(f"Successfully updated vector for user {user_id}: {vector_id}")
            return {
                "user_id": user_id,
                "vector_id": vector_id,
                "status": "success",
                "message": "User vector updated successfully"
            }
        else:
            logger.warning(f"Failed to update vector for user {user_id}")
            return {
                "user_id": user_id,
                "vector_id": None,
                "status": "failed",
                "message": "Failed to update user vector"
            }
        
    except Exception as e:
        logger.error(f"Error updating vector for user {current_user.user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user vector"
        )

@router.post("/update-project-vector/{project_id}")
async def update_project_vector(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update a project's vector in the vector database
    
    This should be called when project details are updated to ensure
    accurate matching with users.
    """
    try:
        logger.info(f"Updating vector for project {project_id}")
        
        # Update project's vector
        vector_id = VectorRecommendationService.update_project_vector(db, project_id)
        
        if vector_id:
            logger.info(f"Successfully updated vector for project {project_id}: {vector_id}")
            return {
                "project_id": project_id,
                "vector_id": vector_id,
                "status": "success",
                "message": "Project vector updated successfully"
            }
        else:
            logger.warning(f"Failed to update vector for project {project_id}")
            return {
                "project_id": project_id,
                "vector_id": None,
                "status": "failed",
                "message": "Failed to update project vector"
            }
        
    except Exception as e:
        logger.error(f"Error updating vector for project {project_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update project vector"
        )

@router.get("/health")
async def vector_recommendations_health():
    """Health check for vector recommendation service"""
    try:
        from db_utils import get_vdb_collection
        
        # Try to connect to vector database
        collection = get_vdb_collection()
        
        return {
            "status": "healthy",
            "vector_db": "connected",
            "collection": collection.collection_name if hasattr(collection, 'collection_name') else "unknown"
        }
        
    except Exception as e:
        logger.error(f"Vector recommendations health check failed: {e}")
        return {
            "status": "degraded",
            "vector_db": "disconnected",
            "error": str(e)
        }
