"""
Tencent Push Notification Service (TPNS) Integration
Handles mobile push notifications through Tencent Cloud TPNS
"""

import json
import time
import hmac
import hashlib
import base64
import requests
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import logging
from config.settings import Settings

logger = logging.getLogger(__name__)

@dataclass
class PushMessage:
    """Push notification message structure"""
    title: str
    content: str
    custom_content: Optional[Dict[str, Any]] = None
    android_action_type: int = 1  # 1: open app, 2: open URL, 3: open specific intent
    ios_badge_type: int = 1  # 1: increase by 1, -1: decrease by 1, specific number
    ios_sound: str = "default"
    audience_type: str = "account"  # account, tag, token, all
    target_list: Optional[List[str]] = None
    thread_id: Optional[str] = None
    thread_summ_fmt: Optional[str] = None

@dataclass
class PushResult:
    """Push notification result"""
    success: bool
    push_id: Optional[str] = None
    message: str = ""
    error_code: Optional[int] = None


class TPNSService:
    """Tencent Push Notification Service client"""
    
    def __init__(self):
        self.settings = Settings()
        self.access_id = self.settings.TENCENT_SECRET_ID
        self.secret_key = self.settings.TENCENT_SECRET_KEY
        self.region = self.settings.TENCENT_REGION
        
        # TPNS Configuration - you'll need to set these in your .env file
        self.android_access_id = getattr(self.settings, 'TPNS_ANDROID_ACCESS_ID', None)
        self.android_secret_key = getattr(self.settings, 'TPNS_ANDROID_SECRET_KEY', None)
        self.ios_access_id = getattr(self.settings, 'TPNS_IOS_ACCESS_ID', None)
        self.ios_secret_key = getattr(self.settings, 'TPNS_IOS_SECRET_KEY', None)
        
        # TPNS API endpoints
        self.api_host = f"https://api.tpns.tencent.com"
        
        logger.info(f"TPNSService initialized for region: {self.region}")
    
    def _generate_signature(self, method: str, uri: str, params: Dict[str, Any], secret_key: str) -> str:
        """Generate TPNS API signature"""
        try:
            # Sort parameters
            sorted_params = sorted(params.items())
            
            # Create query string
            query_string = '&'.join([f"{k}={v}" for k, v in sorted_params])
            
            # Create string to sign
            string_to_sign = f"{method.upper()}&{uri}&{query_string}"
            
            # Generate signature
            signature = base64.b64encode(
                hmac.new(
                    secret_key.encode('utf-8'),
                    string_to_sign.encode('utf-8'),
                    hashlib.sha1
                ).digest()
            ).decode('utf-8')
            
            return signature
        except Exception as e:
            logger.error(f"Error generating TPNS signature: {e}")
            raise
    
    def _make_request(self, method: str, endpoint: str, data: Dict[str, Any], 
                     access_id: str, secret_key: str) -> Dict[str, Any]:
        """Make authenticated request to TPNS API"""
        try:
            # Prepare common parameters
            timestamp = int(time.time())
            params = {
                'AccessId': access_id,
                'Timestamp': timestamp,
                'ValidTime': 600,
            }
            
            # Generate signature
            signature = self._generate_signature(method, endpoint, params, secret_key)
            params['Sign'] = signature
            
            # Make request
            url = f"{self.api_host}{endpoint}"
            headers = {
                'Content-Type': 'application/json',
                'User-Agent': 'Ques-TPNS-Client/1.0'
            }
            
            if method.upper() == 'POST':
                # Add data to body for POST requests
                response = requests.post(
                    url,
                    params=params,
                    json=data,
                    headers=headers,
                    timeout=30
                )
            else:
                # Add data to params for GET requests
                params.update(data)
                response = requests.get(
                    url,
                    params=params,
                    headers=headers,
                    timeout=30
                )
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"TPNS API request failed: {e}")
            raise
        except Exception as e:
            logger.error(f"Error making TPNS request: {e}")
            raise
    
    def send_android_push(self, message: PushMessage) -> PushResult:
        """Send push notification to Android devices"""
        if not self.android_access_id or not self.android_secret_key:
            logger.error("Android TPNS credentials not configured")
            return PushResult(
                success=False,
                message="Android TPNS credentials not configured"
            )
        
        try:
            # Prepare Android push data
            push_data = {
                "audience_type": message.audience_type,
                "message": {
                    "title": message.title,
                    "content": message.content,
                    "android": {
                        "n_id": int(time.time()),
                        "builder_id": 0,
                        "ring": 1,
                        "ring_raw": "ring",
                        "vibrate": 1,
                        "lights": 1,
                        "clearable": 1,
                        "icon_type": 0,
                        "icon_res": "xg_vip_one_point",
                        "style_id": 1,
                        "small_icon": "xg_vip_one_point",
                        "action": {
                            "action_type": message.android_action_type,
                            "activity": "",
                            "aty_attr": {
                                "if": 0,
                                "pf": 0
                            },
                            "browser": {
                                "url": "",
                                "confirm": 1
                            },
                            "intent": ""
                        },
                        "custom_content": message.custom_content or {}
                    }
                },
                "message_type": "notify",
                "multi_pkg": True,
                "platform": "android",
                "environment": "dev"  # or "product" for production
            }
            
            # Add target list if specified
            if message.target_list:
                push_data["account_list"] = message.target_list
            
            # Send request
            response = self._make_request(
                'POST',
                '/v3/push/app',
                push_data,
                self.android_access_id,
                self.android_secret_key
            )
            
            # Parse response
            if response.get('ret_code') == 0:
                return PushResult(
                    success=True,
                    push_id=response.get('result', {}).get('push_id'),
                    message="Android push sent successfully"
                )
            else:
                return PushResult(
                    success=False,
                    error_code=response.get('ret_code'),
                    message=response.get('err_msg', 'Unknown error')
                )
                
        except Exception as e:
            logger.error(f"Error sending Android push: {e}")
            return PushResult(
                success=False,
                message=f"Android push failed: {str(e)}"
            )
    
    def send_ios_push(self, message: PushMessage) -> PushResult:
        """Send push notification to iOS devices"""
        if not self.ios_access_id or not self.ios_secret_key:
            logger.error("iOS TPNS credentials not configured")
            return PushResult(
                success=False,
                message="iOS TPNS credentials not configured"
            )
        
        try:
            # Prepare iOS push data
            push_data = {
                "audience_type": message.audience_type,
                "message": {
                    "title": message.title,
                    "content": message.content,
                    "ios": {
                        "aps": {
                            "alert": {
                                "title": message.title,
                                "body": message.content
                            },
                            "badge_type": message.ios_badge_type,
                            "category": "INVITE_CATEGORY",
                            "sound": message.ios_sound,
                            "thread-id": message.thread_id or "notifications"
                        },
                        "custom_content": message.custom_content or {}
                    }
                },
                "message_type": "notify",
                "platform": "ios",
                "environment": "dev"  # or "product" for production
            }
            
            # Add target list if specified
            if message.target_list:
                push_data["account_list"] = message.target_list
            
            # Send request
            response = self._make_request(
                'POST',
                '/v3/push/app',
                push_data,
                self.ios_access_id,
                self.ios_secret_key
            )
            
            # Parse response
            if response.get('ret_code') == 0:
                return PushResult(
                    success=True,
                    push_id=response.get('result', {}).get('push_id'),
                    message="iOS push sent successfully"
                )
            else:
                return PushResult(
                    success=False,
                    error_code=response.get('ret_code'),
                    message=response.get('err_msg', 'Unknown error')
                )
                
        except Exception as e:
            logger.error(f"Error sending iOS push: {e}")
            return PushResult(
                success=False,
                message=f"iOS push failed: {str(e)}"
            )
    
    def send_push_to_all_platforms(self, message: PushMessage) -> Dict[str, PushResult]:
        """Send push notification to all platforms"""
        results = {}
        
        # Send to Android
        android_result = self.send_android_push(message)
        results['android'] = android_result
        
        # Send to iOS
        ios_result = self.send_ios_push(message)
        results['ios'] = ios_result
        
        logger.info(f"Multi-platform push results: Android={android_result.success}, iOS={ios_result.success}")
        return results
    
    def send_notification_to_user(self, user_id: str, title: str, content: str, 
                                 custom_data: Optional[Dict[str, Any]] = None,
                                 platform: str = "all") -> Dict[str, PushResult]:
        """Send notification to specific user across platforms"""
        message = PushMessage(
            title=title,
            content=content,
            custom_content=custom_data,
            audience_type="account",
            target_list=[str(user_id)]
        )
        
        if platform == "android":
            return {"android": self.send_android_push(message)}
        elif platform == "ios":
            return {"ios": self.send_ios_push(message)}
        else:
            return self.send_push_to_all_platforms(message)
    
    def send_broadcast_notification(self, title: str, content: str,
                                   custom_data: Optional[Dict[str, Any]] = None,
                                   platform: str = "all") -> Dict[str, PushResult]:
        """Send broadcast notification to all users"""
        message = PushMessage(
            title=title,
            content=content,
            custom_content=custom_data,
            audience_type="all"
        )
        
        if platform == "android":
            return {"android": self.send_android_push(message)}
        elif platform == "ios":
            return {"ios": self.send_ios_push(message)}
        else:
            return self.send_push_to_all_platforms(message)
    
    def send_friend_request_notification(self, target_user_id: str, sender_name: str, 
                                       sender_id: str) -> Dict[str, PushResult]:
        """Send friend request notification"""
        title = "New Friend Request"
        content = f"{sender_name} wants to connect with you"
        custom_data = {
            "type": "friend_request",
            "sender_id": sender_id,
            "sender_name": sender_name,
            "action": "open_friend_requests"
        }
        
        return self.send_notification_to_user(target_user_id, title, content, custom_data)
    
    def send_match_notification(self, user_id: str, match_name: str) -> Dict[str, PushResult]:
        """Send new match notification"""
        title = "New Match!"
        content = f"You have a new match with {match_name}"
        custom_data = {
            "type": "match",
            "action": "open_matches"
        }
        
        return self.send_notification_to_user(user_id, title, content, custom_data)
    
    def send_message_notification(self, user_id: str, sender_name: str, 
                                message_preview: str) -> Dict[str, PushResult]:
        """Send new message notification"""
        title = f"Message from {sender_name}"
        content = message_preview
        custom_data = {
            "type": "message",
            "sender_name": sender_name,
            "action": "open_chat"
        }
        
        return self.send_notification_to_user(user_id, title, content, custom_data)
    
    def get_push_statistics(self, push_id: str, access_id: str, secret_key: str) -> Dict[str, Any]:
        """Get push notification statistics"""
        try:
            data = {
                'pushId': push_id
            }
            
            response = self._make_request(
                'POST',
                '/v3/statistics/get_push_stat_v2',
                data,
                access_id,
                secret_key
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error getting push statistics: {e}")
            return {"error": str(e)}
    
    def bind_account(self, account: str, token: str, platform: str = "android") -> bool:
        """Bind user account to device token"""
        try:
            access_id = self.android_access_id if platform == "android" else self.ios_access_id
            secret_key = self.android_secret_key if platform == "android" else self.ios_secret_key
            
            if not access_id or not secret_key:
                logger.error(f"{platform.capitalize()} TPNS credentials not configured")
                return False
            
            data = {
                'operator_type': 1,  # 1: bind, 0: unbind
                'platform': platform,
                'account_list': [
                    {
                        'account': account,
                        'token': token
                    }
                ]
            }
            
            response = self._make_request(
                'POST',
                '/v3/device/account/batchoperate',
                data,
                access_id,
                secret_key
            )
            
            return response.get('ret_code') == 0
            
        except Exception as e:
            logger.error(f"Error binding account: {e}")
            return False
    
    def unbind_account(self, account: str, token: str, platform: str = "android") -> bool:
        """Unbind user account from device token"""
        try:
            access_id = self.android_access_id if platform == "android" else self.ios_access_id
            secret_key = self.android_secret_key if platform == "android" else self.ios_secret_key
            
            if not access_id or not secret_key:
                logger.error(f"{platform.capitalize()} TPNS credentials not configured")
                return False
            
            data = {
                'operator_type': 0,  # 1: bind, 0: unbind
                'platform': platform,
                'account_list': [
                    {
                        'account': account,
                        'token': token
                    }
                ]
            }
            
            response = self._make_request(
                'POST',
                '/v3/device/account/batchoperate',
                data,
                access_id,
                secret_key
            )
            
            return response.get('ret_code') == 0
            
        except Exception as e:
            logger.error(f"Error unbinding account: {e}")
            return False


# Global TPNS service instance
tpns_service = TPNSService()