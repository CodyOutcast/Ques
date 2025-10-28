# Routers package for the merged backend

# Export all routers for easy import - Only working routers
from . import (
    auth,
    users,
    user_reports,
    sms_router,         # phone verification service
    intelligent_agent,
    basic_operations,
    university_verification,  # now uses existing UserProfile model
    project_management,   # user project CRUD operations
    # settings,           # imports deleted models.settings
    swipes,             # new swipe system with SwipeRecord model
    # matching,           # imports deleted models.swipes
    user_settings,      # user settings and preferences system
    notifications,
    contacts,
    whispers,
    payments,             # payment system with complete implementation
    # card_tracking,      # may import deleted models
    ai_services,
    casual_requests,    # casual requests social activity system  
    # chat_agent,         # imports deleted models.casual_requests
    # projects,           # imports deleted models.projects
    # membership,         # imports deleted models.payments
    tpns
)

__all__ = [
    "auth",
    "users",
    "user_reports",
    # "sms_router",          # Commented - imports deleted models
    "intelligent_agent",
    "basic_operations", 
    "university_verification",  # Fixed - now uses existing models
    "project_management",      # User project CRUD - NEWLY ADDED
    # "settings",            # Commented - imports deleted models
    "swipes",              # New swipe system - NEWLY ADDED
    # "matching",            # Commented - imports deleted models
    "user_settings",       # User settings system - NEWLY ADDED
    "notifications",
    "contacts",
    "whispers",
    "payments",               # Payment system - NEWLY ADDED
    # "card_tracking",       # Commented - imports deleted models
    "ai_services",
    "casual_requests",     # Casual requests system - NEWLY ENABLED
    # "chat_agent",          # Commented - imports deleted models
    # "projects",            # Commented - imports deleted models
    # "membership",          # Commented - imports deleted models
    "tpns"
]
