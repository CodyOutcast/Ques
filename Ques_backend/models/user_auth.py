"""
Minimal user authentication models to match database schema
Only includes models for tables that exist in the database
"""

from sqlalchemy import Column, Integer, String, TIMESTAMP, Boolean, VARCHAR, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base
from enum import Enum

class ProviderType(str, Enum):
    """Authentication provider types"""
    PHONE = "phone"
    WECHAT = "wechat"
    EMAIL = "email"

class VerificationCode(Base):
    """
    Verification codes table - matches existing database schema
    """
    __tablename__ = "verification_codes"

    id = Column(Integer, primary_key=True, index=True)
    provider_type = Column(VARCHAR(50), nullable=False)
    provider_id = Column(VARCHAR(255), nullable=False)  # phone number, email, etc.
    code = Column(VARCHAR(10), nullable=False)
    purpose = Column(VARCHAR(50), nullable=False)  # login, registration, verification, etc.
    expires_at = Column(TIMESTAMP, nullable=False)
    used_at = Column(TIMESTAMP, nullable=True)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)
    attempts = Column(Integer, nullable=False, default=0)

# Minimal auth models for routers (these don't correspond to database tables)
# The actual authentication is handled through User model + verification codes
class UserAuth:
    """Virtual auth model for router compatibility"""
    def __init__(self, user_id: int, provider: str, provider_id: str):
        self.user_id = user_id
        self.provider_type = provider
        self.provider_id = provider_id

class RefreshToken:
    """Virtual refresh token model for router compatibility"""  
    def __init__(self, token: str, user_id: int, expires_at: datetime):
        self.token = token
        self.user_id = user_id
        self.expires_at = expires_at

class UserSession:
    """Virtual user session model for middleware compatibility"""
    def __init__(self, session_id: str, user_id: int, created_at: datetime, last_activity: datetime):
        self.session_id = session_id
        self.user_id = user_id
        self.created_at = created_at
        self.last_activity = last_activity