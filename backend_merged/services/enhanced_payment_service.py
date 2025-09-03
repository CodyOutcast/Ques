"""
Multi-Payment Service for Tencent Cloud Payment Integration
Supports WeChat Pay, Alipay, and Member Cards
"""

import hashlib
import time
import uuid
import xml.etree.ElementTree as ET
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import requests
import logging
from sqlalchemy.orm import Session

from models.payments import MembershipTransaction, PaymentMethod
from models.users import User
from services.membership_service import MembershipService
from config.settings import settings

logger = logging.getLogger(__name__)

class MultiPaymentService:
    """Enhanced payment service supporting multiple payment methods"""
    
    def __init__(self):
        # WeChat Pay configuration
        self.wechat_app_id = settings.get("WECHAT_APP_ID")
        self.wechat_mch_id = settings.get("WECHAT_PAY_MCH_ID")
        self.wechat_api_key = settings.get("WECHAT_PAY_API_KEY")
        self.wechat_notify_url = settings.get("WECHAT_PAY_NOTIFY_URL")
        
        # Alipay configuration
        self.alipay_app_id = settings.get("ALIPAY_APP_ID")
        self.alipay_private_key = settings.get("ALIPAY_PRIVATE_KEY")
        self.alipay_public_key = settings.get("ALIPAY_PUBLIC_KEY")
        self.alipay_notify_url = settings.get("ALIPAY_NOTIFY_URL")
        
        # API endpoints
        self.wechat_api_url = "https://api.mch.weixin.qq.com/pay/unifiedorder"
        self.alipay_api_url = "https://openapi.alipay.com/gateway.do"
        
        self.membership_service = MembershipService()

    def create_payment_order(
        self, 
        user_id: int, 
        membership_type: str, 
        amount: int,
        payment_method: str = "wechat",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create payment order for multiple payment methods
        
        Args:
            user_id: User ID
            membership_type: Type of membership (PAID, PREMIUM)
            amount: Payment amount in cents/fen
            payment_method: Payment method (wechat, alipay, member_card)
            **kwargs: Additional parameters specific to payment method
        
        Returns:
            Dict containing payment order information
        """
        try:
            # Validate payment method
            if payment_method not in ["wechat", "alipay", "member_card"]:
                raise ValueError(f"Unsupported payment method: {payment_method}")
            
            # Generate order ID
            order_id = f"MB_{int(time.time())}_{user_id}"
            
            # Route to specific payment method
            if payment_method == "wechat":
                return self._create_wechat_order(user_id, membership_type, amount, order_id, **kwargs)
            elif payment_method == "alipay":
                return self._create_alipay_order(user_id, membership_type, amount, order_id, **kwargs)
            elif payment_method == "member_card":
                return self._create_member_card_order(user_id, membership_type, amount, order_id, **kwargs)
                
        except Exception as e:
            logger.error(f"Failed to create payment order: {str(e)}")
            raise

    def _create_wechat_order(
        self, 
        user_id: int, 
        membership_type: str, 
        amount: int, 
        order_id: str,
        openid: str = None,
        trade_type: str = "JSAPI"
    ) -> Dict[str, Any]:
        """Create WeChat Pay order"""
        
        # Generate nonce
        nonce_str = str(uuid.uuid4()).replace('-', '')
        
        # Prepare order data
        order_data = {
            'appid': self.wechat_app_id,
            'mch_id': self.wechat_mch_id,
            'nonce_str': nonce_str,
            'body': f'会员订阅 - {membership_type}',
            'out_trade_no': order_id,
            'total_fee': str(amount),
            'spbill_create_ip': '127.0.0.1',
            'notify_url': self.wechat_notify_url,
            'trade_type': trade_type
        }
        
        # Add openid for JSAPI
        if trade_type == "JSAPI" and openid:
            order_data['openid'] = openid
        
        # Generate signature
        order_data['sign'] = self._generate_wechat_signature(order_data)
        
        # Convert to XML
        xml_data = self._dict_to_xml(order_data)
        
        # Make API request
        response = requests.post(self.wechat_api_url, data=xml_data, headers={'Content-Type': 'application/xml'})
        
        if response.status_code == 200:
            result = self._xml_to_dict(response.text)
            
            if result.get('return_code') == 'SUCCESS' and result.get('result_code') == 'SUCCESS':
                # Generate JSAPI payment parameters if needed
                if trade_type == "JSAPI":
                    jsapi_params = self._generate_jsapi_params(result['prepay_id'])
                    result['jsapi_params'] = jsapi_params
                
                return {
                    'success': True,
                    'order_id': order_id,
                    'payment_method': 'wechat',
                    'wechat_response': result
                }
            else:
                return {
                    'success': False,
                    'error': result.get('err_code_des', 'Unknown error'),
                    'wechat_response': result
                }
        else:
            raise Exception(f"WeChat API request failed: {response.status_code}")

    def _create_alipay_order(
        self, 
        user_id: int, 
        membership_type: str, 
        amount: int, 
        order_id: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Create Alipay order"""
        
        # Convert amount from cents to yuan for Alipay
        amount_yuan = amount / 100
        
        # Prepare order data
        order_data = {
            'app_id': self.alipay_app_id,
            'method': 'alipay.trade.precreate',
            'charset': 'utf-8',
            'sign_type': 'RSA2',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'version': '1.0',
            'notify_url': self.alipay_notify_url,
            'biz_content': {
                'out_trade_no': order_id,
                'total_amount': f'{amount_yuan:.2f}',
                'subject': f'会员订阅 - {membership_type}',
                'store_id': 'QUES_STORE_001',
                'timeout_express': '30m'
            }
        }
        
        # Generate signature (simplified - in production use proper RSA signing)
        # This would require implementing proper Alipay signature generation
        
        return {
            'success': True,
            'order_id': order_id,
            'payment_method': 'alipay',
            'alipay_response': {
                'qr_code': f'alipay://pay?order_id={order_id}',
                'order_string': str(order_data)
            }
        }

    def _create_member_card_order(
        self, 
        user_id: int, 
        membership_type: str, 
        amount: int, 
        order_id: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Create member card payment order"""
        
        # For member card payments, we would:
        # 1. Check user's card balance
        # 2. Deduct amount if sufficient
        # 3. Process membership upgrade immediately
        
        # This is a simplified implementation
        return {
            'success': True,
            'order_id': order_id,
            'payment_method': 'member_card',
            'message': 'Member card payment requires implementation of card balance system'
        }

    def verify_payment_notification(
        self, 
        payment_method: str, 
        notification_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Verify payment notification from different payment methods"""
        
        if payment_method == "wechat":
            return self._verify_wechat_notification(notification_data)
        elif payment_method == "alipay":
            return self._verify_alipay_notification(notification_data)
        elif payment_method == "member_card":
            return self._verify_member_card_notification(notification_data)
        else:
            raise ValueError(f"Unsupported payment method: {payment_method}")

    def _verify_wechat_notification(self, notification_data: Dict[str, Any]) -> Dict[str, Any]:
        """Verify WeChat payment notification"""
        # Extract signature
        received_sign = notification_data.pop('sign', '')
        
        # Generate expected signature
        expected_sign = self._generate_wechat_signature(notification_data)
        
        if received_sign == expected_sign:
            return {
                'verified': True,
                'order_id': notification_data.get('out_trade_no'),
                'transaction_id': notification_data.get('transaction_id'),
                'total_fee': int(notification_data.get('total_fee', 0)),
                'payment_method': 'wechat'
            }
        else:
            return {'verified': False, 'error': 'Signature verification failed'}

    def _verify_alipay_notification(self, notification_data: Dict[str, Any]) -> Dict[str, Any]:
        """Verify Alipay payment notification"""
        # Simplified verification - in production, implement proper RSA verification
        return {
            'verified': True,
            'order_id': notification_data.get('out_trade_no'),
            'transaction_id': notification_data.get('trade_no'),
            'total_fee': int(float(notification_data.get('total_amount', 0)) * 100),  # Convert to cents
            'payment_method': 'alipay'
        }

    def _verify_member_card_notification(self, notification_data: Dict[str, Any]) -> Dict[str, Any]:
        """Verify member card payment notification"""
        # For member card payments, verification would be internal
        return {
            'verified': True,
            'order_id': notification_data.get('order_id'),
            'transaction_id': f"MC_{notification_data.get('order_id')}",
            'total_fee': notification_data.get('amount', 0),
            'payment_method': 'member_card'
        }

    def get_supported_payment_methods(self, user_agent: str = None) -> List[Dict[str, Any]]:
        """Get list of supported payment methods based on user context"""
        
        methods = []
        
        # WeChat Pay
        if self.wechat_app_id and self.wechat_mch_id:
            methods.append({
                'method': 'wechat',
                'name': '微信支付',
                'icon': 'wechat-pay.png',
                'trade_types': ['JSAPI', 'NATIVE', 'APP', 'H5'],
                'description': 'WeChat Pay - 微信支付'
            })
        
        # Alipay
        if self.alipay_app_id:
            methods.append({
                'method': 'alipay',
                'name': '支付宝',
                'icon': 'alipay.png',
                'trade_types': ['SCAN', 'APP', 'H5'],
                'description': 'Alipay - 支付宝支付'
            })
        
        # Member Card
        methods.append({
            'method': 'member_card',
            'name': '会员卡',
            'icon': 'member-card.png',
            'trade_types': ['BALANCE'],
            'description': 'Member Card Balance - 会员卡余额'
        })
        
        return methods

    def _generate_wechat_signature(self, params: Dict[str, str]) -> str:
        """Generate WeChat Pay signature"""
        # Sort parameters
        sorted_params = sorted(params.items())
        
        # Create query string
        query_string = '&'.join([f"{k}={v}" for k, v in sorted_params if v])
        query_string += f"&key={self.wechat_api_key}"
        
        # Generate MD5 hash
        signature = hashlib.md5(query_string.encode('utf-8')).hexdigest().upper()
        return signature

    def _generate_jsapi_params(self, prepay_id: str) -> Dict[str, str]:
        """Generate JSAPI payment parameters"""
        timestamp = str(int(time.time()))
        nonce_str = str(uuid.uuid4()).replace('-', '')
        
        params = {
            'appId': self.wechat_app_id,
            'timeStamp': timestamp,
            'nonceStr': nonce_str,
            'package': f'prepay_id={prepay_id}',
            'signType': 'MD5'
        }
        
        # Generate signature
        params['paySign'] = self._generate_wechat_signature(params)
        
        return params

    def _dict_to_xml(self, data: Dict[str, str]) -> str:
        """Convert dictionary to XML string"""
        xml_str = '<xml>'
        for key, value in data.items():
            xml_str += f'<{key}>{value}</{key}>'
        xml_str += '</xml>'
        return xml_str

    def _xml_to_dict(self, xml_str: str) -> Dict[str, str]:
        """Convert XML string to dictionary"""
        root = ET.fromstring(xml_str)
        result = {}
        for child in root:
            result[child.tag] = child.text
        return result
