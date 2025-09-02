"""
Multi-Payment Service supporting WeChat Pay + International Cards
Handles both WeChat Pay (for Chinese users) and Stripe (for international users)
"""

import os
from typing import Dict, Optional
from enum import Enum
import stripe
from .payment_service import TencentWeChatPayService

class PaymentProvider(Enum):
    WECHAT_PAY = "wechat_pay"
    STRIPE = "stripe"
    PAYPAL = "paypal"

class MultiPaymentService:
    """
    Unified payment service supporting multiple payment providers
    """
    
    def __init__(self):
        # Initialize WeChat Pay
        self.wechat_service = TencentWeChatPayService()
        
        # Initialize Stripe
        stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
        self.stripe_publishable_key = os.getenv("STRIPE_PUBLISHABLE_KEY")
    
    def detect_payment_method(self, user_agent: str, region: str = None) -> PaymentProvider:
        """
        Auto-detect the best payment method based on user context
        """
        # WeChat browser or Chinese region
        if "MicroMessenger" in user_agent or region == "CN":
            return PaymentProvider.WECHAT_PAY
        
        # International users - use Stripe for Visa/Mastercard
        return PaymentProvider.STRIPE
    
    def create_membership_order(
        self, 
        user_id: int, 
        membership_type: str, 
        amount: int,
        payment_provider: PaymentProvider,
        **kwargs
    ) -> Dict:
        """
        Create payment order using the specified provider
        """
        
        if payment_provider == PaymentProvider.WECHAT_PAY:
            # Requires openid for WeChat Pay
            openid = kwargs.get("openid")
            if not openid:
                raise ValueError("WeChat Pay requires user openid")
            
            return self.wechat_service.create_membership_order(
                user_id=user_id,
                membership_type=membership_type,
                amount=amount,
                openid=openid
            )
        
        elif payment_provider == PaymentProvider.STRIPE:
            # Create Stripe Payment Intent for Visa/Mastercard
            return self._create_stripe_payment_intent(
                user_id=user_id,
                membership_type=membership_type,
                amount=amount
            )
        
        else:
            raise ValueError(f"Unsupported payment provider: {payment_provider}")
    
    def _create_stripe_payment_intent(
        self, 
        user_id: int, 
        membership_type: str, 
        amount: int
    ) -> Dict:
        """
        Create Stripe Payment Intent for credit card payments
        """
        try:
            # Convert amount from cents to dollars for Stripe
            stripe_amount = amount  # Stripe expects cents
            
            payment_intent = stripe.PaymentIntent.create(
                amount=stripe_amount,
                currency="usd",  # or "cny" for Chinese users
                payment_method_types=["card"],
                metadata={
                    "user_id": str(user_id),
                    "membership_type": membership_type,
                    "provider": "stripe"
                },
                description=f"Membership upgrade to {membership_type}"
            )
            
            return {
                "success": True,
                "provider": "stripe",
                "payment_intent_id": payment_intent.id,
                "client_secret": payment_intent.client_secret,
                "publishable_key": self.stripe_publishable_key,
                "amount": stripe_amount,
                "currency": "usd"
            }
            
        except stripe.error.StripeError as e:
            return {
                "success": False,
                "error": str(e),
                "provider": "stripe"
            }
    
    def verify_payment(
        self, 
        payment_provider: PaymentProvider, 
        payment_data: Dict
    ) -> Dict:
        """
        Verify payment completion regardless of provider
        """
        
        if payment_provider == PaymentProvider.WECHAT_PAY:
            return self.wechat_service.verify_payment_notification(payment_data)
        
        elif payment_provider == PaymentProvider.STRIPE:
            return self._verify_stripe_payment(payment_data)
        
        else:
            raise ValueError(f"Unsupported payment provider: {payment_provider}")
    
    def _verify_stripe_payment(self, payment_data: Dict) -> Dict:
        """
        Verify Stripe payment webhook
        """
        try:
            payment_intent_id = payment_data.get("payment_intent_id")
            payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            
            if payment_intent.status == "succeeded":
                return {
                    "success": True,
                    "transaction_id": payment_intent.id,
                    "user_id": int(payment_intent.metadata.get("user_id")),
                    "membership_type": payment_intent.metadata.get("membership_type"),
                    "amount": payment_intent.amount,
                    "provider": "stripe"
                }
            
            return {
                "success": False,
                "status": payment_intent.status,
                "provider": "stripe"
            }
            
        except stripe.error.StripeError as e:
            return {
                "success": False,
                "error": str(e),
                "provider": "stripe"
            }

# Global instance
multi_payment_service = MultiPaymentService()

def get_multi_payment_service() -> MultiPaymentService:
    return multi_payment_service
