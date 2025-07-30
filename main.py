"""
Main FastAPI application for the merged backend
Combines features from backend_p12 and backend_p34
"""

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from contextlib import asynccontextmanager
import logging
import os
from dotenv import load_dotenv

from dependencies.db import get_db, engine
from models.base import Base
from routers import auth, users, matches, messages, profile, chats
try:
    from routers import recommendations
    RECOMMENDATIONS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Recommendations module not available: {e}")
    RECOMMENDATIONS_AVAILABLE = False, recommendations
from services.monitoring import setup_monitoring

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Security
security = HTTPBearer()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("🚀 Starting Merged Backend Application...")
    
    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)
    
    # Setup monitoring
    setup_monitoring()
    
    logger.info("✅ Application startup complete")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down application...")

# Create FastAPI app
app = FastAPI(
    title="Merged Dating App API",
    description="Combined backend with enterprise authentication, social features, and project matching",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
if RECOMMENDATIONS_AVAILABLE:
    app.include_router(recommendations.router, prefix="/api/v1/recommendations", tags=["Recommendations"])
app.include_router(matches.router, prefix="/api/v1/search", tags=["AI Search"])
app.include_router(messages.router, prefix="/api/v1/messages", tags=["Messaging"])
app.include_router(profile.router, prefix="/api/v1/profile", tags=["Profile"])
app.include_router(chats.router, prefix="/api/v1", tags=["Chats"])

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
    """Health check endpoint"""
    try:
        # Test database connection
        from dependencies.db import get_db
        db = next(get_db())
        db.execute("SELECT 1")
        db.close()
        
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": "2025-07-29T00:00:00Z"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service unavailable"
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
            "Security Monitoring"
        ],
        "endpoints": {
            "auth": "/api/v1/auth",
            "users": "/api/v1/users", 
            "recommendations": "/api/v1/recommendations",
            "search": "/api/v1/search",
            "messages": "/api/v1/messages",
            "profile": "/api/v1/profile"
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
