"""
Authentication service based on backend_p12
Handles user registration, login, verification, and token management
"""

import os
import secrets
import string
import bcrypt
import jwt
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
import logging

from models.users import User
from models.user_auth import UserAuth, VerificationCode, RefreshToken, ProviderType

logger = logging.getLogger(__name__)

# JWT Configuration (same as backend_p12)
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

class AuthService:
    """Service class for handling authentication operations - backend_p12 style"""
    
    def __init__(self):
        self.secret_key = SECRET_KEY
        self.algorithm = ALGORITHM
    
    @staticmethod
    def generate_verification_code() -> str:
        """Generate a cryptographically secure 6-digit verification code"""
        return ''.join(secrets.choice(string.digits) for _ in range(6))
    
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def verify_password(self, password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
    
    def create_access_token(self, data: Dict[str, Any]) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire, "type": "access"})
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
    
    def create_refresh_token(self, db: Session, user_id: int, user_agent: str = "Unknown") -> str:
        """Create and store refresh token"""
        token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(days=30)
        
        refresh_token = RefreshToken(
            user_id=user_id,
            token=token,
            expires_at=expires_at,
            user_agent=user_agent,
            created_at=datetime.utcnow()
        )
        db.add(refresh_token)
        db.commit()
        return token
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify JWT token and return payload"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.JWTError:
            return None
    
    def create_verification_code(
        self,
        db: Session,
        provider_type: ProviderType,
        provider_id: str,
        purpose: str
    ) -> str:
        """Create and store a verification code"""
        # Clean up expired codes first
        db.query(VerificationCode).filter(
            VerificationCode.expires_at < datetime.utcnow()
        ).delete()
        
        # Generate new code
        code = self.generate_verification_code()
        expires_at = datetime.utcnow() + timedelta(minutes=10)  # 10 minutes expiry
        
        verification_code = VerificationCode(
            provider_type=provider_type,
            provider_id=provider_id,
            code=code,
            purpose=purpose,
            expires_at=expires_at,
            created_at=datetime.utcnow()
        )
        
        db.add(verification_code)
        db.commit()
        return code
    
    def verify_code(
        self,
        db: Session,
        provider_type: ProviderType,
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
            VerificationCode.expires_at > datetime.utcnow(),
            VerificationCode.used_at.is_(None)
        ).first()
        
        if not verification_code:
            return False
        
        # Mark as used
        verification_code.used_at = datetime.utcnow()
        db.commit()
        return True
    
    def register_user_email(
        self,
        db: Session,
        name: str,
        email: str,
        password: str,
        bio: Optional[str] = None
    ) -> Tuple[User, Dict[str, Any]]:
        """Register a new user with email authentication - backend_p12 style"""
        
        # Check if user already exists
        existing_auth = db.query(UserAuth).filter(
            UserAuth.provider_type == ProviderType.EMAIL,
            UserAuth.provider_id == email
        ).first()
        
        if existing_auth:
            raise ValueError("User with this email already exists")
        
        # Create user
        user = User(
            name=name,
            bio=bio,
            is_active=True,
            verification_status="verified"  # Skip verification for demo
        )
        db.add(user)
        db.flush()  # Get user_id without committing
        
        # Create authentication method
        password_hash = self.hash_password(password)
        user_auth = UserAuth(
            user_id=user.user_id,
            provider_type=ProviderType.EMAIL,
            provider_id=email,
            password_hash=password_hash,
            is_verified=True,  # Skip verification for demo
            is_primary=True,
            created_at=datetime.utcnow()
        )
        db.add(user_auth)
        db.commit()
        db.refresh(user)
        
        # Generate tokens
        access_token = self.create_access_token({"sub": str(user.user_id)})
        refresh_token = self.create_refresh_token(db, user.user_id)
        
        logger.info(f"User registered: {email}")
        
        return user, {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": 30 * 60  # 30 minutes
        }
    
    def authenticate_user(self, db: Session, email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password - backend_p12 style"""
        user_auth = db.query(UserAuth).filter(
            UserAuth.provider_id == email,
            UserAuth.provider_type == ProviderType.EMAIL
        ).first()
        
        if not user_auth or not user_auth.password_hash:
            return None
            
        if not self.verify_password(password, user_auth.password_hash):
            return None
        
        # Update last login
        user_auth.last_login = datetime.utcnow()
        db.commit()
        
        logger.info(f"User authenticated: {email}")
        return user_auth.user
    
    def get_current_user(self, db: Session, token: str) -> Optional[User]:
        """Get current user from JWT token"""
        payload = self.verify_token(token)
        if not payload:
            return None
        
        user_id = payload.get("sub")
        if not user_id:
            return None
        
        user = db.query(User).filter(User.user_id == int(user_id)).first()
        return user
    
    def refresh_access_token(self, db: Session, refresh_token: str) -> Optional[str]:
        """Refresh access token using refresh token"""
        token_record = db.query(RefreshToken).filter(
            RefreshToken.token == refresh_token,
            RefreshToken.expires_at > datetime.utcnow(),
            RefreshToken.revoked_at.is_(None)
        ).first()
        
        if not token_record:
            return None
        
        # Create new access token
        new_access_token = self.create_access_token({"sub": str(token_record.user_id)})
        
        # Update last used
        token_record.last_used = datetime.utcnow()
        db.commit()
        
        return new_access_token
    
    def revoke_refresh_token(self, db: Session, refresh_token: str) -> bool:
        """Revoke refresh token"""
        token_record = db.query(RefreshToken).filter(
            RefreshToken.token == refresh_token
        ).first()
        
        if token_record:
            token_record.revoked_at = datetime.utcnow()
            db.commit()
            return True
        
        return False
    
    def get_user_auth_methods(self, db: Session, user_id: int) -> list[str]:
        """Get list of authentication methods for a user"""
        auth_methods = db.query(UserAuth).filter(
            UserAuth.user_id == user_id,
            UserAuth.is_verified == True
        ).all()
        
        return [auth.provider_type.value for auth in auth_methods]
