"""
WeChat OAuth service
"""

import os
import aiohttp
import logging
from typing import Optional, Dict
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

class WeChatService:
    def __init__(self):
        self.app_id = os.getenv("WECHAT_APP_ID")
        self.app_secret = os.getenv("WECHAT_APP_SECRET")
        self.access_token_url = "https://api.weixin.qq.com/sns/oauth2/access_token"
        self.user_info_url = "https://api.weixin.qq.com/sns/userinfo"
    
    async def get_user_info(self, code: str) -> Optional[Dict]:
        """
        Get WeChat user info from OAuth code
        """
        try:
            # For development, return mock user data
            if not self.app_id or not self.app_secret:
                logger.warning("WeChat credentials not configured, returning mock data")
                return {
                    "openid": f"mock_openid_{code[:8]}",
                    "nickname": "WeChat Test User",
                    "headimgurl": "https://example.com/avatar.jpg"
                }
            
            # Step 1: Exchange code for access token
            token_params = {
                "appid": self.app_id,
                "secret": self.app_secret,
                "code": code,
                "grant_type": "authorization_code"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(self.access_token_url, params=token_params) as response:
                    token_data = await response.json()
                    
                    if "errcode" in token_data:
                        logger.error(f"WeChat token error: {token_data}")
                        return None
                    
                    access_token = token_data.get("access_token")
                    openid = token_data.get("openid")
                    
                    if not access_token or not openid:
                        logger.error("Missing access_token or openid")
                        return None
                
                # Step 2: Get user info
                user_params = {
                    "access_token": access_token,
                    "openid": openid,
                    "lang": "en"
                }
                
                async with session.get(self.user_info_url, params=user_params) as response:
                    user_data = await response.json()
                    
                    if "errcode" in user_data:
                        logger.error(f"WeChat user info error: {user_data}")
                        return None
                    
                    return user_data
            
        except Exception as e:
            logger.error(f"WeChat OAuth error: {e}")
            return None
    
    def get_auth_url(self, redirect_uri: str, state: str = None) -> str:
        """
        Generate WeChat OAuth authorization URL
        """
        base_url = "https://open.weixin.qq.com/connect/oauth2/authorize"
        params = {
            "appid": self.app_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": "snsapi_userinfo"
        }
        
        if state:
            params["state"] = state
        
        # Build URL manually
        param_string = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"{base_url}?{param_string}#wechat_redirect"
