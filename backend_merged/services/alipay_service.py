"""
Alipay Payment Service for Tencent Cloud Integration
Supports membership payments through Alipay
"""

import hashlib
import json
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, Optional
import requests
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256
import base64

from config.settings import settings
from models.payments import MembershipTransaction, PaymentMethod
from services.membership_service import MembershipService
from dependencies.db import get_db


class TencentAlipayService:
    """
    Alipay payment service integrated with Tencent Cloud
    """
    
    def __init__(self):
        self.app_id = settings.ALIPAY_APP_ID
        self.private_key = settings.ALIPAY_PRIVATE_KEY
        self.alipay_public_key = settings.ALIPAY_PUBLIC_KEY
        self.partner_id = settings.ALIPAY_PARTNER_ID
        self.gateway_url = "https://openapi.alipay.com/gateway.do"
        self.notify_url = settings.ALIPAY_NOTIFY_URL
        self.return_url = settings.ALIPAY_RETURN_URL
        
        self.membership_service = MembershipService()
    
    def _generate_sign(self, params: dict) -> str:
        """Generate RSA signature for Alipay API"""
        # Sort parameters
        sorted_params = sorted(params.items())
        
        # Create sign string
        sign_string = "&".join([f"{k}={v}" for k, v in sorted_params if v])
        
        # Sign with RSA private key
        rsa_key = RSA.importKey(self.private_key)
        signer = PKCS1_v1_5.new(rsa_key)
        digest = SHA256.new(sign_string.encode('utf-8'))
        signature = signer.sign(digest)
        
        return base64.b64encode(signature).decode('utf-8')
    
    def _verify_sign(self, params: dict, signature: str) -> bool:
        """Verify Alipay notification signature"""
        # Remove sign and sign_type from params
        verify_params = {k: v for k, v in params.items() 
                        if k not in ['sign', 'sign_type']}
        
        # Sort parameters
        sorted_params = sorted(verify_params.items())
        
        # Create verify string
        verify_string = "&".join([f"{k}={v}" for k, v in sorted_params if v])
        
        # Verify with Alipay public key
        try:
            rsa_key = RSA.importKey(self.alipay_public_key)
            verifier = PKCS1_v1_5.new(rsa_key)
            digest = SHA256.new(verify_string.encode('utf-8'))
            return verifier.verify(digest, base64.b64decode(signature))
        except Exception:
            return False
    
    def create_membership_order(self, user_id: int, membership_type: str, 
                               amount: int, subject: str = None) -> Dict:
        """
        Create Alipay order for membership payment
        
        Args:
            user_id: User ID
            membership_type: 'PAID' or 'PREMIUM'
            amount: Amount in cents (分)
            subject: Order subject/description
            
        Returns:
            Dictionary with payment URL and order info
        """
        try:
            # Generate unique order number
            out_trade_no = f"ALIPAY_{int(time.time())}_{user_id}_{uuid.uuid4().hex[:8]}"
            
            # Create transaction record
            db = next(get_db())
            transaction = MembershipTransaction(
                user_id=user_id,
                order_number=out_trade_no,
                provider=PaymentProvider.ALIPAY,
                membership_type=membership_type,
                amount=amount,
                currency="CNY",
                status="PENDING"
            )
            db.add(transaction)
            db.commit()
            
            # Prepare Alipay parameters
            biz_content = {
                "out_trade_no": out_trade_no,
                "product_code": "FAST_INSTANT_TRADE_PAY",
                "total_amount": f"{amount / 100:.2f}",  # Convert cents to yuan
                "subject": subject or f"Ques会员服务 - {membership_type}",
                "body": f"用户 {user_id} 购买 {membership_type} 会员",
                "timeout_express": "30m"
            }
            
            # Base parameters
            params = {
                "app_id": self.app_id,
                "method": "alipay.trade.page.pay",
                "charset": "utf-8",
                "sign_type": "RSA2",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "version": "1.0",
                "notify_url": self.notify_url,
                "return_url": self.return_url,
                "biz_content": json.dumps(biz_content, ensure_ascii=False)
            }
            
            # Generate signature
            params["sign"] = self._generate_sign(params)
            
            # Create payment URL
            payment_url = f"{self.gateway_url}?" + "&".join([
                f"{k}={requests.utils.quote(str(v), safe='')}" 
                for k, v in params.items()
            ])
            
            return {
                "success": True,
                "order_id": transaction.transaction_id,
                "out_trade_no": out_trade_no,
                "payment_url": payment_url,
                "payment_method": "ALIPAY_PAGE",
                "expires_at": (datetime.now() + timedelta(minutes=30)).isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to create Alipay order: {str(e)}"
            }
    
    def create_qr_payment(self, user_id: int, membership_type: str, 
                         amount: int, subject: str = None) -> Dict:
        """
        Create Alipay QR code payment for PC/Desktop users
        """
        try:
            # Generate unique order number
            out_trade_no = f"ALIPAY_QR_{int(time.time())}_{user_id}_{uuid.uuid4().hex[:8]}"
            
            # Create transaction record
            db = next(get_db())
            transaction = MembershipTransaction(
                user_id=user_id,
                order_number=out_trade_no,
                provider=PaymentProvider.ALIPAY,
                membership_type=membership_type,
                amount=amount,
                currency="CNY",
                status="PENDING"
            )
            db.add(transaction)
            db.commit()
            
            # Prepare Alipay parameters for QR code
            biz_content = {
                "out_trade_no": out_trade_no,
                "total_amount": f"{amount / 100:.2f}",
                "subject": subject or f"Ques会员服务 - {membership_type}",
                "store_id": "QUES_STORE_001",
                "timeout_express": "30m"
            }
            
            params = {
                "app_id": self.app_id,
                "method": "alipay.trade.precreate",
                "charset": "utf-8",
                "sign_type": "RSA2",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "version": "1.0",
                "notify_url": self.notify_url,
                "biz_content": json.dumps(biz_content, ensure_ascii=False)
            }
            
            # Generate signature
            params["sign"] = self._generate_sign(params)
            
            # Call Alipay API
            response = requests.post(self.gateway_url, data=params)
            result = response.json()
            
            if result.get("alipay_trade_precreate_response", {}).get("code") == "10000":
                qr_code = result["alipay_trade_precreate_response"]["qr_code"]
                
                return {
                    "success": True,
                    "order_id": transaction.transaction_id,
                    "out_trade_no": out_trade_no,
                    "qr_code": qr_code,
                    "payment_method": "ALIPAY_QR",
                    "expires_at": (datetime.now() + timedelta(minutes=30)).isoformat()
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to create Alipay QR payment"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to create Alipay QR payment: {str(e)}"
            }
    
    def handle_payment_notification(self, params: dict) -> Dict:
        """
        Handle Alipay payment notification
        """
        try:
            # Verify signature
            signature = params.get("sign", "")
            if not self._verify_sign(params, signature):
                return {"success": False, "error": "Invalid signature"}
            
            # Get payment info
            out_trade_no = params.get("out_trade_no")
            trade_status = params.get("trade_status")
            total_amount = float(params.get("total_amount", 0))
            
            # Find transaction
            db = next(get_db())
            transaction = db.query(MembershipTransaction).filter(
                MembershipTransaction.order_number == out_trade_no
            ).first()
            
            if not transaction:
                return {"success": False, "error": "Transaction not found"}
            
            # Update transaction status
            if trade_status == "TRADE_SUCCESS":
                transaction.status = "COMPLETED"
                transaction.paid_at = datetime.now()
                transaction.provider_transaction_id = params.get("trade_no")
                
                # Upgrade user membership
                self.membership_service.upgrade_membership(
                    user_id=transaction.user_id,
                    membership_type=transaction.membership_type,
                    payment_method="ALIPAY"
                )
                
                db.commit()
                return {"success": True, "message": "Payment completed"}
                
            elif trade_status in ["TRADE_CLOSED", "TRADE_FINISHED"]:
                transaction.status = "CANCELLED"
                db.commit()
                return {"success": True, "message": "Payment cancelled"}
            
            return {"success": True, "message": "Notification processed"}
            
        except Exception as e:
            return {"success": False, "error": f"Failed to process notification: {str(e)}"}
    
    def query_payment_status(self, out_trade_no: str) -> Dict:
        """
        Query Alipay payment status
        """
        try:
            biz_content = {
                "out_trade_no": out_trade_no
            }
            
            params = {
                "app_id": self.app_id,
                "method": "alipay.trade.query",
                "charset": "utf-8",
                "sign_type": "RSA2",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "version": "1.0",
                "biz_content": json.dumps(biz_content)
            }
            
            params["sign"] = self._generate_sign(params)
            
            response = requests.post(self.gateway_url, data=params)
            result = response.json()
            
            if result.get("alipay_trade_query_response", {}).get("code") == "10000":
                query_result = result["alipay_trade_query_response"]
                trade_status = query_result.get("trade_status", "UNKNOWN")
                
                status_mapping = {
                    "WAIT_BUYER_PAY": "PENDING",
                    "TRADE_SUCCESS": "COMPLETED", 
                    "TRADE_FINISHED": "COMPLETED",
                    "TRADE_CLOSED": "CANCELLED"
                }
                
                return {
                    "success": True,
                    "status": status_mapping.get(trade_status, "UNKNOWN"),
                    "trade_status": trade_status,
                    "total_amount": query_result.get("total_amount"),
                    "trade_no": query_result.get("trade_no")
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to query payment status"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to query payment: {str(e)}"
            }


# Service instance
alipay_service = TencentAlipayService()
