"""
Payment System Router - Complete implementation
Provides all 7 critical payment endpoints required by frontend
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from decimal import Decimal
import uuid
import logging

from dependencies.db import get_db
from dependencies.auth import get_current_user
from models import (
    User, Membership, MembershipTransaction, PaymentMethod, PaymentSession,
    PaymentStatus, PaymentType, PaymentMethodType
)
from schemas.payments import (
    # Request schemas
    PurchaseReceivesRequest, ChangePlanRequest, CreatePaymentSessionRequest, CancelTransactionRequest,
    # Response schemas  
    PurchaseReceivesResponse, ChangePlanResponse, TransactionResponse, TransactionHistoryResponse,
    PaymentMethodResponse, PaymentMethodsResponse, PaymentSessionResponse, PaymentSessionDetailsResponse,
    CancelTransactionResponse, UserPlan,
    # Enums and constants
    PaymentMethodEnum, PlanTypeEnum, TransactionStatusEnum, TransactionTypeEnum,
    RECEIVES_PRICING, PLAN_PRICING, PLAN_RECEIVES
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/payments", tags=["payments"])

# Payment Service Class

class PaymentService:
    """Service class for payment operations"""
    
    @staticmethod
    def calculate_receives_cost(amount: int) -> Decimal:
        """Calculate cost for purchasing receives"""
        if amount in RECEIVES_PRICING:
            return RECEIVES_PRICING[amount]
        
        # For custom amounts, use base pricing with bulk discounts
        base_price = Decimal("2.00")
        if amount >= 20:
            return base_price * amount * Decimal("0.80")  # 20% discount
        elif amount >= 10:
            return base_price * amount * Decimal("0.85")  # 15% discount
        elif amount >= 5:
            return base_price * amount * Decimal("0.90")  # 10% discount
        else:
            return base_price * amount
    
    @staticmethod
    def generate_order_id() -> str:
        """Generate unique order ID"""
        return f"ORD_{int(datetime.utcnow().timestamp())}_{uuid.uuid4().hex[:8].upper()}"
    
    @staticmethod
    def generate_session_id() -> str:
        """Generate unique session ID"""
        return f"SES_{int(datetime.utcnow().timestamp())}_{uuid.uuid4().hex[:8].upper()}"
    
    @staticmethod
    def create_payment_url(session_id: str, payment_method: str, amount: Decimal) -> str:
        """Generate payment URL (mock implementation)"""
        # In production, integrate with actual payment providers
        return f"https://payment.provider.com/pay?session={session_id}&method={payment_method}&amount={amount}"
    
    @staticmethod
    def update_user_receives(db: Session, user: User, additional_receives: int):
        """Update user's receive count"""
        membership = user.membership
        if membership:
            membership.receives_remaining = (membership.receives_remaining or 0) + additional_receives
            membership.receives_total += additional_receives
            membership.updated_at = datetime.utcnow()
            db.commit()
    
    @staticmethod
    def update_user_plan(db: Session, user: User, new_plan: PlanTypeEnum) -> UserPlan:
        """Update user's membership plan"""
        membership = user.membership
        if not membership:
            # Create new membership if doesn't exist
            membership = Membership(
                user_id=user.id,
                plan_type=new_plan.value,
                receives_total=PLAN_RECEIVES[new_plan],
                receives_used=0,
                receives_remaining=PLAN_RECEIVES[new_plan],
                monthly_price=PLAN_PRICING[new_plan],
                plan_start_date=datetime.utcnow(),
                next_reset_date=datetime.utcnow() + timedelta(days=30),
                status="active"
            )
            db.add(membership)
            user.membership = membership
        else:
            # Update existing membership
            membership.plan_type = new_plan.value
            membership.receives_total = PLAN_RECEIVES[new_plan] 
            membership.receives_remaining = PLAN_RECEIVES[new_plan] - membership.receives_used
            membership.monthly_price = PLAN_PRICING[new_plan]
            membership.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(membership)
        
        return UserPlan(
            plan_type=membership.plan_type,
            receives_total=membership.receives_total,
            receives_used=membership.receives_used,
            receives_remaining=membership.receives_remaining or 0,
            monthly_price=membership.monthly_price,
            status=membership.status,
            next_reset_date=membership.next_reset_date
        )

