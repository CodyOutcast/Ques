"""
Tencent Cloud WeChat Pay Service for Membership Payments
Integrates with WeChat Pay API for processing membership subscriptions
"""

import os
import json
import time
import hmac
import hashlib
import base64
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Tuple
from enum import Enum
import aiohttp
import asyncio
from sqlalchemy.orm import Session

# Tencent Cloud SDK imports
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.cpdp.v20190820 import cpdp_client, models as cpdp_models

from config.settings import settings

# Import mock payment service for development
try:
    from services.mock_payment_service import mock_payment_service
    MOCK_AVAILABLE = True
except ImportError:
    MOCK_AVAILABLE = False

logger = logging.getLogger(__name__)

class PaymentStatus(Enum):
    """Payment status enumeration"""
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"

class MembershipPlan(Enum):
    """Membership plan types with pricing"""
    MONTHLY = {
        "name": "monthly",
        "display_name": "Monthly Pro",
        "price": 29.99,  # CNY
        "duration_days": 30,
        "description": "Unlimited swipes, unlimited project cards (10/day), unlimited ideas (30/hour)"
    }
    YEARLY = {
        "name": "yearly", 
        "display_name": "Yearly Pro",
        "price": 299.99,  # CNY (10 months price)
        "duration_days": 365,
        "description": "Same as monthly but with 2 months free!"
    }

