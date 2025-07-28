"""
Complete WeChat OAuth integration service
"""
import os
import requests
import logging
from typing import Optional, Dict, Any
from fastapi import HTTPException, status
from services.error_handling import ErrorCode, APIException

logger = logging.getLogger(__name__)

class WeChatOAuthService:
    """Enhanced WeChat OAuth service with comprehensive error handling and features"""
    
    def __init__(self):
        self.app_id = os.getenv('WECHAT_APP_ID')
        self.secret = os.getenv('WECHAT_SECRET')
        self.mini_program_app_id = os.getenv('WECHAT_MINI_PROGRAM_APP_ID')
        self.mini_program_secret = os.getenv('WECHAT_MINI_PROGRAM_SECRET')
        
        if not self.app_id or not self.secret:
            logger.warning("WeChat OAuth configuration incomplete")
    
    def verify_web_auth_code(self, code: str, redirect_uri: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Verify WeChat web authorization code (Official Account/Website)"""
        
        if not self.app_id or not self.secret:
            raise APIException(
                error_code=ErrorCode.EXTERNAL_SERVICE_ERROR,
                details="WeChat OAuth configuration not found",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        try:
            # Step 1: Exchange code for access token
            token_url = "https://api.weixin.qq.com/sns/oauth2/access_token"
            token_params = {
                'appid': self.app_id,
                'secret': self.secret,
                'code': code,
                'grant_type': 'authorization_code'
            }
            
            logger.info(f"Requesting WeChat access token for code: {code[:10]}...")
            token_response = requests.get(token_url, params=token_params, timeout=10)
            token_data = token_response.json()
            
            if 'access_token' not in token_data:
                error_msg = token_data.get('errmsg', 'Unknown error')
                logger.error(f"WeChat token exchange failed: {error_msg}")
                raise APIException(
                    error_code=ErrorCode.WECHAT_API_ERROR,
                    details=f"Token exchange failed: {error_msg}"
                )
            
            access_token = token_data['access_token']
            openid = token_data['openid']
            
            # Step 2: Validate token (check if still valid)
            validate_url = "https://api.weixin.qq.com/sns/auth"
            validate_params = {
                'access_token': access_token,
                'openid': openid
            }
            
            validate_response = requests.get(validate_url, params=validate_params, timeout=10)
            validate_data = validate_response.json()
            
            if validate_data.get('errcode', 0) != 0:
                logger.warning("WeChat access token invalid, attempting refresh")
                # Try to refresh token if available
                if 'refresh_token' in token_data:
                    refreshed_data = self._refresh_access_token(token_data['refresh_token'])
                    if refreshed_data:
                        access_token = refreshed_data['access_token']
                        openid = refreshed_data['openid']
                    else:
                        raise APIException(
                            error_code=ErrorCode.WECHAT_API_ERROR,
                            details="Access token invalid and refresh failed"
                        )
            
            # Step 3: Get user info
            userinfo_url = "https://api.weixin.qq.com/sns/userinfo"
            userinfo_params = {
                'access_token': access_token,
                'openid': openid,
                'lang': 'en'  # Can be 'zh_CN', 'zh_TW', 'en'
            }
            
            userinfo_response = requests.get(userinfo_url, params=userinfo_params, timeout=10)
            user_data = userinfo_response.json()
            
            if 'openid' not in user_data:
                error_msg = user_data.get('errmsg', 'Failed to get user info')
                logger.error(f"WeChat user info failed: {error_msg}")
                raise APIException(
                    error_code=ErrorCode.WECHAT_API_ERROR,
                    details=f"User info failed: {error_msg}"
                )
            
            # Return standardized user data
            result = {
                'openid': user_data.get('openid'),
                'unionid': user_data.get('unionid'),  # Available if app is in union
                'nickname': user_data.get('nickname', ''),
                'avatar': user_data.get('headimgurl', ''),
                'sex': user_data.get('sex', 0),  # 1=male, 2=female, 0=unknown
                'province': user_data.get('province', ''),
                'city': user_data.get('city', ''),
                'country': user_data.get('country', ''),
                'privilege': user_data.get('privilege', []),
                'language': user_data.get('language', 'en'),
                'access_token': access_token,
                'refresh_token': token_data.get('refresh_token'),
                'expires_in': token_data.get('expires_in', 7200)
            }
            
            logger.info(f"WeChat OAuth success for user: {result['openid']}")
            return result
            
        except requests.RequestException as e:
            logger.error(f"WeChat API request failed: {e}")
            raise APIException(
                error_code=ErrorCode.EXTERNAL_SERVICE_ERROR,
                details="WeChat service temporarily unavailable"
            )
        except APIException:
            raise
        except Exception as e:
            logger.error(f"Unexpected WeChat verification error: {e}")
            raise APIException(
                error_code=ErrorCode.WECHAT_API_ERROR,
                details="WeChat verification failed"
            )
    
    def verify_mini_program_code(self, js_code: str) -> Optional[Dict[str, Any]]:
        """Verify WeChat Mini Program code"""
        
        if not self.mini_program_app_id or not self.mini_program_secret:
            raise APIException(
                error_code=ErrorCode.EXTERNAL_SERVICE_ERROR,
                details="WeChat Mini Program configuration not found",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        try:
            # Mini Program uses different endpoint
            auth_url = "https://api.weixin.qq.com/sns/jscode2session"
            auth_params = {
                'appid': self.mini_program_app_id,
                'secret': self.mini_program_secret,
                'js_code': js_code,
                'grant_type': 'authorization_code'
            }
            
            logger.info(f"Verifying WeChat Mini Program code: {js_code[:10]}...")
            response = requests.get(auth_url, params=auth_params, timeout=10)
            data = response.json()
            
            if 'openid' not in data:
                error_msg = data.get('errmsg', 'Invalid js_code')
                logger.error(f"WeChat Mini Program auth failed: {error_msg}")
                raise APIException(
                    error_code=ErrorCode.WECHAT_API_ERROR,
                    details=f"Mini Program auth failed: {error_msg}"
                )
            
            result = {
                'openid': data['openid'],
                'session_key': data.get('session_key'),
                'unionid': data.get('unionid'),  # Only if unionid is available
                'platform': 'mini_program'
            }
            
            logger.info(f"WeChat Mini Program auth success for user: {result['openid']}")
            return result
            
        except requests.RequestException as e:
            logger.error(f"WeChat Mini Program API request failed: {e}")
            raise APIException(
                error_code=ErrorCode.EXTERNAL_SERVICE_ERROR,
                details="WeChat service temporarily unavailable"
            )
        except APIException:
            raise
        except Exception as e:
            logger.error(f"Unexpected WeChat Mini Program error: {e}")
            raise APIException(
                error_code=ErrorCode.WECHAT_API_ERROR,
                details="WeChat Mini Program verification failed"
            )
    
    def _refresh_access_token(self, refresh_token: str) -> Optional[Dict[str, Any]]:
        """Refresh WeChat access token"""
        try:
            refresh_url = "https://api.weixin.qq.com/sns/oauth2/refresh_token"
            refresh_params = {
                'appid': self.app_id,
                'grant_type': 'refresh_token',
                'refresh_token': refresh_token
            }
            
            response = requests.get(refresh_url, params=refresh_params, timeout=10)
            data = response.json()
            
            if 'access_token' in data:
                logger.info("WeChat access token refreshed successfully")
                return data
            else:
                logger.warning(f"WeChat token refresh failed: {data.get('errmsg', 'Unknown error')}")
                return None
                
        except Exception as e:
            logger.error(f"WeChat token refresh error: {e}")
            return None
    
    def get_oauth_url(self, redirect_uri: str, scope: str = "snsapi_userinfo", state: str = "STATE") -> str:
        """Generate WeChat OAuth authorization URL"""
        if not self.app_id:
            raise APIException(
                error_code=ErrorCode.EXTERNAL_SERVICE_ERROR,
                details="WeChat configuration not found"
            )
        
        # URL encode the redirect_uri
        import urllib.parse
        encoded_redirect = urllib.parse.quote(redirect_uri, safe='')
        
        oauth_url = (
            f"https://open.weixin.qq.com/connect/oauth2/authorize"
            f"?appid={self.app_id}"
            f"&redirect_uri={encoded_redirect}"
            f"&response_type=code"
            f"&scope={scope}"
            f"&state={state}"
            f"#wechat_redirect"
        )
        
        return oauth_url
    
    def verify_signature(self, signature: str, timestamp: str, nonce: str, token: str) -> bool:
        """Verify WeChat webhook signature for message callbacks"""
        import hashlib
        
        # Sort the parameters
        params = sorted([token, timestamp, nonce])
        
        # Create the string to hash
        string_to_hash = ''.join(params)
        
        # Calculate SHA1 hash
        calculated_signature = hashlib.sha1(string_to_hash.encode()).hexdigest()
        
        return calculated_signature == signature

# Global WeChat service instance
wechat_service = WeChatOAuthService()
