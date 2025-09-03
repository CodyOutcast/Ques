# Import all models to ensure they're registered with SQLAlchemy
from .base import Base
from .users import User
from .likes import UserSwipe, Like, SwipeDirection
from .matches import Match
from .messages import Message
from .chats import Chat, ChatMessage, ChatStatus
from .user_auth import UserAuth, RefreshToken, VerificationCode, UserSession, SecurityLog
from .user_features import UserFeature, UserLink
from .user_reports import UserReport
from .project_cards import ProjectCard, UserProject
from .user_membership import UserMembership, UserUsageLog, MembershipType
from .payments import MembershipTransaction, PaymentRefund, PaymentWebhookLog, PaymentStatus, PaymentMethod
from .subscriptions import UserSubscription, ProjectIdeaRequest, SubscriptionType

# Export all models
__all__ = [
    "Base",
    "User", 
    "UserSwipe", 
    "Like",
    "SwipeDirection",
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
    "UserReport",
    "UserProject", 
    "ProjectCard",
    "UserMembership",
    "UserUsageLog",
    "MembershipType",
    "MembershipTransaction",
    "PaymentRefund", 
    "PaymentWebhookLog",
    "PaymentStatus",
    "PaymentMethod",
    "UserSubscription",
    "ProjectIdeaRequest",
    "SubscriptionType"
]
