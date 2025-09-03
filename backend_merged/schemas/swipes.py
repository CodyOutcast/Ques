"""Schemas for swipe functionality"""

from pydantic import BaseModel
from enum import Enum


class SwipeDirectionEnum(str, Enum):
    """Swipe direction enum for API"""
    like = "like"
    dislike = "dislike"


class SwipeInput(BaseModel):
    """Input schema for swipe actions"""
    card_id: int  # ID of the card being swiped
    direction: SwipeDirectionEnum  # Direction of the swipe


class SwipeResponse(BaseModel):
    """Response schema for swipe actions"""
    message: str
    card_id: int
    is_match: bool = False
