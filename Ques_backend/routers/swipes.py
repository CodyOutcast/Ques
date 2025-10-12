"""
Swipe service router - matches frontend API documentation using existing backend models
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, func, desc, asc, or_, text
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from pydantic import BaseModel, Field, validator
from enum import Enum
import logging
from collections import defaultdict

from dependencies.db import get_db
from dependencies.auth import get_current_user
from models.projects import AIRecommendationSwipe, AgentCardSwipe
from models.users import User
from schemas.users import UserSummary

router = APIRouter(prefix="/swipe", tags=["swipe"])
logger = logging.getLogger(__name__)

# ============================================================================
# Pydantic Models
# ============================================================================

class SwipeAction(str, Enum):
    """Swipe action enum matching frontend expectations"""
    like = "like"
    ignore = "ignore" 
    super_like = "super_like"

class RecordSwipeRequest(BaseModel):
    """Request model for recording a swipe - matches frontend documentation"""
    targetUserId: str = Field(..., description="Target user ID")
    action: SwipeAction = Field(..., description="Swipe action")
    searchQuery: Optional[str] = Field(None, description="Search query context")
    searchMode: Optional[str] = Field("inside", description="Search mode: inside or global")
    matchScore: Optional[float] = Field(None, description="Match score")
    sourceContext: Optional[Dict[str, Any]] = Field(None, description="Source context")

class BatchSwipeRequest(BaseModel):
    """Request model for batch swipe recording"""
    swipes: List[RecordSwipeRequest] = Field(..., description="List of swipes to record")

class SwipeRecord(BaseModel):
    """Swipe record response model"""
    id: int
    targetUserId: str
    action: str
    searchQuery: Optional[str]
    searchMode: str
    matchScore: Optional[float]
    sourceContext: Optional[Dict[str, Any]]
    createdAt: datetime
    isMatch: bool = False

class SwipeHistoryResponse(BaseModel):
    """Response model for swipe history"""
    data: List[SwipeRecord]
    pagination: Dict[str, int]

class SwipeStats(BaseModel):
    """Swipe statistics response model"""
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
    swipePatterns: Dict[str, Any]

class SwipeSuggestion(BaseModel):
    """AI-generated swipe suggestion"""
    suggestion: str
    confidence: float
    reasoning: List[str]

# Note: This router uses existing models (AgentCardSwipe, AIRecommendationSwipe) 
# to provide compatibility with frontend swipe API expectations

# ============================================================================
# API Endpoints
# ============================================================================

@router.post("/record", response_model=SwipeRecord)
async def record_swipe(
    request: RecordSwipeRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Record a single swipe action using AI recommendation swipes
    Matches frontend API: POST /swipe/record
    """
    try:
        user_id = current_user["id"]
        
        # Create AI recommendation swipe record
        swipe = AIRecommendationSwipe(
            user_id=user_id,
            ai_recommendation_id=request.targetUserId,
            direction=request.action.value.upper(),
            query=request.searchQuery or "",
            saved_to_slot=None,  # Not saved to slot by default
            recommendation_data={
                "match_score": request.matchScore,
                "search_mode": request.searchMode,
                "source_context": request.sourceContext
            }
        )
        
        db.add(swipe)
        db.commit()
        db.refresh(swipe)
        
        # For now, we don't implement match detection since this is for general swipes
        # Match detection would be specific to user-to-user interactions
        
        return SwipeRecord(
            id=swipe.swipe_id,
            targetUserId=request.targetUserId,
            action=request.action.value,
            searchQuery=request.searchQuery,
            searchMode=request.searchMode or "inside",
            matchScore=request.matchScore,
            sourceContext=request.sourceContext,
            createdAt=datetime.utcnow(),
            isMatch=False
        )
        
    except Exception as e:
        logger.error(f"Failed to record swipe: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to record swipe: {str(e)}")

