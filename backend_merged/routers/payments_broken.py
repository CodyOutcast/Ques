"""
Payment API endpoints for membership subscription management
Handles WeChat Pay integration and payment processing
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from pydantic import BaseModel
import        }
    except Exception as e:
        logger.error(f"Error retrieving payment history: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve payment history"
        )


# === ALIPAY ENDPOINTS ===

class AlipayOrderRequest(BaseModel):
    """Request model for creating Alipay orders"""
    membership_plan: str  # "PAID" or "PREMIUM"
    payment_method: str = "page"  # "page" for web, "qr" for QR code

@router.post("/alipay/orders")
async def create_alipay_order(
    request: AlipayOrderRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new Alipay payment order for membership"""
    try:
        # Validate membership plan
        if request.membership_plan not in ["PAID", "PREMIUM"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid membership plan. Must be 'PAID' or 'PREMIUM'"
            )
        
        # Get plan details
        plan_prices = {
            "PAID": 2999,      # 29.99 CNY
            "PREMIUM": 9999    # 99.99 CNY
        }
        
        amount = plan_prices[request.membership_plan]
        
        # Create order based on payment method
        if request.payment_method == "qr":
            result = alipay_service.create_qr_payment(
                user_id=current_user.user_id,
                membership_type=request.membership_plan,
                amount=amount
            )
        else:
            result = alipay_service.create_membership_order(
                user_id=current_user.user_id,
                membership_type=request.membership_plan,
                amount=amount
            )
        
        if result.get("success"):
            return {
                "order_id": result["order_id"],
                "payment_url": result.get("payment_url"),
                "qr_code": result.get("qr_code"),
                "payment_method": result["payment_method"],
                "amount": amount / 100,  # Convert to yuan
                "currency": "CNY",
                "expires_at": result["expires_at"]
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("error", "Failed to create Alipay order")
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating Alipay order: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create Alipay order"
        )

@router.post("/alipay/notify")
async def alipay_payment_notification(
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Handle Alipay payment notifications"""
    try:
        # Get form data
        form_data = await request.form()
        params = dict(form_data)
        
        # Log the notification
        webhook_log = PaymentWebhookLog(
            provider="ALIPAY",
            event_type="payment_notification",
            raw_data=json.dumps(params),
            processed=False
        )
        db.add(webhook_log)
        db.commit()
        
        # Process notification
        result = alipay_service.handle_payment_notification(params)
        
        # Update log
        webhook_log.processed = result.get("success", False)
        webhook_log.error_message = result.get("error") if not result.get("success") else None
        db.commit()
        
        if result.get("success"):
            return "success"  # Alipay expects "success" response
        else:
            return "fail"
            
    except Exception as e:
        logger.error(f"Error processing Alipay notification: {str(e)}")
        return "fail"

@router.get("/alipay/orders/{order_id}")
async def get_alipay_order_status(
    order_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get Alipay payment order status"""
    try:
        # Find transaction
        transaction = db.query(MembershipTransaction).filter(
            MembershipTransaction.order_id == order_id,
            MembershipTransaction.user_id == current_user.user_id
        ).first()
        
        if not transaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment order not found"
            )
        
        # Query Alipay for latest status
        result = alipay_service.query_payment_status(transaction.order_id)
        
        if result.get("success"):
            # Update local status if needed
            alipay_status = result.get("status", "UNKNOWN")
            if alipay_status != transaction.status.value.upper():
                if alipay_status == "COMPLETED":
                    transaction.status = PaymentStatus.SUCCESS
                elif alipay_status == "CANCELLED":
                    transaction.status = PaymentStatus.CANCELLED
                db.commit()
        
        return {
            "order_id": transaction.order_id,
            "status": transaction.status.value,
            "amount": transaction.amount,
            "currency": transaction.currency,
            "membership_type": transaction.membership_type,
            "created_at": transaction.created_at,
            "paid_at": transaction.paid_at,
            "alipay_status": result.get("trade_status") if result.get("success") else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving Alipay order status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve order status"
        )import logging

from dependencies.db import get_db
from dependencies.auth import get_current_user
from models.users import User
from models.payments import MembershipTransaction, PaymentStatus, PaymentMethod, PaymentWebhookLog
from models.user_membership import UserMembership, MembershipType
from services.payment_service import get_payment_service, MembershipPlan
from services.alipay_service import alipay_service
from services.membership_service import MembershipService

