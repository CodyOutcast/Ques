"""
Tencent Cloud SMS Service for User Registration Verification
Implements SMS verification code sending and validation for phone number verification
"""

import os
import secrets
import string
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any, Tuple, List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

# Tencent Cloud SMS SDK
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.sms.v20210111 import sms_client, models

from models.user_auth import VerificationCode, ProviderType
from models.users import User

logger = logging.getLogger(__name__)

class TencentSMSService:
    """Tencent Cloud SMS Service for verification codes"""
    
    def __init__(self):
        # Load Tencent Cloud credentials
        self.secret_id = os.getenv("TENCENT_SECRET_ID")
        self.secret_key = os.getenv("TENCENT_SECRET_KEY")
        self.region = os.getenv("TENCENT_REGION", "ap-guangzhou")
        
        # SMS Configuration
        self.sms_sdk_app_id = os.getenv("TENCENT_SMS_SDK_APP_ID")
        self.sms_signature = os.getenv("TENCENT_SMS_SIGNATURE", "Ques")
        self.verification_template_id = os.getenv("TENCENT_SMS_VERIFICATION_TEMPLATE_ID")
        
        # Verification code settings
        self.code_length = int(os.getenv("SMS_CODE_LENGTH", "6"))
        self.code_expiry_minutes = int(os.getenv("SMS_CODE_EXPIRY_MINUTES", "10"))
        self.max_attempts = int(os.getenv("SMS_MAX_ATTEMPTS", "3"))
        self.rate_limit_minutes = int(os.getenv("SMS_RATE_LIMIT_MINUTES", "1"))
        
        # Validate required configuration
        if not all([self.secret_id, self.secret_key, self.sms_sdk_app_id, self.verification_template_id]):
            logger.error("Missing required Tencent Cloud SMS configuration")
            raise ValueError("Missing required SMS configuration")
        
        # Initialize SMS client
        try:
            cred = credential.Credential(self.secret_id, self.secret_key)
            httpProfile = HttpProfile()
            httpProfile.endpoint = "sms.tencentcloudapi.com"
            
            clientProfile = ClientProfile()
            clientProfile.httpProfile = httpProfile
            
            self.client = sms_client.SmsClient(cred, self.region, clientProfile)
            logger.info("Tencent Cloud SMS client initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize SMS client: {str(e)}")
            raise

    def _generate_verification_code(self) -> str:
        """Generate a random verification code"""
        return ''.join(secrets.choice(string.digits) for _ in range(self.code_length))

    def _format_phone_number(self, phone_number: str, country_code: str = "+86") -> str:
        """Format phone number to E.164 standard"""
        # Remove any spaces, dashes, or other characters
        clean_phone = ''.join(filter(str.isdigit, phone_number))
        
        # Handle Chinese phone numbers
        if country_code == "+86" or country_code == "86":
            if clean_phone.startswith("86"):
                clean_phone = clean_phone[2:]
            elif clean_phone.startswith("0086"):
                clean_phone = clean_phone[4:]
            
            # Chinese mobile numbers should be 11 digits
            if len(clean_phone) == 11:
                return f"+86{clean_phone}"
            else:
                raise ValueError("Invalid Chinese phone number format")
        
        # For other countries, ensure country code is included
        if not phone_number.startswith("+"):
            return f"{country_code}{clean_phone}"
        
        return phone_number

    def _validate_phone_number(self, phone_number: str) -> bool:
        """Validate phone number format"""
        try:
            formatted = self._format_phone_number(phone_number)
            # Basic validation: should start with + and have 10-15 digits
            if not formatted.startswith("+"):
                return False
            
            digits_only = formatted[1:]  # Remove +
            return digits_only.isdigit() and 10 <= len(digits_only) <= 15
            
        except ValueError:
            return False

    async def send_verification_sms(
        self, 
        db: Session, 
        phone_number: str, 
        purpose: str = "REGISTRATION",
        country_code: str = "+86"
    ) -> Tuple[bool, str, Optional[str]]:
        """
        Send SMS verification code
        
        Args:
            db: Database session
            phone_number: Phone number to send SMS to
            purpose: Purpose of verification (REGISTRATION, PASSWORD_RESET, etc.)
            country_code: Country code (default: +86 for China)
            
        Returns:
            Tuple of (success, message, verification_code_id)
        """
        try:
            # Validate phone number
            if not self._validate_phone_number(phone_number):
                return False, "Invalid phone number format", None
            
            # Format phone number
            formatted_phone = self._format_phone_number(phone_number, country_code)
            
            # Check rate limiting
            recent_code = db.query(VerificationCode).filter(
                VerificationCode.provider_type == ProviderType.PHONE,
                VerificationCode.provider_id == formatted_phone,
                VerificationCode.purpose == purpose,
                VerificationCode.created_at >= datetime.utcnow() - timedelta(minutes=self.rate_limit_minutes),
                VerificationCode.used_at.is_(None)
            ).first()
            
            if recent_code:
                return False, f"Please wait {self.rate_limit_minutes} minute(s) before requesting another code", None
            
            # Generate verification code
            verification_code = self._generate_verification_code()
            expires_at = datetime.utcnow() + timedelta(minutes=self.code_expiry_minutes)
            
            # Prepare SMS request
            req = models.SendSmsRequest()
            req.PhoneNumberSet = [formatted_phone]
            req.SmsSdkAppId = self.sms_sdk_app_id
            req.SignName = self.sms_signature
            req.TemplateId = self.verification_template_id
            req.TemplateParamSet = [verification_code, str(self.code_expiry_minutes)]
            
            # Send SMS via Tencent Cloud
            resp = self.client.SendSms(req)
            
            # Check if SMS was sent successfully
            if resp.SendStatusSet and len(resp.SendStatusSet) > 0:
                send_status = resp.SendStatusSet[0]
                
                if send_status.Code == "Ok":
                    # Store verification code in database
                    db_verification = VerificationCode(
                        provider_type=ProviderType.PHONE,
                        provider_id=formatted_phone,
                        code=verification_code,
                        purpose=purpose,
                        expires_at=expires_at,
                        attempts=0
                    )
                    
                    db.add(db_verification)
                    db.commit()
                    db.refresh(db_verification)
                    
                    logger.info(f"SMS verification code sent successfully to {formatted_phone}")
                    return True, "Verification code sent successfully", str(db_verification.id)
                    
                else:
                    error_msg = f"SMS sending failed: {send_status.Code} - {send_status.Message}"
                    logger.error(error_msg)
                    return False, "Failed to send SMS. Please try again.", None
            
            else:
                logger.error("No response status from SMS service")
                return False, "SMS service error. Please try again.", None
                
        except TencentCloudSDKException as e:
            error_msg = f"Tencent Cloud SMS error: {e.code} - {e.message}"
            logger.error(error_msg)
            return False, "SMS service temporarily unavailable", None
            
        except Exception as e:
            logger.error(f"Unexpected error sending SMS: {str(e)}")
            return False, "Failed to send verification code", None

    async def verify_sms_code(
        self, 
        db: Session, 
        phone_number: str, 
        code: str, 
        purpose: str = "REGISTRATION",
        country_code: str = "+86"
    ) -> Tuple[bool, str, Optional[VerificationCode]]:
        """
        Verify SMS verification code
        
        Args:
            db: Database session
            phone_number: Phone number that received the code
            code: Verification code to verify
            purpose: Purpose of verification
            country_code: Country code
            
        Returns:
            Tuple of (success, message, verification_record)
        """
        try:
            # Format phone number
            formatted_phone = self._format_phone_number(phone_number, country_code)
            
            # Find the verification code
            verification = db.query(VerificationCode).filter(
                VerificationCode.provider_type == ProviderType.PHONE,
                VerificationCode.provider_id == formatted_phone,
                VerificationCode.purpose == purpose,
                VerificationCode.used_at.is_(None),
                VerificationCode.expires_at > datetime.utcnow()
            ).order_by(VerificationCode.created_at.desc()).first()
            
            if not verification:
                return False, "No valid verification code found. Please request a new one.", None
            
            # Check attempt limit
            if verification.attempts >= self.max_attempts:
                return False, "Maximum verification attempts exceeded. Please request a new code.", None
            
            # Verify the code
            if verification.code == code:
                # Mark as used
                verification.used_at = datetime.utcnow()
                db.commit()
                
                logger.info(f"Phone number {formatted_phone} verified successfully")
                return True, "Phone number verified successfully", verification
                
            else:
                # Increment attempts
                verification.attempts += 1
                db.commit()
                
                remaining_attempts = self.max_attempts - verification.attempts
                if remaining_attempts > 0:
                    return False, f"Invalid verification code. {remaining_attempts} attempts remaining.", None
                else:
                    return False, "Invalid verification code. Maximum attempts exceeded.", None
                    
        except Exception as e:
            logger.error(f"Error verifying SMS code: {str(e)}")
            return False, "Verification failed. Please try again.", None

    async def check_phone_verification_status(
        self, 
        db: Session, 
        phone_number: str, 
        purpose: str = "REGISTRATION",
        country_code: str = "+86"
    ) -> Dict[str, Any]:
        """
        Check phone number verification status
        
        Args:
            db: Database session
            phone_number: Phone number to check
            purpose: Purpose of verification
            country_code: Country code
            
        Returns:
            Dictionary with verification status information
        """
        try:
            formatted_phone = self._format_phone_number(phone_number, country_code)
            
            # Check for completed verification
            completed_verification = db.query(VerificationCode).filter(
                VerificationCode.provider_type == ProviderType.PHONE,
                VerificationCode.provider_id == formatted_phone,
                VerificationCode.purpose == purpose,
                VerificationCode.used_at.isnot(None)
            ).order_by(VerificationCode.used_at.desc()).first()
            
            if completed_verification:
                return {
                    "is_verified": True,
                    "verified_at": completed_verification.used_at.isoformat(),
                    "can_request_new": False,
                    "message": "Phone number already verified"
                }
            
            # Check for pending verification
            pending_verification = db.query(VerificationCode).filter(
                VerificationCode.provider_type == ProviderType.PHONE,
                VerificationCode.provider_id == formatted_phone,
                VerificationCode.purpose == purpose,
                VerificationCode.used_at.is_(None),
                VerificationCode.expires_at > datetime.utcnow()
            ).order_by(VerificationCode.created_at.desc()).first()
            
            if pending_verification:
                time_remaining = (pending_verification.expires_at - datetime.utcnow()).total_seconds()
                can_request_new = (datetime.utcnow() - pending_verification.created_at).total_seconds() >= (self.rate_limit_minutes * 60)
                
                return {
                    "is_verified": False,
                    "has_pending_code": True,
                    "expires_in_seconds": int(time_remaining),
                    "attempts_used": pending_verification.attempts,
                    "max_attempts": self.max_attempts,
                    "can_request_new": can_request_new,
                    "message": "Verification code pending"
                }
            
            # No verification found
            return {
                "is_verified": False,
                "has_pending_code": False,
                "can_request_new": True,
                "message": "No verification found"
            }
            
        except Exception as e:
            logger.error(f"Error checking verification status: {str(e)}")
            return {
                "is_verified": False,
                "has_pending_code": False,
                "can_request_new": True,
                "error": "Failed to check verification status"
            }

    async def cleanup_expired_codes(self, db: Session) -> int:
        """
        Clean up expired verification codes
        
        Args:
            db: Database session
            
        Returns:
            Number of codes cleaned up
        """
        try:
            expired_codes = db.query(VerificationCode).filter(
                VerificationCode.expires_at < datetime.utcnow(),
                VerificationCode.used_at.is_(None)
            ).all()
            
            count = len(expired_codes)
            
            for code in expired_codes:
                db.delete(code)
            
            db.commit()
            
            if count > 0:
                logger.info(f"Cleaned up {count} expired verification codes")
            
            return count
            
        except Exception as e:
            logger.error(f"Error cleaning up expired codes: {str(e)}")
            db.rollback()
            return 0

# Global SMS service instance
sms_service = None

def get_sms_service() -> TencentSMSService:
    """Get SMS service instance (singleton pattern)"""
    global sms_service
    if sms_service is None:
        sms_service = TencentSMSService()
    return sms_service
