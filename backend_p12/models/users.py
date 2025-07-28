from sqlalchemy import Column, Integer, String, Boolean, JSON
from .base import Base  # This imports the Base from base.py
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"  # The name of the table in the DB

    user_id = Column(Integer, primary_key=True, index=True)  # Primary key column (matches existing schema)
    name = Column(String)  # User's name
    bio = Column(String)  # User's bio
    verification_status = Column(String)  # Verification status (matches existing schema)
    is_active = Column(Boolean, default=True)  # Active status (corrected to Boolean type)
    feature_tags = Column(JSON)  # Feature tags for vector matching
    vector_id = Column(String)  # Vector ID in external vector database
    
    # Property to access user_id as id for compatibility
    @property
    def id(self):
        return self.user_id
    
    # Relationships
    # likes_sent = relationship("Like", back_populates="liker")  # Likes this user has given - commented for now
    auth_methods = relationship("UserAuth", back_populates="user")  # Authentication methods
    refresh_tokens = relationship("RefreshToken", back_populates="user")  # Refresh tokens