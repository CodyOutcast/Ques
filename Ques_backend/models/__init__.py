# Import ONLY models that match actual database tables
# Based on DATABASE_SCHEMA_COMPLETE.md and new payment system tables
from .base import Base
from .users import User
from .user_profiles import UserProfile
from .user_reports import UserReport
from .locations import Province, City  # cities, provinces tables
from .whispers import Whisper
from .institutions import Institution, UserInstitution  # institutions, user_institutions tables
from .memberships import Membership  # memberships table
from .user_auth import VerificationCode, UserAuth, RefreshToken, ProviderType, UserSession  # verification_codes table + auth helpers
from .user_projects import UserProject  # user_projects table
from .user_quotas import UserQuota  # user_quotas table
from .user_swipes import UserSwipe, SwipeDirection  # user_swipes table
from .swipes import SwipeRecord, SwipeAction, SearchMode  # swipe_records table (new)
from .user_settings import UserSettings  # user_settings table (new)
from .casual_requests import CasualRequest  # casual_requests table (new)
from .chat import ChatSession, ChatMessage, MessageRecommendation, SuggestedQuery  # chat system tables (new)
from .payments import MembershipTransaction, PaymentRefund, PaymentMethod, PaymentSession, PaymentStatus, PaymentType, PaymentMethodType  # payment system tables

# Export only models that match actual database tables
__all__ = [
    # Base
    "Base",
    # Core tables that exist in database
    "User",           # users table
    "UserProfile",    # user_profiles table  
    "UserReport",     # user_reports table
    "Province",       # provinces table
    "City",          # cities table
    "Whisper",       # whispers table
    "Institution",   # institutions table
    "UserInstitution", # user_institutions table
    "Membership",    # memberships table
    "VerificationCode", # verification_codes table
    "UserAuth",      # auth helper (not a table)
    "RefreshToken",  # auth helper (not a table) 
    "ProviderType",  # auth enum
    "UserSession",   # auth helper (not a table)
    "UserProject",   # user_projects table
    "UserQuota",     # user_quotas table
    "UserSwipe",     # user_swipes table (legacy)
    "SwipeDirection", # swipe direction enum (legacy)
    "SwipeRecord",   # swipe_records table (new)
    "SwipeAction",   # swipe action enum (new)
    "SearchMode",    # search mode enum (new)
    "UserSettings",  # user_settings table (new)
    "CasualRequest", # casual_requests table (new)
    # Chat system models (new)
    "ChatSession",         # chat_sessions table
    "ChatMessage",         # chat_messages table
    "MessageRecommendation", # message_recommendations table
    "SuggestedQuery",      # suggested_queries table
    # Payment system models
    "MembershipTransaction",  # membership_transactions table
    "PaymentRefund",         # payment_refunds table  
    "PaymentMethod",         # payment_methods table
    "PaymentSession",        # payment_sessions table
    "PaymentStatus",         # payment status enum
    "PaymentType",           # payment type enum
    "PaymentMethodType",     # payment method type enum
]
