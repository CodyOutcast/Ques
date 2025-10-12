"""
Pydantic schemas for settings management API
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


class ProfileVisibility(str, Enum):
    PUBLIC = "public"
    PRIVATE = "private"
    FRIENDS = "friends"


class MessagePermission(str, Enum):
    EVERYONE = "everyone"
    MATCHES = "matches"
    FRIENDS = "friends"
    NOBODY = "nobody"


class ContentFiltering(str, Enum):
    STRICT = "strict"
    MODERATE = "moderate"
    OFF = "off"


class ActionType(str, Enum):
    DEACTIVATE = "deactivate"
    DELETE = "delete"
    REACTIVATE = "reactivate"
    SUSPEND = "suspend"
    PASSWORD_CHANGE = "password_change"
    TWO_FACTOR_ENABLE = "two_factor_enable"
    TWO_FACTOR_DISABLE = "two_factor_disable"
    DATA_EXPORT = "data_export"
    PRIVACY_UPDATE = "privacy_update"


# Privacy Settings Schemas
class PrivacySettings(BaseModel):
    profile_visibility: ProfileVisibility = ProfileVisibility.PUBLIC
    show_online_status: bool = True
    allow_messages_from: MessagePermission = MessagePermission.EVERYONE
    show_location: bool = True
    show_university: bool = True
    show_age: bool = True


# Safety Settings Schemas  
class SafetySettings(BaseModel):
    block_screenshots: bool = False
    require_verification: bool = False
    auto_reject_spam: bool = True
    content_filtering: ContentFiltering = ContentFiltering.MODERATE


# Security Settings Schemas
class SecuritySettings(BaseModel):
    two_factor_enabled: bool = False
    login_notifications: bool = True
    session_timeout_minutes: int = Field(default=60, ge=5, le=1440)  # 5 minutes to 24 hours
    password_change_required: bool = False


# Communication Settings Schemas
class CommunicationSettings(BaseModel):
    allow_whispers: bool = True
    allow_friend_requests: bool = True
    auto_accept_matches: bool = False
    message_read_receipts: bool = True
    typing_indicators: bool = True


# Data Privacy Settings Schemas
class DataPrivacySettings(BaseModel):
    data_sharing_consent: bool = False
    analytics_tracking: bool = True
    personalized_ads: bool = True
    data_export_requested: bool = False
    marketing_emails: bool = True


# Notification Settings Schemas
class NotificationSettings(BaseModel):
    email_notifications: bool = True
    push_notifications: bool = True
    sms_notifications: bool = False


# Complete Account Settings Schema
class AccountSettingsResponse(BaseModel):
    privacy: PrivacySettings
    safety: SafetySettings
    security: SecuritySettings
    communication: CommunicationSettings
    data_privacy: DataPrivacySettings
    notifications: NotificationSettings
    
    class Config:
        from_attributes = True


class UpdateAccountSettingsRequest(BaseModel):
    privacy: Optional[PrivacySettings] = None
    safety: Optional[SafetySettings] = None
    security: Optional[SecuritySettings] = None
    communication: Optional[CommunicationSettings] = None
    data_privacy: Optional[DataPrivacySettings] = None
    notifications: Optional[NotificationSettings] = None


# Privacy Consent Schemas
class PrivacyConsentRequest(BaseModel):
    consent_type: str = Field(..., description="Type of consent: data_processing, marketing, analytics, cookies")
    consent_given: bool
    consent_version: str = Field(default="1.0")


class PrivacyConsentResponse(BaseModel):
    id: str
    consent_type: str
    consent_given: bool
    consent_version: str
    created_at: datetime
    expires_at: Optional[datetime] = None
    is_active: bool
    
    class Config:
        from_attributes = True


# Account Action Schemas
class AccountActionRequest(BaseModel):
    action_type: ActionType
    reason: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    scheduled_for: Optional[datetime] = None


class AccountActionResponse(BaseModel):
    id: str
    action_type: str
    reason: Optional[str]
    metadata: Optional[Dict[str, Any]]
    ip_address: Optional[str]
    scheduled_for: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: datetime
    is_pending: bool
    
    class Config:
        from_attributes = True


# Data Export Schemas
class DataExportRequest(BaseModel):
    request_type: str = Field(default="full", pattern="^(full|partial|delete)$")
    export_format: str = Field(default="json", pattern="^(json|csv|xml)$")


class DataExportResponse(BaseModel):
    id: str
    request_type: str
    status: str
    export_format: str
    export_url: Optional[str]
    expires_at: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: datetime
    is_completed: bool
    is_expired: bool
    
    class Config:
        from_attributes = True


# Two-Factor Authentication Schemas
class EnableTwoFactorRequest(BaseModel):
    verification_code: str = Field(..., min_length=6, max_length=6)


class TwoFactorSetupResponse(BaseModel):
    secret_key: str
    qr_code_url: str
    backup_codes: List[str]


class VerifyTwoFactorRequest(BaseModel):
    code: str = Field(..., min_length=6, max_length=6)


# Security Event Schemas
class SecurityEventResponse(BaseModel):
    event_type: str
    description: str
    ip_address: Optional[str]
    user_agent: Optional[str]
    created_at: datetime
    severity: str  # low, medium, high, critical


# Account Deactivation/Deletion Schemas
class DeactivateAccountRequest(BaseModel):
    reason: Optional[str] = None
    feedback: Optional[str] = None


class DeleteAccountRequest(BaseModel):
    reason: str = Field(..., min_length=1)
    confirmation_text: str = Field(..., description="Must type 'DELETE MY ACCOUNT' exactly")
    
    @validator('confirmation_text')
    def validate_confirmation(cls, v):
        if v != "DELETE MY ACCOUNT":
            raise ValueError("Confirmation text must be exactly 'DELETE MY ACCOUNT'")
        return v


class AccountDeletionResponse(BaseModel):
    scheduled_for: datetime
    confirmation_code: str
    data_export_available: bool
    export_expires_at: Optional[datetime]


# Password Change Schemas
class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8)
    confirm_password: str
    
    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Passwords do not match')
        return v


class PasswordChangeResponse(BaseModel):
    success: bool
    message: str
    force_logout_other_sessions: bool


# Session Management Schemas
class ActiveSessionResponse(BaseModel):
    session_id: str
    ip_address: Optional[str]
    user_agent: Optional[str]
    created_at: datetime
    last_active: datetime
    is_current: bool


class SessionManagementResponse(BaseModel):
    active_sessions: List[ActiveSessionResponse]
    max_concurrent_sessions: int
    current_session_count: int


# Settings Summary Schema
class SettingsSummaryResponse(BaseModel):
    account_settings: AccountSettingsResponse
    two_factor_enabled: bool
    privacy_consents: List[PrivacyConsentResponse]
    pending_actions: List[AccountActionResponse]
    security_score: int = Field(..., ge=0, le=100, description="Overall security score")
    recommendations: List[str] = Field(default_factory=list, description="Security recommendations")
    
    class Config:
        from_attributes = True