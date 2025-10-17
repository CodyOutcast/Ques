"""
Main FastAPI application for the merged backend
Combines features from backend_p12 and backend_p34
"""

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from contextlib import asynccontextmanager
import logging
import os
from dotenv import load_dotenv

from dependencies.db import get_db, engine
from models.base import Base
from routers import auth, users, user_reports, intelligent_agent, basic_operations, university_verification, notifications, contacts, whispers, payments, ai_services, tpns, project_management, sms_router, swipes, user_settings, chat
# university_verification - now uses existing UserProfile model
# Commented out routers that import deleted models:
# sms_router - phone verification service (field names fixed) 
# settings as settings_router - imports from models.settings
# swipes - imports from models.swipes 
# matching - imports from models.swipes
# payment_system - imports from models.payments
# card_tracking - may import from deleted models
# casual_requests - imports from models.casual_requests 
# chat_agent - imports from models.casual_requests
# projects - imports from models.projects
# membership - imports from models.payments
# admin_project_slots commented out - requires get_current_admin_user which isn't implemented
from config.settings import settings
# Recommendations disabled - router not available
# try:
#     from routers import recommendations
#     RECOMMENDATIONS_AVAILABLE = True
# except ImportError as e:
#     print(f"Warning: Recommendations module not available: {e}")
RECOMMENDATIONS_AVAILABLE = False
from services.monitoring import setup_monitoring

# Load environment variables
load_dotenv()

