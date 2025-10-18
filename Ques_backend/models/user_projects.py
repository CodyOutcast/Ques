"""
User projects model matching actual database schema
"""

from sqlalchemy import Column, BigInteger, String, VARCHAR, Text, TIMESTAMP, Integer, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base

class UserProject(Base):
    """
    User projects table - matches actual database schema
    Table: user_projects
    """
    __tablename__ = "user_projects"

    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    title = Column(VARCHAR(200), nullable=False)
    role = Column(VARCHAR(100), nullable=True)
    description = Column(Text, nullable=True)
    reference_links = Column(JSONB, nullable=True)  # Array of URLs as JSON
    project_order = Column(Integer, nullable=False, default=0)
    is_featured = Column(Boolean, nullable=False, default=False)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship
    user = relationship("User", back_populates="projects")