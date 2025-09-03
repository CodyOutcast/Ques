"""
Membership router for managing user membership tiers and subscriptions
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from pydantic import BaseModel
from enum import Enum

from dependencies.db import get_db
from dependencies.auth import get_current_user
from models.users import User
from services.membership_service import MembershipService
from services.subscription_service_working import SubscriptionService, SubscriptionPeriod
from models.user_membership import MembershipType

router = APIRouter(prefix="/api/membership", tags=["membership"])

class SubscriptionPeriodEnum(str, Enum):
    MONTHLY = "monthly"
    ANNUALLY = "annually"

class UpgradeMembershipRequest(BaseModel):
    duration_days: int = 30
    payment_method: str = "stripe"
    subscription_id: str = None

class CreateSubscriptionRequest(BaseModel):
    membership_type: MembershipType
    period: SubscriptionPeriodEnum
    payment_method: str = "wechat_pay"

class MembershipResponse(BaseModel):
    membership_type: str
    is_paid: bool
    days_remaining: int
    limits: Dict[str, Any]
    usage: Dict[str, Any]
    can_swipe: bool
    can_create_card: bool

class SubscriptionResponse(BaseModel):
    has_subscription: bool
    membership_level: str
    expires_at: Optional[str] = None
    subscription_period: Optional[str] = None
    subscription_status: Optional[str] = None
    auto_renew: bool = False
    next_billing_date: Optional[str] = None

@router.get("/status", response_model=MembershipResponse)
def get_membership_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current membership status and usage statistics
    """
    try:
        stats = MembershipService.get_usage_stats(db, current_user.user_id)
        
        return MembershipResponse(
            membership_type=stats["membership_type"],
            is_paid=stats["is_paid"],
            days_remaining=stats["days_remaining"],
            limits=stats["limits"],
            usage=stats["usage"],
            can_swipe=stats["can_swipe"],
            can_create_card=stats["can_create_card"]
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/limits")
def get_membership_limits(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get detailed membership limits and current usage
    """
    try:
        membership = MembershipService.get_or_create_membership(db, current_user.user_id)
        limits = MembershipService.LIMITS[membership.membership_type]
        
        # Check current limits
        can_swipe, swipe_message, swipe_info = MembershipService.check_swipe_limit(db, current_user.user_id)
        can_create_card, card_message, card_info = MembershipService.check_project_card_limit(db, current_user.user_id)
        
        return {
            "membership_type": membership.membership_type.value,
            "is_paid": membership.is_paid,
            "limits": limits,
            "current_status": {
                "swipes": {
                    "allowed": can_swipe,
                    "message": swipe_message,
                    "info": swipe_info
                },
                "project_cards": {
                    "allowed": can_create_card,
                    "message": card_message,
                    "info": card_info
                }
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/upgrade")
def upgrade_membership(
    upgrade_request: UpgradeMembershipRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upgrade user to paid membership
    """
    try:
        membership = MembershipService.upgrade_to_paid(
            db=db,
            user_id=current_user.user_id,
            duration_days=upgrade_request.duration_days,
            payment_method=upgrade_request.payment_method,
            subscription_id=upgrade_request.subscription_id
        )
        
        return {
            "message": "Membership upgraded successfully",
            "membership_type": membership.membership_type.value,
            "is_paid": membership.is_paid,
            "days_remaining": membership.days_remaining,
            "new_limits": MembershipService.LIMITS[membership.membership_type]
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/downgrade")
def downgrade_membership(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Downgrade user to free membership (admin only or expired)
    """
    try:
        membership = MembershipService.downgrade_to_free(
            db=db,
            user_id=current_user.user_id,
            reason="manual_downgrade"
        )
        
        return {
            "message": "Membership downgraded to free",
            "membership_type": membership.membership_type.value,
            "is_paid": membership.is_paid,
            "new_limits": MembershipService.LIMITS[membership.membership_type]
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/pricing")
def get_pricing_info():
    """
    Get pricing and feature comparison information
    """
    return {
        "plans": {
            "free": {
                "name": "Free",
                "price": 0,
                "features": {
                    "swipes_per_day": 30,
                    "project_cards_max": 2,
                    "project_cards_per_day": 2,
                    "messages_per_day": 50,
                    "vector_recommendations": True,
                    "ai_search": True,
                    "basic_matching": True
                },
                "limitations": [
                    "Limited daily swipes",
                    "Maximum 2 project cards",
                    "Limited daily messages"
                ]
            },
            "paid": {
                "name": "Premium",
                "price": 9.99,
                "duration": "per month",
                "features": {
                    "swipes_per_day": "Unlimited",
                    "swipes_per_hour": 30,  # Rate limiting
                    "project_cards_max": "Unlimited",
                    "project_cards_per_day": 10,
                    "messages_per_day": "Unlimited",
                    "vector_recommendations": True,
                    "ai_search": True,
                    "advanced_matching": True,
                    "priority_support": True,
                    "early_access": True
                },
                "benefits": [
                    "Unlimited daily swipes",
                    "Unlimited project cards (10/day creation limit)",
                    "Unlimited messages",
                    "Anti-bot protection",
                    "Priority support"
                ]
            }
        }
    }

@router.get("/usage-history")
def get_usage_history(
    days: int = 7,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get usage history for the past N days
    """
    try:
        from datetime import datetime, timedelta
        from models.user_membership import UserUsageLog
        from sqlalchemy import func
        
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Get daily usage statistics
        usage_stats = db.query(
            UserUsageLog.day_timestamp,
            UserUsageLog.action_type,
            func.sum(UserUsageLog.action_count).label('total_count')
        ).filter(
            UserUsageLog.user_id == current_user.user_id,
            UserUsageLog.day_timestamp >= start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        ).group_by(
            UserUsageLog.day_timestamp,
            UserUsageLog.action_type
        ).order_by(UserUsageLog.day_timestamp.desc()).all()
        
        # Format the results
        history = {}
        for stat in usage_stats:
            date_str = stat.day_timestamp.strftime('%Y-%m-%d')
            if date_str not in history:
                history[date_str] = {}
            history[date_str][stat.action_type] = stat.total_count
        
        return {
            "period_days": days,
            "usage_history": history,
            "current_membership": MembershipService.get_or_create_membership(db, current_user.user_id).membership_type.value
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# Subscription Management Endpoints

@router.post("/subscription/create")
def create_subscription(
    subscription_request: CreateSubscriptionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new subscription for monthly or annual billing
    """
    try:
        subscription_service = SubscriptionService()
        
        # Map enum to SubscriptionPeriod
        period_mapping = {
            SubscriptionPeriodEnum.MONTHLY: SubscriptionPeriod.MONTHLY,
            SubscriptionPeriodEnum.ANNUALLY: SubscriptionPeriod.ANNUALLY
        }
        
        period = period_mapping[subscription_request.period]
        
        result = subscription_service.create_subscription(
            db=db,
            user_id=current_user.user_id,
            membership_type=subscription_request.membership_type,
            period=period,
            payment_method=subscription_request.payment_method
        )
        
        return {
            "success": True,
            "message": f"Subscription created successfully for {subscription_request.period.value} billing",
            "subscription_details": result
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create subscription: {str(e)}"
        )

@router.get("/subscription/status", response_model=SubscriptionResponse)
def get_subscription_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current subscription status and details
    """
    try:
        subscription_service = SubscriptionService()
        subscription_info = subscription_service.get_subscription_status(
            db=db,
            user_id=current_user.user_id
        )
        
        return SubscriptionResponse(**subscription_info)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/subscription/cancel")
def cancel_subscription(
    immediate: bool = False,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Cancel subscription (immediate or at end of current period)
    """
    try:
        subscription_service = SubscriptionService()
        result = subscription_service.cancel_subscription(
            db=db,
            user_id=current_user.user_id,
            immediate=immediate
        )
        
        if result.get("success"):
            message = "Subscription cancelled immediately" if immediate else "Subscription will be cancelled at the end of current period"
            return {
                "success": True,
                "message": message,
                "expires_at": result.get("expires_at")
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("error", "Failed to cancel subscription")
            )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/subscription/pricing")
def get_subscription_pricing():
    """
    Get pricing information for all subscription periods
    """
    return {
        "pricing": {
            "premium": {
                "monthly": {
                    "price": 29.99,
                    "currency": "USD", 
                    "period": "month",
                    "savings": None
                },
                "annually": {
                    "price": 305.91,
                    "currency": "USD",
                    "period": "year",
                    "savings": "15% off monthly rate"
                }
            },
            "vip": {
                "monthly": {
                    "price": 59.99,
                    "currency": "USD",
                    "period": "month", 
                    "savings": None
                },
                "annually": {
                    "price": 611.91,
                    "currency": "USD",
                    "period": "year",
                    "savings": "15% off monthly rate"
                }
            }
        },
        "features": {
            "premium": [
                "Unlimited daily swipes",
                "Up to 10 project cards per day",
                "Unlimited messages",
                "Basic AI recommendations",
                "Standard support"
            ],
            "vip": [
                "Everything in Premium",
                "Unlimited project cards",
                "Advanced AI recommendations",
                "Priority support",
                "Early access to new features",
                "Custom matching preferences"
            ]
        }
    }
