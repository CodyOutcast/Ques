"""
Payment API endpoints for membership subscription management
Handles WeChat Pay and Alipay integration for subscription payments
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional, List
from pydantic import BaseModel
import logging

from dependencies.db import get_db
from dependencies.auth import get_current_user
from models.users import User
from models.payments import MembershipTransaction, PaymentStatus, PaymentMethod
from models.user_membership import UserMembership, MembershipType
from services.payment_service import TencentWeChatPayService
# from services.alipay_service import AlipayService  # Temporarily disabled due to import issues
from services.subscription_service_working import SubscriptionService, SubscriptionPeriod

router = APIRouter(prefix="/api/payments", tags=["payments"])
logger = logging.getLogger(__name__)

# === REQUEST MODELS ===

class CreatePaymentRequest(BaseModel):
    """Request model for creating payment orders"""
    membership_plan: str  # "premium", "paid"
    subscription_period: str = "monthly"  # "weekly", "monthly", "annually"
    payment_method: str = "wechat_pay"  # "wechat_pay", "alipay"

class PaymentWebhookRequest(BaseModel):
    """Request model for payment webhooks"""
    payment_id: str
    status: str
    transaction_id: Optional[str] = None

# === WECHAT PAY ENDPOINTS ===

@router.post("/wechat/orders")
async def create_wechat_order(
    request: CreatePaymentRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a WeChat Pay order for subscription payment
    """
    try:
        # Validate subscription period
        try:
            period = SubscriptionPeriod(request.subscription_period)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid subscription period: {request.subscription_period}"
            )
        
        # Validate membership plan
        try:
            membership_type = MembershipType(request.membership_plan.upper())
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid membership plan: {request.membership_plan}"
            )
        
        # Create subscription
        subscription_service = SubscriptionService()
        result = subscription_service.create_subscription(
            db=db,
            user_id=current_user.user_id,
            membership_type=membership_type,
            period=period,
            payment_method="wechat_pay"
        )
        
        logger.info(f"WeChat Pay subscription created for user {current_user.user_id}")
        
        return {
            "success": True,
            "message": "WeChat Pay subscription created successfully",
            "subscription_details": result,
            "payment_method": "wechat_pay"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating WeChat Pay order: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create WeChat Pay order: {str(e)}"
        )

# === ALIPAY ENDPOINTS ===

