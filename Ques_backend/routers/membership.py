"""
Membership system router
Handles membership plans, subscriptions, and upgrades
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from typing import List, Optional
import logging
from datetime import datetime, timedelta

from dependencies.db import get_db
from dependencies.auth import get_current_user, get_current_active_user
from models.users import User
from models.memberships import Membership, MembershipPlan
from models.payments import Payment
from services.auth_service import AuthService
from schemas.memberships import (
    MembershipResponse, MembershipPlanResponse,
    MembershipUpgradeRequest, MembershipCreateRequest
)

router = APIRouter(tags=["membership"])
security = HTTPBearer()
logger = logging.getLogger(__name__)

# Initialize services
auth_service = AuthService()

@router.get("/membership/current", response_model=MembershipResponse)
async def get_current_membership(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get current user's membership status
    """
    try:
        membership = db.query(Membership).filter(
            Membership.user_id == current_user.user_id
        ).first()
        
        if not membership:
            # Create default free membership if none exists
            membership = Membership(
                user_id=current_user.user_id,
                type='free',
                start_date=datetime.utcnow(),
                is_active=True
            )
            db.add(membership)
            db.commit()
            db.refresh(membership)
        
        return MembershipResponse(
            membership_id=membership.membership_id,
            user_id=membership.user_id,
            type=membership.type,
            start_date=membership.start_date,
            end_date=membership.end_date,
            is_active=membership.is_active,
            auto_renew=membership.auto_renew,
            billing_cycle=membership.billing_cycle,
            price=float(membership.price) if membership.price else None,
            currency=membership.currency,
            created_at=membership.created_at,
            updated_at=membership.updated_at
        )
        
    except Exception as e:
        logger.error(f"Error getting membership: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get membership status"
        )

@router.get("/membership/plans", response_model=List[MembershipPlanResponse])
async def get_membership_plans(
    db: Session = Depends(get_db)
):
    """
    Get all available membership plans
    """
    try:
        plans = db.query(MembershipPlan).filter(
            MembershipPlan.is_active == True
        ).order_by(MembershipPlan.price_monthly).all()
        
        if not plans:
            # Create default plans if none exist
            default_plans = [
                MembershipPlan(
                    name="Free Plan",
                    type="free",
                    price_monthly=0.00,
                    price_annual=0.00,
                    description="Basic features for getting started",
                    features='{"max_swipes_daily": 10, "max_matches_monthly": 5, "video_calls_enabled": false}',
                    max_swipes_daily=10,
                    max_matches_monthly=5,
                    video_calls_enabled=False,
                    priority_support=False,
                    is_active=True
                ),
                MembershipPlan(
                    name="Premium Plan",
                    type="premium",
                    price_monthly=29.99,
                    price_annual=299.99,
                    description="Enhanced features for serious networking",
                    features='{"max_swipes_daily": 100, "max_matches_monthly": 50, "video_calls_enabled": true}',
                    max_swipes_daily=100,
                    max_matches_monthly=50,
                    video_calls_enabled=True,
                    priority_support=True,
                    is_active=True
                ),
                MembershipPlan(
                    name="VIP Plan",
                    type="vip",
                    price_monthly=99.99,
                    price_annual=999.99,
                    description="Unlimited access and premium features",
                    features='{"max_swipes_daily": -1, "max_matches_monthly": -1, "video_calls_enabled": true}',
                    max_swipes_daily=-1,  # Unlimited
                    max_matches_monthly=-1,  # Unlimited
                    video_calls_enabled=True,
                    priority_support=True,
                    is_active=True
                )
            ]
            
            for plan in default_plans:
                db.add(plan)
            db.commit()
            
            plans = default_plans
        
        return [
            MembershipPlanResponse(
                plan_id=plan.plan_id,
                name=plan.name,
                type=plan.type,
                price_monthly=float(plan.price_monthly) if plan.price_monthly else None,
                price_annual=float(plan.price_annual) if plan.price_annual else None,
                currency=plan.currency,
                description=plan.description,
                features=plan.features,
                max_swipes_daily=plan.max_swipes_daily,
                max_matches_monthly=plan.max_matches_monthly,
                video_calls_enabled=plan.video_calls_enabled,
                priority_support=plan.priority_support,
                is_active=plan.is_active,
                created_at=plan.created_at,
                updated_at=plan.updated_at
            ) for plan in plans
        ]
        
    except Exception as e:
        logger.error(f"Error getting membership plans: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get membership plans"
        )

