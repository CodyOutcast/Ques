"""
Online users API endpoints for tracking concurrent users
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from dependencies.db import get_db
from dependencies.auth import get_current_user
from services.online_users_service import OnlineUsersService
from models.users import User
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/online", tags=["Online Users"])

@router.get("/count")
async def get_online_user_count(
    active_threshold: int = Query(15, description="Minutes to consider a user as online", ge=1, le=60),
    db: Session = Depends(get_db)
):
    """
    Get the current count of online users
    
    **Parameters:**
    - **active_threshold**: Minutes to consider a user as online (1-60 minutes, default: 15)
    
    **Returns:**
    - Current count of online users
    """
    try:
        count = OnlineUsersService.get_online_user_count(db, active_threshold)
        return {
            "online_count": count,
            "threshold_minutes": active_threshold,
            "timestamp": "now"
        }
    except Exception as e:
        logger.error(f"Error getting online user count: {e}")
        raise HTTPException(status_code=500, detail="Failed to get online user count")

@router.get("/users")
async def get_online_users(
    active_threshold: int = Query(15, description="Minutes to consider a user as online", ge=1, le=60),
    limit: int = Query(50, description="Maximum number of users to return", ge=1, le=200),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get list of currently online users (requires authentication)
    
    **Parameters:**
    - **active_threshold**: Minutes to consider a user as online (1-60 minutes)
    - **limit**: Maximum number of users to return (1-200 users)
    
    **Returns:**
    - List of online users with their details
    """
    try:
        users = OnlineUsersService.get_online_users(db, active_threshold, limit)
        return {
            "online_users": users,
            "count": len(users),
            "threshold_minutes": active_threshold,
            "timestamp": "now"
        }
    except Exception as e:
        logger.error(f"Error getting online users: {e}")
        raise HTTPException(status_code=500, detail="Failed to get online users")

@router.get("/stats")
async def get_online_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive online user statistics (requires authentication)
    
    **Returns:**
    - Detailed statistics about online users including:
      - Very active users (last 5 minutes)
      - Online users (last 15 minutes)
      - Recently active users (last hour)
      - Total active sessions
      - Peak activity information
    """
    try:
        stats = OnlineUsersService.get_online_stats(db)
        return stats
    except Exception as e:
        logger.error(f"Error getting online stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get online statistics")

@router.get("/user/{user_id}")
async def get_user_online_status(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get online status for a specific user (requires authentication)
    
    **Parameters:**
    - **user_id**: ID of the user to check
    
    **Returns:**
    - User's online status and last activity information
    """
    try:
        status = OnlineUsersService.get_user_online_status(db, user_id)
        return status
    except Exception as e:
        logger.error(f"Error getting user online status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get user online status")

@router.get("/sessions")
async def get_my_sessions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all active sessions for the current user
    
    **Returns:**
    - List of user's active sessions with device and location information
    """
    try:
        sessions = OnlineUsersService.get_user_sessions(db, current_user.user_id)
        return {
            "sessions": sessions,
            "count": len(sessions),
            "user_id": current_user.user_id
        }
    except Exception as e:
        logger.error(f"Error getting user sessions: {e}")
        raise HTTPException(status_code=500, detail="Failed to get user sessions")

@router.post("/cleanup")
async def cleanup_expired_sessions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Clean up expired sessions (admin function - requires authentication)
    
    **Returns:**
    - Number of sessions that were cleaned up
    """
    try:
        # Note: In production, you might want to restrict this to admin users only
        cleaned_count = OnlineUsersService.cleanup_expired_sessions(db)
        return {
            "message": "Session cleanup completed",
            "cleaned_sessions": cleaned_count,
            "timestamp": "now"
        }
    except Exception as e:
        logger.error(f"Error cleaning up sessions: {e}")
        raise HTTPException(status_code=500, detail="Failed to cleanup sessions")

# Public endpoint for basic online count (no authentication required)
@router.get("/public/count")
async def get_public_online_count(
    db: Session = Depends(get_db)
):
    """
    Get basic online user count (public endpoint)
    
    **Returns:**
    - Current count of online users (public access)
    """
    try:
        count = OnlineUsersService.get_online_user_count(db, active_threshold_minutes=15)
        return {
            "online_count": count,
            "message": "Users currently online"
        }
    except Exception as e:
        logger.error(f"Error getting public online count: {e}")
        # Return 0 instead of error for public endpoint
        return {
            "online_count": 0,
            "message": "Unable to retrieve count"
        }