class TencentWeChatPayService:
    """Tencent Cloud WeChat Pay integration for membership payments"""
    
    def __init__(self):
        # Tencent Cloud credentials
        self.secret_id = os.getenv("TENCENT_SECRET_ID")
        self.secret_key = os.getenv("TENCENT_SECRET_KEY")
        self.region = os.getenv("TENCENT_REGION", "ap-guangzhou")
        
        # WeChat Pay merchant configuration
        self.mch_id = os.getenv("WECHAT_PAY_MCH_ID")  # Merchant ID
        self.app_id = os.getenv("WECHAT_APP_ID")  # WeChat App ID
        self.api_key = os.getenv("WECHAT_PAY_API_KEY")  # API key for signing
        self.notify_url = os.getenv("WECHAT_PAY_NOTIFY_URL", "https://ques.chat/api/v1/payments/notify")
        
        # Payment configuration
        self.pay_host = "api.mch.weixin.qq.com"
        self.is_sandbox = os.getenv("WECHAT_PAY_SANDBOX", "false").lower() == "true"
        
        if self.is_sandbox:
            self.pay_host = "api.mch.weixin.qq.com/sandboxnew"
            logger.info("Using WeChat Pay sandbox environment")
        
        # Validate configuration
        if not all([self.secret_id, self.secret_key, self.mch_id, self.app_id, self.api_key]):
            logger.warning("WeChat Pay configuration incomplete - some features may not work")
        
        logger.info(f"WeChat Pay service initialized for merchant: {self.mch_id}")

    def _generate_nonce_str(self) -> str:
        """Generate random nonce string"""
        import random
        import string
        return ''.join(random.choices(string.ascii_letters + string.digits, k=32))

    def _generate_sign(self, params: Dict[str, Any]) -> str:
        """Generate WeChat Pay signature"""
        # Sort parameters
        sorted_params = sorted(params.items())
        
        # Create string to sign
        string_to_sign = "&".join([f"{k}={v}" for k, v in sorted_params if v])
        string_to_sign += f"&key={self.api_key}"
        
        # Generate MD5 hash
        sign = hashlib.md5(string_to_sign.encode('utf-8')).hexdigest().upper()
        return sign

    def _create_order_params(self, user_id: int, plan: MembershipPlan, order_id: str) -> Dict[str, Any]:
        """Create WeChat Pay unified order parameters"""
        plan_info = plan.value
        
        # Convert price to fen (smallest unit)
        total_fee = int(plan_info["price"] * 100)
        
        params = {
            "appid": self.app_id,
            "mch_id": self.mch_id,
            "nonce_str": self._generate_nonce_str(),
            "body": f"Ques Premium - {plan_info['display_name']}",
            "detail": plan_info["description"],
            "out_trade_no": order_id,
            "total_fee": str(total_fee),
            "spbill_create_ip": "127.0.0.1",  # Will be updated with actual IP
            "notify_url": self.notify_url,
            "trade_type": "JSAPI",  # For WeChat browser payment
            "time_start": datetime.now().strftime("%Y%m%d%H%M%S"),
            "time_expire": (datetime.now() + timedelta(minutes=30)).strftime("%Y%m%d%H%M%S"),
            "attach": json.dumps({
                "user_id": user_id,
                "plan": plan.name,
                "membership_type": "paid"
            })
        }
        
        # Add signature
        params["sign"] = self._generate_sign(params)
        return params

    async def create_payment_order(self, user_id: int, plan: MembershipPlan, user_ip: str = "127.0.0.1") -> Dict[str, Any]:
        """Create a WeChat Pay order for membership purchase"""
        
        # Check if real credentials are available
        if not all([self.secret_id, self.secret_key, self.mch_id, self.app_id, self.api_key]):
            if MOCK_AVAILABLE:
                logger.warning("Using mock payment service - real WeChat Pay credentials not configured")
                plan_info = plan.value
                return await mock_payment_service.create_payment_order(
                    amount=plan_info["price"],
                    description=f"Ques Premium - {plan_info['display_name']}",
                    user_id=str(user_id),
                    payment_method="wechat_pay"
                )
            else:
                return {
                    "success": False,
                    "error": "WeChat Pay credentials not configured and mock service not available"
                }
        
        try:
            # Generate unique order ID
            order_id = f"QUES_MEMBERSHIP_{user_id}_{int(time.time())}_{plan.name}"
            
            # Create order parameters
            params = self._create_order_params(user_id, plan, order_id)
            params["spbill_create_ip"] = user_ip
            
            # Convert to XML
            xml_data = self._dict_to_xml(params)
            
            # Make API request
            async with aiohttp.ClientSession() as session:
                url = f"https://{self.pay_host}/pay/unifiedorder"
                
                async with session.post(
                    url,
                    data=xml_data,
                    headers={"Content-Type": "application/xml"}
                ) as response:
                    response_text = await response.text()
                    result = self._xml_to_dict(response_text)
                    
                    if result.get("return_code") == "SUCCESS" and result.get("result_code") == "SUCCESS":
                        # Prepare JSAPI payment parameters
                        prepay_id = result["prepay_id"]
                        js_api_params = self._prepare_jsapi_params(prepay_id)
                        
                        return {
                            "success": True,
                            "order_id": order_id,
                            "prepay_id": prepay_id,
                            "payment_params": js_api_params,
                            "total_fee": params["total_fee"],
                            "plan": plan.name,
                            "expires_at": params["time_expire"]
                        }
                    else:
                        error_msg = result.get("err_code_des", "Payment order creation failed")
                        logger.error(f"WeChat Pay order creation failed: {error_msg}")
                        return {
                            "success": False,
                            "error": error_msg,
                            "error_code": result.get("err_code")
                        }
                        
        except Exception as e:
            logger.error(f"Error creating WeChat Pay order: {e}")
            return {
                "success": False,
                "error": f"Payment service error: {str(e)}"
            }

    def _prepare_jsapi_params(self, prepay_id: str) -> Dict[str, str]:
        """Prepare JSAPI payment parameters for frontend"""
        timestamp = str(int(time.time()))
        nonce_str = self._generate_nonce_str()
        
        params = {
            "appId": self.app_id,
            "timeStamp": timestamp,
            "nonceStr": nonce_str,
            "package": f"prepay_id={prepay_id}",
            "signType": "MD5"
        }
        
        # Generate paySign
        params["paySign"] = self._generate_sign(params)
        
        return params

    async def verify_payment_notification(self, xml_data: str) -> Dict[str, Any]:
        """Verify WeChat Pay payment notification"""
        try:
            # Parse XML
            result = self._xml_to_dict(xml_data)
            
            # Verify signature
            received_sign = result.pop("sign", "")
            calculated_sign = self._generate_sign(result)
            
            if received_sign != calculated_sign:
                logger.error("WeChat Pay notification signature verification failed")
                return {"success": False, "error": "Invalid signature"}
            
            # Check if payment is successful
            if result.get("return_code") == "SUCCESS" and result.get("result_code") == "SUCCESS":
                # Parse attach data
                attach_data = json.loads(result.get("attach", "{}"))
                
                return {
                    "success": True,
                    "order_id": result["out_trade_no"],
                    "transaction_id": result["transaction_id"],
                    "total_fee": int(result["total_fee"]),
                    "user_id": attach_data.get("user_id"),
                    "plan": attach_data.get("plan"),
                    "payment_time": result.get("time_end"),
                    "attach_data": attach_data
                }
            else:
                error_msg = result.get("err_code_des", "Payment failed")
                return {
                    "success": False,
                    "error": error_msg,
                    "order_id": result.get("out_trade_no")
                }
                
        except Exception as e:
            logger.error(f"Error verifying payment notification: {e}")
            return {"success": False, "error": str(e)}

    async def query_payment_status(self, order_id: str) -> Dict[str, Any]:
        """Query payment status from WeChat Pay"""
        
        # Check if using mock service
        if not all([self.secret_id, self.secret_key, self.mch_id, self.app_id, self.api_key]):
            if MOCK_AVAILABLE:
                # Extract payment_id from order_id for mock service
                if order_id.startswith("QUES_MEMBERSHIP_"):
                    # For real orders, we need to map order_id to payment_id
                    # This is a limitation of the mock service
                    logger.warning("Mock service: Cannot query status for real order_id. Use payment_id instead.")
                    return {
                        "success": False,
                        "error": "Use payment_id for mock service status queries"
                    }
                else:
                    # Assume it's a payment_id for mock service
                    return await mock_payment_service.check_payment_status(order_id)
            else:
                return {
                    "success": False,
                    "error": "WeChat Pay credentials not configured and mock service not available"
                }
        
        try:
            params = {
                "appid": self.app_id,
                "mch_id": self.mch_id,
                "out_trade_no": order_id,
                "nonce_str": self._generate_nonce_str()
            }
            
            params["sign"] = self._generate_sign(params)
            xml_data = self._dict_to_xml(params)
            
            async with aiohttp.ClientSession() as session:
                url = f"https://{self.pay_host}/pay/orderquery"
                
                async with session.post(
                    url,
                    data=xml_data,
                    headers={"Content-Type": "application/xml"}
                ) as response:
                    response_text = await response.text()
                    result = self._xml_to_dict(response_text)
                    
                    if result.get("return_code") == "SUCCESS":
                        trade_state = result.get("trade_state")
                        
                        return {
                            "success": True,
                            "order_id": order_id,
                            "trade_state": trade_state,
                            "trade_state_desc": result.get("trade_state_desc"),
                            "transaction_id": result.get("transaction_id"),
                            "total_fee": result.get("total_fee"),
                            "is_paid": trade_state == "SUCCESS"
                        }
                    else:
                        return {
                            "success": False,
                            "error": result.get("return_msg", "Query failed")
                        }
                        
        except Exception as e:
            logger.error(f"Error querying payment status: {e}")
            return {"success": False, "error": str(e)}

    def _dict_to_xml(self, data: Dict[str, Any]) -> str:
        """Convert dictionary to XML format"""
        xml_items = []
        for key, value in data.items():
            xml_items.append(f"<{key}>{value}</{key}>")
        return f"<xml>{''.join(xml_items)}</xml>"

    def _xml_to_dict(self, xml_str: str) -> Dict[str, str]:
        """Convert XML to dictionary"""
        import xml.etree.ElementTree as ET
        
        try:
            root = ET.fromstring(xml_str)
            result = {}
            for child in root:
                result[child.tag] = child.text or ""
            return result
        except ET.ParseError as e:
            logger.error(f"XML parsing error: {e}")
            return {}

    def get_membership_plans(self) -> Dict[str, Any]:
        """Get available membership plans"""
        return {
            "plans": [
                {
                    "id": "monthly",
                    "name": MembershipPlan.MONTHLY.value["display_name"],
                    "price": MembershipPlan.MONTHLY.value["price"],
                    "duration_days": MembershipPlan.MONTHLY.value["duration_days"],
                    "description": MembershipPlan.MONTHLY.value["description"],
                    "savings": 0
                },
                {
                    "id": "yearly",
                    "name": MembershipPlan.YEARLY.value["display_name"],
                    "price": MembershipPlan.YEARLY.value["price"],
                    "duration_days": MembershipPlan.YEARLY.value["duration_days"],
                    "description": MembershipPlan.YEARLY.value["description"],
                    "savings": round((MembershipPlan.MONTHLY.value["price"] * 12) - MembershipPlan.YEARLY.value["price"], 2)
                }
            ],
            "currency": "CNY",
            "features": [
                "Unlimited swipes per day (with 30/hour rate limit)",
                "Unlimited project cards (10 creations per day)",
                "Unlimited AI project ideas (30 generations per hour)",
                "Priority customer support",
                "Early access to new features"
            ]
        }

# Global payment service instance
payment_service = None

def get_payment_service() -> TencentWeChatPayService:
    """Get payment service instance (singleton pattern)"""
    global payment_service
    if payment_service is None:
        payment_service = TencentWeChatPayService()
    return payment_service
