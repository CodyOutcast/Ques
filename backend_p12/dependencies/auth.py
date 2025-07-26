from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from typing import Optional
import os
import secrets
import hashlib
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from models.base import SessionLocal
from models.auth import UserAuth, RefreshToken, AuthProviderType
from models.users import User

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("SECRET_KEY environment variable is required")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login/email")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Password utilities
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)

# Token utilities
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY not configured")
        
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token() -> str:
    """Create a secure refresh token"""
    return secrets.token_urlsafe(32)

def hash_refresh_token(token: str) -> str:
    """Hash a refresh token for secure storage"""
    return hashlib.sha256(token.encode()).hexdigest()

def store_refresh_token(
    db: Session, 
    user_id: int, 
    token: str, 
    device_info: Optional[str] = None, 
    ip_address: Optional[str] = None
) -> RefreshToken:
    """Store a refresh token in the database"""
    token_hash = hash_refresh_token(token)
    expires_at = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    
    refresh_token = RefreshToken(
        user_id=user_id,
        token_hash=token_hash,
        device_info=device_info,
        ip_address=ip_address,
        expires_at=expires_at
    )
    
    db.add(refresh_token)
    db.commit()
    db.refresh(refresh_token)
    return refresh_token

def verify_refresh_token(db: Session, token: str) -> Optional[RefreshToken]:
    """Verify and return refresh token if valid"""
    token_hash = hash_refresh_token(token)
    
    refresh_token = db.query(RefreshToken).filter(
        RefreshToken.token_hash == token_hash,
        RefreshToken.expires_at > datetime.now(timezone.utc),
        RefreshToken.is_revoked == False
    ).first()
    
    if refresh_token:
        # Update last used timestamp
        db.query(RefreshToken).filter(RefreshToken.id == refresh_token.id).update(
            {"last_used": datetime.now(timezone.utc)}
        )
        db.commit()
    
    return refresh_token

def revoke_refresh_token(db: Session, token: str):
    """Revoke a refresh token"""
    token_hash = hash_refresh_token(token)
    db.query(RefreshToken).filter(
        RefreshToken.token_hash == token_hash
    ).update({"is_revoked": True})
    db.commit()

# User authentication
def authenticate_user_by_email(db: Session, email: str, password: str) -> Optional[User]:
    """Authenticate user by email and password"""
    user_auth = db.query(UserAuth).filter(
        UserAuth.provider_type == AuthProviderType.EMAIL,
        UserAuth.provider_id == email,
        UserAuth.is_verified == True
    ).first()
    
    if not user_auth:
        return None
    
    # Check password hash exists and verify it
    password_hash = getattr(user_auth, 'password_hash', None)
    if not password_hash or not verify_password(password, password_hash):
        return None
    
    # Update last login
    db.query(UserAuth).filter(UserAuth.id == user_auth.id).update(
        {"last_login": datetime.now(timezone.utc)}
    )
    db.commit()
    
    return user_auth.user

def get_user_by_auth_method(db: Session, provider_type: AuthProviderType, provider_id: str) -> Optional[User]:
    """Get user by authentication method"""
    user_auth = db.query(UserAuth).filter(
        UserAuth.provider_type == provider_type,
        UserAuth.provider_id == provider_id,
        UserAuth.is_verified == True
    ).first()
    
    if user_auth:
        return user_auth.user
    return None

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Get current authenticated user from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    if not SECRET_KEY:
        raise credentials_exception
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.user_id == int(user_id)).first()
    if user is None:
        raise credentials_exception
    
    return user