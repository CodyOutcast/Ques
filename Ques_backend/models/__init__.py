# Import all models to ensure they're registered with SQLAlchemy
# ✅ All models following DATABASE_STRUCTURE_UPDATE.md are imported
from .base import Base
from .users import User
from .user_profiles import UserProfile
# UserSwipe and SwipeDirection removed - not in current database schema
from .user_reports import UserReport
from .locations import Province, City
from .whispers import Whisper
from .user_auth import UserAuth, VerificationCode, RefreshToken, UserSession, ProviderType, SecurityLog
from .user_settings import UserAccountSettings, UserSecuritySettings, PrivacyConsent, DataExportRequest, AccountAction
from .university_verification import UniversityVerification
from .projects import Project, ProjectCardSlot, AIRecommendationSwipe
from .institutions import Institution, UserInstitution
from .agent_cards import AgentCard, AgentCardSwipe, AgentCardLike, AgentCardHistory, UserAgentCardPreferences
from .messaging import Match, Chat, ChatMessage, Message
from .memberships import Membership, MembershipPlan, MembershipTransaction
from .payments import Payment, PaymentMethod, RefundRequest, Revenue
from .security import BlockedUser, DeviceToken, AuditLog, APIKey

# Export all models
__all__ = [
    # Base
    "Base",
    # User system
    "User",
    "UserProfile",
    "UserReport",
    # Authentication
    "UserAuth",
    "VerificationCode", 
    "RefreshToken",
    "UserSession",
    "ProviderType",
    # User Settings
    "UserAccountSettings",
    "UserSecuritySettings", 
    "PrivacyConsent",
    "DataExportRequest",
    "AccountAction",
    # University Verification
    "UniversityVerification",
    # Locations
    "Province",
    "City",
    # Content
    "Whisper",
    # Projects
    "Project",
    "ProjectCardSlot",
    "AIRecommendationSwipe",
    # Institutions
    "Institution",
    "UserInstitution",
    # AI Agent Cards
    "AgentCard",
    "AgentCardSwipe",
    "AgentCardLike", 
    "AgentCardHistory",
    "UserAgentCardPreferences",
    # Messaging
    "Match",
    "Chat",
    "ChatMessage",
    "Message",
    # Memberships
    "Membership",
    "MembershipPlan",
    "MembershipTransaction",
    # Payments
    "Payment",
    "PaymentMethod",
    "RefundRequest",
    "Revenue",
    # Security
    "SecurityLog",
    "BlockedUser",
    "DeviceToken",
    "AuditLog",
    "APIKey"
]
