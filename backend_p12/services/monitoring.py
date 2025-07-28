"""
Enhanced performance monitoring and security audit logging
"""
import time
import logging
import json
import os
from datetime import datetime
from typing import Dict, Any, Optional
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

# Create security audit logger
security_logger = logging.getLogger("security_audit")
security_handler = logging.FileHandler("logs/security_audit.log")
security_handler.setFormatter(logging.Formatter(
    '%(asctime)s - %(levelname)s - %(message)s'
))
security_logger.addHandler(security_handler)
security_logger.setLevel(logging.INFO)

# Configure performance logger
perf_logger = logging.getLogger("performance")
perf_logger.setLevel(logging.INFO)

# Create logs directory if it doesn't exist
os.makedirs("logs", exist_ok=True)

# Create file handler for performance logs
perf_handler = logging.FileHandler("logs/performance.log")
perf_formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
perf_handler.setFormatter(perf_formatter)
perf_logger.addHandler(perf_handler)

class PerformanceMiddleware(BaseHTTPMiddleware):
    """Middleware to track API performance metrics"""
    
    async def dispatch(self, request: Request, call_next):
        # Start timing
        start_time = time.time()
        
        # Get request info
        method = request.method
        path = request.url.path
        query_params = str(request.query_params)
        
        # Process request
        response = await call_next(request)
        
        # Calculate metrics
        process_time = time.time() - start_time
        status_code = response.status_code
        
        # Log performance metrics
        metrics = {
            "timestamp": datetime.utcnow().isoformat(),
            "method": method,
            "path": path,
            "query_params": query_params,
            "status_code": status_code,
            "process_time_ms": round(process_time * 1000, 2),
            "slow_request": process_time > 1.0  # Flag slow requests (>1s)
        }
        
        # Add custom headers for monitoring
        response.headers["X-Process-Time"] = str(process_time)
        
        # Log to performance logger
        log_level = logging.WARNING if process_time > 1.0 else logging.INFO
        perf_logger.log(log_level, json.dumps(metrics))
        
        return response

class APIMetrics:
    """Singleton class to collect and provide API metrics"""
    
    _instance = None
    _metrics = {
        "total_requests": 0,
        "endpoint_stats": {},
        "error_stats": {},
        "slow_requests": 0
    }
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(APIMetrics, cls).__new__(cls)
        return cls._instance
    
    def record_request(self, endpoint: str, method: str, status_code: int, process_time: float):
        """Record metrics for a request"""
        self._metrics["total_requests"] += 1
        
        # Endpoint statistics
        endpoint_key = f"{method} {endpoint}"
        if endpoint_key not in self._metrics["endpoint_stats"]:
            self._metrics["endpoint_stats"][endpoint_key] = {
                "count": 0,
                "avg_time": 0,
                "min_time": float('inf'),
                "max_time": 0,
                "error_count": 0
            }
        
        stats = self._metrics["endpoint_stats"][endpoint_key]
        stats["count"] += 1
        
        # Update timing statistics
        old_avg = stats["avg_time"]
        stats["avg_time"] = (old_avg * (stats["count"] - 1) + process_time) / stats["count"]
        stats["min_time"] = min(stats["min_time"], process_time)
        stats["max_time"] = max(stats["max_time"], process_time)
        
        # Track errors
        if status_code >= 400:
            stats["error_count"] += 1
            error_key = f"{status_code}"
            self._metrics["error_stats"][error_key] = self._metrics["error_stats"].get(error_key, 0) + 1
        
        # Track slow requests
        if process_time > 1.0:
            self._metrics["slow_requests"] += 1
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics"""
        return self._metrics.copy()
    
    def reset_metrics(self):
        """Reset all metrics"""
        self._metrics = {
            "total_requests": 0,
            "endpoint_stats": {},
            "error_stats": {},
            "slow_requests": 0
        }

# Global metrics instance
api_metrics = APIMetrics()

class SecurityAuditLogger:
    """Security audit logging functions"""
    
    @staticmethod
    def log_authentication_event(
        event_type: str, 
        user_id: Optional[int] = None, 
        email: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        success: bool = True,
        details: Optional[str] = None
    ):
        """Log authentication events"""
        audit_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,  # login, logout, register, password_reset, etc.
            "user_id": user_id,
            "email": email,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "success": success,
            "details": details
        }
        
        security_logger.info(f"AUTH_EVENT: {json.dumps(audit_entry)}")
    
    @staticmethod
    def log_security_violation(
        violation_type: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        request_path: Optional[str] = None,
        details: Optional[str] = None
    ):
        """Log security violations"""
        audit_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "violation_type": violation_type,  # rate_limit, suspicious_activity, etc.
            "ip_address": ip_address,
            "user_agent": user_agent,
            "request_path": request_path,
            "details": details
        }
        
        security_logger.warning(f"SECURITY_VIOLATION: {json.dumps(audit_entry)}")
    
    @staticmethod
    def log_data_access(
        user_id: int,
        action: str,  # create, read, update, delete
        resource_type: str,  # user, profile, match, etc.
        resource_id: Optional[str] = None,
        ip_address: Optional[str] = None
    ):
        """Log sensitive data access"""
        audit_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "action": action,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "ip_address": ip_address
        }
        
        security_logger.info(f"DATA_ACCESS: {json.dumps(audit_entry)}")

# Global security audit logger
security_audit = SecurityAuditLogger()
