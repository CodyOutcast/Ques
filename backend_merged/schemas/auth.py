"""
Authentication schemas for request/response validation
Based on backend_p12 patterns
"""

from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List
from datetime import datetime

# Request Models
class EmailLoginRequest(BaseModel):
    email: EmailStr
    password: str

class EmailRegisterRequest(BaseModel):
    email: EmailStr
    password: str
    name: str
    bio: Optional[str] = None
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    username: str
    display_name: Optional[str] = None
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v

class VerifyEmailRequest(BaseModel):
    email: EmailStr
    code: str

class WeChatLoginRequest(BaseModel):
    code: str

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    email: EmailStr
    reset_code: str
    new_password: str
    
    @validator('new_password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v

# Response Models
class UserProfile(BaseModel):
    id: int
    name: str
    bio: Optional[str]
    auth_methods: List[str]  # ["email", "wechat"]
    
    class Config:
        from_attributes = True

class UserResponse(BaseModel):
    id: int
    email: Optional[str]
    username: str
    display_name: Optional[str]
    avatar_url: Optional[str]
    is_verified: bool
    created_at: Optional[datetime]
    
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
    user: UserResponse

class MessageResponse(BaseModel):
    message: str
    success: bool = True
