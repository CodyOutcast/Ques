"""
New swipe service router - matches frontend API documentation exactly
Uses the new SwipeRecord model and provides all endpoints from frontend docs
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, desc, case, extract
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging
from collections import Counter

from dependencies.db import get_db
from dependencies.auth import get_current_user
from models.swipes import SwipeRecord, SwipeAction, SearchMode
from schemas.swipes import (
    RecordSwipeRequest, 
    BatchRecordSwipeRequest,
    SwipeRecordResponse, 
    SwipeHistoryQuery,
    SwipeStatistics,
    SwipePreferences,
    SwipeSuggestion,
    BulkDeleteRequest
)

router = APIRouter(prefix="/swipe", tags=["Card Swiping"])
logger = logging.getLogger(__name__)

# ============================================================================
# API Endpoints - Matching Frontend Documentation Exactly
# ============================================================================

@router.post("/record", response_model=SwipeRecordResponse)
async def record_swipe(
    request: RecordSwipeRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Record a single swipe action
    Frontend API: POST /swipe/record
    """
    try:
        user_id = current_user["id"]
        
        # Create new swipe record using the new model
        swipe = SwipeRecord(
            user_id=user_id,
            target_user_id=request.targetUserId,
            action=request.action.value,
            search_query=request.searchQuery,
            search_mode=request.searchMode.value if request.searchMode else None,
            match_score=request.matchScore,
            source_context=request.sourceContext.dict() if request.sourceContext else None
        )
        
        db.add(swipe)
        db.commit()
        db.refresh(swipe)
        
        return SwipeRecordResponse(
            id=swipe.id,
            userId=swipe.user_id,
            targetUserId=swipe.target_user_id,
            action=SwipeAction(swipe.action),
            searchQuery=swipe.search_query,
            searchMode=SearchMode(swipe.search_mode) if swipe.search_mode else None,
            matchScore=float(swipe.match_score) if swipe.match_score else None,
            sourceContext=swipe.source_context,
            createdAt=swipe.created_at,
            updatedAt=swipe.updated_at
        )
        
    except Exception as e:
        logger.error(f"Failed to record swipe: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to record swipe: {str(e)}")

