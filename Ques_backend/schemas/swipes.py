"""
Pydantic schemas for swipe system matching frontend API
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum

class SwipeAction(str, Enum):
    """Swipe action enum matching frontend"""
    LIKE = "like"
    IGNORE = "ignore"
    SUPER_LIKE = "super_like"

class SearchMode(str, Enum):
    """Search mode enum matching frontend"""
    INSIDE = "inside"
    GLOBAL = "global"

class SourceContext(BaseModel):
    """Source context for swipe record"""
    sessionId: Optional[str] = None
    recommendationBatch: Optional[str] = None
    cardPosition: Optional[int] = None

class RecordSwipeRequest(BaseModel):
    """Request schema for recording a swipe - matches frontend exactly"""
    targetUserId: str = Field(..., description="Target user ID")
    action: SwipeAction = Field(..., description="Swipe action")
    searchQuery: Optional[str] = Field(None, max_length=500, description="Search query used")
    searchMode: Optional[SearchMode] = Field(None, description="Search mode")
    matchScore: Optional[float] = Field(None, ge=0, le=1, description="Match score")
    sourceContext: Optional[SourceContext] = Field(None, description="Source context")

class BatchRecordSwipeRequest(BaseModel):
    """Request schema for batch recording swipes"""
    swipes: List[RecordSwipeRequest] = Field(..., description="List of swipe records")

class SwipeRecordResponse(BaseModel):
    """Response schema for swipe record"""
    id: int
    userId: int
    targetUserId: str
    action: SwipeAction
    searchQuery: Optional[str]
    searchMode: Optional[SearchMode]
    matchScore: Optional[float]
    sourceContext: Optional[Dict[str, Any]]
    createdAt: datetime
    updatedAt: datetime

    class Config:
        from_attributes = True

class SwipeHistoryQuery(BaseModel):
    """Query parameters for swipe history"""
    page: int = Field(1, ge=1, description="Page number")
    limit: int = Field(20, ge=1, le=100, description="Items per page")
    action: Optional[SwipeAction] = Field(None, description="Filter by action")
    startDate: Optional[datetime] = Field(None, description="Start date filter")
    endDate: Optional[datetime] = Field(None, description="End date filter")

class SwipeStatistics(BaseModel):
    """Swipe statistics response"""
    totalSwipes: int
    likes: int
    ignores: int
    superLikes: int
    matchRate: float
    mostSwipedSkills: List[str]
    mostSwipedLocations: List[str]
    averageMatchScore: float
    dailySwipeCount: List[Dict[str, Any]]

class SwipePreferences(BaseModel):
    """User swipe preferences"""
    preferredSkills: List[str]
    preferredLocations: List[str]
    preferredUniversities: List[str]
    averageMatchScore: float
    mostActiveHours: List[int]
    swipePatterns: Dict[str, Any]

class SwipeSuggestion(BaseModel):
    """AI-generated swipe suggestion"""
    targetUserId: str
    suggestedAction: SwipeAction
    confidence: float
    reasoning: List[str]
    matchScore: float

class BulkDeleteRequest(BaseModel):
    """Request for bulk deleting swipe records"""
    olderThan: Optional[datetime] = Field(None, description="Delete records older than this date")
    action: Optional[SwipeAction] = Field(None, description="Delete records with this action")
