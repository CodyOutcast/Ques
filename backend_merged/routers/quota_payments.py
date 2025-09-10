"""
Quota-Based Payment API Router
Handles one-time payments for membership days instead of recurring subscriptions
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
import logging

from dependencies.db import get_db
from dependencies.auth import get_current_user
from models.users import User
from models.user_membership import MembershipType
from services.quota_payment_service import QuotaPaymentService

router = APIRouter(prefix="/api/v1/quota-payments", tags=["Quota Payments"])
logger = logging.getLogger(__name__)

# === REQUEST MODELS ===

class PurchaseDaysRequest(BaseModel):
    """Request model for purchasing membership days"""
    days: int = Field(..., ge=1, le=3650, description="Number of days to purchase (1-3650, recommended: 30 or 365)")
    payment_method: str = Field("wechat_pay", description="Payment method (wechat_pay, alipay, bank_card)")
    membership_type: str = Field("premium", description="Membership type (premium, paid)")

class ConfirmPaymentRequest(BaseModel):
    """Request model for confirming payment"""
    order_id: str = Field(..., description="Order ID from payment creation")
    transaction_id: str = Field(..., description="Transaction ID from payment provider")
    payment_data: Optional[Dict[str, Any]] = Field(None, description="Additional payment data")

# === RESPONSE MODELS ===

class PricingResponse(BaseModel):
    """Response model for pricing information"""
    pricing: Dict[str, Any]
    perks: Dict[str, List[str]]

class PurchaseResponse(BaseModel):
    """Response model for purchase creation"""
    success: bool
    order_id: str
    transaction_id: int
    amount: float
    currency: str
    days: int
    package_type: str
    payment_method: str
    expires_at: str
    payment_data: Dict[str, Any]

class MembershipStatusResponse(BaseModel):
    """Response model for membership status"""
    has_membership: bool
    membership_type: str
    days_remaining: int
    end_date: Optional[str]
    is_active: bool
    start_date: Optional[str]

class PurchaseHistoryItem(BaseModel):
    """Purchase history item"""
    transaction_id: int
    order_id: str
    amount: float
    currency: str
    days_purchased: int
    package_type: str
    payment_method: str
    purchase_date: Optional[str]
    created_date: str

# === QUOTA PAYMENT ENDPOINTS ===

@router.get("/pricing", response_model=PricingResponse)
async def get_quota_pricing():
    """
    Get pricing information for membership day packages
    """
    try:
        quota_service = QuotaPaymentService()
        pricing = quota_service.get_quota_pricing()
        return PricingResponse(**pricing)
    except Exception as e:
        logger.error(f"Error getting quota pricing: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve pricing information"
        )

@router.post("/purchase", response_model=PurchaseResponse)
async def purchase_membership_days(
    request: PurchaseDaysRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Purchase membership days (quota-based payment)
    
    Available packages:
    - 30 days: $29.99 (monthly equivalent)
    - 365 days: $305.91 (annual equivalent with 15% discount)
    - Custom days: Calculated based on daily rate
    """
    try:
        quota_service = QuotaPaymentService()
        
        # Validate membership type
        try:
            membership_type = MembershipType(request.membership_type.lower())
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid membership type: {request.membership_type}"
            )
        
        # Validate payment method
        valid_methods = ["wechat_pay", "alipay", "bank_card"]
        if request.payment_method not in valid_methods:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid payment method. Must be one of: {valid_methods}"
            )
        
        result = quota_service.purchase_membership_days(
            db=db,
            user_id=current_user.user_id,
            days=request.days,
            payment_method=request.payment_method,
            membership_type=membership_type
        )
        
        return PurchaseResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error purchasing membership days: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create membership purchase"
        )

