from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from routers.recommendations import router as recommendations_router
from routers.match import router as match_router
from routers.auth import router as auth_router
from services.monitoring import PerformanceMiddleware, api_metrics
from services.security import SecurityMiddleware
from services.input_sanitization import InputSanitizationMiddleware
from services.error_handling import APIException, APIResponse, ErrorCode
from config.settings import config, Environment
import logging
import os
from dotenv import load_dotenv

load_dotenv()

# Configure logging with enhanced format
log_level = os.getenv('LOG_LEVEL', 'INFO')
logging.basicConfig(
    level=getattr(logging, log_level.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
)
logger = logging.getLogger(__name__)

# Create logs directory if it doesn't exist
os.makedirs("logs", exist_ok=True)

app = FastAPI(
    title="Ques Backend", 
    description="Enhanced backend API for Ques - Connect with projects and investment opportunities",
    version="2.0.0"
)

# Add enhanced middleware
app.add_middleware(PerformanceMiddleware)
app.add_middleware(InputSanitizationMiddleware, max_request_size=1024*1024)  # 1MB limit
app.add_middleware(
    SecurityMiddleware,
    rate_limit_requests=config.security.rate_limit_requests,
    rate_limit_window=config.security.rate_limit_window
)

# Enhanced exception handlers
@app.exception_handler(APIException)
async def api_exception_handler(request: Request, exc: APIException):
    return APIResponse.error(
        error_code=exc.error_code,
        details=exc.details,
        field_errors=exc.field_errors,
        status_code=exc.status_code
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return APIResponse.error(
        error_code=ErrorCode.INVALID_REQUEST,
        details=str(exc.detail),
        status_code=exc.status_code
    )

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return APIResponse.error(
        error_code=ErrorCode.INTERNAL_SERVER_ERROR,
        details="An unexpected error occurred" if config.environment.value == "production" else str(exc),
        status_code=500
    )

# Add CORS middleware - use config for origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.security.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(recommendations_router, prefix="/recommendations", tags=["Recommendations"])
app.include_router(match_router, prefix="/search", tags=["AI Search"])

@app.get("/")
async def root():
    """Welcome endpoint with API information"""
    return {
        "status": "success",
        "data": {
            "message": "Ques Backend API - Enhanced Version",
            "version": "2.0.0",
            "features": [
                "User Authentication & Registration",
                "Project Recommendations", 
                "Advanced Search",
                "Real-time Monitoring",
                "Enterprise Security"
            ]
        }
    }

@app.get("/health")
def health_check():
    """Enhanced health check endpoint with system status"""
    return APIResponse.success(
        data={
            "status": "healthy",
            "version": "2.0.0",
            "environment": config.environment.value,
            "config_summary": config.get_config_summary(),
            "metrics": api_metrics.get_metrics()
        }
    )

@app.get("/metrics")
def get_metrics():
    """API metrics endpoint for monitoring"""
    return APIResponse.success(data=api_metrics.get_metrics())

@app.post("/admin/reset-metrics")
def reset_metrics():
    """Reset API metrics (admin endpoint)"""
    api_metrics.reset_metrics()
    return APIResponse.success(message="Metrics reset successfully")