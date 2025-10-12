"""
Project Slots Models
Database models for project card slot management system
"""

from enum import Enum
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, JSON, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

from models.base import Base


class SlotStatus(Enum):
    """Status of a project card slot"""
    EMPTY = "empty"
    OCCUPIED = "occupied"  # Has content but not published/activated
    ACTIVATED = "activated"  # Published and active (visible to others)


class SlotSource(Enum):
    """Source of slot content"""
    AI_RECOMMENDATION = "ai_recommendation"
    MANUAL_ENTRY = "manual_entry"
    IMPORTED = "imported"


class ProjectCardSlot(Base):
    """
    Project Card Slot model for managing user's project card slots
    Users can save AI recommendations to slots and later publish them as project cards
    """
    __tablename__ = "project_card_slots"

    # Primary key
    slot_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # User relationship
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Slot metadata
    slot_number = Column(Integer, nullable=False)  # 1, 2, 3, etc.
    slot_name = Column(String(100), nullable=True)  # User-defined name for the slot
    status = Column(String(20), nullable=False, default=SlotStatus.EMPTY.value)
    source = Column(String(20), nullable=True)  # How content was added to slot
    
    # Project content (when slot is occupied)
    title = Column(String(200), nullable=True)
    description = Column(Text, nullable=True)
    short_description = Column(String(500), nullable=True)
    category = Column(String(50), nullable=True)
    industry = Column(String(50), nullable=True)
    project_type = Column(String(50), nullable=True)
    stage = Column(String(50), nullable=True)
    
    # Lists stored as JSON
    looking_for = Column(JSON, nullable=True)  # List of roles/skills needed
    skills_needed = Column(JSON, nullable=True)  # List of technical skills
    image_urls = Column(JSON, nullable=True)  # List of image URLs
    
    # URLs
    video_url = Column(String(512), nullable=True)
    demo_url = Column(String(512), nullable=True)
    pitch_deck_url = Column(String(512), nullable=True)
    
    # Financial information
    funding_goal = Column(Integer, nullable=True)  # In cents
    equity_offered = Column(Integer, nullable=True)  # Percentage 0-100
    current_valuation = Column(Integer, nullable=True)  # In cents
    revenue = Column(Integer, nullable=True)  # In cents
    
    # AI recommendation metadata (when source is AI)
    ai_recommendation_id = Column(String(100), nullable=True)  # ID from AI service
    ai_confidence_score = Column(Float, nullable=True)  # 0.0 to 1.0
    ai_reasoning = Column(Text, nullable=True)  # Why AI recommended this
    original_query = Column(String(500), nullable=True)  # User's search query
    
    # Publication/Activation tracking
    is_activated = Column(Boolean, nullable=False, default=False)
    activated_at = Column(DateTime, nullable=True)
    project_card_id = Column(Integer, nullable=True)  # Reference to actual project card when activated
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="project_slots")
    
    # Ensure unique slot numbers per user
    __table_args__ = (
        # UniqueConstraint('user_id', 'slot_number', name='unique_user_slot_number'),
    )
    
    @property
    def is_empty(self) -> bool:
        """Check if slot is empty"""
        return self.status == SlotStatus.EMPTY.value
    
    @property
    def is_occupied(self) -> bool:
        """Check if slot is occupied with content"""
        return self.status == SlotStatus.OCCUPIED.value
    
    @property
    def is_activated(self) -> bool:
        """Check if slot content is activated (published and visible)"""
        return self.status == SlotStatus.ACTIVATED.value
    
    def to_dict(self) -> dict:
        """Convert slot to dictionary for API responses"""
        return {
            "slot_id": self.slot_id,
            "slot_number": self.slot_number,
            "slot_name": self.slot_name,
            "status": self.status,
            "source": self.source,
            "title": self.title,
            "description": self.description,
            "short_description": self.short_description,
            "category": self.category,
            "industry": self.industry,
            "project_type": self.project_type,
            "stage": self.stage,
            "looking_for": self.looking_for,
            "skills_needed": self.skills_needed,
            "image_urls": self.image_urls,
            "video_url": self.video_url,
            "demo_url": self.demo_url,
            "pitch_deck_url": self.pitch_deck_url,
            "funding_goal": self.funding_goal,
            "equity_offered": self.equity_offered,
            "current_valuation": self.current_valuation,
            "revenue": self.revenue,
            "ai_recommendation_id": self.ai_recommendation_id,
            "ai_confidence_score": self.ai_confidence_score,
            "ai_reasoning": self.ai_reasoning,
            "original_query": self.original_query,
            "is_activated": self.is_activated,
            "activated_at": self.activated_at.isoformat() if self.activated_at else None,
            "project_card_id": self.project_card_id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }


