"""
Content Moderation Middleware for FastAPI
Automatically moderates user-generated content in API requests
"""
import json
import time
from typing import Dict, Any, Optional
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from services.content_moderation import (
    content_moderation_service, 
    ModerationResult,
    TencentCMSError
)


class ContentModerationMiddleware(BaseHTTPMiddleware):
    """
    Middleware to automatically moderate content in API requests
    """
    
    def __init__(self, app, enabled: bool = True):
        super().__init__(app)
        self.enabled = enabled
        
        # Endpoints that require text moderation
        self.text_moderation_endpoints = {
            "/api/v1/users/profile": ["bio", "display_name", "location", "occupation", "education", "interests"],
            "/api/v1/chats/greeting": ["content", "message"],
            "/api/v1/chats/message": ["content", "message"],
            "/api/v1/messages/send": ["content", "message"],
            "/api/v1/profile/update": ["bio", "display_name", "about_me", "interests"],
            "/api/v1/auth/register": ["username", "display_name"]
        }
        
        # Endpoints that require image moderation
        self.image_moderation_endpoints = {
            "/api/v1/users/profile": ["avatar_url", "cover_image_url"],
            "/api/v1/profile/update": ["avatar_url", "cover_image_url"],
            "/api/v1/media/upload": ["url", "file_url"]
        }
    
    async def dispatch(self, request: Request, call_next):
        """Process request and apply content moderation"""
        if not self.enabled:
            return await call_next(request)
        
        # Skip moderation for GET requests and non-API endpoints
        if request.method == "GET" or not request.url.path.startswith("/api/"):
            return await call_next(request)
        
        # Skip moderation for auth endpoints (except register)
        if "/auth/" in request.url.path and "/register" not in request.url.path:
            return await call_next(request)
        
        try:
            # Get request body
            body = await self._get_request_body(request)
            if not body:
                return await call_next(request)
            
            # Apply content moderation
            moderation_result = await self._moderate_request_content(request.url.path, body)
            
            if moderation_result and moderation_result.get("blocked"):
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content={
                        "error": "Content moderation failed",
                        "message": "Your content contains inappropriate material and cannot be processed",
                        "details": moderation_result.get("violations", []),
                        "suggestion": "Please review and modify your content"
                    }
                )
            
            # Add moderation results to request state for later use
            request.state.moderation_results = moderation_result
            
        except Exception as e:
            # Log error but don't block request if moderation fails
            print(f"Content moderation middleware error: {str(e)}")
        
        return await call_next(request)
    
    async def _get_request_body(self, request: Request) -> Optional[Dict[str, Any]]:
        """Extract and parse request body"""
        try:
            body = await request.body()
            if not body:
                return None
            
            # Parse JSON body
            if request.headers.get("content-type", "").startswith("application/json"):
                return json.loads(body.decode())
            
            # Handle form data
            elif request.headers.get("content-type", "").startswith("application/x-www-form-urlencoded"):
                from urllib.parse import parse_qs
                parsed = parse_qs(body.decode())
                return {k: v[0] if v else "" for k, v in parsed.items()}
            
            return None
        
        except Exception:
            return None
    
    async def _moderate_request_content(self, path: str, body: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Apply content moderation to request body"""
        moderation_results = {}
        blocked_fields = []
        all_violations = []
        
        # Get user ID from request for tracking
        user_id = body.get("user_id") or body.get("sender_id")
        
        # Moderate text content
        if path in self.text_moderation_endpoints:
            text_fields = self.text_moderation_endpoints[path]
            
            for field in text_fields:
                if field in body and body[field]:
                    try:
                        result = await content_moderation_service.moderate_text(
                            content=str(body[field]),
                            user_id=user_id,
                            data_id=f"api_{field}_{int(time.time())}"
                        )
                        
                        moderation_results[field] = {
                            "result": result.result.value,
                            "confidence": result.confidence,
                            "violations": result.violations
                        }
                        
                        if content_moderation_service.should_block_content(result):
                            blocked_fields.append(field)
                            all_violations.extend(result.violations)
                    
                    except TencentCMSError:
                        # If moderation service fails, allow content but log
                        print(f"Text moderation failed for field {field}")
        
        # Moderate image content
        if path in self.image_moderation_endpoints:
            image_fields = self.image_moderation_endpoints[path]
            
            for field in image_fields:
                if field in body and body[field]:
                    try:
                        result = await content_moderation_service.moderate_image(
                            image_url=str(body[field]),
                            user_id=user_id,
                            data_id=f"api_{field}_{int(time.time())}"
                        )
                        
                        moderation_results[field] = {
                            "result": result.result.value,
                            "confidence": result.confidence,
                            "violations": result.violations
                        }
                        
                        if content_moderation_service.should_block_content(result):
                            blocked_fields.append(field)
                            all_violations.extend(result.violations)
                    
                    except TencentCMSError:
                        # If moderation service fails, allow content but log
                        print(f"Image moderation failed for field {field}")
        
        # Return results
        if moderation_results:
            return {
                "results": moderation_results,
                "blocked": len(blocked_fields) > 0,
                "blocked_fields": blocked_fields,
                "violations": list(set(all_violations))
            }
        
        return None


# Content moderation decorator for manual use
def moderate_content(fields: Dict[str, str]):
    """
    Decorator to manually apply content moderation to specific fields
    
    Args:
        fields: Dict mapping field names to content types ('text' or 'image')
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Extract request data (this would need to be customized based on your needs)
            request_data = kwargs.get('data') or (args[0] if args else {})
            
            if hasattr(request_data, 'dict'):
                request_data = request_data.dict()
            
            # Apply moderation
            for field_name, content_type in fields.items():
                if field_name in request_data and request_data[field_name]:
                    content = request_data[field_name]
                    
                    if content_type == "text":
                        result = await content_moderation_service.moderate_text(content)
                    elif content_type == "image":
                        result = await content_moderation_service.moderate_image(content)
                    else:
                        continue
                    
                    if content_moderation_service.should_block_content(result):
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Content in field '{field_name}' violates community guidelines"
                        )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


# Utility function to get moderation results from request
def get_moderation_results(request: Request) -> Optional[Dict[str, Any]]:
    """Get moderation results from request state"""
    return getattr(request.state, 'moderation_results', None)
