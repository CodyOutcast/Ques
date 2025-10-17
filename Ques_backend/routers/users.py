"""
Users router
Handles user profile management, search, and basic operations
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional
import logging
import math

from dependencies.db import get_db
from models.users import User
from models.user_swipes import UserSwipe, SwipeDirection
from services.auth_service import AuthService
from services.monitoring import log_security_event
from schemas.users import (
    UserProfileResponse, UserCardResponse, LikedUserResponse, 
    LikedUsersResponse, UserSearchResponse, UpdateProfileRequest
)

router = APIRouter()
security = HTTPBearer()
logger = logging.getLogger(__name__)
auth_service = AuthService()

@router.get("/profile", response_model=UserProfileResponse)
async def get_my_profile(
    token: str = Depends(security),
    db: Session = Depends(get_db)
):
    """Get current user's profile"""
    current_user = auth_service.get_current_user(db, token.credentials)
    if not current_user:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # Get user's projects
    from models.user_projects import UserProject
    user_projects = db.query(UserProject).filter(
        UserProject.user_id == current_user.user_id
    ).order_by(UserProject.project_order.asc(), UserProject.created_at.desc()).all()
    
    return UserProfileResponse(
        id=current_user.user_id,
        username=current_user.username or f"user_{current_user.user_id}",
        display_name=current_user.display_name,
        email=current_user.email,
        avatar_url=current_user.avatar_url,
        bio=current_user.bio,
        location=current_user.location,
        age=current_user.age,
        gender=current_user.gender,
        is_verified=current_user.is_verified or False,
        created_at=current_user.created_at,
        projects=user_projects
    )

@router.put("/profile")
async def update_profile(
    profile_data: dict,
    token: str = Depends(security),
    db: Session = Depends(get_db)
):
    """Update user profile"""
    current_user = auth_service.get_current_user(db, token.credentials)
    if not current_user:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # Update allowed fields
    allowed_fields = ['display_name', 'bio', 'location', 'age', 'gender', 'avatar_url']
    for field in allowed_fields:
        if field in profile_data:
            setattr(current_user, field, profile_data[field])
    
    db.commit()
    db.refresh(current_user)
    
    return {"message": "Profile updated successfully"}

@router.get("/discover")
async def discover_users(
    limit: int = Query(10, le=50),
    offset: int = Query(0, ge=0),
    token: str = Depends(security),
    db: Session = Depends(get_db)
):
    """Discover potential matches"""
    current_user = auth_service.get_current_user(db, token.credentials)
    if not current_user:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # Simplified discovery - just get other users for now
    potential_matches = db.query(User).filter(
        User.user_id != current_user.user_id
    ).offset(offset).limit(limit).all()
    
    return [
        {
            "id": user.user_id,
            "username": user.username,
            "display_name": user.display_name,
            "avatar_url": user.avatar_url,
            "bio": user.bio,
            "age": user.age,
            "location": user.location
        }
        for user in potential_matches
    ]

@router.get("/{user_id}")
async def get_user_profile(
    user_id: int,
    token: str = Depends(security),
    db: Session = Depends(get_db)
):
    """Get specific user's profile"""
    current_user = auth_service.get_current_user(db, token.credentials)
    if not current_user:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "id": user.user_id,
        "username": user.username,
        "display_name": user.display_name,
        "avatar_url": user.avatar_url,
        "bio": user.bio,
        "age": user.age,
        "location": user.location,
        "created_at": user.created_at
    }

@router.post("/swipe")
async def swipe_user(
    swipe_data: dict,
    token: str = Depends(security),
    db: Session = Depends(get_db)
):
    """Swipe on a user (like/pass) - temporarily disabled"""
    current_user = auth_service.get_current_user(db, token.credentials)
    if not current_user:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # Temporarily return success without doing anything
    return {
        "message": "Swipe functionality temporarily disabled during setup",
        "is_match": False
    }

