"""
Page 3: User Creation/Registration Router
Handles user registration, profile setup, and user management
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from dependencies.db import get_db
from models.users import User, UserFeature, UserLink

router = APIRouter()

# Pydantic models for API requests/responses
class UserCreateRequest(BaseModel):
    name: str
    bio: Optional[str] = None
    feature_tags: Optional[List[str]] = []
    portfolio_links: Optional[List[str]] = []

class UserResponse(BaseModel):
    user_id: int
    name: str
    bio: Optional[str]
    verification_status: str
    is_active: bool
    created_at: datetime
    feature_tags: List[str]
    portfolio_links: List[str]

    class Config:
        from_attributes = True

class UserUpdateRequest(BaseModel):
    name: Optional[str] = None
    bio: Optional[str] = None
    feature_tags: Optional[List[str]] = None
    portfolio_links: Optional[List[str]] = None

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user_data: UserCreateRequest, db: Session = Depends(get_db)):
    """
    Page 3: Create a new user account with profile information
    """
    try:
        # Create the user
        new_user = User(
            name=user_data.name,
            bio=user_data.bio,
            verification_status="pending",
            is_active=True
        )
        
        db.add(new_user)
        db.flush()  # Get the user_id without committing
        
        # Add feature tags if provided
        for tag in user_data.feature_tags:
            user_feature = UserFeature(
                user_id=new_user.user_id,
                feature_name=tag
            )
            db.add(user_feature)
        
        # Add portfolio links if provided
        for link in user_data.portfolio_links:
            user_link = UserLink(
                user_id=new_user.user_id,
                link_url=link
            )
            db.add(user_link)
        
        db.commit()
        db.refresh(new_user)
        
        # Prepare response with related data
        feature_tags = [uf.feature_name for uf in new_user.features]
        portfolio_links = [ul.link_url for ul in new_user.links]
        
        return UserResponse(
            user_id=new_user.user_id,
            name=new_user.name,
            bio=new_user.bio,
            verification_status=new_user.verification_status,
            is_active=new_user.is_active,
            created_at=new_user.created_at,
            feature_tags=feature_tags,
            portfolio_links=portfolio_links
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create user: {str(e)}"
        )

@router.get("/profile/{user_id}", response_model=UserResponse)
def get_user_profile(user_id: int, db: Session = Depends(get_db)):
    """
    Get user profile information by user ID
    """
    user = db.query(User).filter(User.user_id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Get related data
    feature_tags = [uf.feature_name for uf in user.features]
    portfolio_links = [ul.link_url for ul in user.links]
    
    return UserResponse(
        user_id=user.user_id,
        name=user.name,
        bio=user.bio,
        verification_status=user.verification_status,
        is_active=user.is_active,
        created_at=user.created_at,
        feature_tags=feature_tags,
        portfolio_links=portfolio_links
    )

@router.put("/profile/{user_id}", response_model=UserResponse)
def update_user_profile(user_id: int, update_data: UserUpdateRequest, db: Session = Depends(get_db)):
    """
    Update user profile information
    """
    user = db.query(User).filter(User.user_id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    try:
        # Update basic user info
        if update_data.name is not None:
            user.name = update_data.name
        if update_data.bio is not None:
            user.bio = update_data.bio
        
        # Update feature tags if provided
        if update_data.feature_tags is not None:
            # Remove existing features
            db.query(UserFeature).filter(UserFeature.user_id == user_id).delete()
            
            # Add new features
            for tag in update_data.feature_tags:
                user_feature = UserFeature(
                    user_id=user_id,
                    feature_name=tag
                )
                db.add(user_feature)
        
        # Update portfolio links if provided
        if update_data.portfolio_links is not None:
            # Remove existing links
            db.query(UserLink).filter(UserLink.user_id == user_id).delete()
            
            # Add new links
            for link in update_data.portfolio_links:
                user_link = UserLink(
                    user_id=user_id,
                    link_url=link
                )
                db.add(user_link)
        
        db.commit()
        db.refresh(user)
        
        # Prepare response
        feature_tags = [uf.feature_name for uf in user.features]
        portfolio_links = [ul.link_url for ul in user.links]
        
        return UserResponse(
            user_id=user.user_id,
            name=user.name,
            bio=user.bio,
            verification_status=user.verification_status,
            is_active=user.is_active,
            created_at=user.created_at,
            feature_tags=feature_tags,
            portfolio_links=portfolio_links
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to update user: {str(e)}"
        )

@router.delete("/profile/{user_id}")
def deactivate_user(user_id: int, db: Session = Depends(get_db)):
    """
    Deactivate user account (soft delete)
    """
    user = db.query(User).filter(User.user_id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user.is_active = False
    db.commit()
    
    return {"message": "User account deactivated successfully"}

@router.get("/")
def get_all_users(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    """
    Get list of all active users (for admin or discovery)
    """
    users = db.query(User).filter(User.is_active == True).offset(skip).limit(limit).all()
    
    user_list = []
    for user in users:
        feature_tags = [uf.feature_name for uf in user.features]
        portfolio_links = [ul.link_url for ul in user.links]
        
        user_list.append(UserResponse(
            user_id=user.user_id,
            name=user.name,
            bio=user.bio,
            verification_status=user.verification_status,
            is_active=user.is_active,
            created_at=user.created_at,
            feature_tags=feature_tags,
            portfolio_links=portfolio_links
        ))
    
    return {"users": user_list, "total": len(user_list)}
