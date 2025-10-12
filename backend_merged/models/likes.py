"""
Likes and swipes models matching actual database schema
Updated to match production database

Database schema for user_swipes:
- id: BIGINT (primary key)
- swiper_id: BIGINT (FK to users.id)
- swiped_user_id: BIGINT (FK to users.id)
- swipe_direction: VARCHAR(10) - 'left' or 'right' (constraint: chk_swipe_direction)
- match_score: NUMERIC(5, 4)
- swipe_context: VARCHAR(200)
- triggered_whisper: BOOLEAN
- created_at: TIMESTAMP
"""

from sqlalchemy import Column, BigInteger, String, TIMESTAMP, Boolean, ForeignKey, NUMERIC
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from .base import Base

class SwipeDirection(enum.Enum):
    """Swipe direction enumeration - matches database constraint"""
    RIGHT = "right"  # Swipe right (like/interested)
    LEFT = "left"    # Swipe left (dislike/not interested)

class UserSwipe(Base):
    """
    User swipe actions matching actual production database schema
    
    Tracks when users swipe on each other's profiles
    Unique constraint: (swiper_id, swiped_user_id)
    """
    __tablename__ = "user_swipes"
    
    # Primary key - actual column name is 'id'
    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    
    # Foreign keys - actual column names
    swiper_id = Column(BigInteger, ForeignKey("users.id"), nullable=False, index=True)
    swiped_user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False, index=True)
    
    # Swipe details - actual column names
    swipe_direction = Column(String(10), nullable=False)  # 'like' or 'dislike'
    match_score = Column(NUMERIC(5, 4), nullable=True)
    swipe_context = Column(String(200), nullable=True)
    triggered_whisper = Column(Boolean, nullable=False, default=False, index=True)
    
    # Timestamp - actual column name
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow, index=True)
    
    # Relationships - using actual column names
    swiper = relationship("User", foreign_keys=[swiper_id], back_populates="sent_swipes")
    swiped_user = relationship("User", foreign_keys=[swiped_user_id], back_populates="received_swipes")
    
    # Whisper relationship
    whispers = relationship("Whisper", foreign_keys="Whisper.swipe_id", back_populates="swipe")
    
    # Compatibility properties for backward compatibility
    @property
    def swipe_id(self):
        """Alias for id"""
        return self.id
    
    @property
    def target_id(self):
        """Alias for swiped_user_id"""
        return self.swiped_user_id
    
    @property
    def target(self):
        """Alias for swiped_user"""
        return self.swiped_user
    
    @property
    def direction(self):
        """Return as enum for compatibility"""
        if self.swipe_direction == 'like':
            return SwipeDirection.like
        else:
            return SwipeDirection.dislike
    
    @property
    def timestamp(self):
        """Alias for created_at"""
        return self.created_at
    
    @property
    def action(self):
        """Map direction to action string"""
        return "like" if self.swipe_direction == 'like' else "pass"
    
    def __repr__(self):
        return f"<UserSwipe(id={self.id}, swiper={self.swiper_id}, swiped={self.swiped_user_id}, direction={self.swipe_direction})>"
