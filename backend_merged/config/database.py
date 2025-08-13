# Database configuration for merged backend
import os
from dotenv import load_dotenv

load_dotenv()

class DatabaseConfig:
    """Database configuration settings"""
    
    # PostgreSQL Configuration
    PG_USER = os.getenv("PG_USER", "postgres")
    PG_PASSWORD = os.getenv("PG_PASSWORD", "password")
    PG_HOST = os.getenv("PG_HOST", "localhost")
    PG_PORT = os.getenv("PG_PORT", "5432")
    PG_DATABASE = os.getenv("PG_DATABASE", "ques_merged_db")
    
    # Connection pooling settings
    DB_POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "10"))
    DB_MAX_OVERFLOW = int(os.getenv("DB_MAX_OVERFLOW", "20"))
    DB_POOL_TIMEOUT = int(os.getenv("DB_POOL_TIMEOUT", "30"))
    DB_POOL_RECYCLE = int(os.getenv("DB_POOL_RECYCLE", "3600"))
    
    @property
    def database_url(self) -> str:
        """Get the complete database URL"""
        db_url = os.getenv("DATABASE_URL")
        if db_url:
            return db_url
        return f"postgresql://{self.PG_USER}:{self.PG_PASSWORD}@{self.PG_HOST}:{self.PG_PORT}/{self.PG_DATABASE}"
    
    @property
    def async_database_url(self) -> str:
        """Get the async database URL"""
        return self.database_url.replace("postgresql://", "postgresql+asyncpg://")

# Global config instance
db_config = DatabaseConfig()
