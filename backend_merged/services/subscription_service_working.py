"""
Subscription Management Service - Working Version
Handles weekly, monthly, and annual subscription billing using current models
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
import logging
from enum import Enum

from models.users import User
from models.user_membership import UserMembership, MembershipType
from models.payments import MembershipTransaction, PaymentStatus, PaymentMethod
from services.payment_service import TencentWeChatPayService
from dependencies.db import get_db

logger = logging.getLogger(__name__)

class SubscriptionPeriod(Enum):
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    ANNUALLY = "annually"

class SubscriptionStatus(Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    CANCELLED = "cancelled"
    SUSPENDED = "suspended"
    PENDING_RENEWAL = "pending_renewal"
    GRACE_PERIOD = "grace_period"

class SubscriptionService:
    def __init__(self):
        self.payment_service = TencentWeChatPayService()
        
    def create_subscription(
        self, 
        db: Session, 
        user_id: int, 
        membership_type: MembershipType,
        period: SubscriptionPeriod,
        payment_method: str = "wechat_pay"
    ) -> Dict[str, Any]:
        """
        Create a new subscription for a user
        """
        try:
            # Calculate subscription details
            amount, duration_days = self._calculate_subscription_details(membership_type, period)
            start_date = datetime.utcnow()
            end_date = start_date + timedelta(days=duration_days)
            next_billing_date = end_date
            
            # Get or create user membership record
            user_membership = db.query(UserMembership).filter(
                UserMembership.user_id == user_id
            ).first()
            
            if not user_membership:
                user_membership = UserMembership(
                    user_id=user_id,
                    membership_type=membership_type,
                    start_date=start_date,
                    end_date=end_date
                )
                db.add(user_membership)
            else:
                # Update existing membership
                user_membership.membership_type = membership_type
                user_membership.start_date = start_date
                user_membership.end_date = end_date
            
            # Add subscription metadata
            # subscription_metadata = {
            #     "subscription_period": period.value,
            #     "auto_renew": True,
            #     "next_billing_date": next_billing_date.isoformat(),
            #     "status": SubscriptionStatus.ACTIVE.value,
            #     "created_at": start_date.isoformat()
            # }
            
            # user_membership.metadata = subscription_metadata
            db.commit()
            db.refresh(user_membership)
            
            # Create initial payment transaction
            transaction = MembershipTransaction(
                user_id=user_id,
                amount=amount,
                payment_method=PaymentMethod(payment_method),
                status=PaymentStatus.PENDING,
                transaction_type="subscription_initial",
                metadata={
                    "subscription_period": period.value,
                    "membership_type": membership_type.value,
                    "next_billing_date": next_billing_date.isoformat()
                }
            )
            
            db.add(transaction)
            db.commit()
            db.refresh(transaction)
            
            logger.info(f"Created subscription for user {user_id}, period: {period}")
            
            return {
                "subscription_id": user_membership.id,
                "transaction_id": transaction.id,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "next_billing_date": next_billing_date.isoformat(),
                "amount": amount,
                "period": period.value,
                "status": SubscriptionStatus.ACTIVE.value
            }
            
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to create subscription: {str(e)}")
            raise Exception(f"Failed to create subscription: {str(e)}")
    
    def get_subscription_status(self, db: Session, user_id: int) -> Dict[str, Any]:
        """
        Get current subscription status for a user
        """
        try:
            user_membership = db.query(UserMembership).filter(
                UserMembership.user_id == user_id
            ).first()
            
            if not user_membership or not user_membership.is_paid:
                return {
                    "has_subscription": False,
                    "membership_level": MembershipType.FREE.value,
                    "is_paid": False
                }
            
            metadata = user_membership.metadata or {}
            
            # Check if subscription is expired
            is_expired = user_membership.end_date and user_membership.end_date < datetime.utcnow()
            
            return {
                "has_subscription": True,
                "membership_level": user_membership.membership_type.value,
                "is_paid": user_membership.is_paid,
                "expires_at": user_membership.end_date.isoformat() if user_membership.end_date else None,
                "subscription_period": metadata.get("subscription_period"),
                "subscription_status": metadata.get("status", "active"),
                "auto_renew": metadata.get("auto_renew", False),
                "next_billing_date": metadata.get("next_billing_date"),
                "is_expired": is_expired
            }
            
        except Exception as e:
            logger.error(f"Failed to get subscription status for user {user_id}: {str(e)}")
            return {"has_subscription": False, "status": "error", "error": str(e)}
    
    def cancel_subscription(
        self,
        db: Session,
        user_id: int,
        immediate: bool = False
    ) -> Dict[str, Any]:
        """
        Cancel a user's subscription
        """
        try:
            user_membership = db.query(UserMembership).filter(
                UserMembership.user_id == user_id
            ).first()
            
            if not user_membership or not user_membership.is_paid:
                return {"success": False, "error": "No active subscription found"}
            
            metadata = user_membership.metadata or {}
            
            if immediate:
                # Cancel immediately
                user_membership.membership_type = MembershipType.FREE
                user_membership.end_date = datetime.utcnow()
                metadata.update({
                    "status": SubscriptionStatus.CANCELLED.value,
                    "cancelled_at": datetime.utcnow().isoformat(),
                    "auto_renew": False
                })
            else:
                # Cancel at end of current period
                metadata.update({
                    "status": SubscriptionStatus.CANCELLED.value,
                    "cancelled_at": datetime.utcnow().isoformat(),
                    "auto_renew": False
                })
            
            user_membership.metadata = metadata
            db.commit()
            
            logger.info(f"Subscription cancelled for user {user_id}, immediate: {immediate}")
            
            return {
                "success": True,
                "cancelled_immediately": immediate,
                "expires_at": user_membership.end_date.isoformat() if user_membership.end_date else None
            }
            
        except Exception as e:
            logger.error(f"Error cancelling subscription: {str(e)}")
            db.rollback()
            return {"success": False, "error": str(e)}
    
    def pause_subscription(
        self,
        db: Session,
        user_id: int,
        pause_until: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Pause a user's subscription
        """
        try:
            user_membership = db.query(UserMembership).filter(
                UserMembership.user_id == user_id
            ).first()
            
            if not user_membership or not user_membership.is_paid:
                return {"success": False, "error": "No active subscription found"}
            
            metadata = user_membership.metadata or {}
            metadata.update({
                "status": SubscriptionStatus.SUSPENDED.value,
                "paused_at": datetime.utcnow().isoformat(),
                "pause_until": pause_until.isoformat() if pause_until else None
            })
            
            user_membership.metadata = metadata
            db.commit()
            
            logger.info(f"Subscription paused for user {user_id}")
            
            return {
                "success": True,
                "paused_until": pause_until.isoformat() if pause_until else None
            }
            
        except Exception as e:
            logger.error(f"Error pausing subscription: {str(e)}")
            db.rollback()
            return {"success": False, "error": str(e)}
    
    def _calculate_subscription_details(self, membership_type: MembershipType, period: SubscriptionPeriod) -> tuple:
        """Calculate subscription amount and duration"""
        base_prices = {
            MembershipType.PREMIUM: 29.99,
            MembershipType.PAID: 29.99,  # Same as premium for now
            MembershipType.FREE: 0.0
        }
        
        base_price = base_prices.get(membership_type, 29.99)
        
        if period == SubscriptionPeriod.WEEKLY:
            # Weekly price is approximately 1/4 of monthly price
            weekly_price = base_price * 0.25
            return weekly_price, 7
        elif period == SubscriptionPeriod.MONTHLY:
            return base_price, 30
        else:  # ANNUALLY
            annual_discount = 0.15  # 15% discount for annual
            annual_price = base_price * 12 * (1 - annual_discount)
            return annual_price, 365
