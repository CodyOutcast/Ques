"""
User authentication models matching the actual database schema
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from .base import Base

class ProviderType(str, enum.Enum):
    """Provider types for authentication"""
    EMAIL = "EMAIL"
    WECHAT = "WECHAT"
    PHONE = "PHONE"

class UserAuth(Base):
    """
    User authentication model matching the actual database schema
    """
    __tablename__ = "user_auth"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    provider_type = Column(Enum(ProviderType), nullable=False)
    provider_id = Column(String(255), nullable=False)  # email, wechat_id, phone number
    password_hash = Column(String(255), nullable=True)  # only for EMAIL provider
    is_verified = Column(Boolean, nullable=True, default=False)
    is_primary = Column(Boolean, nullable=True, default=False)
    created_at = Column(DateTime, nullable=True, default=datetime.utcnow)
    verified_at = Column(DateTime, nullable=True)
    last_login = Column(DateTime, nullable=True)
    
    # Relationship to users table
    user = relationship("User", back_populates="auth_records")

class RefreshToken(Base):
    """
    Refresh token model for JWT authentication
    """
    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    token_hash = Column(String(255), nullable=False)
    device_info = Column(String(255), nullable=True)
    ip_address = Column(String(45), nullable=True)  # Support IPv6
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, nullable=True, default=datetime.utcnow)
    last_used = Column(DateTime, nullable=True)
    is_revoked = Column(Boolean, nullable=True, default=False)
    
    # Relationship to users table
    user = relationship("User", back_populates="refresh_tokens")

class VerificationCode(Base):
    """
    Verification codes for email/phone verification
    """
    __tablename__ = "verification_codes"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    provider_type = Column(Enum(ProviderType), nullable=False)
    provider_id = Column(String(255), nullable=False)  # email or phone
    code = Column(String(10), nullable=False)
    purpose = Column(String(50), nullable=False)  # REGISTRATION, PASSWORD_RESET, etc.
    expires_at = Column(DateTime, nullable=False)
    used_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=True, default=datetime.utcnow)
    attempts = Column(Integer, nullable=True, default=0)

class UserSession(Base):
    """
    User session tracking for security
    """
    __tablename__ = "user_sessions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_token = Column(String(255), nullable=False)
    device_id = Column(String(255), nullable=True)
    device_name = Column(String(255), nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    location = Column(String(255), nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    last_activity = Column(DateTime, nullable=False, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    
    # Relationship to users table
    user = relationship("User", back_populates="sessions")

class SecurityLog(Base):
    """
    Security event logging
    """
    __tablename__ = "security_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    event_type = Column(String(50), nullable=False)
    event_status = Column(String(20), nullable=False)
    event_description = Column(String(500), nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    provider_type = Column(String(20), nullable=True)
    endpoint = Column(String(255), nullable=True)
    risk_score = Column(Integer, nullable=True)
    flags = Column(String(255), nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationship to users table (optional)
    user = relationship("User", back_populates="security_logs")