@router.post("/alipay/orders")
async def create_alipay_order(
    request: CreatePaymentRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create an Alipay order for subscription payment
    """
    try:
        # Validate subscription period
        try:
            period = SubscriptionPeriod(request.subscription_period)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid subscription period: {request.subscription_period}"
            )
        
        # Validate membership plan
        try:
            membership_type = MembershipType(request.membership_plan.upper())
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid membership plan: {request.membership_plan}"
            )
        
        # Create subscription
        subscription_service = SubscriptionService()
        result = subscription_service.create_subscription(
            db=db,
            user_id=current_user.user_id,
            membership_type=membership_type,
            period=period,
            payment_method="alipay"
        )
        
        logger.info(f"Alipay subscription created for user {current_user.user_id}")
        
        return {
            "success": True,
            "message": "Alipay subscription created successfully",
            "subscription_details": result,
            "payment_method": "alipay"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating Alipay order: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create Alipay order: {str(e)}"
        )

# === PAYMENT HISTORY ===

@router.get("/history")
def get_payment_history(
    limit: int = 10,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get payment history for the current user
    """
    try:
        transactions = db.query(MembershipTransaction).filter(
            MembershipTransaction.user_id == current_user.user_id
        ).order_by(
            MembershipTransaction.created_at.desc()
        ).offset(offset).limit(limit).all()
        
        history = []
        for transaction in transactions:
            history.append({
                "id": transaction.id,
                "amount": transaction.amount,
                "payment_method": transaction.payment_method.value,
                "status": transaction.status.value,
                "transaction_type": transaction.transaction_type,
                "created_at": transaction.created_at.isoformat(),
                "metadata": transaction.metadata
            })
        
        return {
            "success": True,
            "payments": history,
            "total": len(history)
        }
        
    except Exception as e:
        logger.error(f"Error retrieving payment history: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve payment history"
        )

# === PAYMENT STATUS ===

@router.get("/status/{transaction_id}")
def get_payment_status(
    transaction_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get status of a specific payment transaction
    """
    try:
        transaction = db.query(MembershipTransaction).filter(
            MembershipTransaction.id == transaction_id,
            MembershipTransaction.user_id == current_user.user_id
        ).first()
        
        if not transaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment transaction not found"
            )
        
        return {
            "success": True,
            "transaction": {
                "id": transaction.id,
                "amount": transaction.amount,
                "payment_method": transaction.payment_method.value,
                "status": transaction.status.value,
                "transaction_type": transaction.transaction_type,
                "created_at": transaction.created_at.isoformat(),
                "updated_at": transaction.updated_at.isoformat() if transaction.updated_at else None,
                "metadata": transaction.metadata
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving payment status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve payment status"
        )

# === WEBHOOK ENDPOINTS ===

@router.post("/webhooks/wechat")
async def wechat_payment_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Handle WeChat Pay payment webhooks
    """
    try:
        # Get raw request body for signature verification
        body = await request.body()
        
        # TODO: Implement actual WeChat Pay webhook verification
        # For now, we'll simulate successful payment processing
        
        logger.info("WeChat Pay webhook received")
        
        return {
            "success": True,
            "message": "Webhook processed successfully"
        }
        
    except Exception as e:
        logger.error(f"Error processing WeChat Pay webhook: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process webhook"
        )

@router.post("/webhooks/alipay")
async def alipay_payment_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Handle Alipay payment webhooks
    """
    try:
        # Get raw request body for signature verification
        body = await request.body()
        
        # TODO: Implement actual Alipay webhook verification
        # For now, we'll simulate successful payment processing
        
        logger.info("Alipay webhook received")
        
        return {
            "success": True,
            "message": "Webhook processed successfully"
        }
        
    except Exception as e:
        logger.error(f"Error processing Alipay webhook: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process webhook"
        )

# === SUBSCRIPTION MANAGEMENT ===

@router.get("/subscription/current")
def get_current_subscription(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current subscription details for the user
    """
    try:
        subscription_service = SubscriptionService()
        subscription_info = subscription_service.get_subscription_status(
            db=db,
            user_id=current_user.user_id
        )
        
        return {
            "success": True,
            "subscription": subscription_info
        }
        
    except Exception as e:
        logger.error(f"Error getting subscription info: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get subscription information"
        )

# === PRICING INFORMATION ===

@router.get("/pricing")
def get_pricing_info():
    """
    Get pricing information for all subscription plans
    """
    return {
        "success": True,
        "pricing": {
            "premium": {
                "weekly": {
                    "amount": 7.50,
                    "currency": "USD",
                    "period": "week",
                    "description": "Premium membership - weekly billing"
                },
                "monthly": {
                    "amount": 29.99,
                    "currency": "USD",
                    "period": "month",
                    "description": "Premium membership - monthly billing"
                },
                "annually": {
                    "amount": 305.91,
                    "currency": "USD",
                    "period": "year",
                    "description": "Premium membership - annual billing (15% discount)",
                    "savings": "15% off monthly rate"
                }
            },
            "paid": {
                "weekly": {
                    "amount": 7.50,
                    "currency": "USD",
                    "period": "week",
                    "description": "Paid membership - weekly billing"
                },
                "monthly": {
                    "amount": 29.99,
                    "currency": "USD",
                    "period": "month",
                    "description": "Paid membership - monthly billing"
                },
                "annually": {
                    "amount": 305.91,
                    "currency": "USD",
                    "period": "year",
                    "description": "Paid membership - annual billing (15% discount)",
                    "savings": "15% off monthly rate"
                }
            }
        },
        "payment_methods": ["wechat_pay", "alipay"],
        "supported_currencies": ["USD", "CNY"]
    }
