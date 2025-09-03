# Routers package for the merged backend

# Export all routers for easy import
from . import (
    auth,
    users,
    matches,
    messages,
    profile,
    chats,
    projects,
    project_cards,
    membership,
    location,
    user_reports,
    sms_router,
    project_ideas,
    payments,
    online_users
)

__all__ = [
    "auth",
    "users", 
    "matches",
    "messages",
    "profile",
    "chats",
    "projects",
    "project_cards",
    "membership",
    "location",
    "user_reports",
    "sms_router",
    "project_ideas",
    "payments",
    "online_users"
]
