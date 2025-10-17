"""
User swipes model matching database schema
"""

from sqlalchemy import Column, Integer, String, TIMESTAMP, Boolean, ForeignKey, DECIMAL
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum
from .base import Base

class SwipeDirection(str, Enum):
    """Swipe direction enum"""
    LEFT = "left"   # dislike
    RIGHT = "right" # like 
    SUPER = "super" # super like

class UserSwipe(Base):
    """
    User swipes table - matches existing database schema
    """
    __tablename__ = "user_swipes"

    id = Column(Integer, primary_key=True, index=True)
    swiper_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    swiped_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    swipe_direction = Column(String(10), nullable=False)  # 'left', 'right', 'super'
    match_score = Column(DECIMAL(5, 4), nullable=True)
    swipe_context = Column(String(200), nullable=True)
    triggered_whisper = Column(Boolean, nullable=False, default=False)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)

    # Relationships
    swiper = relationship("User", foreign_keys=[swiper_id], back_populates="swipes_made")
    swiped_user = relationship("User", foreign_keys=[swiped_user_id], back_populates="swipes_received")