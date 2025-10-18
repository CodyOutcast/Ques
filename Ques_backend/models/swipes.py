"""
New swipes model matching frontend API documentation structure
"""

from sqlalchemy import Column, Integer, String, TIMESTAMP, Boolean, ForeignKey, DECIMAL, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum
from .base import Base

class SwipeAction(str, Enum):
    """Swipe action enum matching frontend"""
    LIKE = "like"
    IGNORE = "ignore"
    SUPER_LIKE = "super_like"

class SearchMode(str, Enum):
    """Search mode enum matching frontend"""
    INSIDE = "inside"
    GLOBAL = "global"

class SwipeRecord(Base):
    """
    New swipe records table - matches frontend API structure exactly
    Schema matches frontend JSON structure:
    {
        targetUserId: string;
        action: 'like' | 'ignore' | 'super_like';
        searchQuery?: string;
        searchMode?: 'inside' | 'global';
        matchScore?: number;
        sourceContext?: {
            sessionId?: string;
            recommendationBatch?: string;
            cardPosition?: number;
        };
    }
    """
    __tablename__ = "swipe_records"

    # Primary key and basic fields
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    target_user_id = Column(String, nullable=False, index=True)  # Can be external user ID
    
    # Core swipe data
    action = Column(String(20), nullable=False, index=True)  # 'like', 'ignore', 'super_like'
    search_query = Column(String(500), nullable=True)
    search_mode = Column(String(20), nullable=True)  # 'inside', 'global'
    match_score = Column(DECIMAL(5, 4), nullable=True)
    
    # Source context as JSON field
    source_context = Column(JSON, nullable=True)
    # source_context structure:
    # {
    #     "sessionId": string,
    #     "recommendationBatch": string, 
    #     "cardPosition": number
    # }
    
    # Metadata
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow, index=True)
    updated_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="swipe_records")

    def __repr__(self):
        return f"<SwipeRecord(id={self.id}, user_id={self.user_id}, target={self.target_user_id}, action={self.action})>"