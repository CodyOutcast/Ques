"""
SMS Service
Handles SMS verification functionality
"""

import random
import string
from typing import Tuple, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_
import logging
import re

from models.user_auth import UserAuth, VerificationCode
from models.users import User

logger = logging.getLogger(__name__)


class SMSService:
    """SMS verification service"""
    
    def __init__(self):
        self.code_expiry_minutes = 10  # Verification code expires in 10 minutes
        self.rate_limit_minutes = 1    # Rate limit between SMS sends
        self.max_attempts = 3          # Maximum verification attempts
        self.code_length = 6           # Length of verification code
    
    def _format_phone_number(self, phone_number: str, country_code: str = "+86") -> str:
        """Format phone number with country code"""
        # Remove any non-digit characters from phone number
        clean_phone = re.sub(r'\D', '', phone_number)
        
        # Ensure country code starts with +
        if not country_code.startswith('+'):
            country_code = '+' + country_code
        
        # Remove + from country code for concatenation
        clean_country = country_code[1:]
        
        return f"+{clean_country}{clean_phone}"
    
    def _generate_verification_code(self) -> str:
        """Generate random 6-digit verification code"""
        return ''.join(random.choices(string.digits, k=self.code_length))
    
    async def send_verification_sms(
        self,
        db: Session,
        phone_number: str,
        purpose: str = "REGISTRATION",
        country_code: str = "+86"
    ) -> Tuple[bool, str, Optional[str]]:
        """
        Send SMS verification code
        Returns: (success, message, verification_id)
        """
        try:
            formatted_phone = self._format_phone_number(phone_number, country_code)
            
            # Check rate limiting
            recent_code = db.query(VerificationCode).filter(
                and_(
                    VerificationCode.provider_id == formatted_phone,
                    VerificationCode.provider_type == "SMS",
                    VerificationCode.created_at > datetime.utcnow() - timedelta(minutes=self.rate_limit_minutes)
                )
            ).first()
            
            if recent_code:
                return False, f"Please wait {self.rate_limit_minutes} minute(s) before requesting another code", None
            
            # Generate verification code
            verification_code = self._generate_verification_code()
            
            # Create verification record
            verification_record = VerificationCode(
                provider_id=formatted_phone,
                code=verification_code,
                provider_type="SMS",
                purpose=purpose,
                expires_at=datetime.utcnow() + timedelta(minutes=self.code_expiry_minutes),
                created_at=datetime.utcnow()
            )
            
            db.add(verification_record)
            db.commit()
            db.refresh(verification_record)
            
            # In a real implementation, you would integrate with SMS provider here
            # For now, we'll log the code (in production, remove this!)
            logger.info(f"SMS Code for {formatted_phone}: {verification_code} (Purpose: {purpose})")
            
            # Mock SMS sending - in production, integrate with SMS provider
            success = self._mock_send_sms(formatted_phone, verification_code, purpose)
            
            if success:
                return True, "Verification code sent successfully", str(verification_record.id)
            else:
                return False, "Failed to send SMS", None
                
        except Exception as e:
            logger.error(f"Error sending SMS verification: {str(e)}")
            return False, "Failed to send verification code", None
    
    def _mock_send_sms(self, phone_number: str, code: str, purpose: str) -> bool:
        """
        Mock SMS sending function
        In production, replace with actual SMS provider integration (Twilio, AWS SNS, etc.)
        """
        try:
            # Mock successful SMS sending
            logger.info(f"[MOCK SMS] To: {phone_number}, Code: {code}, Purpose: {purpose}")
            return True
        except Exception as e:
            logger.error(f"Mock SMS sending failed: {str(e)}")
            return False
    
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
        Returns: (success, message, verification_record)
        """
        try:
            formatted_phone = self._format_phone_number(phone_number, country_code)
            
            # Find the verification record
            verification_record = db.query(VerificationCode).filter(
                and_(
                    VerificationCode.provider_id == formatted_phone,
                    VerificationCode.provider_type == "SMS",
                    VerificationCode.purpose == purpose,
                    VerificationCode.used_at == None
                )
            ).order_by(VerificationCode.created_at.desc()).first()
            
            if not verification_record:
                return False, "No verification code found or code already used", None
            
            # Check if code is expired
            if verification_record.expires_at < datetime.utcnow():
                return False, "Verification code has expired", verification_record
            
            # Check attempts
            if verification_record.attempts >= self.max_attempts:
                return False, "Maximum verification attempts exceeded", verification_record
            
            # Increment attempts
            verification_record.attempts += 1
            
            # Verify code
            if verification_record.code == code:
                verification_record.used_at = datetime.utcnow()
                db.commit()
                return True, "Phone number verified successfully", verification_record
            else:
                db.commit()
                remaining = self.max_attempts - verification_record.attempts
                if remaining > 0:
                    return False, f"Invalid verification code. {remaining} attempts remaining.", verification_record
                else:
                    return False, "Invalid verification code. Maximum attempts reached.", verification_record
                    
        except Exception as e:
            logger.error(f"Error verifying SMS code: {str(e)}")
            return False, "Failed to verify code", None
    
    async def check_phone_verification_status(
        self,
        db: Session,
        phone_number: str,
        purpose: str = "REGISTRATION",
        country_code: str = "+86"
    ) -> Dict[str, Any]:
        """
        Check phone verification status
        Returns status information about phone verification
        """
        try:
            formatted_phone = self._format_phone_number(phone_number, country_code)
            
            # Check if there's a verified record
            verified_record = db.query(VerificationCode).filter(
                and_(
                    VerificationCode.provider_id == formatted_phone,
                    VerificationCode.provider_type == "SMS",
                    VerificationCode.purpose == purpose,
                    VerificationCode.used_at != None
                )
            ).order_by(VerificationCode.used_at.desc()).first()
            
            if verified_record:
                return {
                    "is_verified": True,
                    "verified_at": verified_record.used_at,
                    "phone_number": formatted_phone
                }
            
            # Check for pending verification
            pending_record = db.query(VerificationCode).filter(
                and_(
                    VerificationCode.provider_id == formatted_phone,
                    VerificationCode.provider_type == "SMS",
                    VerificationCode.purpose == purpose,
                    VerificationCode.used_at == None,
                    VerificationCode.expires_at > datetime.utcnow()
                )
            ).order_by(VerificationCode.created_at.desc()).first()
            
            if pending_record:
                remaining_attempts = self.max_attempts - pending_record.attempts
                return {
                    "is_verified": False,
                    "has_pending_code": True,
                    "remaining_attempts": remaining_attempts,
                    "expires_at": pending_record.expires_at,
                    "phone_number": formatted_phone
                }
            
            return {
                "is_verified": False,
                "has_pending_code": False,
                "phone_number": formatted_phone
            }
            
        except Exception as e:
            logger.error(f"Error checking phone verification status: {str(e)}")
            return {
                "is_verified": False,
                "has_pending_code": False,
                "phone_number": formatted_phone,
                "error": str(e)
            }
    
    async def cleanup_expired_codes(self, db: Session) -> int:
        """
        Clean up expired verification codes
        Returns number of codes cleaned up
        """
        try:
            expired_codes = db.query(VerificationCode).filter(
                and_(
                    VerificationCode.provider_type == "SMS",
                    VerificationCode.expires_at < datetime.utcnow(),
                    VerificationCode.used_at == None
                )
            ).all()
            
            count = len(expired_codes)
            
            for code in expired_codes:
                db.delete(code)
            
            db.commit()
            logger.info(f"Cleaned up {count} expired SMS verification codes")
            return count
            
        except Exception as e:
            logger.error(f"Error cleaning up expired codes: {str(e)}")
            return 0


# Global SMS service instance
_sms_service_instance = None


def get_sms_service() -> SMSService:
    """Get SMS service instance (singleton pattern)"""
    global _sms_service_instance
    if _sms_service_instance is None:
        _sms_service_instance = SMSService()
    return _sms_service_instance