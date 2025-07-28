"""
Enhanced configuration management with validation and environment detection
"""
import os
import logging
from typing import Optional, Dict, Any, List
from pathlib import Path
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class Environment(Enum):
    """Application environments"""
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"

@dataclass
class DatabaseConfig:
    """Database configuration"""
    url: str
    echo: bool = False
    pool_size: int = 20
    max_overflow: int = 30
    pool_timeout: int = 30
    pool_recycle: int = 3600

@dataclass
class EmailConfig:
    """Email service configuration"""
    service_type: str = "tencent"  # tencent, sendgrid, etc.
    
    # Tencent Cloud SES
    secret_id: Optional[str] = None
    secret_key: Optional[str] = None
    region: str = "ap-guangzhou"
    sender_email_1: Optional[str] = None
    sender_email_2: Optional[str] = None
    template_id_en: Optional[str] = None
    template_id_cn: Optional[str] = None
    
    # Alternative email services
    sendgrid_api_key: Optional[str] = None
    smtp_host: Optional[str] = None
    smtp_port: Optional[int] = None
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None

@dataclass
class WeChatConfig:
    """WeChat OAuth configuration"""
    app_id: Optional[str] = None
    secret: Optional[str] = None
    mini_program_app_id: Optional[str] = None
    mini_program_secret: Optional[str] = None
    webhook_token: Optional[str] = None

@dataclass
class SecurityConfig:
    """Security and authentication configuration"""
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    refresh_token_expire_days: int = 30
    password_hash_rounds: int = 12
    rate_limit_requests: int = 100
    rate_limit_window: int = 3600
    cors_origins: List[str] = None

@dataclass
class AIConfig:
    """AI and ML service configuration"""
    deepseek_api_key: Optional[str] = None
    deepseek_base_url: str = "https://api.deepseek.com"
    vector_db_url: Optional[str] = None
    embedding_model: str = "text-embedding-ada-002"
    max_tokens: int = 4000

@dataclass
class RedisConfig:
    """Redis configuration for caching and sessions"""
    url: Optional[str] = None
    host: str = "localhost"
    port: int = 6379
    db: int = 0
    password: Optional[str] = None
    ssl: bool = False

