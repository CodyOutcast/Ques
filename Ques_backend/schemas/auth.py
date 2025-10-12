"""
Authentication schemas for request/response validation
Updated to support only PHONE and WECHAT providers
"""

from pydantic import BaseModel, validator, Field
from typing import Optional, List
from datetime import datetime
import re

# Request Models
class PhoneLoginRequest(BaseModel):
    phone: str = Field(..., description="Phone number for login")
    verification_code: str = Field(..., description="SMS verification code")
    
    @validator('phone')
    def validate_phone(cls, v):
        # Basic phone validation - adjust pattern for your region
        if not re.match(r'^\+?1?\d{9,15}$', v.replace(' ', '').replace('-', '')):
            raise ValueError('Invalid phone number format')
        return v

class PhoneRegisterRequest(BaseModel):
    phone: str = Field(..., description="Phone number for registration")
    verification_code: str = Field(..., description="SMS verification code")
    name: str = Field(..., min_length=1, max_length=100, description="User name")
    bio: Optional[str] = Field(None, max_length=500, description="User bio")
    
    @validator('phone')
    def validate_phone(cls, v):
        if not re.match(r'^\+?1?\d{9,15}$', v.replace(' ', '').replace('-', '')):
            raise ValueError('Invalid phone number format')
        return v

class SendVerificationCodeRequest(BaseModel):
    phone: str = Field(..., description="Phone number to send verification code")
    purpose: str = Field("REGISTRATION", description="Purpose: REGISTRATION, LOGIN, PASSWORD_RESET")
    
    @validator('phone')
    def validate_phone(cls, v):
        if not re.match(r'^\+?1?\d{9,15}$', v.replace(' ', '').replace('-', '')):
            raise ValueError('Invalid phone number format')
        return v

class VerifyPhoneRequest(BaseModel):
    phone: str = Field(..., description="Phone number to verify")
    code: str = Field(..., description="Verification code")
    
    @validator('phone')
    def validate_phone(cls, v):
        if not re.match(r'^\+?1?\d{9,15}$', v.replace(' ', '').replace('-', '')):
            raise ValueError('Invalid phone number format')
        return v

class WeChatLoginRequest(BaseModel):
    code: str = Field(..., description="WeChat authorization code")
    
class WeChatRegisterRequest(BaseModel):
    code: str = Field(..., description="WeChat authorization code")
    name: str = Field(..., min_length=1, max_length=100, description="User name")
    bio: Optional[str] = Field(None, max_length=500, description="User bio")

class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(..., description="Refresh token")

class LogoutRequest(BaseModel):
    refresh_token: Optional[str] = Field(None, description="Refresh token to revoke")

# Response Models
class UserProfile(BaseModel):
    id: int
    name: str
    bio: Optional[str]
    phone: Optional[str] = None
    wechat_id: Optional[str] = None
    auth_methods: List[str] = []  # ["phone", "wechat"]
    is_verified: bool = False
    
    class Config:
        from_attributes = True

class UserResponse(BaseModel):
    id: int
    name: str
    phone: Optional[str] = None
    wechat_id: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    is_verified: bool = False
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class AuthResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds
    user: UserProfile

class TokenRefreshResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int

class VerificationResponse(BaseModel):
    success: bool
    message: str
    expires_in: Optional[int] = None  # seconds until code expires

class LogoutResponse(BaseModel):
    success: bool
    message: str = "Successfully logged out"

class AuthMethodResponse(BaseModel):
    """Response showing available authentication methods for a user"""
    phone: Optional[str] = None
    wechat_id: Optional[str] = None  
    has_phone: bool = False
    has_wechat: bool = False
    is_verified: bool = False

class MessageResponse(BaseModel):
    message: str
    success: bool = True