router = APIRouter(prefix="/api/v1/payments", tags=["payments"])
logger = logging.getLogger(__name__)

# Request/Response Models
class CreatePaymentRequest(BaseModel):
    plan: str  # monthly, yearly
    payment_method: str = "wechat_pay"

class CreatePaymentResponse(BaseModel):
    success: bool
    order_id: Optional[str] = None
    payment_params: Optional[Dict[str, Any]] = None
    expires_at: Optional[str] = None
    error: Optional[str] = None

class PaymentStatusResponse(BaseModel):
    success: bool
    order_id: str
    status: str
    is_paid: bool
    error: Optional[str] = None

class MembershipPlansResponse(BaseModel):
    plans: list
    currency: str
    features: list

@router.get("/plans", response_model=MembershipPlansResponse)
async def get_membership_plans():
    """Get available membership plans and pricing"""
    try:
        payment_service = get_payment_service()
        plans_data = payment_service.get_membership_plans()
        
        return MembershipPlansResponse(**plans_data)
        
    except Exception as e:
        logger.error(f"Error getting membership plans: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve membership plans"
        )

@router.post("/create", response_model=CreatePaymentResponse)
async def create_payment_order(
    request: CreatePaymentRequest,
    user_request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new payment order for membership upgrade"""
    try:
        user_id = current_user.user_id if hasattr(current_user, 'user_id') else current_user.id
        
        # Validate plan
        if request.plan not in ["monthly", "yearly"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid membership plan. Must be 'monthly' or 'yearly'"
            )
        
        # Check if user already has an active membership
        membership = MembershipService.get_or_create_membership(db, user_id)
        if membership.membership_type == MembershipType.PAID:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already has an active paid membership"
            )
        
        # Get user IP
        user_ip = user_request.client.host if user_request.client else "127.0.0.1"
        
        # Create payment order
        payment_service = get_payment_service()
        plan_enum = MembershipPlan.MONTHLY if request.plan == "monthly" else MembershipPlan.YEARLY
        
        result = await payment_service.create_payment_order(user_id, plan_enum, user_ip)
        
        if result["success"]:
            # Save transaction to database
            transaction = MembershipTransaction(
                user_id=user_id,
                order_id=result["order_id"],
                amount=plan_enum.value["price"],
                currency="CNY",
                payment_method=PaymentMethod.WECHAT_PAY,
                payment_status=PaymentStatus.PENDING,
                plan_type=request.plan,
                plan_duration_days=plan_enum.value["duration_days"],
                prepay_id=result.get("prepay_id"),
                payment_params=json.dumps(result.get("payment_params", {})),
                user_ip=user_ip,
                user_agent=user_request.headers.get("user-agent")
            )
            
            db.add(transaction)
            db.commit()
            
            return CreatePaymentResponse(
                success=True,
                order_id=result["order_id"],
                payment_params=result.get("payment_params"),
                expires_at=result.get("expires_at")
            )
        else:
            return CreatePaymentResponse(
                success=False,
                error=result.get("error", "Payment order creation failed")
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating payment order: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create payment order"
        )

@router.get("/status/{order_id}", response_model=PaymentStatusResponse)
async def check_payment_status(
    order_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Check the status of a payment order"""
    try:
        user_id = current_user.user_id if hasattr(current_user, 'user_id') else current_user.id
        
        # Get transaction from database
        transaction = db.query(MembershipTransaction).filter(
            MembershipTransaction.order_id == order_id,
            MembershipTransaction.user_id == user_id
        ).first()
        
        if not transaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment order not found"
            )
        
        # If already successful, return cached status
        if transaction.is_successful:
            return PaymentStatusResponse(
                success=True,
                order_id=order_id,
                status="success",
                is_paid=True
            )
        
        # Query live status from payment provider
        payment_service = get_payment_service()
        result = await payment_service.query_payment_status(order_id)
        
        if result["success"] and result.get("is_paid"):
            # Update transaction status
            transaction.mark_as_paid(result.get("transaction_id", ""))
            db.commit()
            
            # Update user membership
            await update_user_membership_after_payment(db, user_id, transaction.plan_type)
        
        return PaymentStatusResponse(
            success=True,
            order_id=order_id,
            status=result.get("trade_state", "unknown").lower(),
            is_paid=result.get("is_paid", False),
            error=result.get("error")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error checking payment status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to check payment status"
        )

