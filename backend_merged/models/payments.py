"""
Payment models for tracking membership transactions and payment history
"""

from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime, timedelta
import enum

from models.base import Base

class PaymentStatus(enum.Enum):
    """Payment status enumeration"""
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"

class PaymentMethod(enum.Enum):
    """Payment method enumeration"""
    WECHAT_PAY = "wechat_pay"
    ALIPAY = "alipay"
    BANK_CARD = "bank_card"

class MembershipTransaction(Base):
    """Model for tracking membership payment transactions"""
    __tablename__ = "membership_transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # User and order information
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False, index=True)
    order_id = Column(String(100), unique=True, nullable=False, index=True)
    transaction_id = Column(String(100), unique=True, nullable=True, index=True)  # From payment provider
    
    # Payment details
    amount = Column(Float, nullable=False)  # Amount in CNY
    currency = Column(String(3), nullable=False, default="CNY")
    payment_method = Column(SQLEnum(PaymentMethod), nullable=False, default=PaymentMethod.WECHAT_PAY)
    payment_status = Column(SQLEnum(PaymentStatus), nullable=False, default=PaymentStatus.PENDING)
    
    # Membership plan details
    plan_type = Column(String(20), nullable=False)  # monthly, yearly
    plan_duration_days = Column(Integer, nullable=False)
    
    # Payment provider details
    prepay_id = Column(String(100), nullable=True)  # WeChat Pay prepay ID
    payment_params = Column(Text, nullable=True)  # JSON string of payment parameters
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    paid_at = Column(DateTime(timezone=True), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)  # Payment expiration
    
    # Additional information
    user_ip = Column(String(45), nullable=True)  # User IP address
    user_agent = Column(String(500), nullable=True)  # User agent
    error_message = Column(Text, nullable=True)  # Error details if payment fails
    notification_data = Column(Text, nullable=True)  # Raw notification data from payment provider
    
    # Relationships
    user = relationship("User", back_populates="membership_transactions")
    
    def __repr__(self):
        return f"<MembershipTransaction(id={self.id}, user_id={self.user_id}, order_id={self.order_id}, status={self.payment_status})>"
    
    @property
    def is_expired(self) -> bool:
        """Check if payment has expired"""
        if not self.expires_at:
            return False
        return datetime.utcnow() > self.expires_at
    
    @property
    def is_successful(self) -> bool:
        """Check if payment was successful"""
        return self.payment_status == PaymentStatus.SUCCESS
    
    @property
    def is_pending(self) -> bool:
        """Check if payment is pending"""
        return self.payment_status == PaymentStatus.PENDING
    
    def mark_as_paid(self, transaction_id: str, notification_data: str = None):
        """Mark transaction as successfully paid"""
        self.payment_status = PaymentStatus.SUCCESS
        self.transaction_id = transaction_id
        self.paid_at = datetime.utcnow()
        if notification_data:
            self.notification_data = notification_data
    
    def mark_as_failed(self, error_message: str):
        """Mark transaction as failed"""
        self.payment_status = PaymentStatus.FAILED
        self.error_message = error_message
    
    def mark_as_cancelled(self):
        """Mark transaction as cancelled"""
        self.payment_status = PaymentStatus.CANCELLED

class PaymentRefund(Base):
    """Model for tracking payment refunds"""
    __tablename__ = "payment_refunds"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Reference to original transaction
    transaction_id = Column(Integer, ForeignKey("membership_transactions.id"), nullable=False)
    
    # Refund details
    refund_id = Column(String(100), unique=True, nullable=False, index=True)  # From payment provider
    refund_amount = Column(Float, nullable=False)
    refund_reason = Column(String(200), nullable=True)
    refund_status = Column(String(20), nullable=False, default="pending")  # pending, success, failed
    
    # Timestamps
    requested_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    processed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Additional information
    admin_user_id = Column(Integer, nullable=True)  # Admin who processed the refund
    notes = Column(Text, nullable=True)
    
    # Relationships
    transaction = relationship("MembershipTransaction")
    
    def __repr__(self):
        return f"<PaymentRefund(id={self.id}, transaction_id={self.transaction_id}, amount={self.refund_amount})>"

class PaymentWebhookLog(Base):
    """Model for logging payment webhook/notification attempts"""
    __tablename__ = "payment_webhook_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Webhook details
    webhook_id = Column(String(100), nullable=True)  # Unique webhook ID if provided
    payment_provider = Column(String(20), nullable=False)  # wechat_pay, alipay, etc.
    webhook_type = Column(String(50), nullable=False)  # payment_success, payment_failed, etc.
    
    # Request details
    raw_data = Column(Text, nullable=False)  # Raw webhook data
    headers = Column(Text, nullable=True)  # Request headers as JSON
    user_agent = Column(String(500), nullable=True)
    source_ip = Column(String(45), nullable=True)
    
    # Processing details
    processed = Column(Boolean, nullable=False, default=False)
    processing_result = Column(Text, nullable=True)  # Processing result or error message
    related_order_id = Column(String(100), nullable=True, index=True)
    
    # Timestamps
    received_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    processed_at = Column(DateTime(timezone=True), nullable=True)
    
    def __repr__(self):
        return f"<PaymentWebhookLog(id={self.id}, provider={self.payment_provider}, type={self.webhook_type})>"
