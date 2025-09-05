"""
Project Slots Router
API endpoints for managing project card slots and AI recommendations
"""

import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field
from datetime import datetime

from dependencies.auth import get_current_user
from services.project_slots_service import ProjectSlotsService
from services.ai_project_recommendations import AIProjectRecommendationService
from models.users import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/project-slots", tags=["project-slots"])

# Pydantic models
class SlotUpdateRequest(BaseModel):
    slot_name: Optional[str] = Field(None, max_length=100)
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    short_description: Optional[str] = Field(None, max_length=500)
    category: Optional[str] = Field(None, max_length=50)
    industry: Optional[str] = Field(None, max_length=50)
    project_type: Optional[str] = Field(None, max_length=50)
    stage: Optional[str] = Field(None, max_length=50)
    looking_for: Optional[List[str]] = None
    skills_needed: Optional[List[str]] = None
    image_urls: Optional[List[str]] = None
    video_url: Optional[str] = Field(None, max_length=512)
    demo_url: Optional[str] = Field(None, max_length=512)
    pitch_deck_url: Optional[str] = Field(None, max_length=512)
    funding_goal: Optional[int] = Field(None, ge=0)
    equity_offered: Optional[int] = Field(None, ge=0, le=100)
    current_valuation: Optional[int] = Field(None, ge=0)
    revenue: Optional[int] = Field(None, ge=0)

class SlotConfigurationRequest(BaseModel):
    max_slots: Optional[int] = Field(None, ge=1, le=20)
    auto_save_recommendations: Optional[bool] = None
    stop_recommendations_on_save: Optional[bool] = None

class SwipeRequest(BaseModel):
    ai_recommendation_id: str = Field(..., description="ID of the AI recommendation")
    direction: str = Field(..., pattern="^(left|right)$", description="Swipe direction: left or right")
    recommendation_data: dict = Field(..., description="Full recommendation data")
    query: Optional[str] = Field(None, description="Original search query")
    slot_number: Optional[int] = Field(None, ge=1, description="Specific slot to save to (for right swipes)")

class RecommendationRequest(BaseModel):
    query: Optional[str] = Field(None, max_length=500, description="Search query for recommendations")
    limit: int = Field(10, ge=1, le=50, description="Maximum number of recommendations")
    exclude_swiped: bool = Field(True, description="Whether to exclude previously swiped recommendations")

