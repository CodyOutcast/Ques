"""
Likes and swipes models matching actual database schema
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from .base import Base

class SwipeDirection(enum.Enum):
    """Swipe direction enumeration"""
    like = "like"
    dislike = "dislike"

class UserSwipe(Base):
    """
    User swipe actions matching actual database schema
    """
    __tablename__ = "user_swipes"
    
    swipe_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    swiper_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    target_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    direction = Column(SQLEnum(SwipeDirection, name='swipedirection'), nullable=False)
    timestamp = Column(DateTime, nullable=True, default=datetime.utcnow)
    
    # Relationships
    swiper = relationship("User", foreign_keys=[swiper_id], back_populates="sent_swipes")
    target = relationship("User", foreign_keys=[target_id], back_populates="received_swipes")
    
    # Compatibility properties
    @property
    def id(self):
        return self.swipe_id
    
    @property
    def user_id(self):
        return self.swiper_id
    
    @property
    def target_user_id(self):
        return self.target_id
    
    @property
    def action(self):
        # Map direction to action for compatibility
        if self.direction == SwipeDirection.like:
            return "like"
        else:
            return "pass"
    
    @property
    def created_at(self):
        return self.timestamp

class Like(Base):
    """
    User likes matching the actual database schema
    """
    __tablename__ = "likes"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    liker_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    liked_item_id = Column(Integer, nullable=False)  # Could be user_id or other entity
    liked_item_type = Column(String(50), nullable=False)  # "USER", "POST", etc.
    timestamp = Column(DateTime, nullable=True, default=datetime.utcnow)
    granted_chat_access = Column(Boolean, nullable=True, default=False)
    
    # Relationship to liker
    liker = relationship("User", foreign_keys=[liker_id], back_populates="given_likes")
    __tablename__ = "likes"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    target_user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    is_like = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
