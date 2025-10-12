"""
Payment and transaction models following DATABASE_STRUCTURE_UPDATE.md
"""

from sqlalchemy import Column, Integer, String, TIMESTAMP, Boolean, VARCHAR, ForeignKey, DECIMAL, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base

class Payment(Base):
    """
    Payment transactions
    """
    __tablename__ = "payments"

    payment_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    membership_id = Column(Integer, ForeignKey("memberships.membership_id"), nullable=True)
    amount = Column(DECIMAL(10, 2), nullable=False)
    currency = Column(VARCHAR(3), nullable=False, default='CNY')
    payment_method = Column(VARCHAR(20), nullable=False)  # wechat, alipay, card, etc.
    status = Column(VARCHAR(20), nullable=False, default='pending')  # pending, completed, failed, refunded
    transaction_id = Column(VARCHAR(100), nullable=True, unique=True)  # External payment provider ID
    provider_response = Column(Text, nullable=True)  # JSON response from payment provider
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)
    processed_at = Column(TIMESTAMP, nullable=True)
    refunded_at = Column(TIMESTAMP, nullable=True)
    refund_amount = Column(DECIMAL(10, 2), nullable=True)
    failure_reason = Column(Text, nullable=True)

    # Relationships
    user = relationship("User", back_populates="payments")
    membership = relationship("Membership", back_populates="payments")
    membership_transaction = relationship("MembershipTransaction", back_populates="payment")

class PaymentMethod(Base):
    """
    User saved payment methods
    """
    __tablename__ = "payment_methods"

    method_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    method_type = Column(VARCHAR(20), nullable=False)  # wechat, alipay, card
    provider_id = Column(VARCHAR(100), nullable=True)  # ID from payment provider
    last_four = Column(VARCHAR(4), nullable=True)  # Last 4 digits for cards
    expiry_month = Column(Integer, nullable=True)
    expiry_year = Column(Integer, nullable=True)
    cardholder_name = Column(VARCHAR(100), nullable=True)
    is_default = Column(Boolean, nullable=False, default=False)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, nullable=True)
    verified_at = Column(TIMESTAMP, nullable=True)

    # Relationships
    user = relationship("User", back_populates="payment_methods")

class RefundRequest(Base):
    """
    Payment refund requests
    """
    __tablename__ = "refund_requests"

    request_id = Column(Integer, primary_key=True, index=True)
    payment_id = Column(Integer, ForeignKey("payments.payment_id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    amount_requested = Column(DECIMAL(10, 2), nullable=False)
    reason = Column(Text, nullable=False)
    status = Column(VARCHAR(20), nullable=False, default='pending')  # pending, approved, rejected, processed
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)
    reviewed_at = Column(TIMESTAMP, nullable=True)
    processed_at = Column(TIMESTAMP, nullable=True)
    reviewer_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    admin_notes = Column(Text, nullable=True)
    refund_transaction_id = Column(VARCHAR(100), nullable=True)

    # Relationships
    payment = relationship("Payment", back_populates="refund_requests")
    user = relationship("User", foreign_keys=[user_id], back_populates="refund_requests")
    reviewer = relationship("User", foreign_keys=[reviewer_id], back_populates="reviewed_refunds")

class Revenue(Base):
    """
    Revenue tracking and analytics
    """
    __tablename__ = "revenue"

    revenue_id = Column(Integer, primary_key=True, index=True)
    date = Column(TIMESTAMP, nullable=False)
    payment_id = Column(Integer, ForeignKey("payments.payment_id"), nullable=True)
    membership_type = Column(VARCHAR(10), nullable=True)  # free, premium, vip
    billing_cycle = Column(VARCHAR(12), nullable=True)  # monthly, annual
    gross_amount = Column(DECIMAL(10, 2), nullable=False)
    fees = Column(DECIMAL(10, 2), nullable=True)
    net_amount = Column(DECIMAL(10, 2), nullable=False)
    currency = Column(VARCHAR(3), nullable=False, default='CNY')
    payment_method = Column(VARCHAR(20), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    refunded_amount = Column(DECIMAL(10, 2), nullable=True, default=0.00)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)

    # Relationships
    payment = relationship("Payment", back_populates="revenue_entry")
    user = relationship("User", back_populates="revenue_contributions")

# Add back-references to existing models
Payment.refund_requests = relationship("RefundRequest", back_populates="payment")
Payment.revenue_entry = relationship("Revenue", back_populates="payment")