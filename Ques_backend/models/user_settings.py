"""
User settings model for managing user preferences and notification settings
"""

from sqlalchemy import Column, BigInteger, String, Boolean, TIMESTAMP, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum
from .base import Base

class SearchMode(str, Enum):
    """Search mode enum"""
    INSIDE = "inside"
    GLOBAL = "global"

class Theme(str, Enum):
    """Theme options"""
    LIGHT = "light"
    DARK = "dark"
    AUTO = "auto"

class UserSettings(Base):
    """
    User settings table for managing all user preferences and notification settings
    Matches frontend API requirements exactly while avoiding data duplication
    """
    __tablename__ = "user_settings"

    # Primary key and foreign key
    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False, unique=True, index=True)
    
    # Notification Settings - matching frontend API
    email_notifications = Column(Boolean, nullable=False, default=True)
    push_notifications = Column(Boolean, nullable=False, default=True)
    whisper_requests = Column(Boolean, nullable=False, default=True)
    friend_requests = Column(Boolean, nullable=False, default=True)
    matches_notifications = Column(Boolean, nullable=False, default=True)
    messages_notifications = Column(Boolean, nullable=False, default=True)
    system_notifications = Column(Boolean, nullable=False, default=True)
    gifts_notifications = Column(Boolean, nullable=False, default=True)
    
    # User Preferences - matching frontend API
    search_mode = Column(String(20), nullable=False, default="inside", index=True)  # 'inside' | 'global'
    auto_accept_matches = Column(Boolean, nullable=False, default=False)
    show_online_status = Column(Boolean, nullable=False, default=True)
    
    # Whisper Settings - matching frontend API (excluding wechatId which is in user_profiles)
    custom_message = Column(Text, nullable=True)
    whisper_auto_accept = Column(Boolean, nullable=False, default=False)
    whisper_show_status = Column(Boolean, nullable=False, default=True)
    whisper_enable_notifications = Column(Boolean, nullable=False, default=True)
    
    # Additional Settings for future expansion
    language = Column(String(10), nullable=False, default="en")  # 'en', 'cn'
    theme = Column(String(20), nullable=False, default="light")  # 'light', 'dark', 'auto'
    timezone = Column(String(50), nullable=False, default="UTC")
    
    # Timestamps
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow, index=True)
    updated_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="settings")

    def __repr__(self):
        return f"<UserSettings(id={self.id}, user_id={self.user_id}, search_mode={self.search_mode})>"