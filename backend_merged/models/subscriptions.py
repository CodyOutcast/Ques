"""
User subscription and quota models
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
import enum
from .base import Base

class SubscriptionType(str, enum.Enum):
    """User subscription types"""
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"  # For future expansion

class UserSubscription(Base):
    """
    User Subscription Model
    Manages user subscription tiers and quota limits
    """
    __tablename__ = "user_subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False, unique=True)
    subscription_type = Column(SQLEnum('free', 'pro', 'enterprise', name='subscriptiontype'), nullable=False, default='free')
    monthly_quota_limit = Column(Integer, nullable=False, default=30)
    current_period_start = Column(DateTime, nullable=False, default=datetime.utcnow)
    current_period_end = Column(DateTime, nullable=False)
    current_period_usage = Column(Integer, nullable=False, default=0)
    total_requests_count = Column(Integer, nullable=False, default=0)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship to users table
    user = relationship("User", backref="subscription")
    
    def __init__(self, user_id: int, subscription_type: str = "free"):
        self.user_id = user_id
        self.subscription_type = subscription_type
        self.current_period_start = datetime.utcnow()
        self.current_period_end = self._calculate_period_end()
        self.monthly_quota_limit = self._get_quota_limit(subscription_type)
        self.current_period_usage = 0
        self.is_active = True
        
    def _calculate_period_end(self) -> datetime:
        """Calculate the end of the current billing period (next month)"""
        start = self.current_period_start
        if start.month == 12:
            return start.replace(year=start.year + 1, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        else:
            return start.replace(month=start.month + 1, day=1, hour=0, minute=0, second=0, microsecond=0)
    
    def _get_quota_limit(self, subscription_type: str) -> int:
        """Get quota limit based on subscription type"""
        quota_limits = {
            "free": 30,
            "pro": 300,
            "enterprise": 1000
        }
        return quota_limits.get(subscription_type, 30)
    
    @property
    def remaining_quota(self) -> int:
        """Calculate remaining quota for current period"""
        return max(0, self.monthly_quota_limit - self.current_period_usage)
    
    @property
    def is_quota_exceeded(self) -> bool:
        """Check if quota is exceeded"""
        return self.current_period_usage >= self.monthly_quota_limit
    
    @property
    def quota_reset_date(self) -> datetime:
        """Get the date when quota will reset"""
        return self.current_period_end
    
    def is_current_period(self) -> bool:
        """Check if we're still in the current billing period"""
        now = datetime.utcnow()
        return self.current_period_start <= now <= self.current_period_end
    
    def reset_period_if_needed(self):
        """Reset the period and usage if current period has ended"""
        if not self.is_current_period():
            self.current_period_start = datetime.utcnow()
            self.current_period_end = self._calculate_period_end()
            self.current_period_usage = 0
            self.updated_at = datetime.utcnow()
    
    def upgrade_subscription(self, new_type: str):
        """Upgrade subscription type"""
        self.subscription_type = new_type
        self.monthly_quota_limit = self._get_quota_limit(new_type)
        self.updated_at = datetime.utcnow()
    
    def increment_usage(self, amount: int = 1):
        """Increment usage for current period"""
        self.current_period_usage += amount
        self.updated_at = datetime.utcnow()

class ProjectIdeaRequest(Base):
    """
    Track project idea generation requests for quota management
    """
    __tablename__ = "project_idea_requests"
    
    request_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    subscription_id = Column(Integer, ForeignKey("user_subscriptions.id"), nullable=False)
    query = Column(String(500), nullable=False)
    
    # Response metadata
    total_sources_found = Column(Integer, nullable=True)
    total_ideas_extracted = Column(Integer, nullable=True)
    processing_time_seconds = Column(Integer, nullable=True)
    
    # Success tracking
    success = Column(Boolean, nullable=False, default=True)
    error_message = Column(String(500), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationship to users table
    user = relationship("User")
