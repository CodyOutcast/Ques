"""
Pydantic schemas for user settings matching frontend API documentation
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum

class SearchMode(str, Enum):
    """Search mode enum"""
    INSIDE = "inside"
    GLOBAL = "global"

class Theme(str, Enum):
    """Theme options"""
    LIGHT = "light"
    DARK = "dark"
    AUTO = "auto"

class Plan(str, Enum):
    """Plan types"""
    BASIC = "basic"
    PRO = "pro"

# ============================================================================
# Notification Settings
# ============================================================================

class NotificationSettings(BaseModel):
    """Notification settings structure matching frontend API"""
    emailNotifications: bool = Field(True, description="Email notifications enabled")
    pushNotifications: bool = Field(True, description="Push notifications enabled")
    whisperRequests: bool = Field(True, description="Whisper request notifications")
    friendRequests: bool = Field(True, description="Friend request notifications")
    matches: bool = Field(True, description="Match notifications")
    messages: bool = Field(True, description="Message notifications")
    system: bool = Field(True, description="System notifications")
    gifts: bool = Field(True, description="Gift notifications")

class UpdateNotificationSettings(BaseModel):
    """Request schema for updating notification settings"""
    notifications: NotificationSettings = Field(..., description="Notification settings to update")

# ============================================================================
# User Preferences
# ============================================================================

class UserPreferences(BaseModel):
    """User preferences structure matching frontend API"""
    searchMode: SearchMode = Field(SearchMode.INSIDE, description="Search mode preference")
    autoAcceptMatches: bool = Field(False, description="Auto accept matches")
    showOnlineStatus: bool = Field(True, description="Show online status to others")

class UpdateUserPreferences(BaseModel):
    """Request schema for updating user preferences"""
    preferences: UserPreferences = Field(..., description="User preferences to update")

# ============================================================================
# Whisper Settings
# ============================================================================

class WhisperSettings(BaseModel):
    """Whisper settings structure matching frontend API"""
    wechatId: str = Field(..., description="WeChat ID for whispers")  # From user_profiles
    customMessage: Optional[str] = Field(None, description="Custom whisper message")
    autoAccept: bool = Field(False, description="Auto accept whispers")
    showOnlineStatus: bool = Field(True, description="Show online status in whispers")
    enableNotifications: bool = Field(True, description="Enable whisper notifications")

class UpdateWhisperSettings(BaseModel):
    """Request schema for updating whisper settings"""
    customMessage: Optional[str] = Field(None, description="Custom whisper message")
    autoAccept: Optional[bool] = Field(None, description="Auto accept whispers")
    showOnlineStatus: Optional[bool] = Field(None, description="Show online status")
    enableNotifications: Optional[bool] = Field(None, description="Enable notifications")

# ============================================================================
# Complete Settings Response
# ============================================================================

class UserSettingsResponse(BaseModel):
    """Complete user settings response matching frontend API exactly"""
    id: str = Field(..., description="Settings ID")
    userId: str = Field(..., description="User ID")
    plan: Plan = Field(..., description="User's current plan")  # From memberships table
    receivesLeft: int = Field(..., description="Receives remaining")  # From memberships table
    whisperCount: int = Field(..., description="Whispers sent count")  # From quotas or calculated
    
    notifications: NotificationSettings = Field(..., description="Notification settings")
    preferences: UserPreferences = Field(..., description="User preferences")
    
    createdAt: datetime = Field(..., description="Settings created timestamp")
    updatedAt: datetime = Field(..., description="Settings updated timestamp")

    class Config:
        from_attributes = True

# ============================================================================
# Statistics Response
# ============================================================================

class UserStatistics(BaseModel):
    """User statistics response matching frontend API"""
    totalWhispersSent: int = Field(0, description="Total whispers sent")
    totalWhispersReceived: int = Field(0, description="Total whispers received")
    totalMatches: int = Field(0, description="Total matches")
    totalReceivesUsed: int = Field(0, description="Total receives used")
    joinDate: datetime = Field(..., description="User join date")
    lastActiveDate: Optional[datetime] = Field(None, description="Last active timestamp")

# ============================================================================
# Account Management
# ============================================================================

class LogoutRequest(BaseModel):
    """Logout request schema"""
    allDevices: Optional[bool] = Field(False, description="Logout from all devices")

class DeleteAccountRequest(BaseModel):
    """Delete account request schema"""
    confirmPassword: str = Field(..., description="Password confirmation")
    reason: Optional[str] = Field(None, description="Reason for deletion")
    feedback: Optional[str] = Field(None, description="User feedback")

class DeleteAccountResponse(BaseModel):
    """Delete account response schema"""
    message: str = Field(..., description="Deletion confirmation message")
    deletedAt: datetime = Field(..., description="Deletion timestamp")
    dataRetentionDays: int = Field(30, description="Days data will be retained")

class ExportDataResponse(BaseModel):
    """Export data response schema"""
    downloadUrl: str = Field(..., description="Download URL for exported data")
    expiresAt: datetime = Field(..., description="URL expiration time")

class AccountInfo(BaseModel):
    """Account information response"""
    userId: str = Field(..., description="User ID")
    email: Optional[str] = Field(None, description="User email")
    phoneNumber: Optional[str] = Field(None, description="User phone number")  
    createdAt: datetime = Field(..., description="Account creation date")
    lastLoginAt: Optional[datetime] = Field(None, description="Last login timestamp")
    dataRetentionDays: int = Field(30, description="Data retention policy")