"""
Membership schemas for API requests and responses
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class MembershipResponse(BaseModel):
    """Schema for membership responses"""
    membership_id: int
    user_id: int
    type: str = Field(..., description="Membership type: free, premium, vip")
    start_date: datetime
    end_date: Optional[datetime] = None
    is_active: bool
    auto_renew: bool
    billing_cycle: Optional[str] = None
    price: Optional[float] = None
    currency: str = "CNY"
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class MembershipPlanResponse(BaseModel):
    """Schema for membership plan responses"""
    plan_id: int
    name: str
    type: str
    price_monthly: Optional[float] = None
    price_annual: Optional[float] = None
    currency: str = "CNY"
    description: Optional[str] = None
    features: Optional[str] = None  # JSON string
    max_swipes_daily: Optional[int] = None
    max_matches_monthly: Optional[int] = None
    video_calls_enabled: bool = False
    priority_support: bool = False
    is_active: bool = True
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class MembershipUpgradeRequest(BaseModel):
    """Schema for membership upgrade requests"""
    plan_id: int = Field(..., description="Target plan ID")
    billing_cycle: str = Field(..., description="monthly or annual")
    auto_renew: bool = Field(False, description="Enable auto-renewal")
    payment_method: Optional[str] = Field(None, description="Payment method ID")

class MembershipCreateRequest(BaseModel):
    """Schema for creating new membership"""
    user_id: int
    type: str = Field(..., description="Membership type: free, premium, vip")
    billing_cycle: Optional[str] = None
    auto_renew: bool = False

class MembershipBenefitsResponse(BaseModel):
    """Schema for membership benefits response"""
    membership_type: str
    benefits: dict
    usage: dict
    expires_at: Optional[datetime] = None

class MembershipStatsResponse(BaseModel):
    """Schema for membership statistics"""
    total_members: int
    free_members: int
    premium_members: int
    vip_members: int
    monthly_revenue: float
    annual_revenue: float
    upgrade_conversion_rate: float
    churn_rate: float