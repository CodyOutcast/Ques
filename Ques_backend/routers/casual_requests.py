"""
Casual Requests API Router
Handles social activity requests and matching
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import logging
from datetime import datetime, timedelta

from dependencies.db import get_db
from dependencies.auth import get_current_user
from models.casual_requests import CasualRequest
from schemas.casual_requests import (
    CasualRequestCreate,
    CasualRequestUpdate,
    CasualRequestResponse,
    CasualRequestSearch,
    CasualRequestMatch,
    CasualRequestStats,
    CasualRequestList
)

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/", response_model=CasualRequestResponse, status_code=status.HTTP_201_CREATED)
async def create_or_update_casual_request(
    request_data: CasualRequestCreate,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Create or update a casual request for the current user
    Only one active request per user is maintained
    """
    try:
        user_id = str(current_user["id"])
        
        # Simple AI optimization (in production, use proper AI service)
        optimized_query = f"Seeking: {request_data.query}"
        if request_data.province_id and request_data.city_id:
            # You might want to fetch province/city names for the optimized query
            optimized_query += f" in province {request_data.province_id}, city {request_data.city_id}"
        if request_data.preferences:
            if "activity_type" in request_data.preferences:
                optimized_query += f" - {request_data.preferences['activity_type']} activity"
        
        casual_request = CasualRequest.upsert_request(
            db=db,
            user_id=user_id,
            query=request_data.query,
            optimized_query=optimized_query,
            province_id=request_data.province_id,
            city_id=request_data.city_id,
            preferences=request_data.preferences
        )
        
        logger.info(f"Casual request created/updated for user {user_id}")
        return casual_request
        
    except Exception as e:
        logger.error(f"Error creating casual request: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create casual request"
        )

@router.get("/my-request", response_model=Optional[CasualRequestResponse])
async def get_my_casual_request(
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get the current user's active casual request"""
    try:
        user_id = str(current_user["id"])
        request = CasualRequest.get_active_by_user(db, user_id)
        
        if request:
            # Update last activity
            request.update_activity(db)
        
        return request
        
    except Exception as e:
        logger.error(f"Error fetching casual request: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch casual request"
        )

@router.put("/my-request", response_model=CasualRequestResponse)
async def update_my_casual_request(
    updates: CasualRequestUpdate,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Update the current user's casual request"""
    try:
        user_id = str(current_user["id"])
        request = CasualRequest.get_active_by_user(db, user_id)
        
        if not request:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No active casual request found"
            )
        
        # Update fields if provided
        if updates.query is not None:
            request.query = updates.query
            # Re-optimize query
            request.optimized_query = f"Seeking: {updates.query}"
            if request.province_id and request.city_id:
                request.optimized_query += f" in province {request.province_id}, city {request.city_id}"
        
        if updates.province_id is not None:
            request.province_id = updates.province_id
            
        if updates.city_id is not None:
            request.city_id = updates.city_id
        
        if updates.preferences is not None:
            request.preferences = updates.preferences
            
        if updates.is_active is not None:
            request.is_active = updates.is_active
        
        request.updated_at = datetime.utcnow()
        request.last_activity_at = datetime.utcnow()
        
        db.commit()
        db.refresh(request)
        
        logger.info(f"Casual request updated for user {user_id}")
        return request
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating casual request: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update casual request"
        )

@router.delete("/my-request", status_code=status.HTTP_204_NO_CONTENT)
async def delete_my_casual_request(
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Delete/deactivate the current user's casual request"""
    try:
        user_id = str(current_user["id"])
        request = CasualRequest.get_active_by_user(db, user_id)
        
        if not request:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No active casual request found"
            )
        
        request.deactivate(db)
        logger.info(f"Casual request deactivated for user {user_id}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting casual request: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete casual request"
        )

