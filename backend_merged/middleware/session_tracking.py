"""
Session tracking middleware for monitoring online users
"""

import os
import logging
from datetime import datetime, timedelta
from fastapi import Request, Response
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional
from jose import JWTError, jwt
from models.user_auth import UserSession
from models.users import User
from dependencies.db import SessionLocal

logger = logging.getLogger(__name__)

# JWT configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
ALGORITHM = "HS256"

class SessionTrackingMiddleware:
    """Middleware to track user sessions and update last_activity"""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            request = Request(scope, receive)
            
            # Skip tracking for certain paths
            skip_paths = ["/docs", "/redoc", "/openapi.json", "/health", "/favicon.ico"]
            if any(request.url.path.startswith(path) for path in skip_paths):
                return await self.app(scope, receive, send)
            
            # Get authorization header
            auth_header = request.headers.get("authorization")
            if auth_header and auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]
                await self.update_user_activity(token, request)
        
        return await self.app(scope, receive, send)
    
    async def update_user_activity(self, token: str, request: Request):
        """Update user's last activity in the database"""
        try:
            db = SessionLocal()
            
            # Get current user from token (simplified version)
            current_user = await self.get_user_from_token(db, token)
            if not current_user:
                return
            
            # Update or create session
            ip_address = self.get_client_ip(request)
            user_agent = request.headers.get("user-agent", "Unknown")
            
            # Find existing active session
            existing_session = db.query(UserSession).filter(
                UserSession.user_id == current_user.user_id,
                UserSession.session_token == token,
                UserSession.is_active == True
            ).first()
            
            if existing_session:
                # Update existing session
                existing_session.last_activity = datetime.utcnow()
                existing_session.ip_address = ip_address
                existing_session.user_agent = user_agent
            else:
                # Create new session if none exists
                new_session = UserSession(
                    user_id=current_user.user_id,
                    session_token=token,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    last_activity=datetime.utcnow(),
                    expires_at=datetime.utcnow() + timedelta(hours=24),
                    is_active=True
                )
                db.add(new_session)
            
            db.commit()
            
        except Exception as e:
            logger.error(f"Error updating user activity: {e}")
        finally:
            if 'db' in locals():
                db.close()
    
    async def get_user_from_token(self, db: Session, token: str) -> Optional[User]:
        """Get user from JWT token"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id = payload.get("sub")
            
            if user_id:
                return db.query(User).filter(User.user_id == int(user_id)).first()
        except Exception as e:
            logger.error(f"Error decoding token: {e}")
        return None
    
    def get_client_ip(self, request: Request) -> str:
        """Get client IP address from request"""
        # Check for forwarded headers first (for load balancers/proxies)
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip
        
        # Fallback to direct client IP
        if request.client:
            return request.client.host
        
        return "unknown"
