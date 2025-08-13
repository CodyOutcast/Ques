"""
Profile router
Handles enhanced profile features, links, and profile management
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from typing import List
import logging

from dependencies.db import get_db
from models.users import User
from services.auth_service import AuthService

router = APIRouter()
security = HTTPBearer()
logger = logging.getLogger(__name__)
auth_service = AuthService()

@router.get("/")
async def get_profile(
    token: str = Depends(security),
    db: Session = Depends(get_db)
):
    """Get enhanced user profile"""
    current_user = auth_service.get_current_user(db, token.credentials)
    if not current_user:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    return {
        "id": current_user.id,
        "username": current_user.username,
        "display_name": current_user.display_name,
        "email": current_user.email,
        "avatar_url": current_user.avatar_url,
        "bio": current_user.bio,
        "location": current_user.location,
        "age": current_user.age,
        "gender": current_user.gender,
        "is_verified": current_user.is_verified,
        "created_at": current_user.created_at,
        "updated_at": current_user.updated_at
    }

@router.put("/")
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
    allowed_fields = [
        'display_name', 'bio', 'location', 'age', 'gender', 
        'avatar_url', 'interests', 'occupation', 'education'
    ]
    
    for field in allowed_fields:
        if field in profile_data:
            setattr(current_user, field, profile_data[field])
    
    db.commit()
    db.refresh(current_user)
    
    return {"message": "Profile updated successfully"}

@router.get("/links")
async def get_profile_links(
    token: str = Depends(security),
    db: Session = Depends(get_db)
):
    """Get user's social media links"""
    current_user = auth_service.get_current_user(db, token.credentials)
    if not current_user:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # Placeholder for user links
    # In a real implementation, you'd query the UserLinks table
    return {
        "links": [
            # {"platform": "instagram", "url": "https://instagram.com/username"},
            # {"platform": "linkedin", "url": "https://linkedin.com/in/username"}
        ]
    }

@router.post("/links")
async def add_profile_link(
    link_data: dict,
    token: str = Depends(security),
    db: Session = Depends(get_db)
):
    """Add a social media link to profile"""
    current_user = auth_service.get_current_user(db, token.credentials)
    if not current_user:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    platform = link_data.get("platform")
    url = link_data.get("url")
    
    if not platform or not url:
        raise HTTPException(status_code=400, detail="Platform and URL are required")
    
    # Placeholder for adding link
    # In a real implementation, you'd create a UserLink record
    
    return {"message": f"Added {platform} link successfully"}

@router.delete("/links/{platform}")
async def remove_profile_link(
    platform: str,
    token: str = Depends(security),
    db: Session = Depends(get_db)
):
    """Remove a social media link from profile"""
    current_user = auth_service.get_current_user(db, token.credentials)
    if not current_user:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # Placeholder for removing link
    # In a real implementation, you'd delete the UserLink record
    
    return {"message": f"Removed {platform} link successfully"}

@router.get("/features")
async def get_user_features(
    token: str = Depends(security),
    db: Session = Depends(get_db)
):
    """Get user's enabled features"""
    current_user = auth_service.get_current_user(db, token.credentials)
    if not current_user:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # Placeholder for user features
    # In a real implementation, you'd query the UserFeatures table
    return {
        "features": {
            "premium": False,
            "verified": current_user.is_verified,
            "boost": False,
            "super_like": True
        }
    }
