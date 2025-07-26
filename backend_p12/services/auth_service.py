import os
import random
import string
import requests
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from models.users import User
from models.auth import UserAuth, VerificationCode, AuthProviderType
from dependencies.auth import get_password_hash, create_access_token, create_refresh_token, store_refresh_token

class AuthService:
    """Service class for handling authentication operations"""
    
    @staticmethod
    def generate_verification_code() -> str:
        """Generate a 6-digit verification code"""
        return ''.join(random.choices(string.digits, k=6))
    
    @staticmethod
    def create_user_auth(
        db: Session,
        user_id: int,
        provider_type: AuthProviderType,
        provider_id: str,
        password: Optional[str] = None,
        is_verified: bool = False,
        is_primary: bool = False
    ) -> UserAuth:
        """Create a new authentication method for a user"""
        password_hash = get_password_hash(password) if password else None
        
        user_auth = UserAuth(
            user_id=user_id,
            provider_type=provider_type,
            provider_id=provider_id,
            password_hash=password_hash,
            is_verified=is_verified,
            is_primary=is_primary
        )
        
        db.add(user_auth)
        db.commit()
        db.refresh(user_auth)
        return user_auth
    
    @staticmethod
    def create_verification_code(
        db: Session,
        provider_type: AuthProviderType,
        provider_id: str,
        purpose: str
    ) -> VerificationCode:
        """Create and store a verification code"""
        # Clean up expired codes first
        db.query(VerificationCode).filter(
            VerificationCode.expires_at < datetime.now(timezone.utc)
        ).delete()
        
        # Generate new code
        code = AuthService.generate_verification_code()
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)  # 10 minutes expiry
        
        verification_code = VerificationCode(
            provider_type=provider_type,
            provider_id=provider_id,
            code=code,
            purpose=purpose,
            expires_at=expires_at
        )
        
        db.add(verification_code)
        db.commit()
        db.refresh(verification_code)
        return verification_code
    
    @staticmethod
    def verify_code(
        db: Session,
        provider_type: AuthProviderType,
        provider_id: str,
        code: str,
        purpose: str
    ) -> bool:
        """Verify a verification code"""
        verification_code = db.query(VerificationCode).filter(
            VerificationCode.provider_type == provider_type,
            VerificationCode.provider_id == provider_id,
            VerificationCode.code == code,
            VerificationCode.purpose == purpose,
            VerificationCode.expires_at > datetime.now(timezone.utc),
            VerificationCode.used_at.is_(None)
        ).first()
        
        if not verification_code:
            return False
        
        # Mark as used
        db.query(VerificationCode).filter(VerificationCode.id == verification_code.id).update(
            {"used_at": datetime.now(timezone.utc)}
        )
        db.commit()
        return True
    
    @staticmethod
    def send_email_verification(email: str, code: str, purpose: str) -> bool:
        """Send email verification code using Tencent Cloud SES"""
        try:
            from services.email_service import email_service
            return email_service.send_verification_email(email, code, purpose)
        except ImportError:
            # Fallback to console logging if email service not available
            print(f"📧 Sending email to {email}: Your verification code is {code} for {purpose}")
            return True
    
    @staticmethod
    def verify_wechat_code(wechat_code: str) -> Optional[Dict[str, Any]]:
        """Verify WeChat authorization code using WeChat Developer API"""
        # TODO: Implement WeChat Developer API OAuth integration
        # This is a placeholder implementation
        
        wechat_app_id = os.getenv('WECHAT_APP_ID')
        wechat_secret = os.getenv('WECHAT_SECRET')
        
        if not wechat_app_id or not wechat_secret:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="WeChat configuration not found"
            )
        
        # Step 1: Exchange code for access token
        token_url = "https://api.weixin.qq.com/sns/oauth2/access_token"
        token_params = {
            'appid': wechat_app_id,
            'secret': wechat_secret,
            'code': wechat_code,
            'grant_type': 'authorization_code'
        }
        
        try:
            token_response = requests.get(token_url, params=token_params)
            token_data = token_response.json()
            
            if 'access_token' not in token_data:
                return None
            
            # Step 2: Get user info
            userinfo_url = "https://api.weixin.qq.com/sns/userinfo"
            userinfo_params = {
                'access_token': token_data['access_token'],
                'openid': token_data['openid'],
                'lang': 'en'
            }
            
            userinfo_response = requests.get(userinfo_url, params=userinfo_params)
            user_data = userinfo_response.json()
            
            return {
                'openid': user_data.get('openid'),
                'nickname': user_data.get('nickname'),
                'avatar': user_data.get('headimgurl'),
                'unionid': user_data.get('unionid')
            }
            
        except Exception as e:
            print(f"WeChat verification error: {e}")
            return None
    
    @staticmethod
    def register_user(
        db: Session,
        provider_type: AuthProviderType,
        provider_id: str,
        name: str,
        bio: Optional[str] = None,
        password: Optional[str] = None,
        verification_code: Optional[str] = None,
        wechat_data: Optional[Dict[str, Any]] = None
    ) -> tuple[User, Dict[str, Any]]:
        """Register a new user with specified authentication method"""
        
        # Verify codes for email registration (skip if verification_code is None for development)
        if provider_type == AuthProviderType.EMAIL and verification_code is not None:
            if not AuthService.verify_code(
                db, provider_type, provider_id, verification_code, "registration"
            ):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid or expired verification code"
                )
        
        # Check if user already exists
        existing_auth = db.query(UserAuth).filter(
            UserAuth.provider_type == provider_type,
            UserAuth.provider_id == provider_id
        ).first()
        
        if existing_auth:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User already exists with this {provider_type.value}"
            )
        
        # Create user
        user = User(name=name, bio=bio)
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # Create authentication method
        user_id_value = getattr(user, 'id')
        AuthService.create_user_auth(
            db=db,
            user_id=user_id_value,
            provider_type=provider_type,
            provider_id=provider_id,
            password=password,
            is_verified=True,  # Already verified through code
            is_primary=True
        )
        
        # Generate tokens
        access_token = create_access_token(data={"sub": str(user_id_value)})
        refresh_token_str = create_refresh_token()
        store_refresh_token(db, user_id_value, refresh_token_str)
        
        return user, {
            "access_token": access_token,
            "refresh_token": refresh_token_str,
            "token_type": "bearer",
            "expires_in": 30 * 60  # 30 minutes
        }
    
    @staticmethod
    def get_user_auth_methods(db: Session, user_id: int) -> list[str]:
        """Get list of authentication methods for a user"""
        auth_methods = db.query(UserAuth).filter(
            UserAuth.user_id == user_id,
            UserAuth.is_verified == True
        ).all()
        
        return [auth.provider_type.value for auth in auth_methods]
