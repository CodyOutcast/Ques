"""
Membership and subscription models following DATABASE_STRUCTURE_UPDATE.md
"""

from sqlalchemy import Column, Integer, String, TIMESTAMP, Boolean, VARCHAR, ForeignKey, DECIMAL, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base

class Membership(Base):
    """
    User membership subscriptions - aligned with actual database schema
    """
    __tablename__ = "memberships"

    id = Column(Integer, primary_key=True, index=True)  # Changed from membership_id to id
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    plan_type = Column(VARCHAR(20), nullable=False, default='basic')  # Changed from type to plan_type
    receives_total = Column(Integer, nullable=False, default=3)
    receives_used = Column(Integer, nullable=False, default=0)
    receives_remaining = Column(Integer, nullable=True)
    monthly_price = Column(DECIMAL(10, 2), nullable=False, default=0.00)
    plan_start_date = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)  # Changed from start_date
    plan_end_date = Column(TIMESTAMP, nullable=True)  # Changed from end_date
    status = Column(VARCHAR(20), nullable=False, default='active')  # Changed from is_active
    auto_renewal = Column(Boolean, nullable=False, default=True)  # Changed from auto_renew
    payment_method = Column(VARCHAR(20), nullable=True)
    last_payment_date = Column(TIMESTAMP, nullable=True)
    last_reset_date = Column(TIMESTAMP, nullable=True)
    next_reset_date = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="membership")
    transactions = relationship("MembershipTransaction", back_populates="membership")

# MembershipPlan and MembershipTransaction models removed - tables don't exist in DATABASE_SCHEMA_COMPLETE.md
# Only the 'memberships' table exists in the database schema