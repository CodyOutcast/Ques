"""
Payment System Router
Dedicated payment system for receives, plans, and transactions
separate from the existing payment routers for better organization.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
import logging
import uuid

from dependencies.db import get_db
from models.users import User
from services.auth_service import AuthService
from services.monitoring import log_security_event

router = APIRouter()
security = HTTPBearer()
logger = logging.getLogger(__name__)
auth_service = AuthService()

# ==================== Pydantic Models ====================

class PurchaseReceivesRequest(BaseModel):
    """Request model for purchasing receives"""
    amount: int = Field(..., ge=1, le=1000, description="Number of receives to purchase")
    package_type: str = Field(..., pattern="^(basic|standard|premium|custom)$")
    payment_method: str = Field(..., description="Payment method ID")
    promo_code: Optional[str] = Field(None, max_length=50)

class PurchaseReceivesResponse(BaseModel):
    """Response model for receives purchase"""
    transaction_id: str
    amount: int
    cost: float
    currency: str = "USD"
    payment_method: str
    status: str
    confirmation_code: str
    estimated_delivery: datetime

class ChangePlanRequest(BaseModel):
    """Request model for changing subscription plan"""
    new_plan: str = Field(..., pattern="^(basic|pro|premium|enterprise)$")
    billing_cycle: str = Field(..., pattern="^(monthly|yearly)$")
    payment_method: Optional[str] = None
    promo_code: Optional[str] = Field(None, max_length=50)

class ChangePlanResponse(BaseModel):
    """Response model for plan change"""
    transaction_id: str
    old_plan: str
    new_plan: str
    billing_cycle: str
    next_billing_date: datetime
    prorated_amount: Optional[float] = None
    status: str

class Transaction(BaseModel):
    """Transaction model"""
    id: str
    type: str = Field(..., description="Type: receives_purchase, plan_change, refund, adjustment")
    amount: float
    currency: str = "USD"
    status: str = Field(..., description="Status: pending, completed, failed, refunded")
    description: str
    payment_method: str
    created_at: datetime
    completed_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None

class TransactionsResponse(BaseModel):
    """Response model for transactions list"""
    transactions: List[Transaction]
    total_count: int
    page: int
    limit: int
    has_more: bool
    total_amount: float
    currency: str = "USD"

class PaymentMethod(BaseModel):
    """Payment method model"""
    id: str
    name: str
    type: str = Field(..., description="Type: wechat_pay, alipay, credit_card, paypal")
    enabled: bool
    description: Optional[str] = None
    icon: Optional[str] = None
    fees: Optional[Dict[str, float]] = None
    supported_currencies: List[str]

class PaymentMethodsResponse(BaseModel):
    """Response model for payment methods"""
    methods: List[PaymentMethod]
    default_method_id: Optional[str] = None

class PaymentSession(BaseModel):
    """Payment session model"""
    session_id: str
    payment_url: Optional[str] = None
    qr_code: Optional[str] = None
    expires_at: datetime
    status: str = Field(..., description="Status: created, pending, completed, expired, cancelled")

class CreatePaymentSessionRequest(BaseModel):
    """Request model for creating payment session"""
    transaction_type: str = Field(..., pattern="^(receives_purchase|plan_change)$")
    amount: float = Field(..., gt=0)
    currency: str = Field("USD", pattern="^(USD|CNY|EUR)$")
    payment_method_id: str
    metadata: Optional[Dict[str, Any]] = None
    return_url: Optional[str] = None
    cancel_url: Optional[str] = None

class ReceivesPricing(BaseModel):
    """Receives pricing model"""
    package_type: str
    amount: int
    price: float
    currency: str = "USD"
    savings_percentage: Optional[float] = None
    popular: bool = False
    bonus_receives: Optional[int] = None

class PlanPricing(BaseModel):
    """Plan pricing model"""
    plan: str
    name: str
    monthly_price: float
    yearly_price: float
    currency: str = "USD"
    features: List[str]
    yearly_savings_percentage: float
    popular: bool = False

class PricingResponse(BaseModel):
    """Response model for pricing information"""
    receives_packages: List[ReceivesPricing]
    subscription_plans: List[PlanPricing]
    currency: str = "USD"
    tax_rate: Optional[float] = None

# ==================== Endpoints ====================

@router.post("/receives/purchase", response_model=PurchaseReceivesResponse)
async def purchase_receives(
    request: PurchaseReceivesRequest,
    token: str = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Purchase receives packages
    """
    try:
        current_user = auth_service.get_current_user(db, token.credentials)
        if not current_user:
            raise HTTPException(status_code=401, detail="Invalid token")

        # Calculate pricing based on package type
        pricing_map = {
            "basic": 0.50,      # $0.50 per receive
            "standard": 0.40,   # $0.40 per receive
            "premium": 0.30,    # $0.30 per receive
            "custom": 0.35      # $0.35 per receive
        }
        
        unit_price = pricing_map.get(request.package_type, 0.50)
        total_cost = request.amount * unit_price
        
        # Apply promo code discount (mock)
        if request.promo_code:
            if request.promo_code.upper() == "SAVE10":
                total_cost *= 0.9  # 10% discount
                logger.info(f"Applied promo code {request.promo_code}: 10% discount")
        
        # Mock transaction creation
        transaction_id = f"rcv_{uuid.uuid4().hex[:12]}"
        confirmation_code = f"CONF_{uuid.uuid4().hex[:8].upper()}"
        
        # Log security event for high-value transactions
        if total_cost > 100:
            log_security_event(
                current_user.id,
                "high_value_purchase",
                {"amount": total_cost, "type": "receives", "transaction_id": transaction_id}
            )
        
        logger.info(f"Receives purchase: {request.amount} receives for ${total_cost:.2f} by user {current_user.id}")
        
        return PurchaseReceivesResponse(
            transaction_id=transaction_id,
            amount=request.amount,
            cost=round(total_cost, 2),
            currency="USD",
            payment_method=request.payment_method,
            status="completed",
            confirmation_code=confirmation_code,
            estimated_delivery=datetime.now() + timedelta(minutes=5)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error purchasing receives: {e}")
        raise HTTPException(status_code=500, detail="Failed to purchase receives")

@router.post("/plan/change", response_model=ChangePlanResponse)
async def change_subscription_plan(
    request: ChangePlanRequest,
    token: str = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Change subscription plan (upgrade/downgrade)
    """
    try:
        current_user = auth_service.get_current_user(db, token.credentials)
        if not current_user:
            raise HTTPException(status_code=401, detail="Invalid token")

        # Mock current plan detection
        current_plan = "basic"  # In real app, get from user profile
        
        if current_plan == request.new_plan:
            raise HTTPException(status_code=400, detail="Already on this plan")

        # Calculate pricing
        plan_pricing = {
            "basic": {"monthly": 0, "yearly": 0},
            "pro": {"monthly": 9.99, "yearly": 99.99},
            "premium": {"monthly": 19.99, "yearly": 199.99},
            "enterprise": {"monthly": 49.99, "yearly": 499.99}
        }
        
        new_price = plan_pricing[request.new_plan][request.billing_cycle]
        current_price = plan_pricing[current_plan][request.billing_cycle]
        prorated_amount = new_price - current_price if new_price > current_price else None
        
        # Mock transaction creation
        transaction_id = f"plan_{uuid.uuid4().hex[:12]}"
        next_billing = datetime.now() + timedelta(days=30 if request.billing_cycle == "monthly" else 365)
        
        logger.info(f"Plan change: {current_plan} -> {request.new_plan} ({request.billing_cycle}) by user {current_user.id}")
        
        return ChangePlanResponse(
            transaction_id=transaction_id,
            old_plan=current_plan,
            new_plan=request.new_plan,
            billing_cycle=request.billing_cycle,
            next_billing_date=next_billing,
            prorated_amount=prorated_amount,
            status="completed"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error changing plan: {e}")
        raise HTTPException(status_code=500, detail="Failed to change plan")

@router.get("/transactions", response_model=TransactionsResponse)
async def get_transactions(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    type: Optional[str] = Query(None, description="Filter by type"),
    status: Optional[str] = Query(None, description="Filter by status"),
    start_date: Optional[datetime] = Query(None, description="Start date filter"),
    end_date: Optional[datetime] = Query(None, description="End date filter"),
    token: str = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Get user's transaction history with filtering
    """
    try:
        current_user = auth_service.get_current_user(db, token.credentials)
        if not current_user:
            raise HTTPException(status_code=401, detail="Invalid token")

        # Calculate offset
        offset = (page - 1) * limit
        
        # Mock transactions data
        transaction_types = ["receives_purchase", "plan_change", "refund", "adjustment"]
        statuses = ["completed", "pending", "failed", "refunded"]
        payment_methods = ["wechat_pay", "alipay", "credit_card", "paypal"]
        
        mock_transactions = []
        total_amount = 0
        
        for i in range(1, 101):  # 100 mock transactions
            transaction_type = transaction_types[i % len(transaction_types)]
            transaction_status = statuses[i % len(statuses)]
            amount = round([9.99, 19.99, 49.99, 99.99][i % 4], 2)
            
            if transaction_status == "completed":
                total_amount += amount
            
            mock_transactions.append({
                "id": f"txn_{i:06d}",
                "type": transaction_type,
                "amount": amount,
                "currency": "USD",
                "status": transaction_status,
                "description": f"Transaction description #{i}",
                "payment_method": payment_methods[i % len(payment_methods)],
                "created_at": datetime.now() - timedelta(days=i),
                "completed_at": datetime.now() - timedelta(days=i, hours=-2) if transaction_status == "completed" else None,
                "metadata": {"package_type": "standard"} if transaction_type == "receives_purchase" else None
            })
        
        # Apply filters
        filtered_transactions = mock_transactions
        if type:
            filtered_transactions = [t for t in filtered_transactions if t["type"] == type]
        if status:
            filtered_transactions = [t for t in filtered_transactions if t["status"] == status]
        if start_date:
            filtered_transactions = [t for t in filtered_transactions if t["created_at"] >= start_date]
        if end_date:
            filtered_transactions = [t for t in filtered_transactions if t["created_at"] <= end_date]
        
        # Apply pagination
        total_count = len(filtered_transactions)
        paginated_transactions = filtered_transactions[offset:offset + limit]
        
        return TransactionsResponse(
            transactions=[Transaction(**t) for t in paginated_transactions],
            total_count=total_count,
            page=page,
            limit=limit,
            has_more=offset + limit < total_count,
            total_amount=round(total_amount, 2),
            currency="USD"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting transactions: {e}")
        raise HTTPException(status_code=500, detail="Failed to get transactions")

@router.get("/methods", response_model=PaymentMethodsResponse)
async def get_payment_methods(
    token: str = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Get available payment methods for the user
    """
    try:
        current_user = auth_service.get_current_user(db, token.credentials)
        if not current_user:
            raise HTTPException(status_code=401, detail="Invalid token")

        # Mock payment methods
        methods = [
            {
                "id": "wechat_pay",
                "name": "WeChat Pay",
                "type": "wechat_pay",
                "enabled": True,
                "description": "Pay with WeChat",
                "icon": "https://icons.example.com/wechat.png",
                "fees": {"fixed": 0, "percentage": 2.9},
                "supported_currencies": ["CNY", "USD"]
            },
            {
                "id": "alipay",
                "name": "Alipay",
                "type": "alipay",
                "enabled": True,
                "description": "Pay with Alipay",
                "icon": "https://icons.example.com/alipay.png",
                "fees": {"fixed": 0, "percentage": 2.9},
                "supported_currencies": ["CNY", "USD"]
            },
            {
                "id": "credit_card",
                "name": "Credit Card",
                "type": "credit_card",
                "enabled": True,
                "description": "Visa, MasterCard, American Express",
                "icon": "https://icons.example.com/cards.png",
                "fees": {"fixed": 0.30, "percentage": 2.9},
                "supported_currencies": ["USD", "EUR", "CNY"]
            },
            {
                "id": "paypal",
                "name": "PayPal",
                "type": "paypal",
                "enabled": True,
                "description": "Pay with PayPal balance or linked account",
                "icon": "https://icons.example.com/paypal.png",
                "fees": {"fixed": 0.30, "percentage": 3.4},
                "supported_currencies": ["USD", "EUR"]
            }
        ]
        
        return PaymentMethodsResponse(
            methods=[PaymentMethod(**m) for m in methods],
            default_method_id="credit_card"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting payment methods: {e}")
        raise HTTPException(status_code=500, detail="Failed to get payment methods")

@router.post("/session", response_model=PaymentSession)
async def create_payment_session(
    request: CreatePaymentSessionRequest,
    token: str = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Create a payment session for processing payment
    """
    try:
        current_user = auth_service.get_current_user(db, token.credentials)
        if not current_user:
            raise HTTPException(status_code=401, detail="Invalid token")

        # Mock session creation
        session_id = f"sess_{uuid.uuid4().hex}"
        
        # Generate payment URL or QR code based on method
        payment_url = None
        qr_code = None
        
        if request.payment_method_id in ["wechat_pay", "alipay"]:
            qr_code = f"https://qr.example.com/{session_id}"
        else:
            payment_url = f"https://checkout.example.com/{session_id}"
        
        expires_at = datetime.now() + timedelta(minutes=15)  # 15-minute expiry
        
        logger.info(f"Created payment session {session_id} for {request.amount} {request.currency} by user {current_user.id}")
        
        return PaymentSession(
            session_id=session_id,
            payment_url=payment_url,
            qr_code=qr_code,
            expires_at=expires_at,
            status="created"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating payment session: {e}")
        raise HTTPException(status_code=500, detail="Failed to create payment session")

@router.get("/pricing", response_model=PricingResponse)
async def get_pricing(
    currency: str = Query("USD", pattern="^(USD|CNY|EUR)$"),
    token: str = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Get pricing information for receives and plans
    """
    try:
        current_user = auth_service.get_current_user(db, token.credentials)
        if not current_user:
            raise HTTPException(status_code=401, detail="Invalid token")

        # Mock receives packages
        receives_packages = [
            {
                "package_type": "basic",
                "amount": 50,
                "price": 25.0,
                "currency": currency,
                "savings_percentage": None,
                "popular": False,
                "bonus_receives": None
            },
            {
                "package_type": "standard",
                "amount": 100,
                "price": 40.0,
                "currency": currency,
                "savings_percentage": 20.0,
                "popular": True,
                "bonus_receives": 10
            },
            {
                "package_type": "premium",
                "amount": 200,
                "price": 60.0,
                "currency": currency,
                "savings_percentage": 40.0,
                "popular": False,
                "bonus_receives": 30
            }
        ]
        
        # Mock subscription plans
        subscription_plans = [
            {
                "plan": "basic",
                "name": "Basic",
                "monthly_price": 0.0,
                "yearly_price": 0.0,
                "currency": currency,
                "features": ["Limited swipes", "Basic matching"],
                "yearly_savings_percentage": 0.0,
                "popular": False
            },
            {
                "plan": "pro",
                "name": "Pro",
                "monthly_price": 9.99,
                "yearly_price": 99.99,
                "currency": currency,
                "features": ["Unlimited swipes", "Advanced matching", "See who likes you"],
                "yearly_savings_percentage": 16.7,
                "popular": True
            },
            {
                "plan": "premium",
                "name": "Premium",
                "monthly_price": 19.99,
                "yearly_price": 199.99,
                "currency": currency,
                "features": ["All Pro features", "Priority support", "Exclusive events"],
                "yearly_savings_percentage": 16.7,
                "popular": False
            }
        ]
        
        return PricingResponse(
            receives_packages=[ReceivesPricing(**p) for p in receives_packages],
            subscription_plans=[PlanPricing(**p) for p in subscription_plans],
            currency=currency,
            tax_rate=0.08 if currency == "USD" else None  # Mock tax rate
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting pricing: {e}")
        raise HTTPException(status_code=500, detail="Failed to get pricing")
