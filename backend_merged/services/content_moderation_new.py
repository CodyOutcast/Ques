"""
Tencent Cloud Content Moderation Service
Provides text and image content moderation using Tencent Cloud CMS/TMS
"""
import asyncio
import hashlib
import hmac
import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Any

import httpx
from pydantic import BaseModel

from config.settings import get_settings

settings = get_settings()


class ModerationResult(BaseModel):
    is_approved: bool
    confidence: float
    reason: Optional[str] = None
    blocked_words: List[str] = []
    suggestion: str  # "Pass", "Block", "Review"
    mode: str = "production"  # "production" or "fallback"


class TencentContentModerationService:
    def __init__(self):
        self.secret_id = settings.TENCENT_SECRET_ID
        self.secret_key = settings.TENCENT_SECRET_KEY
        self.region = getattr(settings, 'TENCENT_REGION', 'ap-guangzhou')
        self.service = "cms"
        self.host = f"{self.service}.tencentcloudapi.com"
        self.endpoint = f"https://{self.host}"
        self.algorithm = "TC3-HMAC-SHA256"
        self.enable_moderation = getattr(settings, 'ENABLE_CONTENT_MODERATION', False)
        
        # HTTP client for API calls
        self.client = httpx.AsyncClient(timeout=30.0)
    
    def _sign(self, key: bytes, msg: str) -> bytes:
        """HMAC-SHA256 signing"""
        return hmac.new(key, msg.encode('utf-8'), hashlib.sha256).digest()
    
    def _get_authorization(self, params: dict, timestamp: int, date: str) -> str:
        """Generate Tencent Cloud API v3 authorization header"""
        # Step 1: Create canonical request
        http_request_method = "POST"
        canonical_uri = "/"
        canonical_querystring = ""
        canonical_headers = f"content-type:application/json; charset=utf-8\nhost:{self.host}\n"
        signed_headers = "content-type;host"
        payload = json.dumps(params, separators=(',', ':'))
        hashed_request_payload = hashlib.sha256(payload.encode('utf-8')).hexdigest()
        
        canonical_request = (
            f"{http_request_method}\n"
            f"{canonical_uri}\n"
            f"{canonical_querystring}\n"
            f"{canonical_headers}\n"
            f"{signed_headers}\n"
            f"{hashed_request_payload}"
        )
        
        # Step 2: Create string to sign
        credential_scope = f"{date}/{self.service}/tc3_request"
        hashed_canonical_request = hashlib.sha256(canonical_request.encode('utf-8')).hexdigest()
        string_to_sign = (
            f"{self.algorithm}\n"
            f"{timestamp}\n"
            f"{credential_scope}\n"
            f"{hashed_canonical_request}"
        )
        
        # Step 3: Calculate signature
        secret_date = self._sign(f"TC3{self.secret_key}".encode('utf-8'), date)
        secret_service = self._sign(secret_date, self.service)
        secret_signing = self._sign(secret_service, "tc3_request")
        signature = hmac.new(secret_signing, string_to_sign.encode('utf-8'), hashlib.sha256).hexdigest()
        
        # Step 4: Create authorization header
        authorization = (
            f"{self.algorithm} "
            f"Credential={self.secret_id}/{credential_scope}, "
            f"SignedHeaders={signed_headers}, "
            f"Signature={signature}"
        )
        
        return authorization
    
    async def moderate_text(self, text: str, user_id: Optional[str] = None) -> ModerationResult:
        """
        Moderate text content using Tencent Cloud Text Moderation Service (TMS)
        """
        if not self.enable_moderation or not self.secret_id or not self.secret_key:
            # Fallback mode - approve all content
            return ModerationResult(
                is_approved=True,
                confidence=0.5,
                reason="Content moderation disabled or credentials missing",
                suggestion="Pass",
                mode="fallback"
            )
        
        try:
            # Prepare API request
            timestamp = int(time.time())
            date = datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d')
            
            params = {
                "BizType": getattr(settings, 'TENCENT_MODERATION_BIZ_TYPE', 'default'),
                "DataId": f"user_{user_id}_{timestamp}" if user_id else f"text_{timestamp}",
                "Content": text
            }
            
            # Generate authorization
            authorization = self._get_authorization(params, timestamp, date)
            
            # Prepare headers
            headers = {
                "Authorization": authorization,
                "Content-Type": "application/json; charset=utf-8",
                "Host": self.host,
                "X-TC-Action": "TextModeration",
                "X-TC-Timestamp": str(timestamp),
                "X-TC-Version": "2020-12-29",
                "X-TC-Region": self.region
            }
            
            # Make API call
            response = await self.client.post(
                self.endpoint,
                headers=headers,
                json=params
            )
            
            if response.status_code != 200:
                print(f"TMS API Error: {response.status_code} - {response.text}")
                # Fallback to approval for API errors
                return ModerationResult(
                    is_approved=True,
                    confidence=0.5,
                    reason=f"API error: {response.status_code}",
                    suggestion="Pass",
                    mode="fallback"
                )
            
            result = response.json()
            
            # Check for API errors
            if "Response" not in result:
                print(f"TMS API Invalid Response: {result}")
                return ModerationResult(
                    is_approved=True,
                    confidence=0.5,
                    reason="Invalid API response",
                    suggestion="Pass",
                    mode="fallback"
                )
            
            response_data = result["Response"]
            
            # Check for errors in response
            if "Error" in response_data:
                error = response_data["Error"]
                print(f"TMS API Error: {error.get('Code')} - {error.get('Message')}")
                return ModerationResult(
                    is_approved=True,
                    confidence=0.5,
                    reason=f"API error: {error.get('Message')}",
                    suggestion="Pass",
                    mode="fallback"
                )
            
            # Parse moderation result
            suggestion = response_data.get("Suggestion", "Pass")
            label = response_data.get("Label", "Normal")
            
            # Extract detailed results
            details = response_data.get("DetailResults", [])
            blocked_words = []
            reasons = []
            
            for detail in details:
                if detail.get("Suggestion") == "Block":
                    reasons.append(detail.get("Label", "Unknown"))
                    # Extract keywords if available
                    keywords = detail.get("Keywords", [])
                    for keyword in keywords:
                        if keyword.get("Suggestion") == "Block":
                            blocked_words.append(keyword.get("Keyword", ""))
            
            # Determine approval status
            is_approved = suggestion == "Pass"
            confidence = 1.0 if suggestion in ["Pass", "Block"] else 0.7  # Review gets medium confidence
            
            return ModerationResult(
                is_approved=is_approved,
                confidence=confidence,
                reason=", ".join(reasons) if reasons else None,
                blocked_words=blocked_words,
                suggestion=suggestion,
                mode="production"
            )
            
        except Exception as e:
            print(f"Content moderation error: {str(e)}")
            # Fallback to approval for unexpected errors
            return ModerationResult(
                is_approved=True,
                confidence=0.5,
                reason=f"Moderation service error: {str(e)}",
                suggestion="Pass",
                mode="fallback"
            )
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()


# Global instance
content_moderation_service = TencentContentModerationService()


async def moderate_content(text: str, user_id: Optional[str] = None) -> ModerationResult:
    """Convenience function for moderating text content"""
    return await content_moderation_service.moderate_text(text, user_id)