@router.post("/confirm")
async def confirm_payment(
    request: ConfirmPaymentRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Confirm payment and add purchased days to user's membership
    """
    try:
        quota_service = QuotaPaymentService()
        
        result = quota_service.confirm_payment(
            db=db,
            order_id=request.order_id,
            transaction_id=request.transaction_id,
            payment_data=request.payment_data
        )
        
        # Verify the payment belongs to current user
        if result.get("user_id") != current_user.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Payment confirmation not authorized for this user"
            )
        
        return {
            "success": True,
            "message": f"Payment confirmed! {result['days_added']} days added to your membership.",
            "days_added": result["days_added"],
            "amount_paid": result["amount_paid"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error confirming payment: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to confirm payment"
        )

@router.get("/status", response_model=MembershipStatusResponse)
async def get_membership_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current user's membership status and remaining days
    """
    try:
        quota_service = QuotaPaymentService()
        status_info = quota_service.get_user_membership_status(db, current_user.user_id)
        return MembershipStatusResponse(**status_info)
    except Exception as e:
        logger.error(f"Error getting membership status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve membership status"
        )

@router.get("/history", response_model=List[PurchaseHistoryItem])
async def get_purchase_history(
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user's purchase history
    """
    try:
        quota_service = QuotaPaymentService()
        history = quota_service.get_purchase_history(db, current_user.user_id, limit)
        return [PurchaseHistoryItem(**item) for item in history]
    except Exception as e:
        logger.error(f"Error getting purchase history: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve purchase history"
        )

@router.get("/calculate-price")
async def calculate_custom_price(
    days: int,
    membership_type: str = "premium"
):
    """
    Calculate price for custom number of days
    """
    try:
        if days < 1 or days > 3650:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Days must be between 1 and 3650"
            )
        
        try:
            membership_enum = MembershipType(membership_type.lower())
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid membership type: {membership_type}"
            )
        
        quota_service = QuotaPaymentService()
        price, package_type = quota_service.calculate_package_price(days, membership_enum)
        
        return {
            "days": days,
            "price": price,
            "currency": "USD",
            "price_per_day": round(price / days, 2),
            "package_type": package_type,
            "membership_type": membership_type,
            "savings_vs_30day": None if days <= 30 else {
                "monthly_equivalent_cost": round((29.99 / 30) * days, 2),
                "actual_cost": price,
                "savings": round(((29.99 / 30) * days) - price, 2) if days >= 365 else 0
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error calculating price: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to calculate price"
        )

# === WEBHOOK ENDPOINTS ===

@router.post("/webhook/payment")
async def payment_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Handle payment webhooks from payment providers
    This would be called by WeChat Pay, Alipay, etc. when payment status changes
    """
    try:
        # Get raw body for signature verification
        body = await request.body()
        headers = dict(request.headers)
        
        # TODO: Implement webhook signature verification
        # TODO: Parse webhook data based on payment provider
        # TODO: Update payment status and add days to membership
        
        logger.info(f"Received payment webhook: {len(body)} bytes")
        
        return {"success": True, "message": "Webhook received"}
        
    except Exception as e:
        logger.error(f"Error processing payment webhook: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process webhook"
        )

# === ADMIN ENDPOINTS ===

@router.get("/admin/stats")
async def get_quota_payment_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get statistics about quota-based payments (admin only)
    TODO: Add admin role verification
    """
    try:
        # TODO: Add admin check
        # if not current_user.is_admin:
        #     raise HTTPException(status_code=403, detail="Admin access required")
        
        from models.payments import MembershipTransaction, PaymentStatus
        from sqlalchemy import func, extract
        
        # Get basic stats
        total_transactions = db.query(func.count(MembershipTransaction.id)).filter(
            MembershipTransaction.payment_status == PaymentStatus.SUCCESS
        ).scalar()
        
        total_revenue = db.query(func.sum(MembershipTransaction.amount)).filter(
            MembershipTransaction.payment_status == PaymentStatus.SUCCESS
        ).scalar() or 0
        
        total_days_sold = db.query(func.sum(MembershipTransaction.plan_duration_days)).filter(
            MembershipTransaction.payment_status == PaymentStatus.SUCCESS
        ).scalar() or 0
        
        # Package distribution
        package_stats = db.query(
            MembershipTransaction.plan_duration_days,
            func.count(MembershipTransaction.id).label('count'),
            func.sum(MembershipTransaction.amount).label('revenue')
        ).filter(
            MembershipTransaction.payment_status == PaymentStatus.SUCCESS
        ).group_by(
            MembershipTransaction.plan_duration_days
        ).all()
        
        return {
            "total_transactions": total_transactions,
            "total_revenue": float(total_revenue),
            "total_days_sold": int(total_days_sold),
            "average_transaction": float(total_revenue / total_transactions) if total_transactions > 0 else 0,
            "package_distribution": [
                {
                    "days": stat.plan_duration_days,
                    "transactions": stat.count,
                    "revenue": float(stat.revenue),
                    "percentage": round((stat.count / total_transactions) * 100, 1) if total_transactions > 0 else 0
                }
                for stat in package_stats
            ]
        }
        
    except Exception as e:
        logger.error(f"Error getting quota payment stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve statistics"
        )

# === HEALTH CHECK ===

@router.get("/health")
async def quota_payment_health():
    """
    Health check for quota payment service
    """
    return {
        "status": "healthy",
        "service": "quota_payment",
        "payment_model": "one_time_purchase",
        "available_packages": [30, 365],
        "custom_days_supported": True,
        "max_days": 3650
    }
