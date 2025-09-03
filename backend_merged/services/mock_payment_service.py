"""
Mock Payment Service for Development/Testing
Use this while waiting for real WeChat Pay credentials
"""

from datetime import datetime, timedelta
import uuid
import json
import random
from typing import Dict, Any, Optional
import asyncio

class MockPaymentService:
    """
    Mock payment service that simulates WeChat Pay behavior
    Useful for development and testing without real credentials
    """
    
    def __init__(self):
        self.payments = {}  # In-memory storage for mock payments
        self.mock_delay = 2  # Simulate API delay
    
    async def create_payment_order(
        self,
        amount: float,
        description: str,
        user_id: str,
        payment_method: str = "wechat_pay"
    ) -> Dict[str, Any]:
        """
        Create a mock payment order
        """
        await asyncio.sleep(self.mock_delay)  # Simulate API delay
        
        payment_id = str(uuid.uuid4())
        order_id = f"MOCK_{int(datetime.now().timestamp())}"
        
        # Simulate different payment methods
        if payment_method == "wechat_pay":
            qr_code_url = f"weixin://wxpay/bizpayurl?pr={payment_id}"
            pay_url = f"https://wx.tenpay.com/cgi-bin/mmpayweb-bin/checkmweb?prepay_id={payment_id}"
        elif payment_method == "alipay":
            qr_code_url = f"https://qr.alipay.com/bax12345?t={payment_id}"
            pay_url = f"https://openapi.alipay.com/gateway.do?prepay_id={payment_id}"
        else:
            qr_code_url = f"https://mock-payment.com/qr/{payment_id}"
            pay_url = f"https://mock-payment.com/pay/{payment_id}"
        
        payment_data = {
            "payment_id": payment_id,
            "order_id": order_id,
            "amount": amount,
            "description": description,
            "user_id": user_id,
            "payment_method": payment_method,
            "status": "pending",
            "qr_code_url": qr_code_url,
            "pay_url": pay_url,
            "created_at": datetime.now().isoformat(),
            "expires_at": (datetime.now() + timedelta(minutes=30)).isoformat()
        }
        
        self.payments[payment_id] = payment_data
        
        print(f"🎭 MOCK PAYMENT: Created {payment_method} order {order_id} for ¥{amount}")
        
        return {
            "success": True,
            "payment_id": payment_id,
            "order_id": order_id,
            "qr_code_url": qr_code_url,
            "pay_url": pay_url,
            "amount": amount,
            "currency": "CNY",
            "status": "pending",
            "expires_at": payment_data["expires_at"]
        }
    
    async def check_payment_status(self, payment_id: str) -> Dict[str, Any]:
        """
        Check mock payment status
        Randomly simulates payment completion for testing
        """
        await asyncio.sleep(1)  # Simulate API delay
        
        if payment_id not in self.payments:
            return {
                "success": False,
                "error": "Payment not found",
                "status": "not_found"
            }
        
        payment = self.payments[payment_id]
        
        # Simulate random payment completion (30% chance)
        if payment["status"] == "pending" and random.random() < 0.3:
            payment["status"] = "completed"
            payment["completed_at"] = datetime.now().isoformat()
            payment["transaction_id"] = f"TXN_{int(datetime.now().timestamp())}"
            print(f"🎭 MOCK PAYMENT: Order {payment['order_id']} completed!")
        
        # Simulate expiration
        expires_at = datetime.fromisoformat(payment["expires_at"])
        if datetime.now() > expires_at and payment["status"] == "pending":
            payment["status"] = "expired"
            print(f"🎭 MOCK PAYMENT: Order {payment['order_id']} expired")
        
        return {
            "success": True,
            "payment_id": payment_id,
            "status": payment["status"],
            "amount": payment["amount"],
            "order_id": payment["order_id"],
            "transaction_id": payment.get("transaction_id"),
            "completed_at": payment.get("completed_at")
        }
    
    async def simulate_payment_callback(self, payment_id: str) -> Dict[str, Any]:
        """
        Manually trigger payment completion for testing
        """
        if payment_id not in self.payments:
            return {"success": False, "error": "Payment not found"}
        
        payment = self.payments[payment_id]
        if payment["status"] != "pending":
            return {"success": False, "error": f"Payment already {payment['status']}"}
        
        payment["status"] = "completed"
        payment["completed_at"] = datetime.now().isoformat()
        payment["transaction_id"] = f"TXN_{int(datetime.now().timestamp())}"
        
        print(f"🎭 MOCK PAYMENT: Manually completed order {payment['order_id']}")
        
        return {
            "success": True,
            "payment_id": payment_id,
            "status": "completed",
            "transaction_id": payment["transaction_id"]
        }
    
    def list_payments(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        List all mock payments (for debugging)
        """
        payments = list(self.payments.values())
        
        if user_id:
            payments = [p for p in payments if p["user_id"] == user_id]
        
        return {
            "success": True,
            "payments": payments,
            "total": len(payments)
        }
    
    def clear_payments(self) -> Dict[str, Any]:
        """
        Clear all mock payments (for testing)
        """
        count = len(self.payments)
        self.payments.clear()
        print(f"🎭 MOCK PAYMENT: Cleared {count} mock payments")
        return {"success": True, "cleared": count}

# Global instance for use in FastAPI
mock_payment_service = MockPaymentService()

# Test functions
async def test_mock_payment():
    """Test the mock payment service"""
    print("🧪 Testing Mock Payment Service...\n")
    
    # Create a payment
    result = await mock_payment_service.create_payment_order(
        amount=99.99,
        description="Premium Membership",
        user_id="test_user_123",
        payment_method="wechat_pay"
    )
    
    print(f"✅ Created payment: {json.dumps(result, indent=2)}\n")
    
    payment_id = result["payment_id"]
    
    # Check status a few times
    for i in range(5):
        status = await mock_payment_service.check_payment_status(payment_id)
        print(f"📊 Status check {i+1}: {status['status']}")
        
        if status["status"] == "completed":
            print(f"🎉 Payment completed! Transaction ID: {status.get('transaction_id')}")
            break
        
        await asyncio.sleep(2)
    
    # If still pending, manually complete it
    if status["status"] == "pending":
        print("\n🔧 Manually completing payment...")
        result = await mock_payment_service.simulate_payment_callback(payment_id)
        print(f"✅ Manual completion result: {json.dumps(result, indent=2)}")
    
    # List all payments
    all_payments = mock_payment_service.list_payments()
    print(f"\n📋 Total payments: {all_payments['total']}")

if __name__ == "__main__":
    asyncio.run(test_mock_payment())
