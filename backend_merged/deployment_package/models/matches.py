"""
Match and messaging models matching actual database schema
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base

class Match(Base):
    """
    Match model matching the actual database schema
    """
    __tablename__ = "matches"

    match_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user1_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    user2_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    timestamp = Column(DateTime, nullable=True, default=datetime.utcnow)
    is_active = Column(Boolean, nullable=True, default=True)
    
    # Relationships
    user1 = relationship("User", foreign_keys=[user1_id], back_populates="matches_as_user1")
    user2 = relationship("User", foreign_keys=[user2_id], back_populates="matches_as_user2")
    messages = relationship("Message", back_populates="match")
    
    # Compatibility properties
    @property
    def id(self):
        return self.match_id
    
    @property
    def matched_at(self):
        return self.timestamp
    
    @property
    def created_at(self):
        return self.timestamp
    match_reason = Column(String(200), nullable=True)  # "mutual_interests", "location", etc.
    
    # Communication preferences (from p34)
    chat_enabled = Column(Boolean, default=True, nullable=False)
    video_call_enabled = Column(Boolean, default=False, nullable=False)
    
    # Activity tracking
    last_message_at = Column(DateTime, nullable=True)
    last_activity_at = Column(DateTime, default=datetime.utcnow)
    
    # Compatibility score (from p12 recommendations)
    compatibility_score = Column(Integer, nullable=True)  # 0-100
    
    # Properties for compatibility
    @property
    def id(self):
        return self.match_id
    
    @property
    def created_at(self):
        return self.matched_at
    
    @property
    def status(self):
        if not self.is_active:
            return "inactive"
        elif self.is_blocked:
            return "blocked"
        else:
            return "active"
    
    # Unique constraint: user can only match with someone once
    __table_args__ = (
        {"schema": None}  # Will add: unique(user1_id, user2_id), check(user1_id != user2_id)
    )
