"""
Project models following DATABASE_STRUCTURE_UPDATE.md
"""

from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, Boolean, JSON, VARCHAR, ForeignKey, DOUBLE_PRECISION
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base

class Project(Base):
    """
    Core project information
    """
    __tablename__ = "projects"

    project_id = Column(Integer, primary_key=True, index=True)
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(VARCHAR(200), nullable=False)
    description = Column(Text, nullable=False)
    short_description = Column(VARCHAR(500), nullable=True)
    long_description = Column(Text, nullable=True)
    start_time = Column(TIMESTAMP, nullable=False)
    media_link_id = Column(Integer, nullable=True)
    status = Column(VARCHAR(8), nullable=False)
    category = Column(VARCHAR(50), nullable=True)
    industry = Column(VARCHAR(50), nullable=True)
    project_type = Column(VARCHAR(13), nullable=False)
    stage = Column(VARCHAR(50), nullable=True)
    looking_for = Column(JSON, nullable=True)
    skills_needed = Column(JSON, nullable=True)
    image_urls = Column(JSON, nullable=True)
    video_url = Column(VARCHAR(512), nullable=True)
    demo_url = Column(VARCHAR(512), nullable=True)
    pitch_deck_url = Column(VARCHAR(512), nullable=True)
    funding_goal = Column(Integer, nullable=True)
    equity_offered = Column(Integer, nullable=True)
    current_valuation = Column(Integer, nullable=True)
    revenue = Column(Integer, nullable=True)
    vector_id = Column(VARCHAR(255), nullable=True)
    feature_tags = Column(JSON, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    is_featured = Column(Boolean, nullable=False, default=False)
    is_verified = Column(Boolean, nullable=False, default=False)
    moderation_status = Column(VARCHAR(8), nullable=False, default='pending')
    moderation_notes = Column(Text, nullable=True)
    view_count = Column(Integer, nullable=False, default=0)
    like_count = Column(Integer, nullable=False, default=0)
    interest_count = Column(Integer, nullable=False, default=0)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = Column(TIMESTAMP, nullable=True)
    expires_at = Column(TIMESTAMP, nullable=True)

    # Relationships
    creator = relationship("User", back_populates="projects")

class ProjectCardSlot(Base):
    """
    User project card slots system
    """
    __tablename__ = "project_card_slots"

    slot_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    slot_number = Column(Integer, nullable=False)
    slot_name = Column(VARCHAR(100), nullable=True)
    status = Column(VARCHAR(20), nullable=False)
    source = Column(VARCHAR(20), nullable=True)
    title = Column(VARCHAR(200), nullable=True)
    description = Column(Text, nullable=True)
    short_description = Column(VARCHAR(500), nullable=True)
    category = Column(VARCHAR(50), nullable=True)
    industry = Column(VARCHAR(50), nullable=True)
    project_type = Column(VARCHAR(50), nullable=True)
    stage = Column(VARCHAR(50), nullable=True)
    looking_for = Column(JSON, nullable=True)
    skills_needed = Column(JSON, nullable=True)
    image_urls = Column(JSON, nullable=True)
    video_url = Column(VARCHAR(512), nullable=True)
    demo_url = Column(VARCHAR(512), nullable=True)
    pitch_deck_url = Column(VARCHAR(512), nullable=True)
    funding_goal = Column(Integer, nullable=True)
    equity_offered = Column(Integer, nullable=True)
    current_valuation = Column(Integer, nullable=True)
    revenue = Column(Integer, nullable=True)
    ai_recommendation_id = Column(VARCHAR(100), nullable=True)
    ai_confidence_score = Column(DOUBLE_PRECISION, nullable=True)
    ai_reasoning = Column(Text, nullable=True)
    original_query = Column(VARCHAR(500), nullable=True)
    activated_at = Column(TIMESTAMP, nullable=True)
    project_card_id = Column(Integer, nullable=True)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="project_slots")

class AIRecommendationSwipe(Base):
    """
    AI recommendation interaction tracking
    """
    __tablename__ = "ai_recommendation_swipes"

    swipe_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    ai_recommendation_id = Column(VARCHAR(100), nullable=False)
    direction = Column(VARCHAR(10), nullable=False)
    query = Column(VARCHAR(500), nullable=True)
    saved_to_slot = Column(Integer, nullable=True)
    recommendation_data = Column(JSON, nullable=True)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="ai_recommendation_swipes")