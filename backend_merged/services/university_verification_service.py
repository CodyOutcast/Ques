"""
University Verification Service
Handles verification of Chinese university emails (.edu.cn domains)
"""

import re
import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Tuple, Dict, List
from sqlalchemy.orm import Session
from models.university_verification import UniversityVerification
from services.email_service import EmailService
import logging

logger = logging.getLogger(__name__)

class UniversityVerificationService:
    """Service for handling university email verification"""
    
    def __init__(self, db: Session, email_service: EmailService = None):
        self.db = db
        self.email_service = email_service or EmailService()
        
        # Chinese university domains (can be extended)
        self.valid_domains = [
            '.edu.cn',
            '.ac.cn'  # Some Chinese academic institutions use .ac.cn
        ]
        
        # University name mapping from domains (can be extended)
        self.university_mapping = {
            'pku.edu.cn': 'Peking University (北京大学)',
            'tsinghua.edu.cn': 'Tsinghua University (清华大学)',
            'fudan.edu.cn': 'Fudan University (复旦大学)',
            'sjtu.edu.cn': 'Shanghai Jiao Tong University (上海交通大学)',
            'zju.edu.cn': 'Zhejiang University (浙江大学)',
            'nju.edu.cn': 'Nanjing University (南京大学)',
            'hit.edu.cn': 'Harbin Institute of Technology (哈尔滨工业大学)',
            'xjtu.edu.cn': 'Xi\'an Jiaotong University (西安交通大学)',
            'buaa.edu.cn': 'Beihang University (北京航空航天大学)',
            'bit.edu.cn': 'Beijing Institute of Technology (北京理工大学)'
        }
    
    def validate_university_email(self, email: str) -> Tuple[bool, str]:
        """
        Validate if email is from a Chinese university
        
        Args:
            email: Email address to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not email:
            return False, "Email is required"
        
        # Basic email format validation
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            return False, "Invalid email format"
        
        email_lower = email.lower()
        
        # Check if email ends with valid Chinese university domain
        is_valid = any(email_lower.endswith(domain) for domain in self.valid_domains)
        
        if not is_valid:
            return False, f"Email must be from a Chinese university (.edu.cn or .ac.cn domain)"
        
        return True, ""
    
    def extract_university_info(self, email: str) -> Dict[str, str]:
        """
        Extract university information from email domain
        
        Args:
            email: University email address
            
        Returns:
            Dictionary with university_name and domain
        """
        email_lower = email.lower()
        
        # Extract domain (e.g., user@pku.edu.cn -> pku.edu.cn)
        domain = email_lower.split('@')[1] if '@' in email_lower else ''
        
        # Try to get university name from mapping
        university_name = self.university_mapping.get(domain, '')
        
        if not university_name:
            # Extract university name from domain (e.g., pku.edu.cn -> PKU)
            if domain.endswith('.edu.cn'):
                university_code = domain.replace('.edu.cn', '').upper()
                university_name = f"{university_code} University"
            elif domain.endswith('.ac.cn'):
                university_code = domain.replace('.ac.cn', '').upper()
                university_name = f"{university_code} Academic Institution"
        
        return {
            'university_name': university_name,
            'domain': domain
        }
    
    def generate_verification_token(self) -> str:
        """Generate secure verification token"""
        # Generate a secure random token
        token = secrets.token_urlsafe(32)
        
        # Add timestamp hash for additional security
        timestamp = str(int(datetime.utcnow().timestamp()))
        hash_input = f"{token}_{timestamp}".encode()
        token_hash = hashlib.sha256(hash_input).hexdigest()[:16]
        
        return f"{token}_{token_hash}"
    
    def initiate_verification(self, user_id: int, email: str) -> Tuple[bool, str, Optional[str]]:
        """
        Initiate university email verification process
        
        Args:
            user_id: ID of the user requesting verification
            email: University email to verify
            
        Returns:
            Tuple of (success, message, verification_id)
        """
        try:
            # Validate email format and domain
            is_valid, error_msg = self.validate_university_email(email)
            if not is_valid:
                return False, error_msg, None
            
            # Check if this email is already verified by another user
            existing_verified = self.db.query(UniversityVerification).filter(
                UniversityVerification.email == email.lower(),
                UniversityVerification.verified == True
            ).first()
            
            if existing_verified and existing_verified.user_id != user_id:
                return False, "This university email is already verified by another user", None
            
            # Check if user already has a pending verification for this email
            existing_pending = self.db.query(UniversityVerification).filter(
                UniversityVerification.user_id == user_id,
                UniversityVerification.email == email.lower(),
                UniversityVerification.verified == False
            ).first()
            
            if existing_pending and not existing_pending.is_expired() and not existing_pending.can_resend():
                return False, "Maximum verification attempts reached. Please try again later.", None
            
            # Extract university information
            university_info = self.extract_university_info(email)
            
            # Generate verification token
            token = self.generate_verification_token()
            
            # Create or update verification record
            if existing_pending:
                # Update existing record
                existing_pending.verification_token = token
                existing_pending.expires_at = datetime.utcnow() + timedelta(hours=24)
                existing_pending.attempts += 1
                existing_pending.created_at = datetime.utcnow()
                verification = existing_pending
            else:
                # Create new verification record
                verification = UniversityVerification(
                    user_id=user_id,
                    email=email.lower(),
                    university_name=university_info['university_name'],
                    domain=university_info['domain'],
                    verification_token=token,
                    expires_at=datetime.utcnow() + timedelta(hours=24),
                    attempts=1
                )
                self.db.add(verification)
            
            self.db.commit()
            
            # Send verification email
            email_sent = self._send_verification_email(
                email=email,
                token=token,
                university_name=university_info['university_name'],
                user_id=user_id
            )
            
            if not email_sent:
                return False, "Failed to send verification email. Please try again.", None
            
            logger.info(f"University verification initiated for user {user_id}, email {email}")
            return True, "Verification email sent successfully. Please check your university email.", str(verification.id)
            
        except Exception as e:
            logger.error(f"Error initiating university verification: {e}")
            self.db.rollback()
            return False, "An error occurred while sending verification email", None
    
    def verify_token(self, email: str, token: str) -> Tuple[bool, str, Optional[Dict]]:
        """
        Verify the university email using the provided token
        
        Args:
            email: University email address
            token: Verification token from email
            
        Returns:
            Tuple of (success, message, verification_data)
        """
        try:
            # Find verification record
            verification = self.db.query(UniversityVerification).filter(
                UniversityVerification.email == email.lower(),
                UniversityVerification.verification_token == token
            ).first()
            
            if not verification:
                return False, "Invalid verification token or email", None
            
            if verification.verified:
                return False, "This email has already been verified", None
            
            if verification.is_expired():
                return False, "Verification token has expired. Please request a new one.", None
            
            # Mark as verified
            verification.verified = True
            verification.verified_at = datetime.utcnow()
            
            # Update user's university information in profile
            from models.users import User
            from models.user_profiles import UserProfile
            
            user = self.db.query(User).filter(User.id == verification.user_id).first()
            
            if user and user.profile:
                user.profile.university_email = verification.email
                user.profile.university_verified = True
                user.profile.current_university = verification.university_name
            
            self.db.commit()
            
            verification_data = {
                'user_id': verification.user_id,
                'email': verification.email,
                'university_name': verification.university_name,
                'verified_at': verification.verified_at
            }
            
            logger.info(f"University email verified successfully for user {verification.user_id}")
            return True, "University email verified successfully!", verification_data
            
        except Exception as e:
            logger.error(f"Error verifying university email: {e}")
            self.db.rollback()
            return False, "An error occurred during verification", None
    
    def get_verification_status(self, user_id: int) -> Dict:
        """
        Get university verification status for a user
        
        Args:
            user_id: User ID to check
            
        Returns:
            Dictionary with verification status information
        """
        try:
            verification = self.db.query(UniversityVerification).filter(
                UniversityVerification.user_id == user_id,
                UniversityVerification.verified == True
            ).first()
            
            if verification:
                return {
                    'verified': True,
                    'email': verification.email,
                    'university_name': verification.university_name,
                    'verified_at': verification.verified_at.isoformat() if verification.verified_at else None
                }
            
            # Check for pending verification
            pending = self.db.query(UniversityVerification).filter(
                UniversityVerification.user_id == user_id,
                UniversityVerification.verified == False
            ).order_by(UniversityVerification.created_at.desc()).first()
            
            if pending:
                return {
                    'verified': False,
                    'pending': True,
                    'email': pending.email,
                    'expires_at': pending.expires_at.isoformat(),
                    'can_resend': pending.can_resend()
                }
            
            return {
                'verified': False,
                'pending': False
            }
            
        except Exception as e:
            logger.error(f"Error getting verification status for user {user_id}: {e}")
            return {
                'verified': False,
                'pending': False,
                'error': 'Failed to get verification status'
            }
    
    def resend_verification(self, user_id: int) -> Tuple[bool, str]:
        """
        Resend verification email for pending verification
        
        Args:
            user_id: User ID requesting resend
            
        Returns:
            Tuple of (success, message)
        """
        try:
            # Find pending verification
            verification = self.db.query(UniversityVerification).filter(
                UniversityVerification.user_id == user_id,
                UniversityVerification.verified == False
            ).order_by(UniversityVerification.created_at.desc()).first()
            
            if not verification:
                return False, "No pending verification found"
            
            if not verification.can_resend():
                return False, "Maximum resend attempts reached"
            
            # Generate new token
            new_token = self.generate_verification_token()
            verification.verification_token = new_token
            verification.expires_at = datetime.utcnow() + timedelta(hours=24)
            verification.attempts += 1
            
            self.db.commit()
            
            # Send new verification email
            email_sent = self._send_verification_email(
                email=verification.email,
                token=new_token,
                university_name=verification.university_name,
                user_id=user_id
            )
            
            if not email_sent:
                return False, "Failed to send verification email"
            
            return True, "Verification email resent successfully"
            
        except Exception as e:
            logger.error(f"Error resending verification for user {user_id}: {e}")
            self.db.rollback()
            return False, "An error occurred while resending verification email"
    
    def _send_verification_email(self, email: str, token: str, university_name: str, user_id: int) -> bool:
        """
        Send verification email with token
        
        Args:
            email: University email address
            token: Verification token
            university_name: Name of the university
            user_id: User ID for tracking
            
        Returns:
            True if email sent successfully, False otherwise
        """
        try:
            # Create verification URL (replace with your frontend URL)
            base_url = "https://your-app.com"  # Replace with actual frontend URL
            verification_url = f"{base_url}/verify-university?email={email}&token={token}"
            
            # Email content
            subject = "Verify Your University Email - Ques"
            
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>University Email Verification</title>
            </head>
            <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="text-align: center; margin-bottom: 30px;">
                    <h1 style="color: #333; margin-bottom: 10px;">🎓 University Email Verification</h1>
                    <p style="color: #666; font-size: 16px;">Verify your university email to unlock exclusive features</p>
                </div>
                
                <div style="background: #f8f9fa; padding: 25px; border-radius: 8px; margin-bottom: 25px;">
                    <h2 style="color: #333; margin-bottom: 15px;">Hello from Ques!</h2>
                    <p style="color: #555; line-height: 1.6; margin-bottom: 15px;">
                        We received a request to verify your university email address:
                    </p>
                    <p style="color: #0066cc; font-weight: bold; margin-bottom: 15px;">{email}</p>
                    {f"<p style='color: #555; margin-bottom: 20px;'>University: <strong>{university_name}</strong></p>" if university_name else ""}
                </div>
                
                <div style="text-align: center; margin-bottom: 30px;">
                    <a href="{verification_url}" 
                       style="display: inline-block; background: #0066cc; color: white; padding: 15px 30px; 
                              text-decoration: none; border-radius: 5px; font-weight: bold; font-size: 16px;">
                        Verify University Email
                    </a>
                </div>
                
                <div style="background: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 5px; margin-bottom: 20px;">
                    <p style="color: #856404; margin: 0; font-size: 14px;">
                        <strong>⚠️ Important:</strong> This verification link will expire in 24 hours.
                    </p>
                </div>
                
                <div style="color: #666; font-size: 14px; line-height: 1.6;">
                    <p><strong>Why verify your university email?</strong></p>
                    <ul>
                        <li>Connect with verified students from your university</li>
                        <li>Access university-specific features and groups</li>
                        <li>Build trust and credibility in your profile</li>
                        <li>Get priority in matching with other verified students</li>
                    </ul>
                    
                    <hr style="margin: 20px 0; border: none; height: 1px; background: #eee;">
                    
                    <p><strong>Didn't request this verification?</strong></p>
                    <p>You can safely ignore this email. The verification link will expire automatically.</p>
                    
                    <p style="margin-top: 30px; color: #999; font-size: 12px;">
                        If the button doesn't work, copy and paste this link into your browser:<br>
                        <a href="{verification_url}" style="color: #0066cc; word-break: break-all;">{verification_url}</a>
                    </p>
                </div>
                
                <div style="text-align: center; margin-top: 40px; padding-top: 20px; border-top: 1px solid #eee;">
                    <p style="color: #999; font-size: 12px; margin: 0;">
                        © 2025 Ques - Connecting Students Worldwide<br>
                        <a href="https://ques.chat" style="color: #0066cc;">ques.chat</a>
                    </p>
                </div>
            </body>
            </html>
            """
            
            # Plain text version for email clients that don't support HTML
            text_content = f"""
University Email Verification - Ques

Hello!

We received a request to verify your university email address: {email}
{f"University: {university_name}" if university_name else ""}

Click the link below to verify your email:
{verification_url}

This link will expire in 24 hours.

Why verify your university email?
- Connect with verified students from your university
- Access university-specific features and groups  
- Build trust and credibility in your profile
- Get priority in matching with other verified students

If you didn't request this verification, you can safely ignore this email.

© 2025 Ques - Connecting Students Worldwide
https://ques.chat
            """
            
            # Send email using email service
            success = self.email_service.send_email(
                to_email=email,
                subject=subject,
                html_content=html_content,
                text_content=text_content
            )
            
            if success:
                logger.info(f"Verification email sent successfully to {email}")
            else:
                logger.error(f"Failed to send verification email to {email}")
                
            return success
            
        except Exception as e:
            logger.error(f"Error sending verification email to {email}: {e}")
            return False