"""
Project Cards router for card-based project management API
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from dependencies.db import get_db
from dependencies.auth import get_current_user
from models.users import User
from services.project_card_service import ProjectCardService
from pydantic import BaseModel

router = APIRouter(prefix="/api/project-cards", tags=["project-cards"])

class CreateProjectCardRequest(BaseModel):
    title: str
    description: str
    short_description: Optional[str] = None
    category: Optional[str] = None
    industry: Optional[str] = None
    project_type: Optional[str] = "startup"
    stage: Optional[str] = None
    looking_for: Optional[List[str]] = None
    skills_needed: Optional[List[str]] = None
    image_urls: Optional[List[str]] = None
    video_url: Optional[str] = None
    demo_url: Optional[str] = None
    pitch_deck_url: Optional[str] = None
    funding_goal: Optional[int] = None
    equity_offered: Optional[int] = None  # Percentage * 100 (e.g., 1000 = 10%)
    current_valuation: Optional[int] = None
    revenue: Optional[int] = None
    feature_tags: Optional[List[str]] = None

class ProjectCardResponse(BaseModel):
    project_id: int
    title: str
    description: str
    short_description: Optional[str]
    category: Optional[str]
    industry: Optional[str]
    project_type: str
    stage: Optional[str]
    looking_for: Optional[List[str]]
    skills_needed: Optional[List[str]]
    is_active: bool
    view_count: int
    like_count: int
    interest_count: int
    created_at: str
    
    class Config:
        from_attributes = True

@router.get("/my-cards")
def get_my_cards(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all project cards owned by the current user
    """
    try:
        cards = ProjectCardService.get_user_cards(db, current_user.user_id)
        current_count = len(cards)
        
        return {
            "cards": [card.to_card_dict() for card in cards],
            "total_cards": current_count,
            "max_cards": 2,
            "can_create_more": current_count < 2
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/card-limit-status")
def get_card_limit_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Check the current card limit status for the user
    """
    try:
        current_count = ProjectCardService.get_user_card_count(db, current_user.user_id)
        can_create_more = ProjectCardService.check_user_card_limit(db, current_user.user_id)
        
        return {
            "current_cards": current_count,
            "max_cards": 2,
            "can_create_more": can_create_more,
            "remaining_slots": 2 - current_count if current_count < 2 else 0
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_project_card(
    card_data: CreateProjectCardRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new project card
    Maximum of 2 cards per user allowed
    """
    try:
        # Convert Pydantic model to dict
        card_dict = card_data.dict()
        
        # Create the card
        new_card = ProjectCardService.create_project_card(db, current_user.user_id, card_dict)
        
        return {
            "message": "Project card created successfully",
            "card": new_card.to_card_dict(),
            "cards_remaining": 2 - ProjectCardService.get_user_card_count(db, current_user.user_id)
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.delete("/{card_id}")
def deactivate_project_card(
    card_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Deactivate (soft delete) a project card to free up a slot
    """
    try:
        success = ProjectCardService.deactivate_project_card(db, current_user.user_id, card_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project card not found or you don't have permission to delete it"
            )
        
        remaining_count = ProjectCardService.get_user_card_count(db, current_user.user_id)
        
        return {
            "message": "Project card deactivated successfully",
            "remaining_cards": remaining_count,
            "can_create_more": remaining_count < 2
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
