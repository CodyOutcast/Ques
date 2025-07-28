"""
Enhanced security middleware and rate limiting
"""
import time
import hashlib
from typing import Dict, Optional, Tuple, Any
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import ipaddress
import logging
from collections import defaultdict, deque
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)

class RateLimitStorage:
    """In-memory storage for rate limiting (could be Redis in production)"""
    
    def __init__(self):
        self.requests: Dict[str, deque] = defaultdict(deque)
        self.blocked_ips: Dict[str, datetime] = {}
    
    def add_request(self, key: str, timestamp: float):
        """Add a request timestamp for a key"""
        self.requests[key].append(timestamp)
    
    def get_request_count(self, key: str, window_seconds: int) -> int:
        """Get number of requests in the time window"""
        current_time = time.time()
        cutoff_time = current_time - window_seconds
        
        # Remove old requests
        while self.requests[key] and self.requests[key][0] < cutoff_time:
            self.requests[key].popleft()
        
        return len(self.requests[key])
    
    def block_ip(self, ip: str, duration_minutes: int = 60):
        """Block an IP address for a duration"""
        self.blocked_ips[ip] = datetime.utcnow() + timedelta(minutes=duration_minutes)
        logger.warning(f"IP {ip} blocked for {duration_minutes} minutes due to rate limiting")
    
    def is_ip_blocked(self, ip: str) -> bool:
        """Check if an IP is currently blocked"""
        if ip not in self.blocked_ips:
            return False
        
        if datetime.utcnow() > self.blocked_ips[ip]:
            del self.blocked_ips[ip]
            return False
        
        return True
    
    def cleanup_old_data(self, max_age_hours: int = 24):
        """Clean up old data to prevent memory leaks"""
        cutoff_time = time.time() - (max_age_hours * 3600)
        
        # Clean old requests
        for key in list(self.requests.keys()):
            while self.requests[key] and self.requests[key][0] < cutoff_time:
                self.requests[key].popleft()
            
            if not self.requests[key]:
                del self.requests[key]

# Global rate limit storage
rate_limit_storage = RateLimitStorage()

