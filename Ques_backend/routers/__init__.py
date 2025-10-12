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
    online_users,
    matching,
    notifications,
    contacts,
    whispers,
    payment_system,
    card_tracking,
    ai_services
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
    "online_users",
    "matching",
    "notifications",
    "contacts",
    "whispers",
    "payment_system",
    "card_tracking",
    "ai_services"
]
