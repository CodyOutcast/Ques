"""
User membership models for paid/free user tiers
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
import enum
from .base import Base

class MembershipType(enum.Enum):
    """Membership type enumeration"""
    FREE = "free"
    PAID = "paid"
    PREMIUM = "premium"  # Future use

class UserMembership(Base):
    """
    User membership model to track paid vs free users
    """
    __tablename__ = "user_memberships"

    # Primary key
    membership_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # User relationship
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False, unique=True)
    
    # Membership details
    membership_type = Column(Enum(MembershipType), nullable=False, default=MembershipType.FREE)
    is_active = Column(Boolean, nullable=False, default=True)
    
    # Subscription details
    start_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    end_date = Column(DateTime, nullable=True)  # NULL for free users, set for paid users
    auto_renew = Column(Boolean, nullable=False, default=False)
    
    # Payment tracking
    payment_method = Column(String(50), nullable=True)  # "stripe", "paypal", etc.
    subscription_id = Column(String(255), nullable=True)  # External subscription ID
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="membership")
    usage_logs = relationship("UserUsageLog", back_populates="membership")
    
    @property
    def is_paid(self) -> bool:
        """Check if user has active paid membership"""
        if self.membership_type == MembershipType.FREE:
            return False
        
        if self.end_date is None:
            return True  # Lifetime membership
        
        return self.is_active and datetime.utcnow() <= self.end_date
    
    @property
    def days_remaining(self) -> int:
        """Get days remaining in paid membership"""
        if not self.is_paid or self.end_date is None:
            return 0
        
        remaining = self.end_date - datetime.utcnow()
        return max(0, remaining.days)

class UserUsageLog(Base):
    """
    Track user usage for enforcing limits
    """
    __tablename__ = "user_usage_logs"

    # Primary key
    log_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # User and membership relationship
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    membership_id = Column(Integer, ForeignKey("user_memberships.membership_id"), nullable=False)
    
    # Usage tracking
    action_type = Column(String(50), nullable=False)  # "swipe", "project_card_create", "message_send"
    action_count = Column(Integer, nullable=False, default=1)
    
    # Rate limiting and quota tracking
    hour_timestamp = Column(DateTime, nullable=False)  # Rounded to hour for rate limiting
    day_timestamp = Column(DateTime, nullable=False)   # Rounded to day for daily limits
    month_timestamp = Column(DateTime, nullable=False)  # Rounded to month for monthly quotas
    
    # Metadata
    action_metadata = Column(String(500), nullable=True)  # JSON string for additional data
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User")
    membership = relationship("UserMembership", back_populates="usage_logs")
    
    @staticmethod
    def get_hour_timestamp(dt: datetime = None) -> datetime:
        """Get hour timestamp (rounded down to the hour)"""
        if dt is None:
            dt = datetime.utcnow()
        return dt.replace(minute=0, second=0, microsecond=0)
    
    @staticmethod
    def get_day_timestamp(dt: datetime = None) -> datetime:
        """Get day timestamp (rounded down to the day)"""
        if dt is None:
            dt = datetime.utcnow()
        return dt.replace(hour=0, minute=0, second=0, microsecond=0)
    
    @staticmethod
    def get_month_timestamp(dt: datetime = None) -> datetime:
        """Get month timestamp (rounded down to the first day of the month)"""
        if dt is None:
            dt = datetime.utcnow()
        return dt.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
