from pydantic import BaseModel, EmailStr, validator
from typing import Optional, Literal
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

class WeChatLoginRequest(BaseModel):
    wechat_code: str  # Authorization code from WeChat
    name: Optional[str] = None  # For first-time registration
    bio: Optional[str] = None

class SendVerificationCodeRequest(BaseModel):
    provider_type: Literal["email"]
    provider_id: str  # email address
    purpose: Literal["registration", "login", "password_reset"]
    language: Optional[Literal["en", "zh"]] = "en"  # Default to English

class PasswordResetRequest(BaseModel):
    email: EmailStr
    verification_code: str
    new_password: str

class RefreshTokenRequest(BaseModel):
    refresh_token: str

# Response Models
class AuthResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds
    user: "UserProfile"

class UserProfile(BaseModel):
    id: int
    name: str
    bio: Optional[str]
    auth_methods: list[str]  # ["email", "wechat"]
    
    class Config:
        from_attributes = True

class VerificationCodeResponse(BaseModel):
    message: str
    expires_in: int  # seconds

class TokenRefreshResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds

# Update the forward reference
AuthResponse.model_rebuild()