@router.get("/search/", response_model=List[UserSearchResponse])
async def search_users(
    q: str = Query(..., min_length=2),
    limit: int = Query(10, le=50),
    token: str = Depends(security),
    db: Session = Depends(get_db)
):
    """Search users by username or display name"""
    current_user = auth_service.get_current_user(db, token.credentials)
    if not current_user:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    users = db.query(User).filter(
        User.user_id != current_user.user_id,
        or_(User.username.ilike(f"%{q}%"), User.display_name.ilike(f"%{q}%"))
    ).limit(limit).all()
    
    return [
        UserSearchResponse(
            id=user.user_id,
            username=user.username or f"user_{user.user_id}",
            display_name=user.display_name,
            avatar_url=user.avatar_url,
            is_verified=user.is_verified or False
        )
        for user in users
    ]

@router.get("/liked", response_model=LikedUsersResponse)
async def get_liked_profiles(
    page: int = Query(1, ge=1, description="Page number (starts from 1)"),
    per_page: int = Query(20, ge=1, le=100, description="Number of users per page"),
    token: str = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Get profiles of users you have liked
    
    Returns paginated list of users that the current user has liked,
    with information about whether the like is mutual.
    """
    # Authenticate user
    current_user = auth_service.get_current_user(db, token.credentials)
    if not current_user:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    try:
        # Calculate offset for pagination
        offset = (page - 1) * per_page
        
        # Query for users the current user has liked using UserSwipe model
        # We'll check both UserSwipe and Like tables for comprehensive results
        
        # Get likes from UserSwipe table (direction = "like")
        swipe_likes_query = db.query(UserSwipe, User).join(
            User, UserSwipe.target_id == User.user_id
        ).filter(
            UserSwipe.swiper_id == current_user.user_id,
            UserSwipe.direction == SwipeDirection.like
        )
        
        # Get likes from Like table (for user-to-user likes)
        like_likes_query = db.query(Like, User).join(
            User, Like.liked_item_id == User.user_id
        ).filter(
            Like.liker_id == current_user.user_id,
            Like.liked_item_type == "USER"
        )
        
        # For now, let's focus on UserSwipe since it seems to be the primary model
        total_likes = swipe_likes_query.count()
        
        # Get paginated results
        swipe_results = swipe_likes_query.offset(offset).limit(per_page).all()
        
        # Build response with mutual like checking
        liked_users = []
        for swipe, user in swipe_results:
            # Check if it's a mutual like (they also liked the current user)
            mutual_like = db.query(UserSwipe).filter(
                UserSwipe.swiper_id == user.user_id,
                UserSwipe.target_id == current_user.user_id,
                UserSwipe.direction == SwipeDirection.like
            ).first() is not None
            
            liked_user = LikedUserResponse(
                id=user.user_id,
                username=user.username or f"user_{user.user_id}",
                display_name=user.display_name,
                bio=user.bio,
                age=user.age,
                location=user.location,
                avatar_url=user.avatar_url,
                is_verified=user.is_verified or False,
                liked_at=swipe.timestamp or swipe.timestamp,
                is_mutual_like=mutual_like
            )
            liked_users.append(liked_user)
        
        # Calculate pagination info
        total_pages = math.ceil(total_likes / per_page) if total_likes > 0 else 1
        has_next = page < total_pages
        has_prev = page > 1
        
        # Log the request for analytics
        log_security_event(
            event_type="liked_profiles_viewed",
            user_id=current_user.user_id,
            ip_address="unknown",  # You can get this from request if needed
            details={
                "page": page,
                "per_page": per_page,
                "total_likes": total_likes
            }
        )
        
        return LikedUsersResponse(
            page=page,
            per_page=per_page,
            total=total_likes,
            total_pages=total_pages,
            has_next=has_next,
            has_prev=has_prev,
            users=liked_users
        )
        
    except Exception as e:
        logger.error(f"Error fetching liked profiles for user {current_user.user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch liked profiles"
        )

@router.get("/liked/mutual", response_model=LikedUsersResponse)
async def get_mutual_likes(
    page: int = Query(1, ge=1, description="Page number (starts from 1)"),
    per_page: int = Query(20, ge=1, le=100, description="Number of users per page"),
    token: str = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Get profiles of users with mutual likes (matches)
    
    Returns paginated list of users where both users have liked each other.
    """
    # Authenticate user
    current_user = auth_service.get_current_user(db, token.credentials)
    if not current_user:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    try:
        # Calculate offset for pagination
        offset = (page - 1) * per_page
        
        # Query for mutual likes - users who liked current user AND current user liked them
        mutual_likes_query = db.query(UserSwipe, User).join(
            User, UserSwipe.target_id == User.user_id
        ).filter(
            UserSwipe.swiper_id == current_user.user_id,
            UserSwipe.direction == SwipeDirection.like
        ).filter(
            # Check if they also liked the current user back
            db.query(UserSwipe).filter(
                UserSwipe.swiper_id == User.user_id,
                UserSwipe.target_id == current_user.user_id,
                UserSwipe.direction == SwipeDirection.like
            ).exists()
        )
        
        total_mutual = mutual_likes_query.count()
        mutual_results = mutual_likes_query.offset(offset).limit(per_page).all()
        
        # Build response
        mutual_users = []
        for swipe, user in mutual_results:
            mutual_user = LikedUserResponse(
                id=user.user_id,
                username=user.username or f"user_{user.user_id}",
                display_name=user.display_name,
                bio=user.bio,
                age=user.age,
                location=user.location,
                avatar_url=user.avatar_url,
                is_verified=user.is_verified or False,
                liked_at=swipe.timestamp,
                is_mutual_like=True  # All results are mutual by definition
            )
            mutual_users.append(mutual_user)
        
        # Calculate pagination info
        total_pages = math.ceil(total_mutual / per_page) if total_mutual > 0 else 1
        has_next = page < total_pages
        has_prev = page > 1
        
        return LikedUsersResponse(
            page=page,
            per_page=per_page,
            total=total_mutual,
            total_pages=total_pages,
            has_next=has_next,
            has_prev=has_prev,
            users=mutual_users
        )
        
    except Exception as e:
        logger.error(f"Error fetching mutual likes for user {current_user.user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch mutual likes"
        )


@router.delete("/account", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_account(
    token: str = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Delete the current user's account permanently
    
    This will:
    - Remove all user data (profile, matches, messages, projects, etc.)
    - Invalidate all authentication tokens
    - Trigger CASCADE DELETE for all related entities
    - Cannot be undone
    
    Requires user authentication.
    """
    # Authenticate user
    current_user = auth_service.get_current_user(db, token.credentials)
    if not current_user:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    try:
        # Import here to avoid circular imports
        from ..services.user_service import UserService
        
        # Delete the user account (will cascade to all related entities)
        success = UserService.delete_user_account(db, current_user.user_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User account not found or already deleted"
            )
        
        logger.info(f"User account deleted successfully: user_id={current_user.user_id}")
        # Return 204 No Content (successful deletion)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting user account {current_user.user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete user account"
        )


@router.get("/account/deletion-preview")
async def get_deletion_preview(
    token: str = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Get a preview of what data will be deleted when the user deletes their account
    
    This shows users exactly what data will be permanently removed,
    helping them make an informed decision about account deletion.
    """
    # Authenticate user
    current_user = auth_service.get_current_user(db, token.credentials)
    if not current_user:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    try:
        from ..services.user_service import UserService
        
        preview = UserService.get_user_deletion_preview(db, current_user.user_id)
        
        if "error" in preview:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=preview["error"]
            )
        
        return preview
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating deletion preview for user {current_user.user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate deletion preview"
        )


@router.post("/account/deactivate", status_code=status.HTTP_200_OK)
async def deactivate_user_account(
    token: str = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Deactivate the current user's account (soft delete)
    
    This will:
    - Mark the account as inactive
    - Hide the user from discovery
    - Anonymize basic profile information
    - Preserve data for potential account recovery
    - Can be reversed by contacting support
    
    Requires user authentication.
    """
    # Authenticate user
    current_user = auth_service.get_current_user(db, token.credentials)
    if not current_user:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    try:
        from ..services.user_service import UserService
        
        # Soft delete the user account
        success = UserService.soft_delete_user_account(db, current_user.user_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User account not found"
            )
        
        logger.info(f"User account deactivated successfully: user_id={current_user.user_id}")
        return {
            "message": "Account deactivated successfully",
            "note": "Your account has been deactivated. Contact support to reactivate if needed."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deactivating user account {current_user.user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to deactivate user account"
        )
