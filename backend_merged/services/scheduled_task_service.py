"""
Scheduled Task Service - Handles automatic recurring subscription payments

This service should be run as a scheduled task (cron job) to process:
- Subscription renewals
- Failed payment retries
- Subscription expiration handling
- Grace period management
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any
from sqlalchemy.orm import Session

from services.subscription_service import SubscriptionService
from services.payment_service import TencentWeChatPayService
from dependencies.database import get_db
from models.user_membership import UserMembership
from models.payments import MembershipTransaction, PaymentStatus

logger = logging.getLogger(__name__)

class ScheduledTaskService:
    def __init__(self):
        self.subscription_service = SubscriptionService()
        self.payment_service = PaymentService()
        self.notification_service = NotificationService()
    
    async def run_daily_tasks(self) -> Dict[str, Any]:
        """
        Run all daily scheduled tasks
        This should be called once per day
        """
        logger.info("Starting daily scheduled tasks")
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "renewals_processed": 0,
            "failed_payments_handled": 0,
            "grace_periods_started": 0,
            "subscriptions_expired": 0,
            "errors": []
        }
        
        try:
            # Get database session
            db = next(get_db())
            
            # 1. Process subscription renewals
            renewal_results = await self._process_subscription_renewals(db)
            results["renewals_processed"] = renewal_results["processed"]
            results["errors"].extend(renewal_results.get("errors", []))
            
            # 2. Handle failed payments
            failed_payment_results = await self._handle_failed_payments(db)
            results["failed_payments_handled"] = failed_payment_results["handled"]
            results["errors"].extend(failed_payment_results.get("errors", []))
            
            # 3. Start grace periods for overdue subscriptions
            grace_period_results = await self._start_grace_periods(db)
            results["grace_periods_started"] = grace_period_results["started"]
            results["errors"].extend(grace_period_results.get("errors", []))
            
            # 4. Expire subscriptions past grace period
            expiration_results = await self._expire_subscriptions(db)
            results["subscriptions_expired"] = expiration_results["expired"]
            results["errors"].extend(expiration_results.get("errors", []))
            
            logger.info(f"Daily tasks completed: {results}")
            
        except Exception as e:
            error_msg = f"Error in daily tasks: {str(e)}"
            logger.error(error_msg)
            results["errors"].append(error_msg)
        
        return results
    
    async def _process_subscription_renewals(self, db: Session) -> Dict[str, Any]:
        """
        Process subscriptions that are due for renewal
        """
        try:
            # Get subscriptions due for renewal (within next 24 hours)
            renewal_due_date = datetime.now() + timedelta(hours=24)
            
            due_renewals = db.query(Membership).filter(
                Membership.auto_renew == True,
                Membership.status == "active",
                Membership.next_billing_date <= renewal_due_date,
                Membership.next_billing_date > datetime.now() - timedelta(hours=1)  # Not already processed
            ).all()
            
            processed = 0
            errors = []
            
            for membership in due_renewals:
                try:
                    # Process automatic renewal
                    result = self.subscription_service.process_automatic_renewal(
                        db, membership.id
                    )
                    
                    if result.get("status") == "initiated":
                        processed += 1
                        logger.info(f"Renewal initiated for subscription {membership.id}")
                    elif result.get("status") == "failed":
                        errors.append(f"Failed to renew subscription {membership.id}: {result.get('error')}")
                    
                except Exception as e:
                    error_msg = f"Error processing renewal for subscription {membership.id}: {str(e)}"
                    logger.error(error_msg)
                    errors.append(error_msg)
            
            return {"processed": processed, "errors": errors}
            
        except Exception as e:
            logger.error(f"Error in subscription renewal processing: {str(e)}")
            return {"processed": 0, "errors": [str(e)]}
    
    async def _handle_failed_payments(self, db: Session) -> Dict[str, Any]:
        """
        Handle subscriptions with failed payment attempts
        """
        try:
            # Find memberships with failed payments in the last 24 hours
            failed_payments = db.query(Payment).filter(
                Payment.status == PaymentStatus.FAILED,
                Payment.created_at >= datetime.now() - timedelta(hours=24),
                Payment.metadata.contains("subscription_id")
            ).all()
            
            handled = 0
            errors = []
            
            for payment in failed_payments:
                try:
                    subscription_id = payment.metadata.get("subscription_id")
                    if not subscription_id:
                        continue
                    
                    membership = db.query(Membership).filter(
                        Membership.id == subscription_id
                    ).first()
                    
                    if not membership:
                        continue
                    
                    # Increment failed attempts
                    failed_attempts = getattr(membership, 'failed_renewal_attempts', 0) + 1
                    membership.failed_renewal_attempts = failed_attempts
                    
                    if failed_attempts >= 3:
                        # Start grace period after 3 failed attempts
                        membership.status = "grace_period"
                        membership.grace_period_start = datetime.now()
                        membership.grace_period_end = datetime.now() + timedelta(days=7)
                        
                        # Send grace period notification
                        self.notification_service.send_grace_period_notification(
                            user_id=membership.user_id,
                            subscription_id=membership.id,
                            grace_end=membership.grace_period_end
                        )
                        
                        logger.warning(f"Subscription {subscription_id} moved to grace period")
                    else:
                        # Retry payment in 24 hours
                        membership.next_billing_date = datetime.now() + timedelta(hours=24)
                        
                        logger.info(f"Scheduled retry for subscription {subscription_id}, attempt {failed_attempts}")
                    
                    db.commit()
                    handled += 1
                    
                except Exception as e:
                    error_msg = f"Error handling failed payment for subscription {subscription_id}: {str(e)}"
                    logger.error(error_msg)
                    errors.append(error_msg)
                    db.rollback()
            
            return {"handled": handled, "errors": errors}
            
        except Exception as e:
            logger.error(f"Error in failed payment handling: {str(e)}")
            return {"handled": 0, "errors": [str(e)]}
    
    async def _start_grace_periods(self, db: Session) -> Dict[str, Any]:
        """
        Start grace periods for overdue subscriptions
        """
        try:
            # Find subscriptions that are overdue but not in grace period
            overdue_subscriptions = db.query(Membership).filter(
                Membership.status == "active",
                Membership.end_date < datetime.now(),
                Membership.auto_renew == True
            ).all()
            
            started = 0
            errors = []
            
            for membership in overdue_subscriptions:
                try:
                    # Check if payment failed recently
                    recent_failed_payment = db.query(Payment).filter(
                        Payment.metadata.contains(f'"subscription_id": {membership.id}'),
                        Payment.status == PaymentStatus.FAILED,
                        Payment.created_at >= datetime.now() - timedelta(days=3)
                    ).first()
                    
                    if recent_failed_payment:
                        # Start grace period
                        membership.status = "grace_period"
                        membership.grace_period_start = datetime.now()
                        membership.grace_period_end = datetime.now() + timedelta(days=7)
                        
                        # Send notification
                        self.notification_service.send_grace_period_notification(
                            user_id=membership.user_id,
                            subscription_id=membership.id,
                            grace_end=membership.grace_period_end
                        )
                        
                        db.commit()
                        started += 1
                        
                        logger.info(f"Grace period started for subscription {membership.id}")
                    
                except Exception as e:
                    error_msg = f"Error starting grace period for subscription {membership.id}: {str(e)}"
                    logger.error(error_msg)
                    errors.append(error_msg)
                    db.rollback()
            
            return {"started": started, "errors": errors}
            
        except Exception as e:
            logger.error(f"Error in grace period handling: {str(e)}")
            return {"started": 0, "errors": [str(e)]}
    
    async def _expire_subscriptions(self, db: Session) -> Dict[str, Any]:
        """
        Expire subscriptions that are past their grace period
        """
        try:
            # Find subscriptions past grace period
            expired_subscriptions = db.query(Membership).filter(
                Membership.status == "grace_period",
                Membership.grace_period_end < datetime.now()
            ).all()
            
            expired = 0
            errors = []
            
            for membership in expired_subscriptions:
                try:
                    # Expire the subscription
                    membership.status = "expired"
                    membership.auto_renew = False
                    membership.expired_date = datetime.now()
                    
                    # Send expiration notification
                    self.notification_service.send_subscription_expired_notification(
                        user_id=membership.user_id,
                        subscription_id=membership.id
                    )
                    
                    db.commit()
                    expired += 1
                    
                    logger.info(f"Subscription {membership.id} expired")
                    
                except Exception as e:
                    error_msg = f"Error expiring subscription {membership.id}: {str(e)}"
                    logger.error(error_msg)
                    errors.append(error_msg)
                    db.rollback()
            
            return {"expired": expired, "errors": errors}
            
        except Exception as e:
            logger.error(f"Error in subscription expiration: {str(e)}")
            return {"expired": 0, "errors": [str(e)]}

# CLI function to run the scheduled tasks
async def run_scheduled_tasks():
    """
    CLI function to run scheduled tasks
    Usage: python -m services.scheduled_task_service
    """
    service = ScheduledTaskService()
    results = await service.run_daily_tasks()
    print(f"Scheduled tasks completed: {results}")

if __name__ == "__main__":
    asyncio.run(run_scheduled_tasks())
