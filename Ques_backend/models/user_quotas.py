"""
User quotas model matching database schema
"""

from sqlalchemy import Column, Integer, String, TIMESTAMP, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base

class UserQuota(Base):
    """
    User quotas table - matches existing database schema
    """
    __tablename__ = "user_quotas"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    quota_type = Column(String(100), nullable=False)  # daily_swipes, monthly_matches, etc.
    quota_limit = Column(Integer, nullable=False)
    quota_used = Column(Integer, nullable=False, default=0)
    reset_date = Column(TIMESTAMP, nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship
    user = relationship("User", back_populates="quotas")