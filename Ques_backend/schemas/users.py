"""
User-related schemas for request/response validation
"""

from pydantic import BaseModel, HttpUrl
from typing import Optional, List
from datetime import datetime

# User profile schemas
class UserProfileBase(BaseModel):
    """Base user profile information"""
    username: str
    display_name: Optional[str] = None
    bio: Optional[str] = None
    age: Optional[int] = None
    location: Optional[str] = None
    gender: Optional[str] = None
    avatar_url: Optional[str] = None

class UserProfileResponse(UserProfileBase):
    """User profile response with read-only fields"""
    id: int
    email: Optional[str] = None
    is_verified: bool = False
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class UserCardResponse(BaseModel):
    """Simplified user card for browsing (used in recommendations, likes, etc.)"""
    id: int
    username: str
    display_name: Optional[str] = None
    bio: Optional[str] = None
    age: Optional[int] = None
    location: Optional[str] = None
    avatar_url: Optional[str] = None
    is_verified: bool = False
    
    class Config:
        from_attributes = True

class LikedUserResponse(UserCardResponse):
    """User profile with like information"""
    liked_at: datetime
    is_mutual_like: bool = False  # Whether they liked you back
    
    class Config:
        from_attributes = True

# Pagination schemas
class PaginatedResponse(BaseModel):
    """Generic paginated response"""
    page: int
    per_page: int
    total: int
    total_pages: int
    has_next: bool
    has_prev: bool

class LikedUsersResponse(PaginatedResponse):
    """Paginated response for liked users"""
    users: List[LikedUserResponse]

# Search schemas
class UserSearchResponse(BaseModel):
    """User search result"""
    id: int
    username: str
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None
    is_verified: bool = False
    
    class Config:
        from_attributes = True

# Update profile schema
class UpdateProfileRequest(BaseModel):
    """Request to update user profile"""
    display_name: Optional[str] = None
    bio: Optional[str] = None
    age: Optional[int] = None
    location: Optional[str] = None
    gender: Optional[str] = None
    avatar_url: Optional[str] = None
