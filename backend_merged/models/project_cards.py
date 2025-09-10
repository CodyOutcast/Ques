"""
Enhanced Project and User models for vector-based recommendations
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum, Boolean, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from .base import Base

class ProjectType(enum.Enum):
    """Project type enumeration"""
    STARTUP = "startup"
    SIDE_PROJECT = "side_project" 
    INVESTMENT = "investment"
    COLLABORATION = "collaboration"

class ProjectStatus(enum.Enum):
    """Project status enumeration"""
    ONGOING = "ONGOING"
    ON_HOLD = "ON_HOLD"
    FINISHED = "FINISHED"

class ModerationStatus(enum.Enum):
    """Moderation status enumeration"""
    PENDING = "pending"
    APPROVED = "approved" 
    REJECTED = "rejected"

class ProjectCard(Base):
    """
    Enhanced Project model for card-based interface with vector support
    Based on migration 003_projects_content.py structure
    """
    __tablename__ = "projects"

    # Primary key
    project_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Creator relationship
    creator_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    
    # Basic project information
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    short_description = Column(String(500), nullable=True)
    
    # Legacy fields from original projects table
    long_description = Column(Text, nullable=True)  # Keep for backward compatibility
    start_time = Column(DateTime, nullable=False, default=datetime.utcnow)
    media_link_id = Column(Integer, nullable=True)  # Keep for backward compatibility
    status = Column(Enum(ProjectStatus), nullable=False, default=ProjectStatus.ONGOING)
    
    # Project categorization
    category = Column(String(50), nullable=True)  # e.g., "tech", "fintech", "healthcare"
    industry = Column(String(50), nullable=True)  # e.g., "software", "biotechnology"
    project_type = Column(Enum(ProjectType), nullable=False)
    stage = Column(String(50), nullable=True)  # e.g., "idea", "prototype", "mvp", "scaling"
    
    # What this project is looking for
    looking_for = Column(JSON, nullable=True)  # ["investor", "co-founder", "developer"]
    skills_needed = Column(JSON, nullable=True)  # ["python", "react", "marketing"]
    
    # Media and presentation
    image_urls = Column(JSON, nullable=True)  # ["url1", "url2", "url3"]
    video_url = Column(String(512), nullable=True)
    demo_url = Column(String(512), nullable=True)
    pitch_deck_url = Column(String(512), nullable=True)
    
    # Financial information
    funding_goal = Column(Integer, nullable=True)  # Amount in USD
    equity_offered = Column(Integer, nullable=True)  # Percentage * 100 (e.g., 1000 = 10%)
    current_valuation = Column(Integer, nullable=True)  # Amount in USD
    revenue = Column(Integer, nullable=True)  # Monthly revenue in USD
    
    # Vector-based matching
    vector_id = Column(String(255), nullable=True)  # ID in vector database
    feature_tags = Column(JSON, nullable=True)  # Tags for vector embedding
    
    # Status and moderation
    is_active = Column(Boolean, nullable=False, default=True)
    is_featured = Column(Boolean, nullable=False, default=False)
    is_verified = Column(Boolean, nullable=False, default=False)
    moderation_status = Column(Enum(ModerationStatus), nullable=False, default=ModerationStatus.PENDING)
    moderation_notes = Column(Text, nullable=True)
    
    # Analytics
    view_count = Column(Integer, nullable=False, default=0)
    like_count = Column(Integer, nullable=False, default=0)
    interest_count = Column(Integer, nullable=False, default=0)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    
    # Relationships
    creator = relationship("User", foreign_keys=[creator_id], back_populates="created_projects")
    user_projects = relationship("UserProject", back_populates="project")
    
    # Helper properties
    @property
    def id(self):
        """Alias for project_id for compatibility"""
        return self.project_id
    
    @property
    def owner(self):
        """Get project owner (creator)"""
        return self.creator
    
    @property
    def collaborators(self):
        """Get project collaborators (non-owners)"""
        return [up.user for up in self.user_projects if up.role != "Owner"]
    
    @property
    def all_members(self):
        """Get all project members"""
        return [up.user for up in self.user_projects]
    
    def to_card_dict(self):
        """Convert to card format for frontend"""
        return {
            "id": self.project_id,
            "title": self.title,
            "description": self.short_description or self.description[:200] + "...",
            "tags": self.feature_tags or [],
            "type": "project",
            "cardStyle": "rich" if self.image_urls else "text-only",
            "status": self.project_type.value if self.project_type else "startup",
            "owner": {
                "name": self.creator.name if self.creator else "Unknown",
                "avatar": f"https://api.dicebear.com/7.x/avataaars/svg?seed={self.creator.name}" if self.creator else None,
                "role": "Owner",
                "tags": self.creator.feature_tags if self.creator else []
            },
            "collaborators": len(self.collaborators),
            "collaboratorsList": [
                {
                    "name": collab.name,
                    "role": "Collaborator", 
                    "avatar": f"https://api.dicebear.com/7.x/avataaars/svg?seed={collab.name}"
                } 
                for collab in self.collaborators[:3]  # Show first 3
            ],
            "detailedDescription": self.description,
            "lookingFor": {
                "tags": self.looking_for or [],
                "description": f"Looking for: {', '.join(self.looking_for or [])}"
            },
            "skillsNeeded": self.skills_needed or [],
            "media": self.image_urls or [],
            "cover": self.image_urls[0] if self.image_urls else None,
            "videoUrl": self.video_url,
            "demoUrl": self.demo_url,
            "fundingGoal": self.funding_goal,
            "equityOffered": self.equity_offered / 100 if self.equity_offered else None,
            "stage": self.stage,
            "category": self.category,
            "industry": self.industry,
            "viewCount": self.view_count,
            "likeCount": self.like_count,
            "interestCount": self.interest_count,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
            "publishedAt": self.published_at.isoformat() if self.published_at else None
        }


class UserProject(Base):
    """
    Junction table linking users to their projects (many-to-many relationship)
    """
    __tablename__ = "user_projects"

    # Composite primary key
    user_id = Column(Integer, ForeignKey("users.user_id"), primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.project_id"), primary_key=True)
    
    # Additional metadata for the relationship
    role = Column(String(100), nullable=True)  # e.g., "Owner", "Collaborator", "Contributor"
    joined_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="user_projects")
    project = relationship("ProjectCard", back_populates="user_projects")
