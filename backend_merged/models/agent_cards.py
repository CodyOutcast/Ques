"""
Agent Cards Models
Models for AI-generated project idea cards that users can swipe on
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum, Boolean, JSON, Float
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from .base import Base

class DifficultyLevel(enum.Enum):
    """Difficulty level enumeration"""
    BEGINNER = "Beginner"
    INTERMEDIATE = "Intermediate"
    ADVANCED = "Advanced"

class ProjectScope(enum.Enum):
    """Project scope enumeration"""
    SMALL_TEAM = "Small team (2-4 people)"
    MEDIUM_TEAM = "Medium team (5-8 people)"
    LARGE_TEAM = "Large team (9+ people)"
    SOLO = "Solo project"

class SwipeAction(enum.Enum):
    """Swipe action enumeration"""
    LEFT = "left"   # Add to history (reject)
    RIGHT = "right"  # Like the card

class AgentCard(Base):
    """
    Model for AI-generated project idea cards
    Based on agent_card.json structure
    """
    __tablename__ = "agent_cards"

    # Primary key
    card_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Card content from AI agent
    project_idea_title = Column(String(300), nullable=False, index=True)
    project_scope = Column(Enum(ProjectScope), nullable=False)
    description = Column(Text, nullable=False)
    key_features = Column(JSON, nullable=False)  # Array of strings
    estimated_timeline = Column(String(50), nullable=False)
    difficulty_level = Column(Enum(DifficultyLevel), nullable=False)
    required_skills = Column(JSON, nullable=False)  # Array of strings
    similar_examples = Column(JSON, nullable=True)  # Array of URLs
    relevance_score = Column(Float, nullable=False, index=True)  # 0.0 to 1.0
    
    # AI generation metadata
    ai_agent_id = Column(String(255), nullable=True)  # ID from AI system
    generation_prompt = Column(Text, nullable=True)  # Original user prompt
    generation_timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Card status
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    swipes = relationship("AgentCardSwipe", back_populates="card")
    likes = relationship("AgentCardLike", back_populates="card")
    
    def __repr__(self):
        return f"<AgentCard(card_id={self.card_id}, title='{self.project_idea_title[:50]}...', relevance={self.relevance_score})>"

class AgentCardSwipe(Base):
    """
    Track user swipes on agent cards (both left and right)
    """
    __tablename__ = "agent_card_swipes"
    
    # Primary key
    swipe_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # User and card info
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False, index=True)
    card_id = Column(Integer, ForeignKey("agent_cards.card_id"), nullable=False, index=True)
    
    # Swipe details
    action = Column(Enum(SwipeAction), nullable=False, index=True)  # left or right
    swipe_context = Column(JSON, nullable=True)  # Additional context about the swipe
    
    # Timestamps
    swiped_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    
    # Relationships
    user = relationship("User")
    card = relationship("AgentCard", back_populates="swipes")
    
    def __repr__(self):
        return f"<AgentCardSwipe(swipe_id={self.swipe_id}, user_id={self.user_id}, action={self.action.value})>"

class AgentCardLike(Base):
    """
    Store likes for agent cards (created when user swipes right)
    """
    __tablename__ = "agent_card_likes"
    
    # Primary key
    like_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # User and card info
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False, index=True)
    card_id = Column(Integer, ForeignKey("agent_cards.card_id"), nullable=False, index=True)
    
    # Like metadata
    interest_level = Column(Integer, nullable=True)  # 1-5 scale, optional
    notes = Column(Text, nullable=True)  # User's notes about why they liked it
    
    # Status
    is_active = Column(Boolean, nullable=False, default=True)
    
    # Timestamps
    liked_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User")
    card = relationship("AgentCard", back_populates="likes")
    
    # Unique constraint: one like per user per card
    __table_args__ = (
        {"schema": None}  # Use default schema
    )
    
    def __repr__(self):
        return f"<AgentCardLike(like_id={self.like_id}, user_id={self.user_id}, card_id={self.card_id})>"

class AgentCardHistory(Base):
    """
    Store history of agent cards (created when user swipes left)
    """
    __tablename__ = "agent_card_history"
    
    # Primary key
    history_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # User and card info
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False, index=True)
    card_id = Column(Integer, ForeignKey("agent_cards.card_id"), nullable=False, index=True)
    
    # History metadata
    rejection_reason = Column(String(100), nullable=True)  # Why user swiped left
    feedback = Column(Text, nullable=True)  # Optional user feedback
    
    # Timestamps
    added_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    
    # Relationships
    user = relationship("User")
    card = relationship("AgentCard")
    
    def __repr__(self):
        return f"<AgentCardHistory(history_id={self.history_id}, user_id={self.user_id}, card_id={self.card_id})>"

class UserAgentCardPreferences(Base):
    """
    Store user preferences for agent card recommendations
    """
    __tablename__ = "user_agent_card_preferences"
    
    # Primary key
    preference_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # User relationship
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False, unique=True, index=True)
    
    # Preferences
    preferred_difficulty_levels = Column(JSON, nullable=True)  # Array of preferred difficulty levels
    preferred_project_scopes = Column(JSON, nullable=True)  # Array of preferred project scopes
    preferred_skills = Column(JSON, nullable=True)  # Array of skills user is interested in
    excluded_skills = Column(JSON, nullable=True)  # Array of skills user wants to avoid
    
    # Recommendation settings
    min_relevance_score = Column(Float, nullable=False, default=0.5)  # Minimum relevance score to show
    max_cards_per_day = Column(Integer, nullable=False, default=20)  # Daily card limit
    
    # Timeline preferences
    preferred_timeline_min = Column(String(20), nullable=True)  # e.g., "2 weeks"
    preferred_timeline_max = Column(String(20), nullable=True)  # e.g., "12 weeks"
    
    # Notification preferences
    daily_cards_enabled = Column(Boolean, nullable=False, default=True)
    weekly_summary_enabled = Column(Boolean, nullable=False, default=True)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="agent_card_preferences")
    
    def __repr__(self):
        return f"<UserAgentCardPreferences(user_id={self.user_id}, min_relevance={self.min_relevance_score})>"
