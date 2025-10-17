"""
Authentication router
Handles user registration, login, verification, and token management
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from typing import Optional
import logging

from dependencies.db import get_db
from dependencies.auth import get_current_user, get_current_active_user
from models.users import User
from models.user_auth import UserAuth, VerificationCode, RefreshToken, ProviderType
from services.auth_service import AuthService
from services.email_service import EmailService
from services.monitoring import log_security_event, setup_monitoring
from schemas.auth import (
    PhoneRegisterRequest, PhoneLoginRequest, WeChatRegisterRequest, WeChatLoginRequest,
    SendVerificationCodeRequest, VerifyPhoneRequest,
    RefreshTokenRequest, AuthResponse, UserResponse,
    UserProfile, MessageResponse, LogoutRequest
)

router = APIRouter(tags=["authentication"])
security = HTTPBearer()
logger = logging.getLogger(__name__)

# Initialize services
auth_service = AuthService()
email_service = EmailService()

@router.post("/register/phone", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register_with_phone(
    request: PhoneRegisterRequest,
    http_request: Request,
    db: Session = Depends(get_db)
):
    """
    Register a new user with phone number and SMS verification
    """
    client_ip = http_request.client.host if http_request.client else "unknown"
    
    try:
        # Register user using phone
        user, tokens = auth_service.register_user_phone(
            db=db,
            name=request.name,
            phone=request.phone,
            verification_code=request.verification_code,
            bio=request.bio
        )
        
        # Log security event
        log_security_event(
            "USER_REGISTRATION_SUCCESS",
            str(user.user_id),
            f"User registered with phone: {request.phone}"
        )
        
        # Create user profile response
        user_profile = UserProfile(
            id=user.user_id,
            name=user.name,
            bio=user.bio,
            auth_methods=["phone"]
        )
        
        return AuthResponse(
            user=user_profile,
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
            token_type=tokens["token_type"],
            expires_in=tokens["expires_in"]
        )
        
    except ValueError as e:
        log_security_event(
            "USER_REGISTRATION_FAILED",
            None,
            f"Registration failed: {str(e)}"
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )

@router.post("/login/phone", response_model=AuthResponse)
async def login_with_phone(
    request: PhoneLoginRequest,
    http_request: Request,
    db: Session = Depends(get_db)
):
    """
    Login with phone number and SMS verification code
    """
    client_ip = http_request.client.host if http_request.client else "unknown"
    
    try:
        # Authenticate user with phone and verification code
        user = auth_service.authenticate_user_phone(db, request.phone, request.verification_code)
        
        if not user:
            log_security_event(
                "USER_LOGIN_FAILED",
                None,
                f"Invalid credentials for phone: {request.phone}"
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid phone number or verification code"
            )
        
        # Generate tokens
        access_token = auth_service.create_access_token({"sub": str(user.user_id)})
        refresh_token = auth_service.create_refresh_token(
            db, user.user_id, 
            http_request.headers.get("user-agent", "Unknown")
        )
        
        # Log successful login
        log_security_event(
            "USER_LOGIN_SUCCESS",
            str(user.user_id),
            f"User logged in: {request.phone}"
        )
        
        # Create user profile response
        user_profile = UserProfile(
            id=user.user_id,
            name=user.name,
            bio=user.bio,
            auth_methods=["phone"]
        )
        
        return AuthResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=30 * 60,
            user=user_profile
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )

@router.post("/verify-phone")
async def verify_phone(
    verify_data: VerifyPhoneRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Verify user phone number with SMS verification code
    """
    try:
        is_verified = auth_service.verify_code(
            db, ProviderType.PHONE, verify_data.phone, 
            verify_data.verification_code, "PHONE_VERIFICATION"
        )
        
        if not is_verified:
            log_security_event(
                "PHONE_VERIFICATION_FAILED",
                None,
                f"Invalid verification code for: {verify_data.phone}"
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired verification code"
            )
        
        # Log successful verification
        user_auth = db.query(UserAuth).filter(
            UserAuth.provider_id == verify_data.phone
        ).first()
        
        if user_auth:
            log_security_event(
                "PHONE_VERIFICATION_SUCCESS",
                str(user_auth.user_id),
                f"Phone verified: {verify_data.phone}"
            )
        
        return {"message": "Phone number verified successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Phone verification error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Phone verification failed"
        )

@router.post("/refresh", response_model=dict)
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Refresh access token using refresh token
    """
    try:
        new_access_token = auth_service.refresh_access_token(db, refresh_data.refresh_token)
        
        if not new_access_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        return {
            "access_token": new_access_token,
            "token_type": "bearer"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh failed"
        )

@router.post("/logout")
async def logout(
    refresh_data: RefreshTokenRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Logout user by revoking refresh token
    """
    try:
        success = auth_service.revoke_refresh_token(db, refresh_data.refresh_token)
        
        if success:
            return {"message": "Logged out successfully"}
        else:
            return {"message": "Token already invalid"}
            
    except Exception as e:
        logger.error(f"Logout error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed"
        )

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current user information
    """
    # Get user's primary email
    primary_auth = None
    for auth_record in current_user.auth_records:
        if auth_record.is_primary and auth_record.provider_type == ProviderType.EMAIL:
            primary_auth = auth_record
            break
    
    return UserResponse(
        id=current_user.user_id,
        email=primary_auth.provider_id if primary_auth else None,
        username=current_user.name,
        display_name=current_user.name,
        avatar_url=None,  # TODO: Implement avatar system
        is_verified=current_user.verification_status == "verified",
        created_at=primary_auth.created_at if primary_auth else None
    )

@router.post("/resend-verification")
async def resend_verification_email(
    email_data: dict,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Resend verification email
    """
    try:
        email = email_data.get("email")
        if not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email is required"
            )
        
        # Check if user exists
        user_auth = db.query(UserAuth).filter(
            UserAuth.provider_id == email,
            UserAuth.provider_type == ProviderType.EMAIL
        ).first()
        
        if not user_auth:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        if user_auth.is_verified:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already verified"
            )
        
        # Create new verification code
        verification_code = auth_service.create_verification_code(
            db, ProviderType.EMAIL, email, "EMAIL_VERIFICATION"
        )
        
        # Send verification email
        await email_service.send_verification_email(email, verification_code)
        
        return {"message": "Verification email sent"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Resend verification error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send verification email"
        )

# Password reset functionality removed - using phone/SMS authentication only