@router.post("/notify")
async def payment_notification(
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Handle payment notifications from WeChat Pay"""
    try:
        # Get raw XML data
        xml_data = await request.body()
        xml_string = xml_data.decode('utf-8')
        
        # Log the webhook
        webhook_log = PaymentWebhookLog(
            payment_provider="wechat_pay",
            webhook_type="payment_notification",
            raw_data=xml_string,
            headers=json.dumps(dict(request.headers)),
            user_agent=request.headers.get("user-agent"),
            source_ip=request.client.host if request.client else None
        )
        db.add(webhook_log)
        db.commit()
        
        # Process notification in background
        background_tasks.add_task(process_payment_notification, xml_string, webhook_log.id)
        
        # Return success response to WeChat Pay
        return """<xml><return_code><![CDATA[SUCCESS]]></return_code><return_msg><![CDATA[OK]]></return_msg></xml>"""
        
    except Exception as e:
        logger.error(f"Error handling payment notification: {e}")
        # Still return success to avoid retries
        return """<xml><return_code><![CDATA[SUCCESS]]></return_code><return_msg><![CDATA[OK]]></return_msg></xml>"""

async def process_payment_notification(xml_data: str, webhook_log_id: int):
    """Process payment notification in background"""
    try:
        from dependencies.db import SessionLocal
        db = SessionLocal()
        
        try:
            payment_service = get_payment_service()
            result = await payment_service.verify_payment_notification(xml_data)
            
            # Update webhook log
            webhook_log = db.query(PaymentWebhookLog).filter(
                PaymentWebhookLog.id == webhook_log_id
            ).first()
            
            if webhook_log:
                webhook_log.processed = True
                webhook_log.processing_result = json.dumps(result)
                webhook_log.related_order_id = result.get("order_id")
            
            if result["success"]:
                # Find and update transaction
                order_id = result["order_id"]
                transaction = db.query(MembershipTransaction).filter(
                    MembershipTransaction.order_id == order_id
                ).first()
                
                if transaction:
                    transaction.mark_as_paid(
                        result["transaction_id"], 
                        xml_data
                    )
                    
                    # Update user membership
                    await update_user_membership_after_payment(
                        db, 
                        transaction.user_id, 
                        transaction.plan_type
                    )
                    
                    logger.info(f"Payment processed successfully for order {order_id}")
                else:
                    logger.error(f"Transaction not found for order {order_id}")
            else:
                logger.error(f"Payment notification verification failed: {result}")
            
            db.commit()
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Error processing payment notification: {e}")

async def update_user_membership_after_payment(db: Session, user_id: int, plan_type: str):
    """Update user membership after successful payment"""
    try:
        # Upgrade membership to paid
        MembershipService.upgrade_membership(db, user_id, "paid")
        
        logger.info(f"User {user_id} membership upgraded to paid ({plan_type})")
        
    except Exception as e:
        logger.error(f"Error updating membership for user {user_id}: {e}")

@router.get("/history")
async def get_payment_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get payment history for current user"""
    try:
        user_id = current_user.user_id if hasattr(current_user, 'user_id') else current_user.id
        
        transactions = db.query(MembershipTransaction).filter(
            MembershipTransaction.user_id == user_id
        ).order_by(MembershipTransaction.created_at.desc()).limit(50).all()
        
        history = []
        for transaction in transactions:
            history.append({
                "id": transaction.id,
                "order_id": transaction.order_id,
                "amount": transaction.amount,
                "currency": transaction.currency,
                "plan_type": transaction.plan_type,
                "status": transaction.payment_status.value,
                "created_at": transaction.created_at.isoformat(),
                "paid_at": transaction.paid_at.isoformat() if transaction.paid_at else None,
                "expires_at": transaction.expires_at.isoformat() if transaction.expires_at else None
            })
        
        return {
            "success": True,
            "transactions": history,
            "total": len(history)
        }
        
    except Exception as e:
        logger.error(f"Error getting payment history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve payment history"
        )