@router.post("/membership/upgrade", response_model=MembershipResponse)
async def upgrade_membership(
    upgrade_request: MembershipUpgradeRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Upgrade user's membership plan
    """
    try:
        # Get current membership
        current_membership = db.query(Membership).filter(
            Membership.user_id == current_user.user_id
        ).first()
        
        if not current_membership:
            current_membership = Membership(
                user_id=current_user.user_id,
                type='free',
                start_date=datetime.utcnow(),
                is_active=True
            )
            db.add(current_membership)
            db.commit()
            db.refresh(current_membership)
        
        # Get target plan
        target_plan = db.query(MembershipPlan).filter(
            MembershipPlan.plan_id == upgrade_request.plan_id
        ).first()
        
        if not target_plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Membership plan not found"
            )
        
        # Calculate end date based on billing cycle
        if upgrade_request.billing_cycle == "monthly":
            end_date = datetime.utcnow() + timedelta(days=30)
            price = target_plan.price_monthly
        elif upgrade_request.billing_cycle == "annual":
            end_date = datetime.utcnow() + timedelta(days=365)
            price = target_plan.price_annual
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid billing cycle. Must be 'monthly' or 'annual'"
            )
        
        # Update membership
        current_membership.type = target_plan.type
        current_membership.end_date = end_date
        current_membership.billing_cycle = upgrade_request.billing_cycle
        current_membership.price = price
        current_membership.auto_renew = upgrade_request.auto_renew
        current_membership.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(current_membership)
        
        logger.info(f"Membership upgraded for user {current_user.user_id} to {target_plan.type}")
        
        return MembershipResponse(
            membership_id=current_membership.membership_id,
            user_id=current_membership.user_id,
            type=current_membership.type,
            start_date=current_membership.start_date,
            end_date=current_membership.end_date,
            is_active=current_membership.is_active,
            auto_renew=current_membership.auto_renew,
            billing_cycle=current_membership.billing_cycle,
            price=float(current_membership.price) if current_membership.price else None,
            currency=current_membership.currency,
            created_at=current_membership.created_at,
            updated_at=current_membership.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error upgrading membership: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upgrade membership"
        )

@router.post("/membership/cancel")
async def cancel_membership(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Cancel current membership (downgrade to free)
    """
    try:
        membership = db.query(Membership).filter(
            Membership.user_id == current_user.user_id
        ).first()
        
        if not membership:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No membership found"
            )
        
        if membership.type == 'free':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Already on free plan"
            )
        
        # Downgrade to free
        membership.type = 'free'
        membership.end_date = None
        membership.billing_cycle = None
        membership.price = 0.00
        membership.auto_renew = False
        membership.updated_at = datetime.utcnow()
        
        db.commit()
        
        logger.info(f"Membership cancelled for user {current_user.user_id}")
        
        return {"message": "Membership cancelled successfully. You've been downgraded to the free plan."}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cancelling membership: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to cancel membership"
        )

@router.get("/membership/benefits")
async def get_membership_benefits(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get current membership benefits and usage
    """
    try:
        membership = db.query(Membership).filter(
            Membership.user_id == current_user.user_id
        ).first()
        
        if not membership:
            membership_type = 'free'
        else:
            membership_type = membership.type
        
        # Define benefits based on membership type
        benefits = {
            'free': {
                'max_swipes_daily': 10,
                'max_matches_monthly': 5,
                'video_calls_enabled': False,
                'priority_support': False,
                'unlimited_search': False,
                'advanced_filters': False
            },
            'premium': {
                'max_swipes_daily': 100,
                'max_matches_monthly': 50,
                'video_calls_enabled': True,
                'priority_support': True,
                'unlimited_search': True,
                'advanced_filters': True
            },
            'vip': {
                'max_swipes_daily': -1,  # Unlimited
                'max_matches_monthly': -1,  # Unlimited
                'video_calls_enabled': True,
                'priority_support': True,
                'unlimited_search': True,
                'advanced_filters': True
            }
        }
        
        current_benefits = benefits.get(membership_type, benefits['free'])
        
        # TODO: Add actual usage tracking from database
        current_usage = {
            'swipes_used_today': 5,  # Placeholder - implement actual tracking
            'matches_this_month': 2,  # Placeholder - implement actual tracking
        }
        
        return {
            'membership_type': membership_type,
            'benefits': current_benefits,
            'usage': current_usage,
            'expires_at': membership.end_date if membership else None
        }
        
    except Exception as e:
        logger.error(f"Error getting membership benefits: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get membership benefits"
        )
