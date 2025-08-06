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
    RegisterRequest, LoginRequest, VerifyEmailRequest,
    RefreshTokenRequest, AuthResponse, UserResponse,
    EmailRegisterRequest, UserProfile, EmailLoginRequest,
    ForgotPasswordRequest, ResetPasswordRequest, MessageResponse
)

router = APIRouter(tags=["authentication"])
security = HTTPBearer()
logger = logging.getLogger(__name__)

# Initialize services
auth_service = AuthService()
email_service = EmailService()

@router.post("/register/email", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register_with_email(
    request: EmailRegisterRequest,
    http_request: Request,
    db: Session = Depends(get_db)
):
    """
    Register a new user with email and password - backend_p12 style
    """
    client_ip = http_request.client.host if http_request.client else "unknown"
    user_agent = http_request.headers.get("User-Agent", "unknown")
    
    try:
        # Register user using backend_p12 style
        user, tokens = auth_service.register_user_email(
            db=db,
            name=request.name,
            email=request.email,
            password=request.password,
            bio=request.bio
        )
        
        # Log security event
        log_security_event(
            "USER_REGISTRATION_SUCCESS",
            str(user.user_id),
            f"User registered with email: {request.email}"
        )
        
        # Create user profile response
        user_profile = UserProfile(
            id=user.user_id,
            name=user.name,
            bio=user.bio,
            auth_methods=["email"]
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

@router.post("/login/email", response_model=AuthResponse)
async def login_with_email(
    request: EmailLoginRequest,
    http_request: Request,
    db: Session = Depends(get_db)
):
    """
    Login with email and password - backend_p12 style
    """
    client_ip = http_request.client.host if http_request.client else "unknown"
    user_agent = http_request.headers.get("User-Agent", "unknown")
    
    try:
        # Authenticate user
        user = auth_service.authenticate_user(db, request.email, request.password)
        
        if not user:
            log_security_event(
                "USER_LOGIN_FAILED",
                None,
                f"Invalid credentials for email: {request.email}"
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
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
            f"User logged in: {request.email}"
        )
        
        # Create user profile response
        user_profile = UserProfile(
            id=user.user_id,
            name=user.name,
            bio=user.bio,
            auth_methods=["email"]
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

@router.post("/verify-email")
async def verify_email(
    verify_data: VerifyEmailRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Verify user email with verification code
    """
    try:
        is_verified = auth_service.verify_code(
            db, ProviderType.EMAIL, verify_data.email, 
            verify_data.code, "EMAIL_VERIFICATION"
        )
        
        if not is_verified:
            log_security_event(
                "EMAIL_VERIFICATION_FAILED",
                None,
                f"Invalid verification code for: {verify_data.email}"
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired verification code"
            )
        
        # Log successful verification
        user_auth = db.query(UserAuth).filter(
            UserAuth.provider_id == verify_data.email
        ).first()
        
        if user_auth:
            log_security_event(
                "EMAIL_VERIFICATION_SUCCESS",
                str(user_auth.user_id),
                f"Email verified: {verify_data.email}"
            )
        
        return {"message": "Email verified successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Email verification error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Email verification failed"
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

@router.post("/forgot-password", response_model=MessageResponse)
async def forgot_password(
    request: ForgotPasswordRequest,
    http_request: Request,
    db: Session = Depends(get_db)
):
    """
    Send password reset email with verification code
    """
    client_ip = http_request.client.host if http_request.client else "unknown"
    
    try:
        # Send password reset email
        success = auth_service.send_password_reset_email(db, request.email)
        
        # Log the security event
        log_security_event(
            event_type="password_reset_requested",
            user_id=None,  # Don't reveal if user exists
            ip_address=client_ip,
            details={"email_domain": request.email.split("@")[1] if "@" in request.email else "unknown"}
        )
        
        # Always return success to prevent email enumeration
        return MessageResponse(
            message="If the email exists, a password reset code has been sent.",
            success=True
        )
        
    except Exception as e:
        logger.error(f"Forgot password error: {e}")
        # Still return success to prevent email enumeration
        return MessageResponse(
            message="If the email exists, a password reset code has been sent.",
            success=True
        )

@router.post("/reset-password", response_model=MessageResponse)
async def reset_password(
    request: ResetPasswordRequest,
    http_request: Request,
    db: Session = Depends(get_db)
):
    """
    Reset password using verification code
    """
    client_ip = http_request.client.host if http_request.client else "unknown"
    
    try:
        # Reset password
        success = auth_service.reset_password_with_code(
            db, request.email, request.reset_code, request.new_password
        )
        
        if success:
            # Log successful password reset
            log_security_event(
                event_type="password_reset_successful",
                user_id=None,  # We could get user_id but keep it simple for now
                ip_address=client_ip,
                details={"email": request.email}
            )
            
            return MessageResponse(
                message="Password reset successfully. Please log in with your new password.",
                success=True
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to reset password"
            )
        
    except HTTPException:
        # Log failed attempt
        log_security_event(
            event_type="password_reset_failed",
            user_id=None,
            ip_address=client_ip,
            details={"email": request.email, "reason": "invalid_code_or_email"}
        )
        raise
    except Exception as e:
        logger.error(f"Reset password error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reset password"
        )