from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import enum
from .base import Base

class AuthProviderType(enum.Enum):
    EMAIL = "email"
    WECHAT = "wechat"

class UserAuth(Base):
    __tablename__ = "user_auth"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    provider_type = Column(Enum(AuthProviderType), nullable=False)
    provider_id = Column(String, nullable=False)  # email or wechat_openid
    password_hash = Column(String, nullable=True)  # Only for email auth
    is_verified = Column(Boolean, default=False)
    is_primary = Column(Boolean, default=False)  # One primary auth method per user
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    verified_at = Column(DateTime, nullable=True)
    last_login = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="auth_methods")
    
    # Ensure unique provider_id for each provider_type
    __table_args__ = (
        {"schema": None}  # Can add unique constraints here if needed
    )

class VerificationCode(Base):
    __tablename__ = "verification_codes"
    
    id = Column(Integer, primary_key=True, index=True)
    provider_type = Column(Enum(AuthProviderType), nullable=False)
    provider_id = Column(String, nullable=False)  # email only
    code = Column(String, nullable=False)  # 6-digit verification code
    purpose = Column(String, nullable=False)  # "registration", "login", "password_reset"
    expires_at = Column(DateTime, nullable=False)
    used_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    attempts = Column(Integer, default=0)  # Track failed verification attempts
    
class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    token_hash = Column(String, nullable=False)  # Hashed refresh token
    device_info = Column(String, nullable=True)  # Device/browser info
    ip_address = Column(String, nullable=True)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    last_used = Column(DateTime, nullable=True)
    is_revoked = Column(Boolean, default=False)
    
    # Relationships
    user = relationship("User", back_populates="refresh_tokens")
