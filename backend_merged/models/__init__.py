# Import all models to ensure they're registered with SQLAlchemy
# ✅ Only models with actual database tables are imported
from .base import Base
from .users import User
from .user_profiles import UserProfile
from .likes import UserSwipe, SwipeDirection
from .user_reports import UserReport
from .locations import Province, City
from .whispers import Whisper
from .user_auth import UserAuth, VerificationCode, RefreshToken, UserSession, ProviderType

# Export all models
__all__ = [
    "Base",
    "User",
    "UserProfile",
    "UserSwipe", 
    "SwipeDirection",
    "UserReport",
    "Province",
    "City",
    "Whisper",
    "UserAuth",
    "VerificationCode", 
    "RefreshToken",
    "UserSession",
    "ProviderType"
]