# Configure logging with environment-aware settings
log_config = settings.logging
logging.basicConfig(
    level=getattr(logging, log_config.level),
    format=log_config.format,
    handlers=[
        logging.FileHandler(log_config.file_path) if log_config.file_enabled else logging.NullHandler(),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Create logs directory if it doesn't exist
if log_config.file_enabled:
    os.makedirs(os.path.dirname(log_config.file_path), exist_ok=True)

# Security
security = HTTPBearer()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info(f"🚀 Starting {settings.api_title} in {settings.environment.value} mode...")
    
    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)
    
    # Setup monitoring
    setup_monitoring()
    
    # Start background tasks
    try:
        from services.task_scheduler import start_background_tasks
        await start_background_tasks()
        logger.info("✅ Background tasks started")
    except Exception as e:
        logger.error(f"❌ Failed to start background tasks: {e}")
    
    logger.info("✅ Application startup complete")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down application...")
    
    # Stop background tasks
    try:
        from services.task_scheduler import stop_background_tasks
        await stop_background_tasks()
        logger.info("✅ Background tasks stopped")
    except Exception as e:
        logger.error(f"❌ Error stopping background tasks: {e}")

# Create FastAPI app with environment-aware configuration
app = FastAPI(
    title=settings.api_title,
    description=settings.api_description,
    version=settings.api_version,
    docs_url="/docs" if settings.enable_docs else None,
    redoc_url="/redoc" if settings.enable_docs else None,
    openapi_url="/openapi.json" if settings.enable_docs else None,
    lifespan=lifespan
)

# Production security middleware
if settings.is_production:
    # Trusted host middleware for production
    app.add_middleware(
        TrustedHostMiddleware, 
        allowed_hosts=["ques.chat", "*.ques.chat", "www.ques.chat"]
    )

# Content moderation middleware (before CORS and other middleware)
# TODO: Re-enable after creating services.content_moderation
# from middleware.content_moderation import ContentModerationMiddleware
from middleware.session_tracking import SessionTrackingMiddleware
# moderation_enabled = getattr(settings, 'enable_content_moderation', True)
# app.add_middleware(ContentModerationMiddleware, enabled=moderation_enabled)

# Session tracking middleware (should be after content moderation but before CORS)
app.add_middleware(SessionTrackingMiddleware)

# Gzip compression for all environments
app.add_middleware(GZipMiddleware, minimum_size=1000)

# CORS middleware with environment-aware settings
security_config = settings.security
app.add_middleware(
    CORSMiddleware,
    allow_origins=security_config.cors_origins,
    allow_credentials=security_config.cors_allow_credentials,
    allow_methods=security_config.cors_allow_methods,
    allow_headers=security_config.cors_allow_headers,
)

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
app.include_router(user_reports.router, prefix="/api/v1", tags=["User Reports"])
app.include_router(sms_router.router, prefix="/api/v1/sms", tags=["SMS Verification"])
app.include_router(university_verification.router, prefix="/api/v1/university", tags=["University Verification"])
app.include_router(project_management.router, prefix="/api/v1", tags=["Project Management"])
logger.info("✅ Project management router loaded")
# app.include_router(settings_router.router, prefix="/api/v1/settings", tags=["Settings Management"])  # Commented - imports deleted models
# app.include_router(project_ideas.router, tags=["Project Ideas"])  # Disabled - router not found

# Project Ideas V2 with enhanced features - Disabled (router not found)
# try:
#     from routers import project_ideas_v2
#     app.include_router(project_ideas_v2.router, tags=["Project Ideas V2"])
#     logger.info("✅ Project Ideas V2 router loaded")
# except ImportError as e:
#     logger.warning(f"Project Ideas V2 router not available: {e}")

# Recommendations disabled - router not available
# if RECOMMENDATIONS_AVAILABLE:
#     app.include_router(recommendations.router, prefix="/api/v1/recommendations", tags=["Recommendations"])

# Vector-based recommendations - REMOVED

# Intelligent Agent (Search, Inquiry, Chat)
app.include_router(intelligent_agent.router, tags=["Intelligent Agent"])
logger.info("✅ Intelligent agent router loaded")

# Basic Operations (User Creation, Whispers, Swiping, Top Profiles)
app.include_router(basic_operations.router, tags=["Basic Operations"])
logger.info("✅ Basic operations router loaded")


app.include_router(swipes.router, prefix="/swipes", tags=["swipes"])
app.include_router(user_settings.router, prefix="/user-settings", tags=["user-settings"])
app.include_router(user_reports.router, prefix="/user-reports", tags=["user-reports"])
app.include_router(intelligent_agent.router, prefix="/intelligent-agent", tags=["intelligent-agent"])
app.include_router(notifications.router, prefix="/notifications", tags=["notifications"])
app.include_router(contacts.router, prefix="/contacts", tags=["contacts"])
app.include_router(whispers.router, prefix="/whispers", tags=["whispers"])
app.include_router(payments.router, prefix="/payments", tags=["payments"])
app.include_router(ai_services.router, prefix="/ai-services", tags=["ai-services"])
app.include_router(chat.router, prefix="/chat", tags=["chat"])
app.include_router(university_verification.router, prefix="/university-verification", tags=["university-verification"])
app.include_router(tpns.router, prefix="/tpns", tags=["tpns"])
app.include_router(project_management.router, prefix="/project-management", tags=["project-management"])
app.include_router(sms_router.router, prefix="/sms", tags=["sms"])  # New swipe system
# logger.info("✅ Swipes router loaded")
# app.include_router(matching.router, prefix="/api/v1", tags=["Matching"])  # Commented - imports deleted models.swipes  
# logger.info("✅ Matching router loaded")

# New Service Routers
app.include_router(notifications.router, prefix="/api/v1/notifications", tags=["Notification System"])
logger.info("✅ Notification system router loaded")
app.include_router(contacts.router, prefix="/api/v1/contacts", tags=["Contact Management"])
logger.info("✅ Contact management router loaded")
app.include_router(whispers.router, prefix="/api/v1/whispers", tags=["Whisper Messaging"])
logger.info("✅ Whisper messaging router loaded")
app.include_router(payments.router, prefix="/api/v1/payments", tags=["Payment System"])
logger.info("✅ Payment system router loaded")
# app.include_router(card_tracking.router, prefix="/api/v1/tracking", tags=["Card Tracking"])  # Commented - may import deleted models
# logger.info("✅ Card tracking router loaded")
app.include_router(ai_services.router, prefix="/api/v1/ai", tags=["AI Services"])
logger.info("✅ AI services router loaded")
# app.include_router(casual_requests.router, prefix="/api/v1/casual-requests", tags=["Casual Requests"])  # Commented - imports deleted models.casual_requests
# logger.info("✅ Casual requests router loaded")
# app.include_router(chat_agent.router, prefix="/api/v1", tags=["Chat Agent"])  # Commented - imports deleted models.casual_requests
# logger.info("✅ Chat agent router loaded")

# Project and Membership System
# app.include_router(projects.router, prefix="/api/v1", tags=["Projects"])  # Commented - imports deleted models.projects
# logger.info("✅ Projects router loaded")
# app.include_router(membership.router, prefix="/api/v1", tags=["Membership"])  # Commented - imports deleted models.payments
# logger.info("✅ Membership router loaded")

app.include_router(tpns.router, prefix="/api/v1/tpns", tags=["Push Notifications (TPNS)"])
logger.info("✅ TPNS router loaded")



@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Merged Dating App API",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Enhanced health check endpoint with environment info"""
    try:
        # Test database connection
        from dependencies.db import get_db
        db = next(get_db())
        db.execute("SELECT 1")
        db.close()
        
        return {
            "status": "healthy",
            "environment": settings.environment.value,
            "database": "connected",
            "timestamp": "2025-07-30T00:00:00Z",
            "version": settings.api_version,
            "debug": settings.debug
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "status": "unhealthy",
                "environment": settings.environment.value,
                "error": str(e) if settings.debug else "Service unavailable"
            }
        )

@app.get("/api/v1/info")
async def api_info():
    """API information endpoint"""
    return {
        "api_name": "Merged Dating App API",
        "version": "1.0.0",
        "features": [
            "Enterprise Authentication (Email + WeChat)",
            "Smart Recommendation Engine (Page 1)",
            "AI-Powered Search (Page 2)",
            "Social Matching & Messaging",
            "User Profiles & Links",
            "Swipe History Tracking",
            "Vector Similarity Matching",
            "Feature Flags",
            "Security Monitoring",
            "Project Idea Generation Agent",
            "Concurrent User Tracking",
            "Online User Analytics",
            "Session Management"
        ],
        "endpoints": {
            "auth": "/api/v1/auth",
            "users": "/api/v1/users", 
            "recommendations": "/api/v1/recommendations",
            "search": "/api/v1/search",
            "messages": "/api/v1/messages",
            "profile": "/api/v1/profile",
            "project_ideas": "/api/v1/project-ideas",
            "online_users": "/api/v1/online"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
