"""
Payment system Pydantic schemas
Matches frontend API documentation requirements
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal
from enum import Enum

class PaymentMethodEnum(str, Enum):
    """Payment method enumeration for API"""
    WECHAT_PAY = "wechat_pay"
    ALIPAY = "alipay"
    CREDIT_CARD = "credit_card"

class PlanTypeEnum(str, Enum):
    """Membership plan types"""
    BASIC = "basic"
    PRO = "pro" 
    VIP = "vip"

class TransactionStatusEnum(str, Enum):
    """Transaction status enumeration"""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"

class TransactionTypeEnum(str, Enum):
    """Transaction type enumeration"""
    PURCHASE_RECEIVES = "purchase_receives"
    PLAN_UPGRADE = "plan_upgrade"
    PLAN_DOWNGRADE = "plan_downgrade"
    SUBSCRIPTION_RENEWAL = "subscription_renewal"

# Request Schemas

class PurchaseReceivesRequest(BaseModel):
    """Request schema for purchasing additional receives"""
    amount: int = Field(..., ge=1, le=100, description="Number of receives to purchase (1-100)")
    payment_method: Optional[PaymentMethodEnum] = Field(None, description="Payment method")
    
    class Config:
        use_enum_values = True

class ChangePlanRequest(BaseModel):
    """Request schema for changing membership plan"""
    new_plan: PlanTypeEnum = Field(..., description="Target membership plan")
    payment_method: Optional[PaymentMethodEnum] = Field(None, description="Payment method")
    
    class Config:
        use_enum_values = True

class CreatePaymentSessionRequest(BaseModel):
    """Request schema for creating payment session"""
    type: TransactionTypeEnum = Field(..., description="Payment type")
    amount: Decimal = Field(..., gt=0, description="Payment amount")
    payment_method: PaymentMethodEnum = Field(..., description="Payment method")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    
    class Config:
        use_enum_values = True

class CancelTransactionRequest(BaseModel):
    """Request schema for cancelling transaction"""
    reason: Optional[str] = Field(None, max_length=200, description="Cancellation reason")

# Response Schemas

class PaymentMethodResponse(BaseModel):
    """Response schema for payment method"""
    id: str = Field(..., description="Payment method ID")
    name: str = Field(..., description="Display name")
    type: PaymentMethodEnum = Field(..., description="Payment method type")
    enabled: bool = Field(..., description="Whether method is enabled")
    description: Optional[str] = Field(None, description="Method description")
    icon: Optional[str] = Field(None, description="Icon URL")
    
    class Config:
        use_enum_values = True

class PaymentMethodsResponse(BaseModel):
    """Response schema for available payment methods"""
    methods: List[PaymentMethodResponse] = Field(..., description="Available payment methods")

class TransactionResponse(BaseModel):
    """Response schema for transaction details"""
    id: int = Field(..., description="Transaction ID")
    transaction_id: Optional[str] = Field(None, description="External transaction ID")
    order_id: str = Field(..., description="Order ID")
    amount: Decimal = Field(..., description="Transaction amount")
    currency: str = Field(..., description="Currency code")
    payment_method: PaymentMethodEnum = Field(..., description="Payment method used")
    status: TransactionStatusEnum = Field(..., description="Transaction status")
    transaction_type: TransactionTypeEnum = Field(..., description="Transaction type")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Transaction metadata")
    created_at: datetime = Field(..., description="Creation timestamp")
    paid_at: Optional[datetime] = Field(None, description="Payment completion timestamp")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    
    class Config:
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            Decimal: lambda v: float(v)
        }

class PurchaseReceivesResponse(BaseModel):
    """Response schema for purchase receives"""
    transaction_id: str = Field(..., description="Transaction ID")
    amount: int = Field(..., description="Number of receives purchased")
    cost: Decimal = Field(..., description="Total cost")
    new_balance: int = Field(..., description="New receives balance")
    payment_url: Optional[str] = Field(None, description="Payment URL for redirect")
    status: TransactionStatusEnum = Field(..., description="Transaction status")
    created_at: datetime = Field(..., description="Transaction creation time")
    
    class Config:
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            Decimal: lambda v: float(v)
        }

class UserPlan(BaseModel):
    """User plan information"""
    plan_type: PlanTypeEnum = Field(..., description="Plan type")
    receives_total: int = Field(..., description="Total receives per period")
    receives_used: int = Field(..., description="Receives used this period")
    receives_remaining: int = Field(..., description="Remaining receives")
    monthly_price: Decimal = Field(..., description="Monthly price")
    status: str = Field(..., description="Plan status")
    next_reset_date: datetime = Field(..., description="Next quota reset date")
    
    class Config:
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            Decimal: lambda v: float(v)
        }

class ChangePlanResponse(BaseModel):
    """Response schema for plan change"""
    transaction_id: Optional[str] = Field(None, description="Transaction ID if payment required")
    old_plan: UserPlan = Field(..., description="Previous plan details")
    new_plan: UserPlan = Field(..., description="New plan details")
    monthly_fee: Optional[Decimal] = Field(None, description="New monthly fee")
    payment_url: Optional[str] = Field(None, description="Payment URL if payment required")
    status: TransactionStatusEnum = Field(..., description="Change status")
    effective_date: datetime = Field(..., description="When change takes effect")
    
    class Config:
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            Decimal: lambda v: float(v)
        }

class PaymentSessionResponse(BaseModel):
    """Response schema for payment session creation"""
    session_id: str = Field(..., description="Payment session ID")
    payment_url: str = Field(..., description="Payment URL for redirect")
    qr_code: Optional[str] = Field(None, description="QR code for mobile payment")
    expires_at: datetime = Field(..., description="Session expiration time")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class PaymentSessionDetailsResponse(BaseModel):
    """Response schema for payment session details"""
    session_id: str = Field(..., description="Payment session ID")
    user_id: int = Field(..., description="User ID")
    payment_type: TransactionTypeEnum = Field(..., description="Payment type")
    amount: Decimal = Field(..., description="Payment amount")
    currency: str = Field(..., description="Currency code")
    payment_method: PaymentMethodEnum = Field(..., description="Payment method")
    status: str = Field(..., description="Session status")
    payment_url: Optional[str] = Field(None, description="Payment URL")
    qr_code: Optional[str] = Field(None, description="QR code data")
    created_at: datetime = Field(..., description="Creation time")
    expires_at: datetime = Field(..., description="Expiration time")
    completed_at: Optional[datetime] = Field(None, description="Completion time")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Session metadata")
    
    class Config:
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            Decimal: lambda v: float(v)
        }

class TransactionHistoryResponse(BaseModel):
    """Response schema for transaction history"""
    transactions: List[TransactionResponse] = Field(..., description="Transaction list")
    total: int = Field(..., description="Total transaction count")
    page: int = Field(..., description="Current page")
    limit: int = Field(..., description="Items per page")
    total_pages: int = Field(..., description="Total pages")

class CancelTransactionResponse(BaseModel):
    """Response schema for transaction cancellation"""
    transaction_id: str = Field(..., description="Cancelled transaction ID")
    status: TransactionStatusEnum = Field(..., description="New transaction status")
    refund_amount: Optional[Decimal] = Field(None, description="Refund amount if applicable")
    cancelled_at: datetime = Field(..., description="Cancellation timestamp")
    
    class Config:
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            Decimal: lambda v: float(v)
        }

# Pricing Configuration
RECEIVES_PRICING = {
    1: Decimal("2.00"),    # 1 receive = 2 CNY
    5: Decimal("9.00"),    # 5 receives = 9 CNY (10% discount)
    10: Decimal("17.00"),  # 10 receives = 17 CNY (15% discount)
    20: Decimal("32.00"),  # 20 receives = 32 CNY (20% discount)
}

PLAN_PRICING = {
    PlanTypeEnum.BASIC: Decimal("0.00"),     # Free plan
    PlanTypeEnum.PRO: Decimal("29.00"),      # Pro plan - 29 CNY/month
    PlanTypeEnum.VIP: Decimal("59.00"),      # VIP plan - 59 CNY/month
}

PLAN_RECEIVES = {
    PlanTypeEnum.BASIC: 3,    # 3 receives per month
    PlanTypeEnum.PRO: 20,     # 20 receives per month  
    PlanTypeEnum.VIP: 100,    # 100 receives per month
}