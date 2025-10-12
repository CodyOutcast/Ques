"""
Monitoring Service
Handles logging, metrics, and monitoring functionality
"""

import logging
from datetime import datetime
from typing import Optional, Dict, Any


logger = logging.getLogger(__name__)


def setup_monitoring():
    """Setup monitoring and logging configuration"""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger.info("Monitoring setup completed")


def log_security_event(
    event_type: str,
    user_id: Optional[int] = None,
    details: Optional[Dict[str, Any]] = None,
    ip_address: Optional[str] = None
):
    """Log security-related events"""
    log_data = {
        "timestamp": datetime.utcnow().isoformat(),
        "event_type": event_type,
        "user_id": user_id,
        "ip_address": ip_address,
        "details": details or {}
    }
    
    logger.info(f"Security Event: {event_type}", extra=log_data)


def log_api_request(
    method: str,
    path: str,
    user_id: Optional[int] = None,
    response_status: Optional[int] = None,
    duration_ms: Optional[float] = None
):
    """Log API request"""
    log_data = {
        "timestamp": datetime.utcnow().isoformat(),
        "method": method,
        "path": path,
        "user_id": user_id,
        "response_status": response_status,
        "duration_ms": duration_ms
    }
    
    logger.info(f"API Request: {method} {path}", extra=log_data)


def log_error(
    error_type: str,
    error_message: str,
    user_id: Optional[int] = None,
    context: Optional[Dict[str, Any]] = None
):
    """Log application errors"""
    log_data = {
        "timestamp": datetime.utcnow().isoformat(),
        "error_type": error_type,
        "error_message": error_message,
        "user_id": user_id,
        "context": context or {}
    }
    
    logger.error(f"Application Error: {error_type} - {error_message}", extra=log_data)