# API Endpoints

@router.post("/receives", response_model=PurchaseReceivesResponse)
async def purchase_receives(
    request: PurchaseReceivesRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Purchase additional receives
    Frontend endpoint: POST /payments/receives
    """
    try:
        # Calculate cost
        cost = PaymentService.calculate_receives_cost(request.amount)
        
        # Generate order ID
        order_id = PaymentService.generate_order_id()
        
        # Create transaction record
        transaction = MembershipTransaction(
            user_id=current_user.id,
            membership_id=current_user.membership.id if current_user.membership else None,
            order_id=order_id,
            amount=cost,
            currency="CNY",
            payment_method=request.payment_method or PaymentMethodEnum.WECHAT_PAY,
            payment_status=PaymentStatus.PENDING,
            transaction_type=TransactionTypeEnum.PURCHASE_RECEIVES,
            transaction_metadata=f'{{"receives_count": {request.amount}}}',
            created_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(hours=1)
        )
        
        db.add(transaction)
        db.commit()
        db.refresh(transaction)
        
        # For demo purposes, auto-complete the transaction
        # In production, this would be handled by payment provider webhooks
        transaction.payment_status = PaymentStatus.COMPLETED
        transaction.paid_at = datetime.utcnow()
        transaction.transaction_id = f"TXN_{transaction.id}_{uuid.uuid4().hex[:8]}"
        
        # Update user receives
        PaymentService.update_user_receives(db, current_user, request.amount)
        
        db.commit()
        db.refresh(current_user.membership)
        
        # Generate payment URL (for frontend compatibility)
        payment_url = PaymentService.create_payment_url(
            str(transaction.id), 
            request.payment_method or PaymentMethodEnum.WECHAT_PAY,
            cost
        )
        
        return PurchaseReceivesResponse(
            transaction_id=transaction.transaction_id,
            amount=request.amount,
            cost=cost,
            new_balance=current_user.membership.receives_remaining or 0,
            payment_url=payment_url,
            status=TransactionStatusEnum.COMPLETED,
            created_at=transaction.created_at
        )
        
    except Exception as e:
        logger.error(f"Error purchasing receives: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to process receive purchase")

@router.post("/plan", response_model=ChangePlanResponse) 
async def change_plan(
    request: ChangePlanRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upgrade or downgrade membership plan
    Frontend endpoint: POST /payments/plan
    """
    try:
        # Get current plan
        old_membership = current_user.membership
        old_plan = UserPlan(
            plan_type=old_membership.plan_type if old_membership else PlanTypeEnum.BASIC,
            receives_total=old_membership.receives_total if old_membership else 3,
            receives_used=old_membership.receives_used if old_membership else 0,
            receives_remaining=old_membership.receives_remaining or 0 if old_membership else 3,
            monthly_price=old_membership.monthly_price if old_membership else Decimal("0.00"),
            status=old_membership.status if old_membership else "active",
            next_reset_date=old_membership.next_reset_date if old_membership else datetime.utcnow()
        )
        
        # Check if plan change is needed
        if old_membership and old_membership.plan_type == request.new_plan.value:
            raise HTTPException(status_code=400, detail="Already on requested plan")
        
        transaction_id = None
        payment_url = None
        status = TransactionStatusEnum.COMPLETED
        
        # Create transaction if upgrade requires payment
        current_plan_price = old_membership.monthly_price if old_membership else Decimal("0.00")
        new_plan_price = PLAN_PRICING[request.new_plan]
        
        if new_plan_price > current_plan_price:
            # Payment required for upgrade
            cost = new_plan_price - current_plan_price
            order_id = PaymentService.generate_order_id()
            
            transaction = MembershipTransaction(
                user_id=current_user.id,
                membership_id=old_membership.id if old_membership else None,
                order_id=order_id,
                amount=cost,
                currency="CNY", 
                payment_method=request.payment_method or PaymentMethodEnum.WECHAT_PAY,
                payment_status=PaymentStatus.COMPLETED,  # Auto-complete for demo
                transaction_type=TransactionTypeEnum.PLAN_UPGRADE,
                plan_type=request.new_plan.value,
                transaction_metadata=f'{{"old_plan": "{old_plan.plan_type}", "new_plan": "{request.new_plan}"}}',
                created_at=datetime.utcnow(),
                paid_at=datetime.utcnow(),
                expires_at=datetime.utcnow() + timedelta(days=30)
            )
            
            db.add(transaction)
            db.commit()
            db.refresh(transaction)
            
            transaction_id = f"TXN_{transaction.id}_{uuid.uuid4().hex[:8]}"
            transaction.transaction_id = transaction_id
            payment_url = PaymentService.create_payment_url(str(transaction.id), request.payment_method or PaymentMethodEnum.WECHAT_PAY, cost)
        
        # Update membership plan
        new_plan = PaymentService.update_user_plan(db, current_user, request.new_plan)
        
        return ChangePlanResponse(
            transaction_id=transaction_id,
            old_plan=old_plan,
            new_plan=new_plan,
            monthly_fee=new_plan_price,
            payment_url=payment_url,
            status=status,
            effective_date=datetime.utcnow()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error changing plan: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to change plan")

@router.get("/transactions", response_model=TransactionHistoryResponse)
async def get_transaction_history(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    type: Optional[TransactionTypeEnum] = Query(None, description="Filter by transaction type"),
    status: Optional[TransactionStatusEnum] = Query(None, description="Filter by status"),
    start_date: Optional[datetime] = Query(None, description="Start date filter"),
    end_date: Optional[datetime] = Query(None, description="End date filter"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user's transaction history with pagination and filtering
    Frontend endpoint: GET /payments/transactions
    """
    try:
        # Build query
        query = db.query(MembershipTransaction).filter(MembershipTransaction.user_id == current_user.id)
        
        if type:
            query = query.filter(MembershipTransaction.transaction_type == type.value)
        if status:
            query = query.filter(MembershipTransaction.payment_status == status.value)
        if start_date:
            query = query.filter(MembershipTransaction.created_at >= start_date)
        if end_date:
            query = query.filter(MembershipTransaction.created_at <= end_date)
        
        # Get total count
        total = query.count()
        total_pages = (total + limit - 1) // limit
        
        # Get paginated results
        transactions = query.order_by(MembershipTransaction.created_at.desc()).offset((page - 1) * limit).limit(limit).all()
        
        # Convert to response format
        transaction_responses = [
            TransactionResponse(
                id=t.id,
                transaction_id=t.transaction_id,
                order_id=t.order_id,
                amount=t.amount,
                currency=t.currency,
                payment_method=t.payment_method,
                status=t.payment_status,
                transaction_type=t.transaction_type,
                metadata={"raw": t.transaction_metadata} if t.transaction_metadata else None,
                created_at=t.created_at,
                paid_at=t.paid_at,
                error_message=t.error_message
            )
            for t in transactions
        ]
        
        return TransactionHistoryResponse(
            transactions=transaction_responses,
            total=total,
            page=page,
            limit=limit,
            total_pages=total_pages
        )
        
    except Exception as e:
        logger.error(f"Error getting transaction history: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve transaction history")

@router.get("/methods", response_model=PaymentMethodsResponse)
async def get_payment_methods(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get available payment methods
    Frontend endpoint: GET /payments/methods
    """
    try:
        # Return available payment methods (mock data for demo)
        methods = [
            PaymentMethodResponse(
                id="wechat_pay",
                name="WeChat Pay",
                type=PaymentMethodEnum.WECHAT_PAY,
                enabled=True,
                description="Pay with WeChat",
                icon="/icons/wechat-pay.png"
            ),
            PaymentMethodResponse(
                id="alipay", 
                name="Alipay",
                type=PaymentMethodEnum.ALIPAY,
                enabled=True,
                description="Pay with Alipay",
                icon="/icons/alipay.png"
            ),
            PaymentMethodResponse(
                id="credit_card",
                name="Credit Card",
                type=PaymentMethodEnum.CREDIT_CARD,
                enabled=True,
                description="Pay with credit/debit card",
                icon="/icons/credit-card.png"
            )
        ]
        
        return PaymentMethodsResponse(methods=methods)
        
    except Exception as e:
        logger.error(f"Error getting payment methods: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve payment methods")

@router.post("/sessions", response_model=PaymentSessionResponse)
async def create_payment_session(
    request: CreatePaymentSessionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create payment session for payment processing
    Frontend endpoint: POST /payments/sessions
    """
    try:
        # Generate session ID
        session_id = PaymentService.generate_session_id()
        
        # Create payment session
        session = PaymentSession(
            session_id=session_id,
            user_id=current_user.id,
            payment_type=request.type.value,
            amount=request.amount,
            currency="CNY",
            payment_method=request.payment_method.value,
            session_metadata=str(request.metadata) if request.metadata else None,
            status="created",
            created_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(hours=1)
        )
        
        # Generate payment URL and QR code
        payment_url = PaymentService.create_payment_url(session_id, request.payment_method.value, request.amount)
        qr_code = f"QR_{session_id}" if request.payment_method in [PaymentMethodEnum.WECHAT_PAY, PaymentMethodEnum.ALIPAY] else None
        
        session.payment_url = payment_url
        session.qr_code = qr_code
        
        db.add(session)
        db.commit()
        db.refresh(session)
        
        return PaymentSessionResponse(
            session_id=session_id,
            payment_url=payment_url,
            qr_code=qr_code,
            expires_at=session.expires_at
        )
        
    except Exception as e:
        logger.error(f"Error creating payment session: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create payment session")

@router.get("/sessions/{session_id}", response_model=PaymentSessionDetailsResponse)
async def get_payment_session_details(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get payment session details
    Frontend endpoint: GET /payments/sessions/{id}
    """
    try:
        # Find session
        session = db.query(PaymentSession).filter(
            PaymentSession.session_id == session_id,
            PaymentSession.user_id == current_user.id
        ).first()
        
        if not session:
            raise HTTPException(status_code=404, detail="Payment session not found")
        
        return PaymentSessionDetailsResponse(
            session_id=session.session_id,
            user_id=session.user_id,
            payment_type=session.payment_type,
            amount=session.amount,
            currency=session.currency,
            payment_method=session.payment_method,
            status=session.status,
            payment_url=session.payment_url,
            qr_code=session.qr_code,
            created_at=session.created_at,
            expires_at=session.expires_at,
            completed_at=session.completed_at,
            metadata={"raw": session.session_metadata} if session.session_metadata else None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting payment session details: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve session details")

@router.post("/cancel", response_model=CancelTransactionResponse)
async def cancel_transaction(
    transaction_id: str = Query(..., description="Transaction ID to cancel"),
    request: CancelTransactionRequest = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Cancel transaction or subscription
    Frontend endpoint: POST /payments/cancel
    """
    try:
        # Find transaction
        transaction = db.query(MembershipTransaction).filter(
            MembershipTransaction.transaction_id == transaction_id,
            MembershipTransaction.user_id == current_user.id
        ).first()
        
        if not transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")
        
        if transaction.payment_status != PaymentStatus.PENDING:
            raise HTTPException(status_code=400, detail="Cannot cancel completed transaction")
        
        # Cancel transaction
        transaction.payment_status = PaymentStatus.CANCELLED
        transaction.error_message = request.reason if request and request.reason else "Cancelled by user"
        
        db.commit()
        
        return CancelTransactionResponse(
            transaction_id=transaction_id,
            status=TransactionStatusEnum.CANCELLED,
            refund_amount=None,  # No refund for cancelled pending transactions
            cancelled_at=datetime.utcnow()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cancelling transaction: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to cancel transaction")