class UserSlotConfiguration(Base):
    """
    User-specific configuration for project card slots with membership integration
    """
    __tablename__ = "user_slot_configurations"

    # Primary key
    config_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # User relationship
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True, index=True)
    
    # Configuration settings
    base_slots = Column(Integer, nullable=False, default=2)  # Base slots for free users
    bonus_slots = Column(Integer, nullable=False, default=0)  # Additional slots from membership
    membership_slots_permanent = Column(Boolean, nullable=False, default=False)  # Permanent bonus slots
    membership_expires_at = Column(DateTime, nullable=True)  # When membership expires
    
    # Behavior settings
    auto_save_recommendations = Column(Boolean, nullable=False, default=True)
    stop_recommendations_on_save = Column(Boolean, nullable=False, default=True)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="slot_configuration")
    
    @property
    def current_max_slots(self) -> int:
        """Calculate current maximum slots based on membership status"""
        # Check if membership has expired
        if (self.membership_expires_at and 
            self.membership_expires_at < datetime.utcnow() and 
            not self.membership_slots_permanent):
            return self.base_slots
        
        return self.base_slots + self.bonus_slots
    
    @property
    def is_membership_active(self) -> bool:
        """Check if membership benefits are currently active"""
        if self.membership_slots_permanent:
            return True
        
        if not self.membership_expires_at:
            return False
            
        return self.membership_expires_at > datetime.utcnow()
    
    def update_membership_slots(self, membership_type: str, expires_at: datetime = None, permanent: bool = False):
        """Update slot allocation based on membership type"""
        membership_slot_mapping = {
            "basic": 0,      # 2 total (2 base + 0 bonus)
            "pro": 8,        # 10 total (2 base + 8 bonus)  
            "ai-powered": 8  # 10 total (2 base + 8 bonus)
        }
        
        self.bonus_slots = membership_slot_mapping.get(membership_type, 0)
        self.membership_expires_at = expires_at
        self.membership_slots_permanent = permanent
        self.updated_at = datetime.utcnow()
    
    def to_dict(self) -> dict:
        """Convert configuration to dictionary"""
        return {
            "config_id": self.config_id,
            "user_id": self.user_id,
            "base_slots": self.base_slots,
            "bonus_slots": self.bonus_slots,
            "current_max_slots": self.current_max_slots,
            "membership_slots_permanent": self.membership_slots_permanent,
            "membership_expires_at": self.membership_expires_at.isoformat() if self.membership_expires_at else None,
            "is_membership_active": self.is_membership_active,
            "auto_save_recommendations": self.auto_save_recommendations,
            "stop_recommendations_on_save": self.stop_recommendations_on_save,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }


class AIRecommendationSwipe(Base):
    """
    Track user swipes on AI recommendations for learning and avoiding duplicates
    """
    __tablename__ = "ai_recommendation_swipes"

    # Primary key
    swipe_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # User and recommendation
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    ai_recommendation_id = Column(String(100), nullable=False, index=True)
    
    # Swipe details
    direction = Column(String(10), nullable=False)  # "left" or "right"
    query = Column(String(500), nullable=True)  # Original search query
    saved_to_slot = Column(Integer, nullable=True)  # Slot number if saved
    
    # Recommendation data (for learning)
    recommendation_data = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    
    # Relationships
    user = relationship("User", back_populates="ai_recommendation_swipes")
    
    # Ensure user can't swipe same recommendation twice
    __table_args__ = (
        # UniqueConstraint('user_id', 'ai_recommendation_id', name='unique_user_recommendation_swipe'),
    )
    
    @property
    def is_like(self) -> bool:
        """Check if swipe was a like (right swipe)"""
        return self.direction == "right"
    
    @property
    def is_dislike(self) -> bool:
        """Check if swipe was a dislike (left swipe)"""
        return self.direction == "left"
    
    def to_dict(self) -> dict:
        """Convert swipe to dictionary"""
        return {
            "swipe_id": self.swipe_id,
            "user_id": self.user_id,
            "ai_recommendation_id": self.ai_recommendation_id,
            "direction": self.direction,
            "query": self.query,
            "saved_to_slot": self.saved_to_slot,
            "recommendation_data": self.recommendation_data,
            "created_at": self.created_at.isoformat()
        }
