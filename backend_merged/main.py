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
from routers import auth, users, matches, messages, profile, chats, projects, project_cards, membership, location, user_reports, sms_router, project_ideas, payments, online_users, revenue_analytics, quota_payments, agent_cards, project_slots, admin_project_slots, membership_webhooks
from config.settings import settings
try:
    from routers import recommendations
    RECOMMENDATIONS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Recommendations module not available: {e}")
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
from middleware.content_moderation import ContentModerationMiddleware
from middleware.session_tracking import SessionTrackingMiddleware
moderation_enabled = getattr(settings, 'enable_content_moderation', True)
app.add_middleware(ContentModerationMiddleware, enabled=moderation_enabled)

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
app.include_router(sms_router.router, tags=["SMS Verification"])
app.include_router(project_ideas.router, tags=["Project Ideas"])

# Project Ideas V2 with enhanced features
try:
    from routers import project_ideas_v2
    app.include_router(project_ideas_v2.router, tags=["Project Ideas V2"])
    logger.info("✅ Project Ideas V2 router loaded")
except ImportError as e:
    logger.warning(f"Project Ideas V2 router not available: {e}")

if RECOMMENDATIONS_AVAILABLE:
    app.include_router(recommendations.router, prefix="/api/v1/recommendations", tags=["Recommendations"])

# Vector-based recommendations (always available)
try:
    from routers import vector_recommendations
    app.include_router(vector_recommendations.router, tags=["Vector Recommendations"])
    logger.info("✅ Vector recommendations router loaded")
except ImportError as e:
    logger.warning(f"⚠️ Vector recommendations router not available: {e}")

app.include_router(matches.router, prefix="/api/v1/search", tags=["AI Search"])
app.include_router(messages.router, prefix="/api/v1/messages", tags=["Messaging"])
app.include_router(profile.router, prefix="/api/v1/profile", tags=["Profile"])
app.include_router(chats.router, prefix="/api/v1", tags=["Chats"])
app.include_router(projects.router, prefix="/api/v1", tags=["Projects"])
app.include_router(project_cards.router, tags=["Project Cards"])
app.include_router(agent_cards.router, tags=["Agent Cards"])
app.include_router(membership.router, tags=["Membership"])
app.include_router(payments.router, prefix="/api/v1/payments", tags=["Payments"])
app.include_router(quota_payments.router, tags=["Quota Payments"])
app.include_router(revenue_analytics.router, tags=["Revenue Analytics"])
app.include_router(location.router, prefix="/api/v1", tags=["Location"])
app.include_router(online_users.router, prefix="/api/v1/online", tags=["Online Users"])

# Project Slots System
app.include_router(project_slots.router, prefix="/api/v1", tags=["Project Slots"])
app.include_router(admin_project_slots.router, prefix="/api/v1", tags=["Admin - Project Slots"])
app.include_router(membership_webhooks.router, prefix="/api/v1", tags=["Webhooks - Membership"])

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
