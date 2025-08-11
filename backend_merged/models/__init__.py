# Import all models to ensure they're registered with SQLAlchemy
from .base import Base
from .users import User
from .likes import UserSwipe, Like
from .matches import Match
from .messages import Message
from .chats import Chat, ChatMessage, ChatStatus
from .user_auth import UserAuth, RefreshToken, VerificationCode, UserSession, SecurityLog
from .user_features import UserFeature, UserLink
from .user_reports import UserReport

# Export all models
__all__ = [
    "Base",
    "User", 
    "UserSwipe", 
    "Like",
    "Match",
    "Message",
    "Chat",
    "ChatMessage",
    "ChatStatus",
    "UserAuth", 
    "RefreshToken", 
    "VerificationCode", 
    "UserSession", 
    "SecurityLog",
    "UserFeature",
    "UserLink",
    "UserReport"
]

# Export basic models
__all__ = [
    "Base",
    "User", 
    "UserSwipe",
    "Like"
]
