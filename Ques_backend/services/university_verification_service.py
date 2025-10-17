"""
University Verification Service
"""

import secrets
from datetime import datetime, timedelta
from typing import Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_
from models.user_profiles import UserProfile
from models.user_auth import VerificationCode


class UniversityVerificationService:
    def get_verification_status(self, user_id: int, db: Session) -> Dict[str, Any]:
        user_profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
        if not user_profile:
            return {'status': 'no_profile', 'verified': False}
        return {
            'verified': user_profile.university_verified or False,
            'university_email': user_profile.university_email,
            'status': 'verified' if user_profile.university_verified else 'not_verified'
        }
    
    def initiate_verification(self, user_id: int, university_email: str, db: Session) -> Dict[str, Any]:
        user_profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
        if not user_profile:
            raise ValueError("User profile not found")
        
        if not ('.edu' in university_email or '.ac.' in university_email):
            raise ValueError("Not a university email")
        
        code = secrets.token_hex(3).upper()
        expire_time = datetime.utcnow() + timedelta(hours=1)
        
        # Remove old verification codes for this user/email combo
        db.query(VerificationCode).filter(
            and_(
                VerificationCode.provider_type == 'email',
                VerificationCode.provider_id == university_email,
                VerificationCode.purpose == 'university_verification'
            )
        ).delete()
        
        verification = VerificationCode(
            provider_type='email',
            provider_id=university_email,
            code=code,
            purpose='university_verification',
            expires_at=expire_time
        )
        
        db.add(verification)
        user_profile.university_email = university_email
        user_profile.university_verified = False
        db.commit()
        
        return {
            'status': 'verification_sent',
            'message': f'Code: {code}',
            'expires_in_minutes': 60
        }
    
    def verify_code(self, user_id: int, code: str, db: Session) -> Dict[str, Any]:
        # Get user profile to find university email
        user_profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
        if not user_profile or not user_profile.university_email:
            raise ValueError("No pending university verification found")
        
        verification = db.query(VerificationCode).filter(
            and_(
                VerificationCode.provider_type == 'email',
                VerificationCode.provider_id == user_profile.university_email,
                VerificationCode.code == code.upper(),
                VerificationCode.purpose == 'university_verification',
                VerificationCode.expires_at > datetime.utcnow(),
                VerificationCode.used_at.is_(None)
            )
        ).first()
        
        if not verification:
            raise ValueError("Invalid or expired code")
        
        # Mark code as used
        verification.used_at = datetime.utcnow()
        
        # Mark user as verified
        user_profile.university_verified = True
        user_profile.university_verified_at = datetime.utcnow()
        
        db.commit()
        
        return {
            'status': 'verified',
            'message': 'University email verified successfully',
            'university_email': user_profile.university_email
        }