class AppConfig:
    """Main application configuration"""
    
    def __init__(self):
        self.environment = self._get_environment()
        self.debug = self.environment in [Environment.DEVELOPMENT, Environment.TESTING]
        
        # Load configuration
        self.database = self._load_database_config()
        self.email = self._load_email_config()
        self.wechat = self._load_wechat_config()
        self.security = self._load_security_config()
        self.ai = self._load_ai_config()
        self.redis = self._load_redis_config()
        
        # Validate configuration
        self._validate_config()
    
    def _get_environment(self) -> Environment:
        """Determine the current environment"""
        env_str = os.getenv('ENVIRONMENT', 'development').lower()
        
        for env in Environment:
            if env.value == env_str:
                return env
        
        logger.warning(f"Unknown environment '{env_str}', defaulting to development")
        return Environment.DEVELOPMENT
    
    def _load_database_config(self) -> DatabaseConfig:
        """Load database configuration"""
        return DatabaseConfig(
            url=os.getenv('DATABASE_URL', 'postgresql://user:password@localhost/dating_app'),
            echo=os.getenv('DATABASE_ECHO', 'false').lower() == 'true',
            pool_size=int(os.getenv('DATABASE_POOL_SIZE', '20')),
            max_overflow=int(os.getenv('DATABASE_MAX_OVERFLOW', '30')),
            pool_timeout=int(os.getenv('DATABASE_POOL_TIMEOUT', '30')),
            pool_recycle=int(os.getenv('DATABASE_POOL_RECYCLE', '3600'))
        )
    
    def _load_email_config(self) -> EmailConfig:
        """Load email service configuration"""
        return EmailConfig(
            service_type=os.getenv('EMAIL_SERVICE_TYPE', 'tencent'),
            secret_id=os.getenv('TENCENT_SECRET_ID'),
            secret_key=os.getenv('TENCENT_SECRET_KEY'),
            region=os.getenv('TENCENT_REGION', 'ap-guangzhou'),
            sender_email_1=os.getenv('TENCENT_SENDER_EMAIL_1'),
            sender_email_2=os.getenv('TENCENT_SENDER_EMAIL_2'),
            template_id_en=os.getenv('TENCENT_EMAIL_TEMPLATE_ID_EN'),
            template_id_cn=os.getenv('TENCENT_EMAIL_TEMPLATE_ID_CN'),
            sendgrid_api_key=os.getenv('SENDGRID_API_KEY'),
            smtp_host=os.getenv('SMTP_HOST'),
            smtp_port=int(os.getenv('SMTP_PORT', '587')) if os.getenv('SMTP_PORT') else None,
            smtp_username=os.getenv('SMTP_USERNAME'),
            smtp_password=os.getenv('SMTP_PASSWORD')
        )
    
    def _load_wechat_config(self) -> WeChatConfig:
        """Load WeChat configuration"""
        return WeChatConfig(
            app_id=os.getenv('WECHAT_APP_ID'),
            secret=os.getenv('WECHAT_SECRET'),
            mini_program_app_id=os.getenv('WECHAT_MINI_PROGRAM_APP_ID'),
            mini_program_secret=os.getenv('WECHAT_MINI_PROGRAM_SECRET'),
            webhook_token=os.getenv('WECHAT_WEBHOOK_TOKEN')
        )
    
    def _load_security_config(self) -> SecurityConfig:
        """Load security configuration"""
        secret_key = os.getenv('SECRET_KEY')
        if not secret_key:
            if self.environment == Environment.PRODUCTION:
                raise ValueError("SECRET_KEY must be set in production")
            secret_key = "dev-secret-key-not-for-production"
        
        cors_origins = os.getenv('CORS_ORIGINS', '').split(',') if os.getenv('CORS_ORIGINS') else ['*']
        
        return SecurityConfig(
            secret_key=secret_key,
            algorithm=os.getenv('JWT_ALGORITHM', 'HS256'),
            access_token_expire_minutes=int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', '60')),
            refresh_token_expire_days=int(os.getenv('REFRESH_TOKEN_EXPIRE_DAYS', '30')),
            password_hash_rounds=int(os.getenv('PASSWORD_HASH_ROUNDS', '12')),
            rate_limit_requests=int(os.getenv('RATE_LIMIT_REQUESTS', '100')),
            rate_limit_window=int(os.getenv('RATE_LIMIT_WINDOW', '3600')),
            cors_origins=cors_origins
        )
    
    def _load_ai_config(self) -> AIConfig:
        """Load AI service configuration"""
        return AIConfig(
            deepseek_api_key=os.getenv('DEEPSEEK_API_KEY'),
            deepseek_base_url=os.getenv('DEEPSEEK_BASE_URL', 'https://api.deepseek.com'),
            vector_db_url=os.getenv('VECTOR_DB_URL'),
            embedding_model=os.getenv('EMBEDDING_MODEL', 'text-embedding-ada-002'),
            max_tokens=int(os.getenv('AI_MAX_TOKENS', '4000'))
        )
    
    def _load_redis_config(self) -> RedisConfig:
        """Load Redis configuration"""
        redis_url = os.getenv('REDIS_URL')
        
        return RedisConfig(
            url=redis_url,
            host=os.getenv('REDIS_HOST', 'localhost'),
            port=int(os.getenv('REDIS_PORT', '6379')),
            db=int(os.getenv('REDIS_DB', '0')),
            password=os.getenv('REDIS_PASSWORD'),
            ssl=os.getenv('REDIS_SSL', 'false').lower() == 'true'
        )
    
    def _validate_config(self):
        """Validate critical configuration"""
        errors = []
        
        # Database validation
        if not self.database.url or 'localhost' in self.database.url:
            if self.environment == Environment.PRODUCTION:
                errors.append("Production DATABASE_URL must not be localhost")
        
        # Email validation
        if self.email.service_type == 'tencent':
            if not all([self.email.secret_id, self.email.secret_key]):
                errors.append("Tencent email service requires SECRET_ID and SECRET_KEY")
        
        # Security validation
        if self.environment == Environment.PRODUCTION:
            if self.security.secret_key == "dev-secret-key-not-for-production":
                errors.append("Production SECRET_KEY must be set")
            
            if self.security.cors_origins == ['*']:
                errors.append("Production CORS_ORIGINS should not be '*'")
        
        if errors:
            error_msg = "Configuration validation failed:\n" + "\n".join(f"- {error}" for error in errors)
            if self.environment == Environment.PRODUCTION:
                raise ValueError(error_msg)
            else:
                logger.warning(error_msg)
    
    def get_config_summary(self) -> Dict[str, Any]:
        """Get a summary of the current configuration (safe for logging)"""
        return {
            "environment": self.environment.value,
            "debug": self.debug,
            "database": {
                "driver": self.database.url.split("://")[0] if "://" in self.database.url else "unknown",
                "echo": self.database.echo,
                "pool_size": self.database.pool_size
            },
            "email": {
                "service_type": self.email.service_type,
                "region": self.email.region,
                "configured": bool(self.email.secret_id and self.email.secret_key)
            },
            "wechat": {
                "web_configured": bool(self.wechat.app_id and self.wechat.secret),
                "mini_program_configured": bool(self.wechat.mini_program_app_id and self.wechat.mini_program_secret)
            },
            "security": {
                "algorithm": self.security.algorithm,
                "access_token_expire_minutes": self.security.access_token_expire_minutes,
                "rate_limit_requests": self.security.rate_limit_requests,
                "cors_origins_count": len(self.security.cors_origins)
            },
            "ai": {
                "deepseek_configured": bool(self.ai.deepseek_api_key),
                "vector_db_configured": bool(self.ai.vector_db_url)
            },
            "redis": {
                "configured": bool(self.redis.url or (self.redis.host and self.redis.port))
            }
        }

# Global configuration instance
config = AppConfig()
