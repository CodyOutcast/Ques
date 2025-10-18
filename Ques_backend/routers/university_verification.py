"""
University Verification API Router
Handles university email verification endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional, Dict, Any
from dependencies.db import get_db
from dependencies.auth import get_current_user
from services.university_verification_service import UniversityVerificationService
from models.users import User
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/university", tags=["University Verification"])

# Request/Response Models
class UniversityVerificationRequest(BaseModel):
    """Request model for initiating university email verification"""
    email: EmailStr = Field(..., description="University email address ending with .edu.cn")
    
    @validator('email')
    def validate_email_domain(cls, v):
        """Validate that email ends with .edu.cn or .ac.cn"""
        if not v.lower().endswith(('.edu.cn', '.ac.cn')):
            raise ValueError('Email must be from a Chinese university (.edu.cn or .ac.cn domain)')
        return v.lower()

class ConfirmVerificationRequest(BaseModel):
    """Request model for confirming university email verification"""
    email: EmailStr = Field(..., description="University email address")
    token: str = Field(..., description="Verification token from email")

class UniversityVerificationResponse(BaseModel):
    """Response model for verification operations"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None

class UniversityStatusResponse(BaseModel):
    """Response model for verification status"""
    verified: bool
    email: Optional[str] = None
    university_name: Optional[str] = None
    verified_at: Optional[str] = None
    pending: Optional[bool] = None
    expires_at: Optional[str] = None
    can_resend: Optional[bool] = None

# API Endpoints
@router.post("/verify", response_model=UniversityVerificationResponse)
async def initiate_university_verification(
    request: UniversityVerificationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Initiate university email verification
    
    - **email**: Must be a valid Chinese university email (.edu.cn or .ac.cn)
    - Sends verification email with token
    - Token expires in 24 hours
    - Maximum 3 attempts per email
    """
    try:
        verification_service = UniversityVerificationService(db)
        
        success, message, verification_id = verification_service.initiate_verification(
            user_id=current_user.id,
            email=request.email
        )
        
        if success:
            return UniversityVerificationResponse(
                success=True,
                message=message,
                data={
                    "verification_id": verification_id,
                    "email": request.email,
                    "expires_in_hours": 24
                }
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=message
            )
            
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )
    except Exception as e:
        logger.error(f"Error in university verification endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error occurred"
        )

@router.post("/confirm", response_model=UniversityVerificationResponse)
async def confirm_university_verification(
    request: ConfirmVerificationRequest,
    db: Session = Depends(get_db)
):
    """
    Confirm university email verification using token
    
    - **email**: University email address
    - **token**: Verification token received via email
    - Marks user as university verified
    - Updates user profile with university information
    """
    try:
        verification_service = UniversityVerificationService(db)
        
        success, message, verification_data = verification_service.verify_token(
            email=request.email,
            token=request.token
        )
        
        if success:
            return UniversityVerificationResponse(
                success=True,
                message=message,
                data=verification_data
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=message
            )
            
    except Exception as e:
        logger.error(f"Error in confirm verification endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error occurred"
        )

@router.get("/status", response_model=UniversityStatusResponse)
async def get_verification_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current university verification status for the authenticated user
    
    Returns:
    - Verification status (verified/pending/none)
    - University email if verified
    - University name if available
    - Verification timestamp
    - Pending verification details (if applicable)
    """
    try:
        verification_service = UniversityVerificationService(db)
        
        status_data = verification_service.get_verification_status(current_user.id)
        
        return UniversityStatusResponse(**status_data)
        
    except Exception as e:
        logger.error(f"Error getting verification status for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get verification status"
        )

@router.post("/resend", response_model=UniversityVerificationResponse)
async def resend_verification_email(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Resend university verification email
    
    - Resends verification email for pending verification
    - Updates expiration time to 24 hours from now
    - Increments attempt counter
    - Maximum 3 attempts allowed
    """
    try:
        verification_service = UniversityVerificationService(db)
        
        success, message = verification_service.resend_verification(current_user.id)
        
        if success:
            return UniversityVerificationResponse(
                success=True,
                message=message,
                data={"expires_in_hours": 24}
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=message
            )
            
    except Exception as e:
        logger.error(f"Error resending verification for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to resend verification email"
        )

@router.get("/universities", response_model=Dict[str, Any])
async def get_supported_universities():
    """
    Get list of supported universities and their domains
    
    Returns:
    - List of supported university domains
    - University name mappings
    - Validation rules
    """
    try:
        # This could be moved to a configuration file or database
        supported_universities = {
            "domains": [".edu.cn", ".ac.cn"],
            "universities": {
                "pku.edu.cn": "Peking University (北京大学)",
                "tsinghua.edu.cn": "Tsinghua University (清华大学)", 
                "fudan.edu.cn": "Fudan University (复旦大学)",
                "sjtu.edu.cn": "Shanghai Jiao Tong University (上海交通大学)",
                "zju.edu.cn": "Zhejiang University (浙江大学)",
                "nju.edu.cn": "Nanjing University (南京大学)",
                "hit.edu.cn": "Harbin Institute of Technology (哈尔滨工业大学)",
                "xjtu.edu.cn": "Xi'an Jiaotong University (西安交通大学)",
                "buaa.edu.cn": "Beihang University (北京航空航天大学)",
                "bit.edu.cn": "Beijing Institute of Technology (北京理工大学)"
            },
            "requirements": {
                "email_format": "user@university.edu.cn or user@university.ac.cn",
                "verification_expiry": "24 hours",
                "max_attempts": 3
            }
        }
        
        return {
            "success": True,
            "data": supported_universities
        }
        
    except Exception as e:
        logger.error(f"Error getting supported universities: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get supported universities"
        )

# Health check endpoint
@router.get("/health")
async def university_verification_health():
    """Health check for university verification service"""
    return {
        "service": "University Verification",
        "status": "healthy",
        "version": "1.0.0",
        "supported_domains": [".edu.cn", ".ac.cn"]
    }
