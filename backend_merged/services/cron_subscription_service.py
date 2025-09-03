"""
Cron Job Service - Handles automatic recurring subscription payments

This script should be run as a scheduled task (cron job) to process:
- Monthly subscription renewals (run daily) 
- Annual subscription renewals (run daily)
- Failed payment handling

Usage:
1. Set up a cron job to run this script daily:
   0 9 * * * cd /path/to/project && python -m services.cron_subscription_service

2. Or run manually: python services/cron_subscription_service.py
"""

import sys
import os
import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Import our models and services
from models.user_membership import UserMembership, MembershipLevel
from models.payments import MembershipTransaction, PaymentStatus, PaymentMethod
from models.users import User
from services.payment_service import TencentWeChatPayService
from services.alipay_service import AlipayService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/subscription_cron.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SubscriptionCronService:
    def __init__(self):
        self.wechat_service = TencentWeChatPayService()
        self.alipay_service = AlipayService()
        
        # Set up database connection
        DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./test.db')
        self.engine = create_engine(DATABASE_URL)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
    
    def get_db(self) -> Session:
        """Get database session"""
        db = self.SessionLocal()
        try:
            return db
        except Exception:
            db.close()
            raise
    
    async def run_daily_subscription_check(self) -> Dict[str, Any]:
        """
        Main function to run daily subscription checks
        """
        logger.info("Starting daily subscription renewal check")
        
        results = {
            "timestamp": datetime.utcnow().isoformat(),
            "checked": 0,
            "renewed": 0,
            "failed": 0,
            "grace_period": 0,
            "expired": 0,
            "errors": []
        }
        
        db = self.get_db()
        try:
            # Get all active subscriptions that might need renewal
            subscriptions_to_check = self._get_subscriptions_due_for_renewal(db)
            results["checked"] = len(subscriptions_to_check)
            
            for subscription in subscriptions_to_check:
                try:
                    result = await self._process_subscription_renewal(db, subscription)
                    
                    if result["status"] == "renewed":
                        results["renewed"] += 1
                    elif result["status"] == "failed":
                        results["failed"] += 1
                    elif result["status"] == "grace_period":
                        results["grace_period"] += 1
                    elif result["status"] == "expired":
                        results["expired"] += 1
                        
                except Exception as e:
                    error_msg = f"Error processing subscription for user {subscription.user_id}: {str(e)}"
                    logger.error(error_msg)
                    results["errors"].append(error_msg)
                    results["failed"] += 1
            
            logger.info(f"Daily subscription check completed: {results}")
            
        except Exception as e:
            error_msg = f"Error in daily subscription check: {str(e)}"
            logger.error(error_msg)
            results["errors"].append(error_msg)
        
        finally:
            db.close()
        
        return results
    
    def _get_subscriptions_due_for_renewal(self, db: Session) -> List[UserMembership]:
        """
        Get subscriptions that are due for renewal (expired or expiring within 24 hours)
        """
        try:
            # Check for memberships that:
            # 1. Are premium/VIP (not free)
            # 2. Have expired or expire within 24 hours
            # 3. Have auto-renewal enabled in metadata
            
            cutoff_date = datetime.utcnow() + timedelta(hours=24)
            
            subscriptions = db.query(UserMembership).filter(
                UserMembership.membership_level.in_([MembershipLevel.PREMIUM, MembershipLevel.VIP]),
                UserMembership.expires_at <= cutoff_date
            ).all()
            
            # Filter for those with auto-renewal enabled
            auto_renew_subscriptions = []
            for subscription in subscriptions:
                metadata = subscription.metadata or {}
                if metadata.get("auto_renew", False):
                    auto_renew_subscriptions.append(subscription)
            
            logger.info(f"Found {len(auto_renew_subscriptions)} subscriptions due for renewal")
            return auto_renew_subscriptions
            
        except Exception as e:
            logger.error(f"Error getting subscriptions due for renewal: {str(e)}")
            return []
    
    async def _process_subscription_renewal(self, db: Session, subscription: UserMembership) -> Dict[str, Any]:
        """
        Process renewal for a single subscription
        """
        try:
            user_id = subscription.user_id
            metadata = subscription.metadata or {}
            
            # Check if subscription is already expired and in grace period
            if subscription.expires_at < datetime.utcnow():
                grace_period_start = metadata.get("grace_period_start")
                
                if grace_period_start:
                    # Check if grace period has ended (7 days)
                    grace_start_date = datetime.fromisoformat(grace_period_start)
                    if datetime.utcnow() > grace_start_date + timedelta(days=7):
                        # Expire the subscription
                        return await self._expire_subscription(db, subscription)
                    else:
                        # Still in grace period
                        return {"status": "grace_period", "user_id": user_id}
                else:
                    # Start grace period
                    return await self._start_grace_period(db, subscription)
            
            # Get subscription details
            period = metadata.get("subscription_period", "monthly")
            payment_method = metadata.get("last_payment_method", "wechat_pay")
            
            # Calculate renewal amount
            amount = self._calculate_subscription_amount(subscription.membership_level, period)
            
            # Get last successful payment method
            last_transaction = db.query(MembershipTransaction).filter(
                MembershipTransaction.user_id == user_id,
                MembershipTransaction.status == PaymentStatus.SUCCESS
            ).order_by(MembershipTransaction.created_at.desc()).first()
            
            if last_transaction:
                payment_method = last_transaction.payment_method.value
            
            # Create renewal transaction
            transaction = MembershipTransaction(
                user_id=user_id,
                amount=amount,
                payment_method=PaymentMethod(payment_method),
                status=PaymentStatus.PENDING,
                transaction_type="subscription_renewal",
                metadata={
                    "subscription_period": period,
                    "membership_level": subscription.membership_level.value,
                    "renewal_date": datetime.utcnow().isoformat(),
                    "auto_renewal": True
                }
            )
            
            db.add(transaction)
            db.commit()
            db.refresh(transaction)
            
            # Process payment
            payment_result = await self._process_renewal_payment(
                transaction, PaymentMethod(payment_method)
            )
            
            if payment_result.get("success"):
                # Update subscription
                next_expiry = self._calculate_next_expiry_date(period)
                subscription.expires_at = next_expiry
                subscription.metadata.update({
                    "last_renewal": datetime.utcnow().isoformat(),
                    "next_billing_date": next_expiry.isoformat(),
                    "failed_attempts": 0  # Reset failed attempts
                })
                
                transaction.status = PaymentStatus.SUCCESS
                db.commit()
                
                logger.info(f"Successfully renewed subscription for user {user_id}")
                return {"status": "renewed", "user_id": user_id, "next_expiry": next_expiry}
            
            else:
                # Payment failed
                transaction.status = PaymentStatus.FAILED
                db.commit()
                
                # Handle failed payment
                return await self._handle_failed_renewal(db, subscription, payment_result.get("error"))
                
        except Exception as e:
            db.rollback()
            logger.error(f"Error processing subscription renewal: {str(e)}")
            return {"status": "error", "user_id": subscription.user_id, "error": str(e)}
    
    async def _process_renewal_payment(self, transaction: MembershipTransaction, payment_method: PaymentMethod) -> Dict[str, Any]:
        """
        Process renewal payment using specified method
        """
        try:
            # For automatic renewals, we simulate successful payment for now
            # In production, you would integrate with stored payment methods or tokenized payments
            
            if payment_method == PaymentMethod.WECHAT_PAY:
                # Simulate WeChat Pay renewal
                logger.info(f"Processing WeChat Pay renewal for transaction {transaction.id}")
                # In production: use stored payment token or trigger payment flow
                return {"success": True, "payment_id": f"wx_renewal_{transaction.id}"}
                
            elif payment_method == PaymentMethod.ALIPAY:
                # Simulate Alipay renewal
                logger.info(f"Processing Alipay renewal for transaction {transaction.id}")
                # In production: use stored payment token or trigger payment flow
                return {"success": True, "payment_id": f"alipay_renewal_{transaction.id}"}
            
            else:
                return {"success": False, "error": "Unsupported payment method for auto-renewal"}
                
        except Exception as e:
            logger.error(f"Error processing renewal payment: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def _handle_failed_renewal(self, db: Session, subscription: UserMembership, error: str) -> Dict[str, Any]:
        """
        Handle failed renewal payment
        """
        try:
            metadata = subscription.metadata or {}
            failed_attempts = metadata.get("failed_attempts", 0) + 1
            
            if failed_attempts >= 3:
                # Start grace period after 3 failed attempts
                return await self._start_grace_period(db, subscription)
            else:
                # Increment failed attempts and retry tomorrow
                metadata.update({
                    "failed_attempts": failed_attempts,
                    "last_failure": datetime.utcnow().isoformat(),
                    "last_failure_reason": error
                })
                subscription.metadata = metadata
                db.commit()
                
                logger.warning(f"Renewal failed for user {subscription.user_id}, attempt {failed_attempts}")
                return {"status": "failed", "user_id": subscription.user_id, "attempts": failed_attempts}
                
        except Exception as e:
            logger.error(f"Error handling failed renewal: {str(e)}")
            return {"status": "error", "user_id": subscription.user_id, "error": str(e)}
    
    async def _start_grace_period(self, db: Session, subscription: UserMembership) -> Dict[str, Any]:
        """
        Start grace period for subscription
        """
        try:
            metadata = subscription.metadata or {}
            metadata.update({
                "grace_period_start": datetime.utcnow().isoformat(),
                "grace_period_end": (datetime.utcnow() + timedelta(days=7)).isoformat(),
                "status": "grace_period"
            })
            subscription.metadata = metadata
            db.commit()
            
            logger.warning(f"Started grace period for user {subscription.user_id}")
            return {"status": "grace_period", "user_id": subscription.user_id}
            
        except Exception as e:
            logger.error(f"Error starting grace period: {str(e)}")
            return {"status": "error", "user_id": subscription.user_id, "error": str(e)}
    
    async def _expire_subscription(self, db: Session, subscription: UserMembership) -> Dict[str, Any]:
        """
        Expire subscription after grace period
        """
        try:
            # Downgrade to free membership
            subscription.membership_level = MembershipLevel.FREE
            subscription.expires_at = datetime.utcnow()
            
            metadata = subscription.metadata or {}
            metadata.update({
                "expired_at": datetime.utcnow().isoformat(),
                "auto_renew": False,
                "status": "expired"
            })
            subscription.metadata = metadata
            db.commit()
            
            logger.info(f"Expired subscription for user {subscription.user_id}")
            return {"status": "expired", "user_id": subscription.user_id}
            
        except Exception as e:
            logger.error(f"Error expiring subscription: {str(e)}")
            return {"status": "error", "user_id": subscription.user_id, "error": str(e)}
    
    def _calculate_subscription_amount(self, level: MembershipLevel, period: str) -> int:
        """
        Calculate subscription amount in cents
        """
        # Base prices in cents
        base_prices = {
            MembershipLevel.PREMIUM: {
                "monthly": 2999,  # ¥29.99/month
                "annually": 29999 # ¥299.99/year (2 months free)
            },
            MembershipLevel.VIP: {
                "monthly": 5999,  # ¥59.99/month
                "annually": 59999 # ¥599.99/year (2 months free)
            }
        }
        
        return base_prices.get(level, {}).get(period, 2999)
    
    def _calculate_next_expiry_date(self, period: str) -> datetime:
        """
        Calculate next expiry date based on period
        """
        now = datetime.utcnow()
        
        if period == "monthly":
            return now + timedelta(days=30)
        elif period == "annually":
            return now + timedelta(days=365)
        else:
            return now + timedelta(days=30)  # Default to monthly

async def main():
    """Main function to run the cron job"""
    service = SubscriptionCronService()
    results = await service.run_daily_subscription_check()
    
    print(f"Subscription renewal check completed:")
    print(f"  Checked: {results['checked']}")
    print(f"  Renewed: {results['renewed']}")
    print(f"  Failed: {results['failed']}")
    print(f"  Grace Period: {results['grace_period']}")
    print(f"  Expired: {results['expired']}")
    
    if results['errors']:
        print(f"  Errors: {len(results['errors'])}")
        for error in results['errors'][:3]:  # Show first 3 errors
            print(f"    - {error}")

if __name__ == "__main__":
    asyncio.run(main())
