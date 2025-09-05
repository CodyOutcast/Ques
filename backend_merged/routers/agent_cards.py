"""
Agent Cards Router
API endpoints for AI-generated project idea cards and user interactions
"""

import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field
from datetime import datetime

from dependencies.auth import get_current_user
from services.agent_cards_service import AgentCardsService
from models.users import User
from dependencies.db import get_db
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/agent-cards", tags=["agent-cards"])

# Pydantic models
class SwipeRequest(BaseModel):
    card_id: int = Field(..., description="ID of the agent card")
    action: str = Field(..., pattern="^(left|right)$", description="Swipe action: left or right")
    interest_level: Optional[int] = Field(None, ge=1, le=5, description="Interest level for right swipes (1-5)")
    notes: Optional[str] = Field(None, max_length=500, description="Notes about the card")
    rejection_reason: Optional[str] = Field(None, max_length=100, description="Reason for left swipe")
    feedback: Optional[str] = Field(None, max_length=500, description="Feedback for left swipe")

class PreferencesRequest(BaseModel):
    preferred_difficulty_levels: Optional[List[str]] = Field(None, description="Preferred difficulty levels")
    preferred_project_scopes: Optional[List[str]] = Field(None, description="Preferred project scopes")
    preferred_skills: Optional[List[str]] = Field(None, description="Skills of interest")
    excluded_skills: Optional[List[str]] = Field(None, description="Skills to avoid")
    min_relevance_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Minimum relevance score")
    max_cards_per_day: Optional[int] = Field(None, ge=1, le=100, description="Daily card limit")
    preferred_timeline_min: Optional[str] = Field(None, max_length=20, description="Minimum timeline")
    preferred_timeline_max: Optional[str] = Field(None, max_length=20, description="Maximum timeline")
    daily_cards_enabled: Optional[bool] = Field(None, description="Enable daily cards")
    weekly_summary_enabled: Optional[bool] = Field(None, description="Enable weekly summary")

class CreateCardsRequest(BaseModel):
    cards_data: List[dict] = Field(..., description="List of card data from AI agent")
    generation_prompt: Optional[str] = Field(None, max_length=1000, description="Original prompt")
    ai_agent_id: Optional[str] = Field(None, max_length=255, description="AI agent ID")