class SecurityMiddleware(BaseHTTPMiddleware):
    """Enhanced security middleware with rate limiting and threat detection"""
    
    def __init__(
        self,
        app,
        rate_limit_requests: int = 100,
        rate_limit_window: int = 3600,  # 1 hour
        strict_endpoints: Optional[Dict[str, Tuple[int, int]]] = None,
        trusted_proxies: Optional[list] = None
    ):
        super().__init__(app)
        self.rate_limit_requests = rate_limit_requests
        self.rate_limit_window = rate_limit_window
        self.strict_endpoints = strict_endpoints or {
            "/auth/login": (5, 300),  # 5 requests per 5 minutes
            "/auth/register": (3, 3600),  # 3 requests per hour
            "/auth/send-verification-code": (3, 300),  # 3 requests per 5 minutes (stricter)
            "/auth/reset-password": (3, 3600),  # 3 requests per hour
        }
        self.trusted_proxies = trusted_proxies or []
    
    def get_client_ip(self, request: Request) -> str:
        """Get the real client IP, handling proxies"""
        # Check for forwarded headers (common in production)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # Take the first IP (client IP)
            client_ip = forwarded_for.split(",")[0].strip()
            try:
                ipaddress.ip_address(client_ip)
                return client_ip
            except ValueError:
                pass
        
        # Check other common headers
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            try:
                ipaddress.ip_address(real_ip)
                return real_ip
            except ValueError:
                pass
        
        # Fall back to direct connection IP
        return request.client.host if request.client else "unknown"
    
    def detect_suspicious_activity(self, request: Request, client_ip: str) -> bool:
        """Detect potentially suspicious activity"""
        suspicious_indicators = []
        
        # Check for SQL injection patterns
        query_string = str(request.query_params).lower()
        path = request.url.path.lower()
        
        sql_patterns = [
            "union select", "drop table", "insert into", "delete from",
            "script>", "<script", "javascript:", "onclick=", "onerror="
        ]
        
        for pattern in sql_patterns:
            if pattern in query_string or pattern in path:
                suspicious_indicators.append(f"SQL/XSS pattern detected: {pattern}")
        
        # Check for unusually long requests
        if len(str(request.url)) > 2000:
            suspicious_indicators.append("Unusually long URL")
        
        # Check for suspicious user agents
        user_agent = request.headers.get("User-Agent", "").lower()
        suspicious_agents = ["sqlmap", "nikto", "nmap", "masscan", "bot"]
        
        for agent in suspicious_agents:
            if agent in user_agent:
                suspicious_indicators.append(f"Suspicious user agent: {agent}")
        
        if suspicious_indicators:
            logger.warning(f"Suspicious activity from {client_ip}: {suspicious_indicators}")
            return True
        
        return False
    
    async def dispatch(self, request: Request, call_next):
        """Main security middleware logic"""
        client_ip = self.get_client_ip(request)
        
        # Check if IP is blocked
        if rate_limit_storage.is_ip_blocked(client_ip):
            logger.warning(f"Blocked IP {client_ip} attempted access")
            return Response(
                content=json.dumps({
                    "success": False,
                    "error": {
                        "code": "RATE_001",
                        "message": "IP address temporarily blocked due to rate limiting"
                    }
                }),
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                media_type="application/json"
            )
        
        # Detect suspicious activity
        if self.detect_suspicious_activity(request, client_ip):
            # Block IP for suspicious activity
            rate_limit_storage.block_ip(client_ip, duration_minutes=30)
            return Response(
                content=json.dumps({
                    "success": False,
                    "error": {
                        "code": "SEC_001",
                        "message": "Suspicious activity detected"
                    }
                }),
                status_code=status.HTTP_403_FORBIDDEN,
                media_type="application/json"
            )
        
        # Apply rate limiting
        path = request.url.path
        current_time = time.time()
        
        # Check strict endpoint limits
        if path in self.strict_endpoints:
            limit, window = self.strict_endpoints[path]
            key = f"{client_ip}:{path}"
            
            rate_limit_storage.add_request(key, current_time)
            request_count = rate_limit_storage.get_request_count(key, window)
            
            if request_count > limit:
                logger.warning(f"Rate limit exceeded for {client_ip} on {path}: {request_count}/{limit}")
                # Block IP for repeated violations
                rate_limit_storage.block_ip(client_ip, duration_minutes=15)
                
                return Response(
                    content=json.dumps({
                        "success": False,
                        "error": {
                            "code": "RATE_001",
                            "message": f"Rate limit exceeded. Maximum {limit} requests per {window//60} minutes."
                        }
                    }),
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    media_type="application/json"
                )
        
        # Apply general rate limiting
        general_key = f"{client_ip}:general"
        rate_limit_storage.add_request(general_key, current_time)
        general_count = rate_limit_storage.get_request_count(general_key, self.rate_limit_window)
        
        if general_count > self.rate_limit_requests:
            logger.warning(f"General rate limit exceeded for {client_ip}: {general_count}/{self.rate_limit_requests}")
            rate_limit_storage.block_ip(client_ip, duration_minutes=60)
            
            return Response(
                content=json.dumps({
                    "success": False,
                    "error": {
                        "code": "RATE_001",
                        "message": f"Rate limit exceeded. Maximum {self.rate_limit_requests} requests per hour."
                    }
                }),
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                media_type="application/json"
            )
        
        # Add security headers
        response = await call_next(request)
        
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Rate limit headers
        response.headers["X-RateLimit-Limit"] = str(self.rate_limit_requests)
        response.headers["X-RateLimit-Remaining"] = str(max(0, self.rate_limit_requests - general_count))
        response.headers["X-RateLimit-Reset"] = str(int(current_time + self.rate_limit_window))
        
        return response

def get_rate_limit_status(ip: str) -> Dict[str, Any]:
    """Get current rate limit status for an IP"""
    current_time = time.time()
    
    general_key = f"{ip}:general"
    general_count = rate_limit_storage.get_request_count(general_key, 3600)
    
    return {
        "ip": ip,
        "is_blocked": rate_limit_storage.is_ip_blocked(ip),
        "general_requests": general_count,
        "general_limit": 100,
        "window_seconds": 3600,
        "reset_time": current_time + 3600
    }
