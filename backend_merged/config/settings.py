"""
Production configuration settings for Ques backend
Environment-aware configuration with security best practices
"""
import os
from typing import List, Optional
from pydantic import BaseModel, validator
from enum import Enum

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # dotenv not available, use system environment variables
    pass

class Environment(str, Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"

class SecurityConfig(BaseModel):
    """Security configuration"""
    # CORS settings
    cors_origins: List[str] = ["*"]  # Override in production
    cors_allow_credentials: bool = True
    cors_allow_methods: List[str] = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    cors_allow_headers: List[str] = ["*"]
    
    # Rate limiting
    rate_limit_requests: int = 100  # requests per window
    rate_limit_window: int = 3600   # window in seconds (1 hour)
    
    # JWT settings
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    
    # Security headers
    enable_security_headers: bool = True
    max_request_size: int = 10 * 1024 * 1024  # 10MB

class DatabaseConfig(BaseModel):
    """Database configuration"""
    # Connection settings
    pool_size: int = 5
    max_overflow: int = 10
    pool_timeout: int = 30
    pool_recycle: int = 3600
    
    # SSL settings for production
    ssl_require: bool = False
    ssl_ca: Optional[str] = None
    ssl_cert: Optional[str] = None
    ssl_key: Optional[str] = None

class LoggingConfig(BaseModel):
    """Logging configuration"""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_enabled: bool = True
    file_path: str = "logs/app.log"
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5

class Settings(BaseModel):
    """Main application settings"""
    # Environment
    environment: Environment = Environment.DEVELOPMENT
    debug: bool = False
    
    # API Configuration
    api_title: str = "Ques API"
    api_description: str = "Tinder for Projects - Connect, Collaborate, Create"
    api_version: str = "1.0.0"
    
    # Server configuration
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 1
    
    # Security
    security: SecurityConfig = SecurityConfig()
    
    # Database
    database: DatabaseConfig = DatabaseConfig()
    
    # Logging
    logging: LoggingConfig = LoggingConfig()
    
    # Feature flags
    enable_docs: bool = True
    enable_metrics: bool = True
    enable_health_checks: bool = True
    
    # Tencent Cloud Configuration
    TENCENT_SECRET_ID: Optional[str] = os.getenv('TENCENT_SECRET_ID')
    TENCENT_SECRET_KEY: Optional[str] = os.getenv('TENCENT_SECRET_KEY')
    TENCENT_REGION: str = os.getenv('TENCENT_REGION', 'ap-guangzhou')
    
    # Content Moderation Configuration
    ENABLE_CONTENT_MODERATION: bool = os.getenv('ENABLE_CONTENT_MODERATION', 'false').lower() == 'true'
    TENCENT_MODERATION_BIZ_TYPE: str = os.getenv('TENCENT_MODERATION_BIZ_TYPE', 'default')
    
    @validator('environment', pre=True)
    def validate_environment(cls, v):
        if isinstance(v, str):
            return Environment(v.lower())
        return v
    
    @property
    def is_production(self) -> bool:
        return self.environment == Environment.PRODUCTION
    
    @property
    def is_development(self) -> bool:
        return self.environment == Environment.DEVELOPMENT

def get_settings() -> Settings:
    """Get settings based on environment"""
    env = os.getenv("ENVIRONMENT", "development").lower()
    
    if env == "production":
        return get_production_settings()
    elif env == "staging":
        return get_staging_settings()
    else:
        return get_development_settings()

def get_development_settings() -> Settings:
    """Development environment settings"""
    return Settings(
        environment=Environment.DEVELOPMENT,
        debug=True,
        security=SecurityConfig(
            cors_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:3001", "http://127.0.0.1:3001", "http://localhost:8081"],
            rate_limit_requests=1000,  # More lenient for development
        ),
        logging=LoggingConfig(level="DEBUG"),
        enable_docs=True,
        enable_metrics=True,
    )

def get_staging_settings() -> Settings:
    """Staging environment settings"""
    return Settings(
        environment=Environment.STAGING,
        debug=False,
        security=SecurityConfig(
            cors_origins=[
                "https://staging.ques.chat",
                "https://staging-app.ques.chat"
            ],
            rate_limit_requests=500,
        ),
        logging=LoggingConfig(level="INFO"),
        enable_docs=True,  # Enable docs in staging for testing
        enable_metrics=True,
    )

def get_production_settings() -> Settings:
    """Production environment settings"""
    return Settings(
        environment=Environment.PRODUCTION,
        debug=False,
        workers=4,  # Multiple workers for production
        security=SecurityConfig(
            cors_origins=[
                "https://ques.chat",
                "https://app.ques.chat",
                "https://www.ques.chat"
            ],
            rate_limit_requests=100,
            enable_security_headers=True,
        ),
        database=DatabaseConfig(
            pool_size=20,
            max_overflow=30,
            ssl_require=True,  # Require SSL in production
        ),
        logging=LoggingConfig(
            level="WARNING",  # Less verbose logging in production
            file_enabled=True,
        ),
        enable_docs=False,  # Disable docs in production for security
        enable_metrics=True,
    )

# Global settings instance
settings = get_settings()
