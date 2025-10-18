"""
Payment and transaction models following DATABASE_STRUCTURE_UPDATE.md and frontend API requirements
"""

from sqlalchemy import Column, Integer, String, TIMESTAMP, Boolean, VARCHAR, ForeignKey, DECIMAL, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum
from .base import Base

class PaymentStatus(str, Enum):
    """Payment status enumeration"""
    PENDING = "pending"
    COMPLETED = "completed" 
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"

class PaymentType(str, Enum):
    """Payment type enumeration"""
    PURCHASE_RECEIVES = "purchase_receives"
    PLAN_UPGRADE = "plan_upgrade"
    PLAN_DOWNGRADE = "plan_downgrade"
    SUBSCRIPTION_RENEWAL = "subscription_renewal"

class PaymentMethodType(str, Enum):
    """Payment method type enumeration"""
    WECHAT_PAY = "wechat_pay"
    ALIPAY = "alipay"
    CREDIT_CARD = "credit_card"
    BANK_TRANSFER = "bank_transfer"

class MembershipTransaction(Base):
    """
    Payment transactions for membership purchases and receives
    Based on DATABASE_STRUCTURE_UPDATE.md membership_transactions table
    """
    __tablename__ = "membership_transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    membership_id = Column(Integer, ForeignKey("memberships.id"), nullable=True)  # For plan changes
    
    # Transaction identifiers
    order_id = Column(VARCHAR(100), nullable=False, unique=True, index=True)
    transaction_id = Column(VARCHAR(100), nullable=True, unique=True, index=True)  # External payment provider ID
    
    # Transaction details
    amount = Column(DECIMAL(10, 2), nullable=False)  # Transaction amount
    currency = Column(VARCHAR(3), nullable=False, default='CNY')
    payment_method = Column(VARCHAR(20), nullable=False)  # wechat_pay, alipay, credit_card
    payment_status = Column(VARCHAR(20), nullable=False, default=PaymentStatus.PENDING)
    
    # Transaction type and metadata
    transaction_type = Column(VARCHAR(30), nullable=False)  # purchase_receives, plan_upgrade
    transaction_metadata = Column(Text, nullable=True)  # JSON metadata (receives count, plan details)
    
    # Plan-related fields (for plan changes)
    plan_type = Column(VARCHAR(20), nullable=True)  # Target plan for upgrades
    plan_duration_days = Column(Integer, nullable=True)
    
    # Payment provider data
    prepay_id = Column(VARCHAR(100), nullable=True)  # WeChat/Alipay prepay ID
    payment_params = Column(Text, nullable=True)  # JSON payment parameters
    provider_response = Column(Text, nullable=True)  # JSON response from payment provider
    
    # Timestamps
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)
    paid_at = Column(TIMESTAMP, nullable=True)  # When payment completed
    expires_at = Column(TIMESTAMP, nullable=True)  # Payment session expiration
    
    # Tracking data
    user_ip = Column(VARCHAR(45), nullable=True)
    user_agent = Column(VARCHAR(500), nullable=True)
    error_message = Column(Text, nullable=True)
    notification_data = Column(Text, nullable=True)  # Webhook notification data
    
    # Relationships
    user = relationship("User", back_populates="transactions")
    membership = relationship("Membership", back_populates="transactions")
    refunds = relationship("PaymentRefund", back_populates="transaction")

class PaymentRefund(Base):
    """
    Payment refund records
    Based on DATABASE_STRUCTURE_UPDATE.md payment_refunds table
    """
    __tablename__ = "payment_refunds"
    
    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(Integer, ForeignKey("membership_transactions.id"), nullable=False)
    
    # Refund details
    refund_id = Column(VARCHAR(100), nullable=False, unique=True, index=True)
    refund_amount = Column(DECIMAL(10, 2), nullable=False)
    refund_reason = Column(VARCHAR(200), nullable=False)
    refund_status = Column(VARCHAR(20), nullable=False, default="pending")
    
    # Timestamps
    requested_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)
    processed_at = Column(TIMESTAMP, nullable=True)
    
    # Admin processing
    admin_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    notes = Column(Text, nullable=True)
    
    # Relationships
    transaction = relationship("MembershipTransaction", back_populates="refunds")
    admin_user = relationship("User", foreign_keys=[admin_user_id])

class PaymentMethod(Base):
    """
    User payment methods (stored securely)
    """
    __tablename__ = "payment_methods"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Method details
    method_type = Column(VARCHAR(20), nullable=False)  # wechat_pay, alipay, credit_card
    name = Column(VARCHAR(100), nullable=False)  # User-friendly name
    
    # Tokenized payment data (no sensitive info stored)
    provider_method_id = Column(VARCHAR(100), nullable=True)  # Provider's method ID
    last_four = Column(VARCHAR(4), nullable=True)  # Last 4 digits for cards
    expiry_month = Column(Integer, nullable=True)  # For credit cards
    expiry_year = Column(Integer, nullable=True)
    
    # Status and metadata
    is_default = Column(Boolean, nullable=False, default=False)
    is_active = Column(Boolean, nullable=False, default=True)
    verified = Column(Boolean, nullable=False, default=False)
    
    # Timestamps
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="payment_methods")

class PaymentSession(Base):
    """
    Payment sessions for tracking payment flows
    """
    __tablename__ = "payment_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(VARCHAR(100), nullable=False, unique=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Session details
    payment_type = Column(VARCHAR(30), nullable=False)  # purchase_receives, plan_upgrade
    amount = Column(DECIMAL(10, 2), nullable=False)
    currency = Column(VARCHAR(3), nullable=False, default='CNY')
    payment_method = Column(VARCHAR(20), nullable=False)
    
    # Session data
    session_metadata = Column(Text, nullable=True)  # JSON session metadata
    payment_url = Column(VARCHAR(500), nullable=True)  # Payment redirect URL
    qr_code = Column(Text, nullable=True)  # QR code data for mobile payments
    
    # Status and timing
    status = Column(VARCHAR(20), nullable=False, default="created")
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)
    expires_at = Column(TIMESTAMP, nullable=False)  # Session expiration
    completed_at = Column(TIMESTAMP, nullable=True)
    
    # Related transaction
    transaction_id = Column(Integer, ForeignKey("membership_transactions.id"), nullable=True)
    
    # Relationships
    user = relationship("User")
    transaction = relationship("MembershipTransaction")