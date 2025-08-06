"""
User feature models matching the actual database schema
"""

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class UserFeature(Base):
    """
    User features/tags model matching the actual database schema
    """
    __tablename__ = "user_features"

    user_id = Column(Integer, ForeignKey("users.user_id"), primary_key=True)
    tags = Column(String, nullable=False)  # JSON string or comma-separated tags
    
    # Relationship to users table
    user = relationship("User", back_populates="features")

class UserLink(Base):
    """
    User links model matching the actual database schema
    """
    __tablename__ = "user_links"

    user_id = Column(Integer, ForeignKey("users.user_id"), primary_key=True)
    links = Column(String, nullable=False)  # JSON string of social links
    
    # Relationship to users table
    user = relationship("User", back_populates="links")
