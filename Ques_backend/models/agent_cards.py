"""
Agent card models following DATABASE_STRUCTURE_UPDATE.md
"""

from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, Boolean, JSON, VARCHAR, ForeignKey, DOUBLE_PRECISION
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base

class AgentCard(Base):
    """
    AI-generated project recommendation cards
    """
    __tablename__ = "agent_cards"

    card_id = Column(Integer, primary_key=True, index=True)
    project_idea_title = Column(VARCHAR(300), nullable=False)
    project_scope = Column(VARCHAR(11), nullable=False)  # small, medium, large, enterprise
    description = Column(Text, nullable=False)
    key_features = Column(JSON, nullable=False)
    estimated_timeline = Column(VARCHAR(50), nullable=False)
    difficulty_level = Column(VARCHAR(12), nullable=False)  # beginner, intermediate, advanced, expert
    required_skills = Column(JSON, nullable=False)
    similar_examples = Column(JSON, nullable=True)
    relevance_score = Column(DOUBLE_PRECISION, nullable=False)
    ai_agent_id = Column(VARCHAR(255), nullable=True)
    generation_prompt = Column(Text, nullable=True)
    generation_timestamp = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    swipes = relationship("AgentCardSwipe", back_populates="card")
    likes = relationship("AgentCardLike", back_populates="card")
    history = relationship("AgentCardHistory", back_populates="card")

class AgentCardSwipe(Base):
    """
    User interactions with agent cards
    """
    __tablename__ = "agent_card_swipes"

    swipe_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    card_id = Column(Integer, ForeignKey("agent_cards.card_id"), nullable=False)
    action = Column(VARCHAR(5), nullable=False)  # LIKE, PASS
    swipe_context = Column(JSON, nullable=True)
    swiped_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="agent_card_swipes")
    card = relationship("AgentCard", back_populates="swipes")

class AgentCardLike(Base):
    """
    Liked agent cards with details
    """
    __tablename__ = "agent_card_likes"

    like_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    card_id = Column(Integer, ForeignKey("agent_cards.card_id"), nullable=False)
    interest_level = Column(Integer, nullable=True)  # 1-10 scale
    notes = Column(Text, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    liked_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="agent_card_likes")
    card = relationship("AgentCard", back_populates="likes")

class AgentCardHistory(Base):
    """
    Agent card interaction history
    """
    __tablename__ = "agent_card_history"

    history_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    card_id = Column(Integer, ForeignKey("agent_cards.card_id"), nullable=False)
    rejection_reason = Column(VARCHAR(100), nullable=True)
    feedback = Column(Text, nullable=True)
    added_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="agent_card_history")
    card = relationship("AgentCard", back_populates="history")

class UserAgentCardPreferences(Base):
    """
    User preferences for AI card generation
    """
    __tablename__ = "user_agent_card_preferences"

    preference_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    preferred_difficulty_levels = Column(JSON, nullable=True)
    preferred_project_scopes = Column(JSON, nullable=True)
    preferred_skills = Column(JSON, nullable=True)
    excluded_skills = Column(JSON, nullable=True)
    min_relevance_score = Column(DOUBLE_PRECISION, nullable=False, default=0.5)
    max_cards_per_day = Column(Integer, nullable=False, default=10)
    preferred_timeline_min = Column(VARCHAR(20), nullable=True)
    preferred_timeline_max = Column(VARCHAR(20), nullable=True)
    daily_cards_enabled = Column(Boolean, nullable=False, default=True)
    weekly_summary_enabled = Column(Boolean, nullable=False, default=True)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="agent_card_preferences")