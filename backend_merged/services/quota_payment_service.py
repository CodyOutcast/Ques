"""
Quota-Based Payment Service
Handles one-time payments for membership days (30 or 365 days)
Users pay upfront for days instead of recurring subscriptions
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
import logging
from enum import Enum
import uuid

from models.users import User
from models.user_membership import UserMembership, MembershipType
from models.payments import MembershipTransaction, PaymentStatus, PaymentMethod
from services.payment_service import TencentWeChatPayService
from dependencies.db import get_db

logger = logging.getLogger(__name__)

class QuotaDays(Enum):
    """Available day packages for purchase"""
    MONTHLY_PACKAGE = 30    # 30 days package
    ANNUAL_PACKAGE = 365    # 365 days package

class QuotaPaymentService:
    """Service for handling quota-based membership payments"""
    
    def __init__(self):
        self.payment_service = TencentWeChatPayService()
    
    def get_quota_pricing(self) -> Dict[str, Any]:
        """
        Get pricing for available day packages
        """
        return {
            "pricing": {
                "30_days": {
                    "days": 30,
                    "price": 29.99,
                    "currency": "USD",
                    "price_per_day": 1.00,
                    "description": "30 days of premium access",
                    "package_type": "monthly_equivalent"
                },
                "365_days": {
                    "days": 365,
                    "price": 305.91,
                    "currency": "USD", 
                    "price_per_day": 0.84,
                    "description": "365 days of premium access (15% savings)",
                    "package_type": "annual_equivalent",
                    "savings": "15% compared to buying 30-day packages"
                }
            },
            "perks": {
                "all_packages": [
                    "Full premium features access",
                    "No recurring charges",
                    "Pay once, use for purchased days",
                    "Days don't expire until used",
                    "Can purchase multiple packages"
                ]
            }
        }
    
    def calculate_package_price(self, days: int, membership_type: MembershipType = MembershipType.PREMIUM) -> tuple[float, str]:
        """
        Calculate price for a specific number of days
        """
        base_pricing = {
            MembershipType.PREMIUM: {
                30: 29.99,
                365: 305.91  # 15% discount
            },
            MembershipType.PAID: {
                30: 29.99,
                365: 305.91
            }
        }
        
        if days == 30:
            price = base_pricing[membership_type][30]
            package_type = "30_day_package"
        elif days == 365:
            price = base_pricing[membership_type][365]
            package_type = "365_day_package"
        else:
            # Custom day calculation (based on daily rate of 30-day package)
            daily_rate = base_pricing[membership_type][30] / 30
            price = daily_rate * days
            package_type = f"{days}_day_custom"
        
        return price, package_type
    
    def purchase_membership_days(
        self,
        db: Session,
        user_id: int,
        days: int,
        payment_method: str = "wechat_pay",
        membership_type: MembershipType = MembershipType.PREMIUM
    ) -> Dict[str, Any]:
        """
        Purchase membership days (quota-based payment)
        """
        try:
            # Validate days (must be 30 or 365, or custom amount)
            if days not in [30, 365] and (days < 1 or days > 3650):  # Max 10 years
                raise ValueError(f"Invalid days amount: {days}. Must be 30, 365, or between 1-3650")
            
            # Calculate pricing
            amount, package_type = self.calculate_package_price(days, membership_type)
            
            # Generate unique order ID
            order_id = f"quota_{user_id}_{int(datetime.utcnow().timestamp())}_{uuid.uuid4().hex[:8]}"
            
            # Create transaction record
            transaction = MembershipTransaction(
                user_id=user_id,
                order_id=order_id,
                amount=amount,
                currency="USD",
                payment_method=PaymentMethod(payment_method),
                payment_status=PaymentStatus.PENDING,
                plan_type=package_type,
                plan_duration_days=days,
                created_at=datetime.utcnow(),
                expires_at=datetime.utcnow() + timedelta(hours=24)  # Payment expires in 24h
            )
            
            db.add(transaction)
            db.commit()
            
            # Create payment order with payment provider
            payment_result = self._create_payment_order(
                transaction=transaction,
                user_id=user_id,
                days=days
            )
            
            return {
                "success": True,
                "order_id": order_id,
                "transaction_id": transaction.id,
                "amount": amount,
                "currency": "USD",
                "days": days,
                "package_type": package_type,
                "payment_method": payment_method,
                "expires_at": transaction.expires_at.isoformat(),
                "payment_data": payment_result
            }
            
        except Exception as e:
            logger.error(f"Error purchasing membership days: {str(e)}")
            db.rollback()
            raise e
    
    def _create_payment_order(self, transaction: MembershipTransaction, user_id: int, days: int) -> Dict[str, Any]:
        """
        Create payment order with payment provider
        """
        try:
            # This would integrate with actual payment provider
            # For now, return mock payment data
            return {
                "prepay_id": f"prepay_{transaction.order_id}",
                "payment_url": f"https://pay.example.com/order/{transaction.order_id}",
                "qr_code": f"https://api.qrserver.com/v1/create-qr-code/?size=200x200&data={transaction.order_id}",
                "expires_at": transaction.expires_at.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error creating payment order: {str(e)}")
            raise e
    
    def confirm_payment(
        self,
        db: Session,
        order_id: str,
        transaction_id: str,
        payment_data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Confirm payment and add days to user's membership
        """
        try:
            # Get transaction
            transaction = db.query(MembershipTransaction).filter(
                MembershipTransaction.order_id == order_id
            ).first()
            
            if not transaction:
                raise ValueError(f"Transaction not found: {order_id}")
            
            if transaction.payment_status == PaymentStatus.SUCCESS:
                raise ValueError("Payment already confirmed")
            
            # Mark transaction as successful
            transaction.mark_as_paid(
                transaction_id=transaction_id,
                notification_data=str(payment_data) if payment_data else None
            )
            
            # Add days to user's membership
            self._add_membership_days(
                db=db,
                user_id=transaction.user_id,
                days=transaction.plan_duration_days,
                membership_type=MembershipType.PREMIUM  # Default to premium
            )
            
            db.commit()
            
            return {
                "success": True,
                "message": "Payment confirmed and days added to membership",
                "user_id": transaction.user_id,
                "days_added": transaction.plan_duration_days,
                "amount_paid": transaction.amount,
                "transaction_id": transaction.id
            }
            
        except Exception as e:
            logger.error(f"Error confirming payment: {str(e)}")
            db.rollback()
            raise e
    
    def _add_membership_days(
        self,
        db: Session,
        user_id: int,
        days: int,
        membership_type: MembershipType = MembershipType.PREMIUM
    ):
        """
        Add purchased days to user's membership
        """
        try:
            # Get or create user membership
            membership = db.query(UserMembership).filter(
                UserMembership.user_id == user_id
            ).first()
            
            current_time = datetime.utcnow()
            
            if not membership:
                # Create new membership
                membership = UserMembership(
                    user_id=user_id,
                    membership_type=membership_type,
                    start_date=current_time,
                    end_date=current_time + timedelta(days=days),
                    is_active=True
                )
                db.add(membership)
            else:
                # Extend existing membership
                if membership.end_date and membership.end_date > current_time:
                    # Add days to existing end date
                    membership.end_date = membership.end_date + timedelta(days=days)
                else:
                    # Membership expired or no end date, start from now
                    membership.end_date = current_time + timedelta(days=days)
                
                # Upgrade membership type if needed
                if membership_type == MembershipType.PREMIUM:
                    membership.membership_type = membership_type
                
                membership.is_active = True
                membership.updated_at = current_time
            
            logger.info(f"Added {days} days to user {user_id} membership. New end date: {membership.end_date}")
            
        except Exception as e:
            logger.error(f"Error adding membership days: {str(e)}")
            raise e
    
    def get_user_membership_status(self, db: Session, user_id: int) -> Dict[str, Any]:
        """
        Get user's current membership status including remaining days
        """
        try:
            membership = db.query(UserMembership).filter(
                UserMembership.user_id == user_id
            ).first()
            
            if not membership:
                return {
                    "has_membership": False,
                    "membership_type": "free",
                    "days_remaining": 0,
                    "end_date": None,
                    "is_active": False
                }
            
            current_time = datetime.utcnow()
            
            # Calculate remaining days
            days_remaining = 0
            is_active = False
            
            if membership.end_date and membership.end_date > current_time:
                days_remaining = (membership.end_date - current_time).days
                is_active = True
            
            return {
                "has_membership": membership.membership_type != MembershipType.FREE,
                "membership_type": membership.membership_type.value,
                "days_remaining": days_remaining,
                "end_date": membership.end_date.isoformat() if membership.end_date else None,
                "is_active": is_active,
                "start_date": membership.start_date.isoformat() if membership.start_date else None
            }
            
        except Exception as e:
            logger.error(f"Error getting membership status: {str(e)}")
            raise e
    
    def get_purchase_history(self, db: Session, user_id: int, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get user's purchase history
        """
        try:
            transactions = db.query(MembershipTransaction).filter(
                and_(
                    MembershipTransaction.user_id == user_id,
                    MembershipTransaction.payment_status == PaymentStatus.SUCCESS
                )
            ).order_by(
                MembershipTransaction.paid_at.desc()
            ).limit(limit).all()
            
            history = []
            for transaction in transactions:
                history.append({
                    "transaction_id": transaction.id,
                    "order_id": transaction.order_id,
                    "amount": transaction.amount,
                    "currency": transaction.currency,
                    "days_purchased": transaction.plan_duration_days,
                    "package_type": transaction.plan_type,
                    "payment_method": transaction.payment_method.value,
                    "purchase_date": transaction.paid_at.isoformat() if transaction.paid_at else None,
                    "created_date": transaction.created_at.isoformat()
                })
            
            return history
            
        except Exception as e:
            logger.error(f"Error getting purchase history: {str(e)}")
            raise e