# Card recommendation endpoints
@router.get("/recommendations")
async def get_agent_card_recommendations(
    limit: int = Query(10, ge=1, le=50, description="Maximum number of cards"),
    exclude_swiped: bool = Query(True, description="Exclude previously swiped cards"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get AI-generated project idea card recommendations for the user
    """
    try:
        service = AgentCardsService(db)
        recommendations = service.get_recommendations_for_user(
            user_id=current_user.user_id,
            limit=limit,
            exclude_swiped=exclude_swiped
        )
        
        return {
            "status": "success",
            "data": {
                "recommendations": recommendations,
                "count": len(recommendations),
                "user_id": current_user.user_id
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting recommendations for user {current_user.user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get recommendations"
        )

@router.post("/swipe")
async def swipe_agent_card(
    swipe_data: SwipeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Record a swipe on an agent card
    Left swipe = add to history (reject)
    Right swipe = add to likes
    """
    try:
        service = AgentCardsService(db)
        
        # Prepare swipe context
        swipe_context = {}
        if swipe_data.action == "right":
            if swipe_data.interest_level:
                swipe_context["interest_level"] = swipe_data.interest_level
            if swipe_data.notes:
                swipe_context["notes"] = swipe_data.notes
        elif swipe_data.action == "left":
            if swipe_data.rejection_reason:
                swipe_context["rejection_reason"] = swipe_data.rejection_reason
            if swipe_data.feedback:
                swipe_context["feedback"] = swipe_data.feedback
        
        # Record the swipe
        success = service.record_swipe(
            user_id=current_user.user_id,
            card_id=swipe_data.card_id,
            action=swipe_data.action,
            swipe_context=swipe_context
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to record swipe"
            )
        
        action_message = "liked and saved" if swipe_data.action == "right" else "added to history"
        
        return {
            "status": "success",
            "data": {
                "swipe_recorded": True,
                "action": swipe_data.action,
                "card_id": swipe_data.card_id,
                "message": f"Card {action_message} successfully"
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing swipe for user {current_user.user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process swipe"
        )

@router.get("/likes")
async def get_user_likes(
    limit: int = Query(50, ge=1, le=200, description="Maximum number of likes to return"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user's liked agent cards (right swipes)
    """
    try:
        service = AgentCardsService(db)
        likes = service.get_user_likes(current_user.user_id, limit)
        
        return {
            "status": "success",
            "data": {
                "likes": likes,
                "count": len(likes)
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting likes for user {current_user.user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get likes"
        )

@router.get("/history")
async def get_user_history(
    limit: int = Query(50, ge=1, le=200, description="Maximum number of history records to return"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user's card history (left swipes)
    """
    try:
        service = AgentCardsService(db)
        history = service.get_user_history(current_user.user_id, limit)
        
        return {
            "status": "success",
            "data": {
                "history": history,
                "count": len(history)
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting history for user {current_user.user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get history"
        )

@router.get("/statistics")
async def get_swipe_statistics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user's swipe statistics
    """
    try:
        service = AgentCardsService(db)
        stats = service.get_swipe_statistics(current_user.user_id)
        
        return {
            "status": "success",
            "data": stats
        }
        
    except Exception as e:
        logger.error(f"Error getting statistics for user {current_user.user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get statistics"
        )

@router.get("/preferences")
async def get_user_preferences(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user's agent card preferences
    """
    try:
        from models.agent_cards import UserAgentCardPreferences
        
        preferences = db.query(UserAgentCardPreferences).filter(
            UserAgentCardPreferences.user_id == current_user.user_id
        ).first()
        
        if not preferences:
            # Return default preferences
            return {
                "status": "success",
                "data": {
                    "preferred_difficulty_levels": [],
                    "preferred_project_scopes": [],
                    "preferred_skills": [],
                    "excluded_skills": [],
                    "min_relevance_score": 0.5,
                    "max_cards_per_day": 20,
                    "preferred_timeline_min": None,
                    "preferred_timeline_max": None,
                    "daily_cards_enabled": True,
                    "weekly_summary_enabled": True,
                    "created_at": None,
                    "updated_at": None
                }
            }
        
        return {
            "status": "success",
            "data": {
                "preferred_difficulty_levels": preferences.preferred_difficulty_levels,
                "preferred_project_scopes": preferences.preferred_project_scopes,
                "preferred_skills": preferences.preferred_skills,
                "excluded_skills": preferences.excluded_skills,
                "min_relevance_score": preferences.min_relevance_score,
                "max_cards_per_day": preferences.max_cards_per_day,
                "preferred_timeline_min": preferences.preferred_timeline_min,
                "preferred_timeline_max": preferences.preferred_timeline_max,
                "daily_cards_enabled": preferences.daily_cards_enabled,
                "weekly_summary_enabled": preferences.weekly_summary_enabled,
                "created_at": preferences.created_at.isoformat() if preferences.created_at else None,
                "updated_at": preferences.updated_at.isoformat() if preferences.updated_at else None
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting preferences for user {current_user.user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get preferences"
        )

@router.put("/preferences")
async def update_user_preferences(
    preferences_data: PreferencesRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update user's agent card preferences
    """
    try:
        service = AgentCardsService(db)
        
        # Convert to dict and remove None values
        preferences_dict = {k: v for k, v in preferences_data.dict().items() if v is not None}
        
        if not preferences_dict:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No preference data provided"
            )
        
        success = service.update_user_preferences(
            user_id=current_user.user_id,
            preferences=preferences_dict
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update preferences"
            )
        
        return {
            "status": "success",
            "data": {
                "updated": True,
                "message": "Preferences updated successfully"
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating preferences for user {current_user.user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update preferences"
        )

# Admin endpoints for creating cards
@router.post("/admin/create-cards")
async def create_agent_cards(
    cards_request: CreateCardsRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create agent cards from AI-generated data (admin endpoint)
    """
    try:
        service = AgentCardsService(db)
        
        created_ids = service.create_agent_cards_from_json(
            cards_data=cards_request.cards_data,
            generation_prompt=cards_request.generation_prompt,
            ai_agent_id=cards_request.ai_agent_id
        )
        
        if not created_ids:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create agent cards"
            )
        
        return {
            "status": "success",
            "data": {
                "created_card_ids": created_ids,
                "count": len(created_ids),
                "message": f"Successfully created {len(created_ids)} agent cards"
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating agent cards: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create agent cards"
        )

@router.get("/card/{card_id}")
async def get_agent_card(
    card_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific agent card by ID
    """
    try:
        from models.agent_cards import AgentCard
        
        card = db.query(AgentCard).filter(
            AgentCard.card_id == card_id
        ).first()
        
        if not card:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Agent card not found"
            )
        
        return {
            "status": "success",
            "data": {
                "card_id": card.card_id,
                "project_idea_title": card.project_idea_title,
                "project_scope": card.project_scope.value,
                "description": card.description,
                "key_features": card.key_features,
                "estimated_timeline": card.estimated_timeline,
                "difficulty_level": card.difficulty_level.value,
                "required_skills": card.required_skills,
                "similar_examples": card.similar_examples,
                "relevance_score": card.relevance_score,
                "ai_agent_id": card.ai_agent_id,
                "generation_prompt": card.generation_prompt,
                "created_at": card.created_at.isoformat() if card.created_at else None
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting agent card {card_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get agent card"
        )
