from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from routers.recommendations import router as recommendations_router
from routers.match import router as match_router
from routers.auth import router as auth_router
import logging
import os
from dotenv import load_dotenv

load_dotenv()

# Configure logging
log_level = os.getenv('LOG_LEVEL', 'INFO')
logging.basicConfig(
    level=getattr(logging, log_level.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Project Tinder Backend", 
    description="Backend API for project matchmaking app - Pages 1 & 2",
    version="1.0.0"
)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "type": "internal_error"}
    )

# Add CORS middleware for React Native frontend
environment = os.getenv('ENVIRONMENT', 'development')
allowed_origins = ["*"] if environment == "development" else [
    "http://localhost:3000",  # React Native Metro
    "exp://localhost:19000",  # Expo development
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(recommendations_router, prefix="/recommendations", tags=["Recommendations"])
app.include_router(match_router, prefix="/search", tags=["AI Search"])

@app.get("/")
def root():
    return {"message": "Project Tinder Backend API - Ready for Pages 1 & 2"}

@app.get("/health")
def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "message": "Backend is running",
        "version": "1.0.0",
        "environment": os.getenv('ENVIRONMENT', 'development')
    }