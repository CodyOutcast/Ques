"""
Project models for user projects functionality
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base

class Project(Base):
    """
    Project model for storing user projects
    """
    __tablename__ = "projects"

    # Primary key
    project_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Project details
    short_description = Column(String(200), nullable=False)  # 20 words max (~200 chars)
    long_description = Column(Text, nullable=True)
    start_time = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Optional media (foreign key to user_links for pictures/videos)
    media_link_id = Column(Integer, ForeignKey("user_links.user_id"), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    media_link = relationship("UserLink", foreign_keys=[media_link_id])
    user_projects = relationship("UserProject", back_populates="project")
    
    # Helper properties
    @property
    def id(self):
        """Alias for project_id for compatibility"""
        return self.project_id


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
    project = relationship("Project", back_populates="user_projects")