@router.post("/record/batch")
async def batch_record_swipes(
    request: BatchRecordSwipeRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Record multiple swipe actions in batch
    Frontend API: POST /swipe/record/batch
    """
    try:
        user_id = current_user["id"]
        results = []
        
        for swipe_request in request.swipes:
            try:
                swipe = SwipeRecord(
                    user_id=user_id,
                    target_user_id=swipe_request.targetUserId,
                    action=swipe_request.action.value,
                    search_query=swipe_request.searchQuery,
                    search_mode=swipe_request.searchMode.value if swipe_request.searchMode else None,
                    match_score=swipe_request.matchScore,
                    source_context=swipe_request.sourceContext.dict() if swipe_request.sourceContext else None
                )
                
                db.add(swipe)
                db.flush()  # Get the ID without committing yet
                
                results.append(SwipeRecordResponse(
                    id=swipe.id,
                    userId=swipe.user_id,
                    targetUserId=swipe.target_user_id,
                    action=SwipeAction(swipe.action),
                    searchQuery=swipe.search_query,
                    searchMode=SearchMode(swipe.search_mode) if swipe.search_mode else None,
                    matchScore=float(swipe.match_score) if swipe.match_score else None,
                    sourceContext=swipe.source_context,
                    createdAt=swipe.created_at,
                    updatedAt=swipe.updated_at
                ))
                
            except Exception as e:
                logger.error(f"Failed to record swipe for user {swipe_request.targetUserId}: {e}")
                continue
        
        db.commit()
        
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
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to batch record swipes: {str(e)}")

@router.get("/history")
async def get_swipe_history(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    action: Optional[SwipeAction] = Query(None, description="Filter by action"),
    startDate: Optional[datetime] = Query(None, description="Start date filter"),
    endDate: Optional[datetime] = Query(None, description="End date filter"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user's swipe history with pagination and filters
    Frontend API: GET /swipe/history
    """
    try:
        user_id = current_user["id"]
        offset = (page - 1) * limit
        
        # Build query with filters
        query = db.query(SwipeRecord).filter(SwipeRecord.user_id == user_id)
        
        if action:
            query = query.filter(SwipeRecord.action == action.value)
        
        if startDate:
            query = query.filter(SwipeRecord.created_at >= startDate)
            
        if endDate:
            query = query.filter(SwipeRecord.created_at <= endDate)
        
        # Get total count for pagination
        total = query.count()
        
        # Get paginated results
        swipes = query.order_by(desc(SwipeRecord.created_at)).offset(offset).limit(limit).all()
        
        # Convert to response format
        swipe_records = []
        for swipe in swipes:
            swipe_records.append(SwipeRecordResponse(
                id=swipe.id,
                userId=swipe.user_id,
                targetUserId=swipe.target_user_id,
                action=SwipeAction(swipe.action),
                searchQuery=swipe.search_query,
                searchMode=SearchMode(swipe.search_mode) if swipe.search_mode else None,
                matchScore=float(swipe.match_score) if swipe.match_score else None,
                sourceContext=swipe.source_context,
                createdAt=swipe.created_at,
                updatedAt=swipe.updated_at
            ))
        
        return {
            "success": True,
            "data": {
                "data": swipe_records,
                "pagination": {
                    "page": page,
                    "limit": limit,
                    "total": total,
                    "totalPages": (total + limit - 1) // limit
                }
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get swipe history: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get swipe history: {str(e)}")

@router.get("/stats", response_model=SwipeStatistics)
async def get_swipe_statistics(
    period: Optional[str] = Query("all", description="Period: all, week, month, year"),
    startDate: Optional[datetime] = Query(None, description="Start date filter"),
    endDate: Optional[datetime] = Query(None, description="End date filter"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get swipe statistics for user
    Frontend API: GET /swipe/stats
    """
    try:
        user_id = current_user["id"]
        
        # Build base query
        query = db.query(SwipeRecord).filter(SwipeRecord.user_id == user_id)
        
        # Apply date filters
        if period == "week":
            start_date = datetime.now() - timedelta(days=7)
            query = query.filter(SwipeRecord.created_at >= start_date)
        elif period == "month":
            start_date = datetime.now() - timedelta(days=30)
            query = query.filter(SwipeRecord.created_at >= start_date)
        elif period == "year":
            start_date = datetime.now() - timedelta(days=365)
            query = query.filter(SwipeRecord.created_at >= start_date)
            
        if startDate:
            query = query.filter(SwipeRecord.created_at >= startDate)
        if endDate:
            query = query.filter(SwipeRecord.created_at <= endDate)
        
        # Get all swipes for analysis
        swipes = query.all()
        
        # Calculate statistics
        total_swipes = len(swipes)
        likes = sum(1 for s in swipes if s.action == SwipeAction.LIKE.value)
        ignores = sum(1 for s in swipes if s.action == SwipeAction.IGNORE.value)
        super_likes = sum(1 for s in swipes if s.action == SwipeAction.SUPER_LIKE.value)
        
        # Calculate match rate (simplified - would need actual match data)
        match_rate = (likes + super_likes) / total_swipes if total_swipes > 0 else 0.0
        
        # Calculate average match score
        match_scores = [float(s.match_score) for s in swipes if s.match_score is not None]
        avg_match_score = sum(match_scores) / len(match_scores) if match_scores else 0.0
        
        # Daily swipe count for the period
        daily_counts = {}
        for swipe in swipes:
            date_str = swipe.created_at.date().isoformat()
            daily_counts[date_str] = daily_counts.get(date_str, 0) + 1
        
        daily_swipe_count = [{"date": date, "count": count} for date, count in daily_counts.items()]
        
        return SwipeStatistics(
            totalSwipes=total_swipes,
            likes=likes,
            ignores=ignores,
            superLikes=super_likes,
            matchRate=match_rate,
            mostSwipedSkills=[],  # Would need integration with user profile data
            mostSwipedLocations=[],  # Would need integration with user profile data
            averageMatchScore=avg_match_score,
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
    Get user's swipe preferences based on history
    Frontend API: GET /swipe/stats/preferences
    """
    try:
        user_id = current_user["id"]
        
        # Get user's swipe history for analysis
        swipes = db.query(SwipeRecord).filter(
            and_(
                SwipeRecord.user_id == user_id,
                SwipeRecord.action.in_([SwipeAction.LIKE.value, SwipeAction.SUPER_LIKE.value])
            )
        ).all()
        
        # Analyze patterns (simplified - would need more user data integration)
        avg_match_score = 0.0
        if swipes:
            match_scores = [float(s.match_score) for s in swipes if s.match_score is not None]
            avg_match_score = sum(match_scores) / len(match_scores) if match_scores else 0.0
        
        # Get most active hours
        hour_counts = Counter()
        for swipe in swipes:
            hour_counts[swipe.created_at.hour] += 1
        
        most_active_hours = [hour for hour, count in hour_counts.most_common(5)]
        
        return SwipePreferences(
            preferredSkills=[],  # Would need user profile integration
            preferredLocations=[],  # Would need user profile integration  
            preferredUniversities=[],  # Would need user profile integration
            averageMatchScore=avg_match_score,
            mostActiveHours=most_active_hours,
            swipePatterns={
                "total_positive_swipes": len(swipes),
                "avg_match_score": avg_match_score,
                "most_active_period": max(hour_counts.items(), key=lambda x: x[1])[0] if hour_counts else 0
            }
        )
        
    except Exception as e:
        logger.error(f"Failed to get swipe preferences: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get swipe preferences: {str(e)}")

@router.get("/stats/suggestions/{targetUserId}", response_model=SwipeSuggestion)
async def get_swipe_suggestions(
    targetUserId: str = Path(..., description="Target user ID"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get AI-generated swipe suggestions for a target user
    Frontend API: GET /swipe/stats/suggestions/{targetUserId}
    """
    try:
        user_id = current_user["id"]
        
        # Get user's swipe history to analyze patterns
        user_swipes = db.query(SwipeRecord).filter(SwipeRecord.user_id == user_id).all()
        
        # Simple AI suggestion based on match scores (would be more sophisticated in production)
        avg_match_score = 0.0
        if user_swipes:
            match_scores = [float(s.match_score) for s in user_swipes if s.match_score is not None]
            avg_match_score = sum(match_scores) / len(match_scores) if match_scores else 0.0
        
        # Generate suggestion (simplified logic)
        if avg_match_score > 0.7:
            suggested_action = SwipeAction.LIKE
            confidence = 0.8
            reasoning = ["High average match score indicates compatibility", "Previous swipe patterns suggest positive interest"]
        elif avg_match_score > 0.5:
            suggested_action = SwipeAction.LIKE
            confidence = 0.6
            reasoning = ["Moderate match score", "Could be worth exploring"]
        else:
            suggested_action = SwipeAction.IGNORE
            confidence = 0.7
            reasoning = ["Low historical match scores", "May not align with preferences"]
        
        return SwipeSuggestion(
            targetUserId=targetUserId,
            suggestedAction=suggested_action,
            confidence=confidence,
            reasoning=reasoning,
            matchScore=avg_match_score
        )
        
    except Exception as e:
        logger.error(f"Failed to get swipe suggestions: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get swipe suggestions: {str(e)}")

@router.delete("/record/{swipeId}")
async def delete_swipe_record(
    swipeId: int = Path(..., description="Swipe record ID"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a specific swipe record
    Frontend API: DELETE /swipe/record/{swipeId}
    """
    try:
        user_id = current_user["id"]
        
        # Find the swipe record
        swipe = db.query(SwipeRecord).filter(
            and_(
                SwipeRecord.id == swipeId,
                SwipeRecord.user_id == user_id
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

@router.delete("/record/bulk")
async def clear_swipe_history(
    request: BulkDeleteRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Clear swipe history with optional filters
    Frontend API: DELETE /swipe/record/bulk
    """
    try:
        user_id = current_user["id"]
        
        # Build deletion query
        query = db.query(SwipeRecord).filter(SwipeRecord.user_id == user_id)
        
        if request.olderThan:
            query = query.filter(SwipeRecord.created_at < request.olderThan)
            
        if request.action:
            query = query.filter(SwipeRecord.action == request.action.value)
        
        # Get count before deletion
        count = query.count()
        
        # Delete records
        query.delete()
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