@router.get("/search", response_model=List[CasualRequestResponse])
async def search_casual_requests(
    province_id: Optional[int] = Query(None, description="Filter by province ID"),
    city_id: Optional[int] = Query(None, description="Filter by city ID"),
    limit: int = Query(20, ge=1, le=100, description="Number of results"),
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Search for casual requests by location"""
    try:
        user_id = str(current_user["id"])
        
        if province_id or city_id:
            requests = CasualRequest.search_by_location(db, province_id, city_id, limit)
        else:
            requests = CasualRequest.get_active_requests(db, limit)
        
        # Exclude current user's own request
        filtered_requests = [r for r in requests if r.user_id != user_id]
        
        return filtered_requests
        
    except Exception as e:
        logger.error(f"Error searching casual requests: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to search casual requests"
        )

@router.get("/matches", response_model=List[CasualRequestMatch])
async def get_potential_matches(
    limit: int = Query(10, ge=1, le=50, description="Number of matches to return"),
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get potential matches for the current user's request"""
    try:
        user_id = str(current_user["id"])
        my_request = CasualRequest.get_active_by_user(db, user_id)
        
        if not my_request:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No active casual request found. Create one first."
            )
        
        # Get other active requests
        all_requests = CasualRequest.get_active_requests(db, 100)
        other_requests = [r for r in all_requests if r.user_id != user_id]
        
        matches = []
        for request in other_requests[:limit]:
            # Simple matching algorithm (in production, use AI/ML)
            similarity_score = 0.0
            match_reasons = []
            
            # Location matching
            if my_request.province_id and request.province_id:
                if my_request.province_id == request.province_id:
                    similarity_score += 0.4
                    match_reasons.append(f"Same province")
                    
                    # Additional score for same city
                    if my_request.city_id and request.city_id and my_request.city_id == request.city_id:
                        similarity_score += 0.2
                        match_reasons.append(f"Same city")
            
            # Preferences matching
            if my_request.preferences and request.preferences:
                if my_request.preferences.get("activity_type") == request.preferences.get("activity_type"):
                    similarity_score += 0.3
                    match_reasons.append("Similar activity type")
            
            # Query similarity (simple keyword matching)
            my_words = set(my_request.query.lower().split())
            their_words = set(request.query.lower().split())
            common_words = my_words.intersection(their_words)
            if common_words:
                similarity_score += min(0.3, len(common_words) * 0.1)
                match_reasons.append("Similar interests")
            
            if similarity_score > 0.2:  # Minimum threshold
                matches.append(CasualRequestMatch(
                    request=request,
                    similarity_score=similarity_score,
                    match_reasons=match_reasons
                ))
        
        # Sort by similarity score
        matches.sort(key=lambda x: x.similarity_score, reverse=True)
        
        return matches[:limit]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting matches: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get potential matches"
        )

@router.get("/stats", response_model=CasualRequestStats)
async def get_casual_requests_stats(
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get statistics about casual requests"""
    try:
        # Total active requests
        total_active = db.query(CasualRequest).filter(CasualRequest.is_active == True).count()
        
        # Requests by province
        location_stats = {}
        province_data = db.query(CasualRequest.province_id, db.func.count(CasualRequest.id)).filter(
            CasualRequest.is_active == True,
            CasualRequest.province_id.isnot(None)
        ).group_by(CasualRequest.province_id).all()
        
        for province_id, count in province_data:
            if province_id:
                location_stats[f"province_{province_id}"] = count
        
        # Recent activity (last 24 hours)
        yesterday = datetime.utcnow() - timedelta(days=1)
        recent_activity = db.query(CasualRequest).filter(
            CasualRequest.last_activity_at >= yesterday
        ).count()
        
        # Average requests per day (last 7 days)
        week_ago = datetime.utcnow() - timedelta(days=7)
        week_requests = db.query(CasualRequest).filter(
            CasualRequest.created_at >= week_ago
        ).count()
        avg_per_day = week_requests / 7.0
        
        return CasualRequestStats(
            total_active_requests=total_active,
            requests_by_location=location_stats,
            recent_activity_count=recent_activity,
            average_requests_per_day=avg_per_day
        )
        
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get statistics"
        )

@router.post("/cleanup", status_code=status.HTTP_200_OK)
async def cleanup_expired_requests(
    days: int = Query(7, ge=1, le=30, description="Delete requests older than this many days"),
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Admin endpoint to clean up expired requests"""
    try:
        # In production, add admin role check here
        deleted_count = CasualRequest.cleanup_expired(db, days)
        
        logger.info(f"Cleaned up {deleted_count} expired casual requests (older than {days} days)")
        
        return {
            "message": f"Successfully cleaned up {deleted_count} expired requests",
            "deleted_count": deleted_count,
            "days_threshold": days
        }
        
    except Exception as e:
        logger.error(f"Error cleaning up requests: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to cleanup expired requests"
        )
