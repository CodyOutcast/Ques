"""
Subscription Management Service for Monthly/Annual Memberships

This service handles:
- Subscription creation and management
- Automatic renewal scheduling
- Payment failure handling
- Subscription status tracking
- Grace period management
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
import logging
from enum import Enum

from models.users import User
from models.user_membership import UserMembership, MembershipLevel
from models.payments import MembershipTransaction, PaymentStatus, PaymentMethod
from services.payment_service import TencentWeChatPayService
from services.notification_service import NotificationService
from config.database import get_db

logger = logging.getLogger(__name__)

class SubscriptionStatus(Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    CANCELLED = "cancelled"
    SUSPENDED = "suspended"
    PENDING_RENEWAL = "pending_renewal"
    GRACE_PERIOD = "grace_period"

class SubscriptionPeriod(Enum):
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    ANNUALLY = "annually"

class SubscriptionService:
    def __init__(self):
        self.payment_service = PaymentService()
        self.notification_service = NotificationService()
        
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
            start_date = datetime.now()
            end_date = start_date + timedelta(days=duration_days)
            next_billing_date = end_date
            
            # Create membership record
            membership = Membership(
                user_id=user_id,
                type=membership_type,
                start_date=start_date,
                end_date=end_date,
                auto_renew=True,
                subscription_period=period.value,
                next_billing_date=next_billing_date,
                status=SubscriptionStatus.ACTIVE.value
            )
            
            db.add(membership)
            db.commit()
            db.refresh(membership)
            
            # Create initial payment
            payment_result = self.payment_service.create_payment_order(
                db=db,
                user_id=user_id,
                amount=amount,
                payment_method=payment_method,
                description=f"{membership_type.value} subscription - {period.value}",
                metadata={
                    "subscription_id": membership.id,
                    "subscription_type": "initial",
                    "period": period.value
                }
            )
            
            logger.info(f"Created subscription {membership.id} for user {user_id}")
            
            return {
                "subscription_id": membership.id,
                "payment_info": payment_result,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "next_billing_date": next_billing_date.isoformat(),
                "amount": amount,
                "status": SubscriptionStatus.ACTIVE.value
            }
            
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to create subscription: {str(e)}")
            raise Exception(f"Failed to create subscription: {str(e)}")
    
    def check_renewals_due(self, db: Session) -> List[Dict[str, Any]]:
        """
        Check for subscriptions that need renewal (within 3 days)
        """
        try:
            renewal_date = datetime.now() + timedelta(days=3)
            
            memberships = db.query(Membership).filter(
                and_(
                    Membership.auto_renew == True,
                    Membership.status == SubscriptionStatus.ACTIVE.value,
                    Membership.next_billing_date <= renewal_date
                )
            ).all()
            
            renewal_list = []
            for membership in memberships:
                renewal_list.append({
                    "subscription_id": membership.id,
                    "user_id": membership.user_id,
                    "membership_type": membership.type,
                    "next_billing_date": membership.next_billing_date.isoformat(),
                    "amount": self._calculate_renewal_amount(membership),
                    "period": membership.subscription_period
                })
            
            logger.info(f"Found {len(renewal_list)} subscriptions due for renewal")
            return renewal_list
            
        except Exception as e:
            logger.error(f"Failed to check renewals: {str(e)}")
            return []
    
    def process_automatic_renewal(self, db: Session, subscription_id: int) -> Dict[str, Any]:
        """
        Process automatic renewal for a subscription
        """
        try:
            membership = db.query(Membership).filter(Membership.id == subscription_id).first()
            if not membership:
                raise Exception("Subscription not found")
            
            if not membership.auto_renew:
                return {"status": "skipped", "reason": "Auto-renew disabled"}
            
            # Calculate renewal details
            amount = self._calculate_renewal_amount(membership)
            period = SubscriptionPeriod(membership.subscription_period)
            
            # Create renewal payment
            payment_result = self.payment_service.create_payment_order(
                db=db,
                user_id=membership.user_id,
                amount=amount,
                payment_method="wechat_pay",  # Default to WeChat Pay for renewals
                description=f"Subscription renewal - {membership.type.value}",
                metadata={
                    "subscription_id": subscription_id,
                    "subscription_type": "renewal",
                    "period": membership.subscription_period
                }
            )
            
            # Update subscription status
            membership.status = SubscriptionStatus.PENDING_RENEWAL.value
            membership.last_renewal_attempt = datetime.now()
            
            db.commit()
            
            # Send renewal notification
            self.notification_service.send_renewal_notification(
                user_id=membership.user_id,
                subscription_id=subscription_id,
                amount=amount,
                payment_url=payment_result.get("payment_url")
            )
            
            logger.info(f"Initiated renewal for subscription {subscription_id}")
            
            return {
                "status": "initiated",
                "payment_info": payment_result,
                "amount": amount,
                "subscription_id": subscription_id
            }
            
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to process renewal for subscription {subscription_id}: {str(e)}")
            return {"status": "failed", "error": str(e)}
    
    def handle_successful_payment(self, db: Session, payment_id: str) -> Dict[str, Any]:
        """
        Handle successful payment and update subscription
        """
        try:
            # Get payment details
            payment = db.query(Payment).filter(Payment.id == payment_id).first()
            if not payment:
                raise Exception("Payment not found")
            
            # Get subscription from payment metadata
            subscription_id = payment.metadata.get("subscription_id")
            if not subscription_id:
                return {"status": "skipped", "reason": "Not a subscription payment"}
            
            membership = db.query(Membership).filter(Membership.id == subscription_id).first()
            if not membership:
                raise Exception("Subscription not found")
            
            # Update subscription based on payment type
            payment_type = payment.metadata.get("subscription_type", "initial")
            
            if payment_type == "initial":
                # Initial subscription payment
                membership.status = SubscriptionStatus.ACTIVE.value
                membership.payment_status = "paid"
                
            elif payment_type == "renewal":
                # Renewal payment
                period_days = self._get_period_days(membership.subscription_period)
                
                # Extend subscription
                new_end_date = membership.end_date + timedelta(days=period_days)
                membership.end_date = new_end_date
                membership.next_billing_date = new_end_date
                membership.status = SubscriptionStatus.ACTIVE.value
                membership.payment_status = "paid"
                membership.last_successful_renewal = datetime.now()
                
                # Reset failed attempts
                membership.failed_renewal_attempts = 0
            
            db.commit()
            
            # Send confirmation notification
            self.notification_service.send_payment_confirmation(
                user_id=membership.user_id,
                subscription_id=subscription_id,
                payment_type=payment_type,
                amount=payment.amount,
                end_date=membership.end_date
            )
            
            logger.info(f"Successfully processed payment for subscription {subscription_id}")
            
            return {
                "status": "success",
                "subscription_id": subscription_id,
                "new_end_date": membership.end_date.isoformat()
            }
            
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to handle successful payment {payment_id}: {str(e)}")
            return {"status": "failed", "error": str(e)}
    
    def handle_failed_payment(self, db: Session, payment_id: str) -> Dict[str, Any]:
        """
        Handle failed payment and update subscription
        """
        try:
            payment = db.query(Payment).filter(Payment.id == payment_id).first()
            if not payment:
                raise Exception("Payment not found")
            
            subscription_id = payment.metadata.get("subscription_id")
            if not subscription_id:
                return {"status": "skipped", "reason": "Not a subscription payment"}
            
            membership = db.query(Membership).filter(Membership.id == subscription_id).first()
            if not membership:
                raise Exception("Subscription not found")
            
            # Increment failed attempts
            membership.failed_renewal_attempts = (membership.failed_renewal_attempts or 0) + 1
            membership.last_failed_renewal = datetime.now()
            
            # Determine action based on failed attempts
            if membership.failed_renewal_attempts >= 3:
                # After 3 failed attempts, put subscription in grace period
                membership.status = SubscriptionStatus.GRACE_PERIOD.value
                grace_end = datetime.now() + timedelta(days=7)  # 7-day grace period
                membership.grace_period_end = grace_end
                
                # Send grace period notification
                self.notification_service.send_grace_period_notification(
                    user_id=membership.user_id,
                    subscription_id=subscription_id,
                    grace_end=grace_end
                )
                
            else:
                # Schedule retry
                retry_delay = membership.failed_renewal_attempts * 24  # 24, 48, 72 hours
                membership.next_billing_date = datetime.now() + timedelta(hours=retry_delay)
                
                # Send retry notification
                self.notification_service.send_payment_retry_notification(
                    user_id=membership.user_id,
                    subscription_id=subscription_id,
                    retry_date=membership.next_billing_date,
                    attempt=membership.failed_renewal_attempts
                )
            
            db.commit()
            
            logger.info(f"Handled failed payment for subscription {subscription_id}, attempt {membership.failed_renewal_attempts}")
            
            return {
                "status": "handled",
                "subscription_id": subscription_id,
                "failed_attempts": membership.failed_renewal_attempts,
                "action": "grace_period" if membership.failed_renewal_attempts >= 3 else "retry_scheduled"
            }
            
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to handle failed payment {payment_id}: {str(e)}")
            return {"status": "failed", "error": str(e)}
    
    def cancel_subscription(self, db: Session, subscription_id: int, user_id: int, immediate: bool = False) -> Dict[str, Any]:
        """
        Cancel a subscription
        """
        try:
            membership = db.query(Membership).filter(
                and_(
                    Membership.id == subscription_id,
                    Membership.user_id == user_id
                )
            ).first()
            
            if not membership:
                raise Exception("Subscription not found")
            
            if immediate:
                # Immediate cancellation
                membership.status = SubscriptionStatus.CANCELLED.value
                membership.end_date = datetime.now()
            else:
                # Cancel at end of current period
                membership.auto_renew = False
                membership.cancelled_at = datetime.now()
            
            db.commit()
            
            # Send cancellation confirmation
            self.notification_service.send_cancellation_confirmation(
                user_id=user_id,
                subscription_id=subscription_id,
                immediate=immediate,
                end_date=membership.end_date
            )
            
            logger.info(f"Cancelled subscription {subscription_id} for user {user_id}")
            
            return {
                "status": "cancelled",
                "subscription_id": subscription_id,
                "end_date": membership.end_date.isoformat(),
                "immediate": immediate
            }
            
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to cancel subscription {subscription_id}: {str(e)}")
            raise Exception(f"Failed to cancel subscription: {str(e)}")
    
    def check_expired_subscriptions(self, db: Session) -> List[Dict[str, Any]]:
        """
        Check for expired subscriptions and update their status
        """
        try:
            now = datetime.now()
            
            # Find expired active subscriptions
            expired_memberships = db.query(Membership).filter(
                and_(
                    Membership.end_date < now,
                    Membership.status.in_([
                        SubscriptionStatus.ACTIVE.value,
                        SubscriptionStatus.GRACE_PERIOD.value
                    ])
                )
            ).all()
            
            expired_list = []
            for membership in expired_memberships:
                # Check if grace period has also expired
                if (membership.status == SubscriptionStatus.GRACE_PERIOD.value and 
                    membership.grace_period_end and 
                    membership.grace_period_end < now):
                    
                    # Grace period expired, cancel subscription
                    membership.status = SubscriptionStatus.EXPIRED.value
                    membership.auto_renew = False
                    
                    # Send expiration notification
                    self.notification_service.send_subscription_expired_notification(
                        user_id=membership.user_id,
                        subscription_id=membership.id
                    )
                    
                    expired_list.append({
                        "subscription_id": membership.id,
                        "user_id": membership.user_id,
                        "action": "expired",
                        "end_date": membership.end_date.isoformat()
                    })
                
                elif membership.status == SubscriptionStatus.ACTIVE.value:
                    # Recently expired, send warning
                    self.notification_service.send_subscription_expiring_notification(
                        user_id=membership.user_id,
                        subscription_id=membership.id,
                        end_date=membership.end_date
                    )
                    
                    expired_list.append({
                        "subscription_id": membership.id,
                        "user_id": membership.user_id,
                        "action": "expiring_warning",
                        "end_date": membership.end_date.isoformat()
                    })
            
            db.commit()
            
            logger.info(f"Processed {len(expired_list)} expired subscriptions")
            return expired_list
            
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to check expired subscriptions: {str(e)}")
            return []
    
    def get_subscription_status(self, db: Session, user_id: int) -> Dict[str, Any]:
        """
        Get current subscription status for a user
        """
        try:
            membership = db.query(Membership).filter(
                and_(
                    Membership.user_id == user_id,
                    Membership.status.in_([
                        SubscriptionStatus.ACTIVE.value,
                        SubscriptionStatus.PENDING_RENEWAL.value,
                        SubscriptionStatus.GRACE_PERIOD.value
                    ])
                )
            ).order_by(Membership.end_date.desc()).first()
            
            if not membership:
                return {
                    "has_subscription": False,
                    "status": "none"
                }
            
            days_remaining = (membership.end_date - datetime.now()).days
            
            return {
                "has_subscription": True,
                "subscription_id": membership.id,
                "membership_type": membership.type.value,
                "status": membership.status,
                "start_date": membership.start_date.isoformat(),
                "end_date": membership.end_date.isoformat(),
                "days_remaining": max(0, days_remaining),
                "auto_renew": membership.auto_renew,
                "subscription_period": membership.subscription_period,
                "next_billing_date": membership.next_billing_date.isoformat() if membership.next_billing_date else None
            }
            
        except Exception as e:
            logger.error(f"Failed to get subscription status for user {user_id}: {str(e)}")
            return {"has_subscription": False, "status": "error", "error": str(e)}
    
    def _calculate_subscription_details(self, membership_type: MembershipType, period: SubscriptionPeriod) -> tuple:
        """Calculate subscription amount and duration"""
        base_prices = {
            MembershipType.STANDARD: 29.99,
            MembershipType.PREMIUM: 59.99,
            MembershipType.VIP: 99.99
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
    
    def _calculate_renewal_amount(self, membership: Membership) -> float:
        """Calculate renewal amount for existing subscription"""
        period = SubscriptionPeriod(membership.subscription_period)
        amount, _ = self._calculate_subscription_details(membership.type, period)
        return amount
    
    def _get_period_days(self, period: str) -> int:
        """Get number of days for subscription period"""
        if period == SubscriptionPeriod.WEEKLY.value:
            return 7
        elif period == SubscriptionPeriod.MONTHLY.value:
            return 30
        else:  # ANNUALLY
            return 365


# Notification Service for subscription events
class NotificationService:
    def send_renewal_notification(self, user_id: int, subscription_id: int, amount: float, payment_url: str):
        """Send subscription renewal notification"""
        # Implementation would integrate with email/SMS service
        logger.info(f"Sending renewal notification to user {user_id}")
    
    def send_payment_confirmation(self, user_id: int, subscription_id: int, payment_type: str, amount: float, end_date: datetime):
        """Send payment confirmation notification"""
        logger.info(f"Sending payment confirmation to user {user_id}")
    
    def send_grace_period_notification(self, user_id: int, subscription_id: int, grace_end: datetime):
        """Send grace period notification"""
        logger.info(f"Sending grace period notification to user {user_id}")
    
    def send_payment_retry_notification(self, user_id: int, subscription_id: int, retry_date: datetime, attempt: int):
        """Send payment retry notification"""
        logger.info(f"Sending payment retry notification to user {user_id}")
    
    def send_cancellation_confirmation(self, user_id: int, subscription_id: int, immediate: bool, end_date: datetime):
        """Send cancellation confirmation"""
        logger.info(f"Sending cancellation confirmation to user {user_id}")
    
    def send_subscription_expired_notification(self, user_id: int, subscription_id: int):
        """Send subscription expired notification"""
        logger.info(f"Sending expiration notification to user {user_id}")
    
    def send_subscription_expiring_notification(self, user_id: int, subscription_id: int, end_date: datetime):
        """Send subscription expiring notification"""
        logger.info(f"Sending expiring warning to user {user_id}")
