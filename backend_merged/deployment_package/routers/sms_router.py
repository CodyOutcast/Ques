"""
SMS Verification API Router
Handles SMS verification endpoints for user registration and authentication
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import Dict, Any
import logging

from dependencies.db import get_db
from dependencies.auth import get_current_user
from services.sms_service import get_sms_service
from services.auth_service import AuthService
from schemas.sms_schemas import (
    SMSSendRequest, SMSSendResponse,
    SMSVerifyRequest, SMSVerifyResponse,
    SMSStatusRequest, SMSStatusResponse,
    PhoneRegistrationRequest, PhoneRegistrationResponse,
    ErrorResponse
)
from models.users import User
from models.user_auth import UserAuth, ProviderType

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/sms", tags=["SMS Verification"])

# Initialize services
auth_service = AuthService()

@router.post(
    "/send-code",
    response_model=SMSSendResponse,
    summary="Send SMS Verification Code",
    description="Send a verification code to a phone number for registration or other purposes"
)
async def send_sms_verification_code(
    request: SMSSendRequest,
    db: Session = Depends(get_db),
    client_request: Request = None
):
    """
    Send SMS verification code to a phone number
    
    - **phone_number**: Phone number to send verification code to
    - **country_code**: Country code (default: +86)
    - **purpose**: Purpose of verification (REGISTRATION, PASSWORD_RESET, etc.)
    """
    try:
        sms_service = get_sms_service()
        
        # Rate limiting could be added here based on IP or phone number
        client_ip = client_request.client.host if client_request else None
        logger.info(f"SMS verification request from IP: {client_ip} for phone: {request.phone_number}")
        
        # Check if phone number is already registered (for registration purpose)
        if request.purpose == "REGISTRATION":
            formatted_phone = sms_service._format_phone_number(request.phone_number, request.country_code)
            existing_auth = db.query(UserAuth).filter(
                UserAuth.provider_type == ProviderType.PHONE,
                UserAuth.provider_id == formatted_phone,
                UserAuth.is_verified == True
            ).first()
            
            if existing_auth:
                return SMSSendResponse(
                    success=False,
                    message="Phone number is already registered",
                    rate_limit_seconds=60
                )
        
        # Send SMS
        success, message, verification_id = await sms_service.send_verification_sms(
            db=db,
            phone_number=request.phone_number,
            purpose=request.purpose,
            country_code=request.country_code
        )
        
        response_data = {
            "success": success,
            "message": message,
            "verification_id": verification_id
        }
        
        if success:
            response_data["expires_in_minutes"] = sms_service.code_expiry_minutes
        else:
            response_data["rate_limit_seconds"] = sms_service.rate_limit_minutes * 60
        
        return SMSSendResponse(**response_data)
        
    except Exception as e:
        logger.error(f"Error in send_sms_verification_code: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send verification code"
        )

@router.post(
    "/verify-code",
    response_model=SMSVerifyResponse,
    summary="Verify SMS Code",
    description="Verify SMS verification code"
)
async def verify_sms_code(
    request: SMSVerifyRequest,
    db: Session = Depends(get_db)
):
    """
    Verify SMS verification code
    
    - **phone_number**: Phone number that received the code
    - **verification_code**: The 6-digit verification code
    - **country_code**: Country code
    - **purpose**: Purpose of verification
    """
    try:
        sms_service = get_sms_service()
        
        # Verify SMS code
        success, message, verification_record = await sms_service.verify_sms_code(
            db=db,
            phone_number=request.phone_number,
            code=request.verification_code,
            purpose=request.purpose,
            country_code=request.country_code
        )
        
        response_data = {
            "success": success,
            "message": message
        }
        
        if success and verification_record:
            response_data["verified_at"] = verification_record.used_at
        elif not success and verification_record:
            remaining = sms_service.max_attempts - verification_record.attempts
            response_data["remaining_attempts"] = max(0, remaining)
        
        return SMSVerifyResponse(**response_data)
        
    except Exception as e:
        logger.error(f"Error in verify_sms_code: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to verify code"
        )

@router.get(
    "/status",
    response_model=SMSStatusResponse,
    summary="Check SMS Verification Status",
    description="Check the verification status of a phone number"
)
async def check_sms_verification_status(
    phone_number: str,
    country_code: str = "+86",
    purpose: str = "REGISTRATION",
    db: Session = Depends(get_db)
):
    """
    Check SMS verification status for a phone number
    
    - **phone_number**: Phone number to check
    - **country_code**: Country code
    - **purpose**: Purpose of verification
    """
    try:
        sms_service = get_sms_service()
        
        # Check verification status
        status_info = await sms_service.check_phone_verification_status(
            db=db,
            phone_number=phone_number,
            purpose=purpose,
            country_code=country_code
        )
        
        return SMSStatusResponse(**status_info)
        
    except Exception as e:
        logger.error(f"Error in check_sms_verification_status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to check verification status"
        )

@router.post(
    "/register",
    response_model=PhoneRegistrationResponse,
    summary="Register with Phone Number",
    description="Complete user registration using verified phone number"
)
async def register_with_phone(
    request: PhoneRegistrationRequest,
    db: Session = Depends(get_db)
):
    """
    Register a new user account using verified phone number
    
    - **phone_number**: Verified phone number
    - **verification_code**: SMS verification code
    - **password**: User password
    - **confirm_password**: Password confirmation
    - Plus optional profile information
    """
    try:
        sms_service = get_sms_service()
        
        # First verify the SMS code
        success, verify_message, verification_record = await sms_service.verify_sms_code(
            db=db,
            phone_number=request.phone_number,
            code=request.verification_code,
            purpose="REGISTRATION",
            country_code=request.country_code
        )
        
        if not success:
            return PhoneRegistrationResponse(
                success=False,
                message=verify_message
            )
        
        # Format phone number
        formatted_phone = sms_service._format_phone_number(request.phone_number, request.country_code)
        
        # Check if phone is already registered
        existing_auth = db.query(UserAuth).filter(
            UserAuth.provider_type == ProviderType.PHONE,
            UserAuth.provider_id == formatted_phone,
            UserAuth.is_verified == True
        ).first()
        
        if existing_auth:
            return PhoneRegistrationResponse(
                success=False,
                message="Phone number is already registered"
            )
        
        # Create user account
        try:
            # Prepare user data
            user_data = {
                "phone_number": formatted_phone,
                "password": request.password,
                "full_name": request.full_name,
                "email": request.email,
                "gender": request.gender,
                "date_of_birth": request.date_of_birth
            }
            
            # Create user using auth service
            user, access_token, refresh_token = await auth_service.create_user_with_phone(
                db=db,
                phone_number=formatted_phone,
                password=request.password,
                user_data=user_data
            )
            
            logger.info(f"User registered successfully with phone: {formatted_phone}")
            
            return PhoneRegistrationResponse(
                success=True,
                message="Registration successful",
                user_id=user.user_id,
                access_token=access_token,
                refresh_token=refresh_token,
                expires_in=auth_service.ACCESS_TOKEN_EXPIRE_MINUTES * 60
            )
            
        except Exception as e:
            logger.error(f"Error creating user account: {str(e)}")
            return PhoneRegistrationResponse(
                success=False,
                message="Registration failed. Please try again."
            )
            
    except Exception as e:
        logger.error(f"Error in register_with_phone: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )

@router.post(
    "/cleanup-expired",
    summary="Cleanup Expired Codes",
    description="Clean up expired verification codes (Admin only)"
)
async def cleanup_expired_codes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Clean up expired verification codes (Admin functionality)
    
    Requires authentication and admin privileges
    """
    try:
        # Check if user has admin privileges (implement based on your user model)
        # This is a placeholder - adjust based on your actual admin check
        if not hasattr(current_user, 'is_admin') or not current_user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin privileges required"
            )
        
        sms_service = get_sms_service()
        
        # Clean up expired codes
        cleaned_count = await sms_service.cleanup_expired_codes(db)
        
        return {
            "success": True,
            "message": f"Cleaned up {cleaned_count} expired verification codes",
            "cleaned_count": cleaned_count
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in cleanup_expired_codes: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to cleanup expired codes"
        )

# Note: Exception handlers are handled at the application level in main.py
