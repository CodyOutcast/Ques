"""
Schemas for online users tracking API
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class OnlineUserResponse(BaseModel):
    """Response model for online user information"""
    user_id: int
    username: Optional[str] = None
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None
    last_seen: Optional[str] = None  # ISO format datetime string
    session_count: int = 1
    status: str = "online"  # online, offline, recently_active, very_active

class OnlineCountResponse(BaseModel):
    """Response model for online user count"""
    online_count: int = Field(..., description="Number of users currently online")
    threshold_minutes: int = Field(..., description="Minutes threshold used for 'online' status")
    timestamp: str = Field(..., description="When this count was generated")

class OnlineUsersListResponse(BaseModel):
    """Response model for list of online users"""
    online_users: List[OnlineUserResponse]
    count: int = Field(..., description="Number of online users returned")
    threshold_minutes: int = Field(..., description="Minutes threshold used")
    timestamp: str = Field(..., description="When this list was generated")

class UserSessionResponse(BaseModel):
    """Response model for user session information"""
    session_id: int
    device_name: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    location: Optional[str] = None
    created_at: Optional[str] = None  # ISO format datetime string
    last_activity: Optional[str] = None  # ISO format datetime string
    expires_at: Optional[str] = None  # ISO format datetime string

class UserSessionsResponse(BaseModel):
    """Response model for user's sessions list"""
    sessions: List[UserSessionResponse]
    count: int = Field(..., description="Number of active sessions")
    user_id: int = Field(..., description="User ID these sessions belong to")

class OnlineStatsResponse(BaseModel):
    """Response model for comprehensive online statistics"""
    timestamp: str = Field(..., description="When these stats were generated")
    very_active_users: int = Field(..., description="Users active in last 5 minutes")
    online_users: int = Field(..., description="Users active in last 15 minutes")
    recently_active_users: int = Field(..., description="Users active in last hour")
    total_active_sessions: int = Field(..., description="Total number of active sessions")
    peak_hour_today: Optional[int] = Field(None, description="Hour with most activity today (0-23)")
    peak_users_today: int = Field(..., description="Peak user count today")
    status: str = Field(..., description="Status of the stats generation")

class UserOnlineStatusResponse(BaseModel):
    """Response model for individual user online status"""
    user_id: int
    status: str = Field(..., description="User status: online, offline, recently_active, very_active, unknown")
    last_seen: Optional[str] = Field(None, description="Last activity timestamp (ISO format)")
    is_online: bool = Field(..., description="Whether user is considered online")
    session_count: Optional[int] = Field(None, description="Number of active sessions")

class SessionCleanupResponse(BaseModel):
    """Response model for session cleanup operation"""
    message: str = Field(..., description="Cleanup operation message")
    cleaned_sessions: int = Field(..., description="Number of sessions that were cleaned up")
    timestamp: str = Field(..., description="When cleanup was performed")

class PublicOnlineCountResponse(BaseModel):
    """Response model for public online count endpoint"""
    online_count: int = Field(..., description="Number of users currently online")
    message: str = Field(..., description="Descriptive message")

# WebSocket message schemas (for future real-time updates)
class OnlineUserUpdateMessage(BaseModel):
    """WebSocket message for online user updates"""
    type: str = "online_update"  # Message type
    action: str = Field(..., description="Action: user_online, user_offline, count_update")
    user_id: Optional[int] = None
    username: Optional[str] = None
    online_count: Optional[int] = None
    timestamp: str = Field(..., description="Update timestamp")

class ActivityLevel(BaseModel):
    """Model for different activity levels"""
    very_active: str = "very_active"    # Last 5 minutes
    online: str = "online"              # Last 15 minutes
    recently_active: str = "recently_active"  # Last hour
    offline: str = "offline"            # More than 1 hour
