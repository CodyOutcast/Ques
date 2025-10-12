"""
Membership and subscription models following DATABASE_STRUCTURE_UPDATE.md
"""

from sqlalchemy import Column, Integer, String, TIMESTAMP, Boolean, VARCHAR, ForeignKey, DECIMAL, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base

class Membership(Base):
    """
    User membership subscriptions
    """
    __tablename__ = "memberships"

    membership_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    type = Column(VARCHAR(10), nullable=False, default='free')  # free, premium, vip
    start_date = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)
    end_date = Column(TIMESTAMP, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    auto_renew = Column(Boolean, nullable=False, default=False)
    billing_cycle = Column(VARCHAR(12), nullable=True)  # monthly, annual
    price = Column(DECIMAL(10, 2), nullable=True)
    currency = Column(VARCHAR(3), nullable=False, default='CNY')
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, nullable=True)

    # Relationships
    user = relationship("User", back_populates="membership")
    payments = relationship("Payment", back_populates="membership")

class MembershipPlan(Base):
    """
    Available membership plans
    """
    __tablename__ = "membership_plans"

    plan_id = Column(Integer, primary_key=True, index=True)
    name = Column(VARCHAR(50), nullable=False, unique=True)
    type = Column(VARCHAR(10), nullable=False)  # free, premium, vip
    price_monthly = Column(DECIMAL(10, 2), nullable=True)
    price_annual = Column(DECIMAL(10, 2), nullable=True)
    currency = Column(VARCHAR(3), nullable=False, default='CNY')
    description = Column(Text, nullable=True)
    features = Column(Text, nullable=True)  # JSON string of features
    max_swipes_daily = Column(Integer, nullable=True)
    max_matches_monthly = Column(Integer, nullable=True)
    video_calls_enabled = Column(Boolean, nullable=False, default=False)
    priority_support = Column(Boolean, nullable=False, default=False)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, nullable=True)

class MembershipTransaction(Base):
    """
    Membership subscription transactions
    """
    __tablename__ = "membership_transactions"

    transaction_id = Column(Integer, primary_key=True, index=True)
    membership_id = Column(Integer, ForeignKey("memberships.membership_id"), nullable=False)
    payment_id = Column(Integer, ForeignKey("payments.payment_id"), nullable=True)
    plan_id = Column(Integer, ForeignKey("membership_plans.plan_id"), nullable=False)
    transaction_type = Column(VARCHAR(20), nullable=False)  # subscription, renewal, upgrade, cancellation
    amount = Column(DECIMAL(10, 2), nullable=False)
    currency = Column(VARCHAR(3), nullable=False, default='CNY')
    status = Column(VARCHAR(20), nullable=False, default='pending')  # pending, completed, failed, refunded
    billing_cycle = Column(VARCHAR(12), nullable=False)  # monthly, annual
    start_date = Column(TIMESTAMP, nullable=False)
    end_date = Column(TIMESTAMP, nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)
    processed_at = Column(TIMESTAMP, nullable=True)

    # Relationships
    membership = relationship("Membership", back_populates="transactions")
    payment = relationship("Payment", back_populates="membership_transaction")
    plan = relationship("MembershipPlan", back_populates="transactions")

# Add relationships to existing models
Membership.transactions = relationship("MembershipTransaction", back_populates="membership")
MembershipPlan.transactions = relationship("MembershipTransaction", back_populates="plan")