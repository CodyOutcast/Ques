"""
Monitoring and logging setup
"""

import logging
import os
from datetime import datetime
from pathlib import Path

def setup_monitoring():
    """
    Setup monitoring, logging, and performance tracking
    """
    # Create logs directory if it doesn't exist
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    # Setup application logging
    app_logger = logging.getLogger("app")
    app_logger.setLevel(logging.INFO)
    
    # Setup security audit logging
    security_logger = logging.getLogger("security")
    security_logger.setLevel(logging.WARNING)
    
    # File handlers
    app_handler = logging.FileHandler("logs/app.log")
    security_handler = logging.FileHandler("logs/security_audit.log")
    performance_handler = logging.FileHandler("logs/performance.log")
    
    # Formatters
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    app_handler.setFormatter(formatter)
    security_handler.setFormatter(formatter)
    performance_handler.setFormatter(formatter)
    
    # Add handlers
    app_logger.addHandler(app_handler)
    security_logger.addHandler(security_handler)
    
    print("✅ Monitoring and logging configured")

def log_security_event(event_type: str, user_id: str = None, details: str = None):
    """
    Log security-related events
    """
    security_logger = logging.getLogger("security")
    message = f"Security Event: {event_type}"
    if user_id:
        message += f" | User: {user_id}"
    if details:
        message += f" | Details: {details}"
    
    security_logger.warning(message)

def log_performance_metric(operation: str, duration: float, user_id: str = None):
    """
    Log performance metrics
    """
    performance_logger = logging.getLogger("performance")
    message = f"Performance: {operation} took {duration:.2f}ms"
    if user_id:
        message += f" | User: {user_id}"
    
    performance_logger.info(message)