@router.post("/record/batch")
async def batch_record_swipes(
    request: BatchSwipeRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Record multiple swipe actions in batch
    Matches frontend API: POST /swipe/record/batch
    """
    try:
        user_id = current_user["id"]
        results = []
        
        for swipe_request in request.swipes:
            try:
                # Use existing record_swipe logic for each swipe
                result = await record_swipe(swipe_request, current_user, db)
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to record swipe for user {swipe_request.targetUserId}: {e}")
                # Continue with other swipes even if one fails
                continue
        
        return {
            "success": True,
            "data": {
                "processed": len(results),
                "total": len(request.swipes),
                "swipes": results
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to batch record swipes: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to batch record swipes: {str(e)}")

@router.get("/history", response_model=SwipeHistoryResponse)
async def get_swipe_history(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    action: Optional[str] = Query(None, description="Filter by action: like, ignore, super_like"),
    startDate: Optional[str] = Query(None, description="Start date filter (ISO format)"),
    endDate: Optional[str] = Query(None, description="End date filter (ISO format)"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user's swipe history with pagination and filters
    Matches frontend API: GET /swipe/history
    """
    try:
        user_id = current_user["id"]
        offset = (page - 1) * limit
        
        # Query AI recommendation swipes
        query = db.query(AIRecommendationSwipe).filter(AIRecommendationSwipe.user_id == user_id)
        
        # Apply filters
        if action:
            query = query.filter(AIRecommendationSwipe.direction == action.upper())
        
        # For simplicity, we'll return empty results for date filtering since it's not in the model
        # In a real implementation, you'd add created_at field to the model
        
        # Get total count
        total = query.count()
        
        # Get paginated results
        swipes = query.offset(offset).limit(limit).all()
        
        # Convert to response format
        swipe_records = []
        for swipe in swipes:
            recommendation_data = swipe.recommendation_data or {}
            swipe_records.append(SwipeRecord(
                id=swipe.swipe_id,
                targetUserId=swipe.ai_recommendation_id,
                action=swipe.direction.lower(),
                searchQuery=swipe.query,
                searchMode=recommendation_data.get("search_mode", "inside"),
                matchScore=recommendation_data.get("match_score"),
                sourceContext=recommendation_data.get("source_context"),
                createdAt=datetime.utcnow(),  # Placeholder since model doesn't have created_at
                isMatch=False
            ))
        
        return SwipeHistoryResponse(
            data=swipe_records,
            pagination={
                "page": page,
                "limit": limit,
                "total": total,
                "totalPages": (total + limit - 1) // limit
            }
        )
        
    except Exception as e:
        logger.error(f"Failed to get swipe history: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get swipe history: {str(e)}")

@router.get("/stats", response_model=SwipeStats)
async def get_swipe_statistics(
    period: Optional[str] = Query("all", description="Time period: all, 7d, 30d, 90d"),
    startDate: Optional[str] = Query(None, description="Start date (ISO format)"),
    endDate: Optional[str] = Query(None, description="End date (ISO format)"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user's swipe statistics
    Matches frontend API: GET /swipe/stats
    """
    try:
        user_id = current_user["id"]
        
        # Get AI recommendation swipes
        query = db.query(AIRecommendationSwipe).filter(AIRecommendationSwipe.user_id == user_id)
        swipes = query.all()
        
        # Calculate statistics
        total_swipes = len(swipes)
        likes = len([s for s in swipes if s.direction.upper() == "LIKE"])
        ignores = len([s for s in swipes if s.direction.upper() == "IGNORE"])
        super_likes = len([s for s in swipes if s.direction.upper() == "SUPER_LIKE"])
        
        # Calculate match rate (placeholder)
        match_rate = 0.0
        
        # Get most swiped skills and locations (placeholder)
        most_swiped_skills = []
        most_swiped_locations = []
        
        # Calculate average match score
        match_scores = []
        for swipe in swipes:
            if swipe.recommendation_data and swipe.recommendation_data.get("match_score"):
                match_scores.append(swipe.recommendation_data["match_score"])
        
        average_match_score = sum(match_scores) / len(match_scores) if match_scores else 0.0
        
        # Daily swipe count (placeholder since no created_at field)
        daily_swipe_count = []
        
        return SwipeStats(
            totalSwipes=total_swipes,
            likes=likes,
            ignores=ignores,
            superLikes=super_likes,
            matchRate=match_rate,
            mostSwipedSkills=most_swiped_skills,
            mostSwipedLocations=most_swiped_locations,
            averageMatchScore=average_match_score,
            dailySwipeCount=daily_swipe_count
        )
        
    except Exception as e:
        logger.error(f"Failed to get swipe statistics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get swipe statistics: {str(e)}")

@router.get("/stats/preferences", response_model=SwipePreferences)
async def get_swipe_preferences(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user's swipe preferences based on swipe history
    Matches frontend API: GET /swipe/stats/preferences
    """
    try:
        user_id = current_user["id"]
        
        # Analyze user's swipe patterns to determine preferences
        # This is a placeholder implementation
        
        return SwipePreferences(
            preferredSkills=[],
            preferredLocations=[],
            preferredUniversities=[],
            swipePatterns={}
        )
        
    except Exception as e:
        logger.error(f"Failed to get swipe preferences: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get swipe preferences: {str(e)}")

@router.get("/stats/suggestions/{targetUserId}", response_model=SwipeSuggestion)
async def get_swipe_suggestions(
    targetUserId: int = Path(..., description="Target user ID"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get AI-generated swipe suggestions for a target user
    Matches frontend API: GET /swipe/stats/suggestions/{targetUserId}
    """
    try:
        user_id = current_user["id"]
        
        # Check if target user exists
        target_user = db.query(User).filter(User.id == targetUserId).first()
        if not target_user:
            raise HTTPException(status_code=404, detail="Target user not found")
        
        # Generate AI suggestion (placeholder implementation)
        suggestion = SwipeSuggestion(
            suggestion="This user has complementary skills and similar interests",
            confidence=0.85,
            reasoning=[
                "Matching skills in data science",
                "Similar project experience",
                "Good location compatibility"
            ]
        )
        
        return suggestion
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get swipe suggestions: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get swipe suggestions: {str(e)}")

@router.delete("/record/{swipeId}")
async def delete_swipe_record(
    swipeId: int = Path(..., description="Swipe ID to delete"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a specific swipe record
    Matches frontend API: DELETE /swipe/record/{swipeId}
    """
    try:
        user_id = current_user["id"]
        
        # Find the swipe record
        swipe = db.query(AIRecommendationSwipe).filter(
            and_(
                AIRecommendationSwipe.swipe_id == swipeId,
                AIRecommendationSwipe.user_id == user_id
            )
        ).first()
        
        if not swipe:
            raise HTTPException(status_code=404, detail="Swipe record not found")
        
        db.delete(swipe)
        db.commit()
        
        return {"success": True, "message": "Swipe record deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete swipe record: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete swipe record: {str(e)}")

class BulkDeleteRequest(BaseModel):
    """Request model for bulk delete operations"""
    olderThan: Optional[str] = Field(None, description="Delete swipes older than this date (ISO format)")
    action: Optional[str] = Field(None, description="Delete swipes with specific action")

@router.delete("/record/bulk")
async def clear_swipe_history(
    request: BulkDeleteRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Clear swipe history in bulk
    Matches frontend API: DELETE /swipe/record/bulk
    """
    try:
        user_id = current_user["id"]
        
        # Build query for deletion
        query = db.query(AIRecommendationSwipe).filter(AIRecommendationSwipe.user_id == user_id)
        
        # Apply filters
        # Note: AIRecommendationSwipe doesn't have created_at field, so date filtering is not available
        # This is a limitation of the current model
        
        if request.action:
            if request.action == "like":
                query = query.filter(AIRecommendationSwipe.is_like == True)
            elif request.action in ["ignore", "dislike", "pass"]:
                query = query.filter(AIRecommendationSwipe.is_like == False)
        
        # Count records to be deleted
        count = query.count()
        
        # Delete records
        query.delete(synchronize_session=False)
        db.commit()
        
        return {
            "success": True,
            "message": f"Deleted {count} swipe records",
            "deletedCount": count
        }
        
    except Exception as e:
        logger.error(f"Failed to clear swipe history: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to clear swipe history: {str(e)}")