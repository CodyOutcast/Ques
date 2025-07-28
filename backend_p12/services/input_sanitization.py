"""
Input sanitization and validation middleware
"""
import re
import json
import logging
from typing import Any, Dict, Optional
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import html

logger = logging.getLogger(__name__)

class InputSanitizationMiddleware(BaseHTTPMiddleware):
    """Middleware for input sanitization and validation"""
    
    def __init__(self, app, max_request_size: int = 1024 * 1024):  # 1MB default
        super().__init__(app)
        self.max_request_size = max_request_size
        
        # Email validation regex
        self.email_pattern = re.compile(
            r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        )
        
        # Dangerous patterns to block
        self.dangerous_patterns = [
            r'<script[^>]*>.*?</script>',
            r'javascript:',
            r'on\w+\s*=',
            r'data:text/html',
            r'vbscript:',
            r'<iframe[^>]*>.*?</iframe>',
            r'<object[^>]*>.*?</object>',
            r'<embed[^>]*>.*?</embed>',
        ]
        
        self.compiled_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.dangerous_patterns]
    
    def sanitize_string(self, text: str) -> str:
        """Sanitize a string by escaping HTML and removing dangerous patterns"""
        if not isinstance(text, str):
            return text
        
        # HTML escape
        sanitized = html.escape(text)
        
        # Check for dangerous patterns
        for pattern in self.compiled_patterns:
            if pattern.search(sanitized):
                logger.warning(f"Dangerous pattern detected and blocked: {text[:100]}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid input detected"
                )
        
        return sanitized
    
    def validate_email(self, email: str) -> bool:
        """Validate email format"""
        if not email or len(email) > 254:  # RFC 5321 limit
            return False
        return bool(self.email_pattern.match(email))
    
    def sanitize_json_data(self, data: Any) -> Any:
        """Recursively sanitize JSON data"""
        if isinstance(data, dict):
            return {key: self.sanitize_json_data(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [self.sanitize_json_data(item) for item in data]
        elif isinstance(data, str):
            return self.sanitize_string(data)
        else:
            return data
    
    async def dispatch(self, request: Request, call_next):
        """Main sanitization middleware logic"""
        # Check request size
        content_length = request.headers.get('content-length')
        if content_length and int(content_length) > self.max_request_size:
            client_ip = request.client.host if request.client else "unknown"
            logger.warning(f"Request too large: {content_length} bytes from {client_ip}")
            return Response(
                content=json.dumps({
                    "success": False,
                    "error": {
                        "code": "REQ_001",
                        "message": "Request too large"
                    }
                }),
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                media_type="application/json"
            )
        
        # For POST/PUT requests with JSON, sanitize the body
        if request.method in ["POST", "PUT", "PATCH"] and "application/json" in request.headers.get("content-type", ""):
            try:
                body = await request.body()
                if body:
                    json_data = json.loads(body)
                    
                    # Special validation for email fields
                    if isinstance(json_data, dict):
                        if 'email' in json_data and not self.validate_email(json_data['email']):
                            logger.warning(f"Invalid email format: {json_data.get('email', '')}")
                            return Response(
                                content=json.dumps({
                                    "success": False,
                                    "error": {
                                        "code": "VAL_001",
                                        "message": "Invalid email format",
                                        "field_errors": {
                                            "email": ["Please provide a valid email address"]
                                        }
                                    }
                                }),
                                status_code=status.HTTP_400_BAD_REQUEST,
                                media_type="application/json"
                            )
                        
                        if 'provider_id' in json_data and json_data.get('provider_type') == 'email':
                            if not self.validate_email(json_data['provider_id']):
                                logger.warning(f"Invalid provider_id email format: {json_data.get('provider_id', '')}")
                                return Response(
                                    content=json.dumps({
                                        "success": False,
                                        "error": {
                                            "code": "VAL_001",
                                            "message": "Invalid email format",
                                            "field_errors": {
                                                "provider_id": ["Please provide a valid email address"]
                                            }
                                        }
                                    }),
                                    status_code=status.HTTP_400_BAD_REQUEST,
                                    media_type="application/json"
                                )
                    
                    # Sanitize the data
                    sanitized_data = self.sanitize_json_data(json_data)
                    
                    # Replace request body with sanitized version
                    request._body = json.dumps(sanitized_data).encode()
                    
            except json.JSONDecodeError:
                client_ip = request.client.host if request.client else "unknown"
                logger.warning(f"Invalid JSON in request from {client_ip}")
                return Response(
                    content=json.dumps({
                        "success": False,
                        "error": {
                            "code": "REQ_002",
                            "message": "Invalid JSON format"
                        }
                    }),
                    status_code=status.HTTP_400_BAD_REQUEST,
                    media_type="application/json"
                )
            except Exception as e:
                logger.error(f"Error in input sanitization: {e}")
                return Response(
                    content=json.dumps({
                        "success": False,
                        "error": {
                            "code": "REQ_003",
                            "message": "Request processing error"
                        }
                    }),
                    status_code=status.HTTP_400_BAD_REQUEST,
                    media_type="application/json"
                )
        
        # Sanitize query parameters
        query_params = dict(request.query_params)
        for key, value in query_params.items():
            if isinstance(value, str):
                query_params[key] = self.sanitize_string(value)
        
        response = await call_next(request)
        return response