# AI Recommendations endpoints
@router.get("/recommendations")
async def get_ai_recommendations(
    query: Optional[str] = Query(None, max_length=500, description="Search query"),
    limit: int = Query(10, ge=1, le=50, description="Maximum recommendations"),
    exclude_swiped: bool = Query(True, description="Exclude swiped recommendations"),
    current_user: User = Depends(get_current_user)
):
    """
    Get AI-powered project card recommendations for the user
    """
    try:
        ai_service = AIProjectRecommendationService()
        recommendations = ai_service.generate_recommendations(
            user_id=current_user.user_id,
            query=query,
            limit=limit,
            exclude_swiped=exclude_swiped
        )
        
        return {
            "status": "success",
            "data": {
                "recommendations": recommendations,
                "count": len(recommendations),
                "query": query,
                "user_id": current_user.user_id
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting recommendations for user {current_user.user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate recommendations"
        )

@router.post("/swipe")
async def swipe_recommendation(
    swipe_data: SwipeRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Record a swipe on an AI recommendation and save to slot if right swipe
    """
    try:
        ai_service = AIProjectRecommendationService()
        slots_service = ProjectSlotsService()
        
        slot_id = None
        
        # If right swipe, save to slot
        if swipe_data.direction == "right":
            # Initialize slots if first time user
            slots_service.initialize_user_slots(current_user.user_id)
            
            # Save recommendation to slot
            slot_id = slots_service.save_recommendation_to_slot(
                user_id=current_user.user_id,
                recommendation_data=swipe_data.recommendation_data,
                slot_number=swipe_data.slot_number
            )
            
            if slot_id is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No available slots or slot already occupied"
                )
        
        # Record the swipe
        success = ai_service.record_swipe(
            user_id=current_user.user_id,
            ai_recommendation_id=swipe_data.ai_recommendation_id,
            direction=swipe_data.direction,
            recommendation_data=swipe_data.recommendation_data,
            query=swipe_data.query,
            slot_id=slot_id
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to record swipe"
            )
        
        # Check if recommendations should stop
        stop_recommendations = False
        if swipe_data.direction == "right":
            stop_recommendations = ai_service.should_stop_recommendations(current_user.user_id)
        
        return {
            "status": "success",
            "data": {
                "swipe_recorded": True,
                "direction": swipe_data.direction,
                "saved_to_slot_id": slot_id,
                "stop_recommendations": stop_recommendations,
                "message": f"Recommendation {'saved to slot' if swipe_data.direction == 'right' else 'rejected'}"
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

@router.get("/swipe-history")
async def get_swipe_history(
    limit: int = Query(50, ge=1, le=200, description="Maximum number of swipes to return"),
    current_user: User = Depends(get_current_user)
):
    """
    Get user's swipe history for AI recommendations
    """
    try:
        ai_service = AIProjectRecommendationService()
        history = ai_service.get_user_swipe_history(current_user.user_id, limit)
        
        return {
            "status": "success",
            "data": {
                "swipe_history": history,
                "count": len(history)
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting swipe history for user {current_user.user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get swipe history"
        )

# Project Slots endpoints
@router.get("/slots")
async def get_user_slots(current_user: User = Depends(get_current_user)):
    """
    Get all project slots for the current user
    """
    try:
        slots_service = ProjectSlotsService()
        
        # Initialize slots if first time user
        slots_service.initialize_user_slots(current_user.user_id)
        
        slots = slots_service.get_user_slots(current_user.user_id)
        stats = slots_service.get_slot_statistics(current_user.user_id)
        
        return {
            "status": "success",
            "data": {
                "slots": slots,
                "statistics": stats
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting slots for user {current_user.user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user slots"
        )

@router.get("/slots/{slot_id}")
async def get_slot(
    slot_id: int,
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific slot by ID
    """
    try:
        slots_service = ProjectSlotsService()
        slots = slots_service.get_user_slots(current_user.user_id)
        
        slot = next((s for s in slots if s["slot_id"] == slot_id), None)
        
        if not slot:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Slot not found"
            )
        
        return {
            "status": "success",
            "data": slot
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting slot {slot_id} for user {current_user.user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get slot"
        )

@router.put("/slots/{slot_id}")
async def update_slot(
    slot_id: int,
    updates: SlotUpdateRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Update content of a specific slot
    """
    try:
        slots_service = ProjectSlotsService()
        
        # Convert to dict and remove None values
        update_data = {k: v for k, v in updates.dict().items() if v is not None}
        
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No update data provided"
            )
        
        success = slots_service.update_slot_content(
            user_id=current_user.user_id,
            slot_id=slot_id,
            updates=update_data
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Slot not found or cannot be updated"
            )
        
        return {
            "status": "success",
            "data": {
                "slot_id": slot_id,
                "updated": True,
                "message": "Slot updated successfully"
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating slot {slot_id} for user {current_user.user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update slot"
        )

@router.post("/slots/{slot_id}/activate")
async def activate_slot(
    slot_id: int,
    current_user: User = Depends(get_current_user)
):
    """
    Activate a slot's content (make it visible/published)
    Content stays in the same slot but becomes active
    """
    try:
        slots_service = ProjectSlotsService()
        
        success = slots_service.activate_slot(
            user_id=current_user.user_id,
            slot_id=slot_id
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Slot not found, not occupied, or activation limit reached"
            )
        
        return {
            "status": "success",
            "data": {
                "slot_id": slot_id,
                "activated": True,
                "message": "Slot activated successfully"
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error activating slot {slot_id} for user {current_user.user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to activate slot"
        )

@router.post("/slots/{slot_id}/deactivate")
async def deactivate_slot(
    slot_id: int,
    current_user: User = Depends(get_current_user)
):
    """
    Deactivate a slot's content (keep content but make it inactive)
    """
    try:
        slots_service = ProjectSlotsService()
        
        success = slots_service.deactivate_slot(
            user_id=current_user.user_id,
            slot_id=slot_id
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Slot not found or not activated"
            )
        
        return {
            "status": "success",
            "data": {
                "slot_id": slot_id,
                "deactivated": True,
                "message": "Slot deactivated successfully"
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deactivating slot {slot_id} for user {current_user.user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to deactivate slot"
        )

@router.delete("/slots/{slot_id}")
async def clear_slot(
    slot_id: int,
    current_user: User = Depends(get_current_user)
):
    """
    Clear a slot's content
    """
    try:
        slots_service = ProjectSlotsService()
        
        success = slots_service.clear_slot(
            user_id=current_user.user_id,
            slot_id=slot_id
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Slot not found"
            )
        
        return {
            "status": "success",
            "data": {
                "slot_id": slot_id,
                "cleared": True,
                "message": "Slot cleared successfully"
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error clearing slot {slot_id} for user {current_user.user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to clear slot"
        )

@router.get("/statistics")
async def get_slot_statistics(current_user: User = Depends(get_current_user)):
    """
    Get statistics about user's slot usage
    """
    try:
        slots_service = ProjectSlotsService()
        stats = slots_service.get_slot_statistics(current_user.user_id)
        
        return {
            "status": "success",
            "data": stats
        }
        
    except Exception as e:
        logger.error(f"Error getting slot statistics for user {current_user.user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get slot statistics"
        )

@router.get("/configuration")
async def get_slot_configuration(current_user: User = Depends(get_current_user)):
    """
    Get user's slot configuration
    """
    try:
        slots_service = ProjectSlotsService()
        
        # This will initialize if doesn't exist
        slots_service.initialize_user_slots(current_user.user_id)
        
        # Get configuration from database
        from models.project_slots import UserSlotConfiguration
        from dependencies.db import get_db
        
        db = next(get_db())
        config = db.query(UserSlotConfiguration).filter(
            UserSlotConfiguration.user_id == current_user.user_id
        ).first()
        
        if not config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Configuration not found"
            )
        
        return {
            "status": "success",
            "data": {
                "max_slots": config.max_slots,
                "auto_save_recommendations": config.auto_save_recommendations,
                "stop_recommendations_on_save": config.stop_recommendations_on_save,
                "created_at": config.created_at.isoformat(),
                "updated_at": config.updated_at.isoformat()
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting slot configuration for user {current_user.user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get slot configuration"
        )

@router.put("/configuration")
async def update_slot_configuration(
    config_data: SlotConfigurationRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Update user's slot configuration
    """
    try:
        slots_service = ProjectSlotsService()
        
        success = slots_service.update_slot_configuration(
            user_id=current_user.user_id,
            max_slots=config_data.max_slots,
            auto_save_recommendations=config_data.auto_save_recommendations,
            stop_recommendations_on_save=config_data.stop_recommendations_on_save
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update configuration"
            )
        
        return {
            "status": "success",
            "data": {
                "updated": True,
                "message": "Slot configuration updated successfully"
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating slot configuration for user {current_user.user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update slot configuration"
        )
