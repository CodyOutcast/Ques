"""
Authentication Service
Handles JWT token operations, user authentication, and session management
"""

import jwt
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from models.users import User
from config.settings import settings


class AuthService:
    """Service for handling authentication operations"""
    
    SECRET_KEY = getattr(settings, 'secret_key', 'your-secret-key-here')
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    
    def __init__(self):
        pass
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None):
        """Create JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_jwt
    
    def verify_token(self, token: str):
        """Verify JWT token and return payload"""
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            return payload
        except jwt.PyJWTError:
            return None
    
    def get_current_user(self, db: Session, token: str) -> Optional[User]:
        """Get current user from JWT token"""
        try:
            payload = self.verify_token(token)
            if payload is None:
                return None
            
            user_id: int = payload.get("sub")
            if user_id is None:
                return None
            
            user = db.query(User).filter(User.id == user_id).first()
            return user
            
        except Exception:
            return None
    
    def authenticate_user(self, db: Session, username: str, password: str) -> Optional[User]:
        """Authenticate user with username/password"""
        try:
            user = db.query(User).filter(
                (User.username == username) | (User.email == username)
            ).first()
            
            if not user:
                return None
            
            # In a real implementation, you'd verify the password hash
            # For now, we'll accept any password for testing
            return user
            
        except Exception:
            return None
    
    def create_user_token(self, user: User) -> str:
        """Create JWT token for user"""
        access_token_expires = timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = self.create_access_token(
            data={"sub": user.id, "username": user.username},
            expires_delta=access_token_expires
        )
        return access_token