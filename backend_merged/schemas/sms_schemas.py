"""
SMS Verification Schemas
Pydantic models for SMS verification API requests and responses
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any
from datetime import datetime
import re

class SMSSendRequest(BaseModel):
    """Request model for sending SMS verification code"""
    phone_number: str = Field(..., description="Phone number to send verification code to")
    country_code: str = Field(default="+86", description="Country code (default: +86 for China)")
    purpose: str = Field(default="REGISTRATION", description="Purpose of verification")
    
    @validator('phone_number')
    def validate_phone_number(cls, v):
        """Validate phone number format"""
        # Remove any non-digit characters for validation
        digits_only = re.sub(r'\D', '', v)
        
        # Basic validation - should have reasonable length
        if len(digits_only) < 10 or len(digits_only) > 15:
            raise ValueError('Phone number must be between 10-15 digits')
        
        return v
    
    @validator('country_code')
    def validate_country_code(cls, v):
        """Validate country code format"""
        if not v.startswith('+'):
            v = '+' + v
        
        # Remove + for digit validation
        digits_only = v[1:]
        if not digits_only.isdigit() or len(digits_only) > 4:
            raise ValueError('Invalid country code format')
        
        return v
    
    @validator('purpose')
    def validate_purpose(cls, v):
        """Validate verification purpose"""
        allowed_purposes = ['REGISTRATION', 'PASSWORD_RESET', 'PHONE_CHANGE', 'LOGIN_VERIFICATION']
        if v.upper() not in allowed_purposes:
            raise ValueError(f'Purpose must be one of: {", ".join(allowed_purposes)}')
        return v.upper()

class SMSVerifyRequest(BaseModel):
    """Request model for verifying SMS code"""
    phone_number: str = Field(..., description="Phone number that received the code")
    verification_code: str = Field(..., description="6-digit verification code")
    country_code: str = Field(default="+86", description="Country code")
    purpose: str = Field(default="REGISTRATION", description="Purpose of verification")
    
    @validator('phone_number')
    def validate_phone_number(cls, v):
        """Validate phone number format"""
        digits_only = re.sub(r'\D', '', v)
        if len(digits_only) < 10 or len(digits_only) > 15:
            raise ValueError('Phone number must be between 10-15 digits')
        return v
    
    @validator('verification_code')
    def validate_verification_code(cls, v):
        """Validate verification code format"""
        if not v.isdigit():
            raise ValueError('Verification code must contain only digits')
        if len(v) < 4 or len(v) > 8:
            raise ValueError('Verification code must be between 4-8 digits')
        return v
    
    @validator('country_code')
    def validate_country_code(cls, v):
        """Validate country code format"""
        if not v.startswith('+'):
            v = '+' + v
        
        digits_only = v[1:]
        if not digits_only.isdigit() or len(digits_only) > 4:
            raise ValueError('Invalid country code format')
        
        return v
    
    @validator('purpose')
    def validate_purpose(cls, v):
        """Validate verification purpose"""
        allowed_purposes = ['REGISTRATION', 'PASSWORD_RESET', 'PHONE_CHANGE', 'LOGIN_VERIFICATION']
        if v.upper() not in allowed_purposes:
            raise ValueError(f'Purpose must be one of: {", ".join(allowed_purposes)}')
        return v.upper()

class SMSStatusRequest(BaseModel):
    """Request model for checking SMS verification status"""
    phone_number: str = Field(..., description="Phone number to check status for")
    country_code: str = Field(default="+86", description="Country code")
    purpose: str = Field(default="REGISTRATION", description="Purpose of verification")
    
    @validator('phone_number')
    def validate_phone_number(cls, v):
        """Validate phone number format"""
        digits_only = re.sub(r'\D', '', v)
        if len(digits_only) < 10 or len(digits_only) > 15:
            raise ValueError('Phone number must be between 10-15 digits')
        return v
    
    @validator('country_code')
    def validate_country_code(cls, v):
        """Validate country code format"""
        if not v.startswith('+'):
            v = '+' + v
        
        digits_only = v[1:]
        if not digits_only.isdigit() or len(digits_only) > 4:
            raise ValueError('Invalid country code format')
        
        return v
    
    @validator('purpose')
    def validate_purpose(cls, v):
        """Validate verification purpose"""
        allowed_purposes = ['REGISTRATION', 'PASSWORD_RESET', 'PHONE_CHANGE', 'LOGIN_VERIFICATION']
        if v.upper() not in allowed_purposes:
            raise ValueError(f'Purpose must be one of: {", ".join(allowed_purposes)}')
        return v.upper()

class SMSSendResponse(BaseModel):
    """Response model for SMS send operation"""
    success: bool = Field(..., description="Whether SMS was sent successfully")
    message: str = Field(..., description="Response message")
    verification_id: Optional[str] = Field(None, description="Verification code ID for tracking")
    expires_in_minutes: Optional[int] = Field(None, description="Code expiration time in minutes")
    rate_limit_seconds: Optional[int] = Field(None, description="Seconds to wait before next request")

class SMSVerifyResponse(BaseModel):
    """Response model for SMS verification operation"""
    success: bool = Field(..., description="Whether verification was successful")
    message: str = Field(..., description="Response message")
    verified_at: Optional[datetime] = Field(None, description="Timestamp when verified")
    remaining_attempts: Optional[int] = Field(None, description="Remaining verification attempts")

class SMSStatusResponse(BaseModel):
    """Response model for SMS verification status"""
    is_verified: bool = Field(..., description="Whether phone number is already verified")
    has_pending_code: bool = Field(default=False, description="Whether there's a pending verification code")
    expires_in_seconds: Optional[int] = Field(None, description="Seconds until current code expires")
    attempts_used: Optional[int] = Field(None, description="Number of verification attempts used")
    max_attempts: Optional[int] = Field(None, description="Maximum allowed attempts")
    can_request_new: bool = Field(default=True, description="Whether a new code can be requested")
    verified_at: Optional[datetime] = Field(None, description="When the phone was verified")
    message: str = Field(..., description="Status message")
    error: Optional[str] = Field(None, description="Error message if any")

class PhoneRegistrationRequest(BaseModel):
    """Request model for phone number registration"""
    phone_number: str = Field(..., description="Phone number for registration")
    verification_code: str = Field(..., description="SMS verification code")
    country_code: str = Field(default="+86", description="Country code")
    password: str = Field(..., min_length=6, description="User password")
    confirm_password: str = Field(..., description="Password confirmation")
    
    # Optional user profile fields
    full_name: Optional[str] = Field(None, max_length=100, description="User's full name")
    email: Optional[str] = Field(None, description="Optional email address")
    gender: Optional[str] = Field(None, description="User gender")
    date_of_birth: Optional[str] = Field(None, description="Date of birth (YYYY-MM-DD)")
    
    @validator('phone_number')
    def validate_phone_number(cls, v):
        """Validate phone number format"""
        digits_only = re.sub(r'\D', '', v)
        if len(digits_only) < 10 or len(digits_only) > 15:
            raise ValueError('Phone number must be between 10-15 digits')
        return v
    
    @validator('verification_code')
    def validate_verification_code(cls, v):
        """Validate verification code format"""
        if not v.isdigit():
            raise ValueError('Verification code must contain only digits')
        if len(v) < 4 or len(v) > 8:
            raise ValueError('Verification code must be between 4-8 digits')
        return v
    
    @validator('confirm_password')
    def validate_passwords_match(cls, v, values):
        """Validate that passwords match"""
        if 'password' in values and v != values['password']:
            raise ValueError('Passwords do not match')
        return v
    
    @validator('email')
    def validate_email(cls, v):
        """Validate email format if provided"""
        if v is not None:
            import re
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, v):
                raise ValueError('Invalid email format')
        return v
    
    @validator('gender')
    def validate_gender(cls, v):
        """Validate gender if provided"""
        if v is not None:
            allowed_genders = ['male', 'female', 'other', 'prefer_not_to_say']
            if v.lower() not in allowed_genders:
                raise ValueError(f'Gender must be one of: {", ".join(allowed_genders)}')
            return v.lower()
        return v
    
    @validator('date_of_birth')
    def validate_date_of_birth(cls, v):
        """Validate date of birth format if provided"""
        if v is not None:
            try:
                from datetime import datetime
                birth_date = datetime.strptime(v, '%Y-%m-%d')
                
                # Check if date is reasonable (not in future, not too old)
                today = datetime.now()
                age = today.year - birth_date.year
                
                if birth_date > today:
                    raise ValueError('Date of birth cannot be in the future')
                if age > 120:
                    raise ValueError('Invalid date of birth')
                if age < 13:
                    raise ValueError('Must be at least 13 years old to register')
                    
            except ValueError as e:
                if 'time data' in str(e):
                    raise ValueError('Date of birth must be in YYYY-MM-DD format')
                raise e
        return v

class PhoneRegistrationResponse(BaseModel):
    """Response model for phone registration"""
    success: bool = Field(..., description="Whether registration was successful")
    message: str = Field(..., description="Response message")
    user_id: Optional[int] = Field(None, description="Created user ID")
    access_token: Optional[str] = Field(None, description="JWT access token")
    refresh_token: Optional[str] = Field(None, description="JWT refresh token")
    expires_in: Optional[int] = Field(None, description="Token expiration time in seconds")

class ErrorResponse(BaseModel):
    """Error response model"""
    success: bool = Field(default=False, description="Always false for errors")
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
