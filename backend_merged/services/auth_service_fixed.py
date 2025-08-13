"""
Authentication service based on backend_p12 foundation
Handles user registration, login, token management, and verification
"""

import os
import secrets
import string
import hashlib
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from jose import JWTError, jwt
from passlib.context import CryptContext

from models.users import User
from models.user_auth import UserAuth, VerificationCode, RefreshToken, ProviderType
import logging

logger = logging.getLogger(__name__)

# Load configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 30

# Password context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    """Service class for handling authentication operations - backend_p12 style"""
    
    def __init__(self):
        self.secret_key = SECRET_KEY
        self.algorithm = ALGORITHM
        
    # Password utilities
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return pwd_context.verify(plain_password, hashed_password)
    
    def hash_password(self, password: str) -> str:
        """Hash a password"""
        return pwd_context.hash(password)
    
    # Token utilities
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token"""
        if not self.secret_key:
            raise ValueError("SECRET_KEY not configured")
            
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire, "type": "access"})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Optional[dict]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except JWTError:
            return None
    
    def create_refresh_token_string(self) -> str:
        """Create a secure refresh token string"""
        return secrets.token_urlsafe(32)
    
    def hash_refresh_token(self, token: str) -> str:
        """Hash a refresh token for secure storage"""
        return hashlib.sha256(token.encode()).hexdigest()
    
    def create_refresh_token(self, db: Session, user_id: int, device_info: Optional[str] = None) -> str:
        """Create and store refresh token"""
        token = self.create_refresh_token_string()
        token_hash = self.hash_refresh_token(token)
        expires_at = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        
        refresh_token = RefreshToken(
            user_id=user_id,
            token_hash=token_hash,
            device_info=device_info,
            expires_at=expires_at,
            is_revoked=False
        )
        
        db.add(refresh_token)
        db.commit()
        db.refresh(refresh_token)
        return token
    
    def verify_refresh_token(self, db: Session, token: str) -> Optional[RefreshToken]:
        """Verify refresh token"""
        token_hash = self.hash_refresh_token(token)
        
        refresh_token = db.query(RefreshToken).filter(
            RefreshToken.token_hash == token_hash,
            RefreshToken.expires_at > datetime.utcnow(),
            RefreshToken.is_revoked == False
        ).first()
        
        if refresh_token:
            # Update last used timestamp
            refresh_token.last_used = datetime.utcnow()
            db.commit()
        
        return refresh_token
    
    def revoke_refresh_token(self, db: Session, token: str) -> bool:
        """Revoke refresh token"""
        token_hash = self.hash_refresh_token(token)
        result = db.query(RefreshToken).filter(
            RefreshToken.token_hash == token_hash
        ).update({"is_revoked": True})
        db.commit()
        return result > 0
    
    def refresh_access_token(self, db: Session, refresh_token: str) -> Optional[str]:
        """Create new access token from refresh token"""
        token_record = self.verify_refresh_token(db, refresh_token)
        if not token_record:
            return None
        
        # Create new access token
        return self.create_access_token({"sub": str(token_record.user_id)})
    
    # Verification code utilities
    def generate_verification_code(self) -> str:
        """Generate a cryptographically secure 6-digit verification code"""
        return ''.join(secrets.choice(string.digits) for _ in range(6))
    
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
            expires_at=expires_at
        )
        
        db.add(verification_code)
        db.commit()
        db.refresh(verification_code)
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
    
    # User authentication
    def authenticate_user(self, db: Session, email: str, password: str) -> Optional[User]:
        """Authenticate user by email and password - backend_p12 style"""
        user_auth = db.query(UserAuth).filter(
            UserAuth.provider_type == ProviderType.EMAIL,
            UserAuth.provider_id == email,
            UserAuth.is_verified == True
        ).first()
        
        if not user_auth:
            logger.warning(f"No verified user found for email: {email}")
            return None
        
        # Check password hash exists and verify it
        if not user_auth.password_hash or not self.verify_password(password, user_auth.password_hash):
            logger.warning(f"Password verification failed for email: {email}")
            return None
        
        # Update last login
        user_auth.last_login = datetime.utcnow()
        db.commit()
        
        logger.info(f"User authenticated successfully: {email}")
        return user_auth.user
    
    def get_current_user(self, db: Session, token: str) -> Optional[User]:
        """Get current user from JWT token"""
        payload = self.verify_token(token)
        if not payload:
            return None
        
        user_id = payload.get("sub")
        if not user_id:
            return None
        
        try:
            user = db.query(User).filter(User.user_id == int(user_id)).first()
            return user
        except (ValueError, TypeError):
            return None
    
    # User registration - backend_p12 style
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
            raise ValueError(f"User already exists with this email")
        
        # Create user
        user = User(
            name=name, 
            bio=bio,
            is_active=True,
            verification_status="verified"  # Skip verification for demo
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
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
        db.refresh(user_auth)
        
        # Generate tokens
        access_token = self.create_access_token({"sub": str(user.user_id)})
        refresh_token = self.create_refresh_token(db, user.user_id)
        
        logger.info(f"User registered successfully: {email}")
        
        return user, {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": 30 * 60  # 30 minutes
        }
    
    def get_user_auth_methods(self, db: Session, user_id: int) -> list[str]:
        """Get list of authentication methods for a user"""
        auth_methods = db.query(UserAuth).filter(
            UserAuth.user_id == user_id,
            UserAuth.is_verified == True
        ).all()
        
        return [auth.provider_type.value for auth in auth_methods]
