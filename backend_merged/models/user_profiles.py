"""
User Profile Model
Represents the user_profiles table in the database
"""

from sqlalchemy import Column, BigInteger, Integer, String, Boolean, JSON, Date, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime
from .base import Base


class UserProfile(Base):
    """
    User Profile model matching user_profiles table schema
    """
    __tablename__ = "user_profiles"
    
    # Primary key
    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    
    # Basic Information
    name = Column(String(100), nullable=False)
    birthday = Column(Date, nullable=True)
    age = Column(Integer, nullable=True)  # Auto-calculated via trigger
    gender = Column(String(50), nullable=True)
    
    # Location
    province_id = Column(Integer, ForeignKey("provinces.id", ondelete="SET NULL"), nullable=True)
    city_id = Column(Integer, ForeignKey("cities.id", ondelete="SET NULL"), nullable=True)
    location = Column(String(200), nullable=True)
    
    # Profile Media
    profile_photo = Column(Text, nullable=True)
    profile_image_description = Column(Text, nullable=True)  # AI-generated description
    
    # Introduction
    one_sentence_intro = Column(Text, nullable=True)
    
    # Interests and Skills (JSONB arrays)
    hobbies = Column(JSONB, nullable=True)
    languages = Column(JSONB, nullable=True)
    skills = Column(JSONB, nullable=True)
    resources = Column(JSONB, nullable=True)
    demands = Column(JSONB, nullable=True)
    
    # Goals
    goals = Column(Text, nullable=True)
    
    # University Information
    current_university = Column(String(200), nullable=True)
    university_email = Column(String(200), nullable=True)
    university_verified = Column(Boolean, nullable=False, default=False)
    
    # WeChat Information
    wechat_id = Column(String(100), nullable=True)
    wechat_verified = Column(Boolean, nullable=False, default=False)
    
    # Profile Status
    is_profile_complete = Column(Boolean, nullable=False, default=False)
    profile_visibility = Column(String(20), nullable=False, default='public')
    
    # Counts (denormalized for performance)
    project_count = Column(Integer, nullable=False, default=0)
    institution_count = Column(Integer, nullable=False, default=0)
    
    # Activity Tracking
    last_active = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, server_default=func.current_timestamp())
    updated_at = Column(DateTime, nullable=False, server_default=func.current_timestamp(), onupdate=func.current_timestamp())
    
    # Relationships
    user = relationship("User", back_populates="profile")
    province = relationship("Province", foreign_keys=[province_id], back_populates="user_profiles")
    city = relationship("City", foreign_keys=[city_id], back_populates="user_profiles")
    
    def __repr__(self):
        return f"<UserProfile(id={self.id}, user_id={self.user_id}, name='{self.name}')>"
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "birthday": self.birthday.isoformat() if self.birthday else None,
            "age": self.age,
            "gender": self.gender,
            "province_id": self.province_id,
            "city_id": self.city_id,
            "location": self.location,
            "profile_photo": self.profile_photo,
            "profile_image_description": self.profile_image_description,
            "one_sentence_intro": self.one_sentence_intro,
            "hobbies": self.hobbies,
            "languages": self.languages,
            "skills": self.skills,
            "resources": self.resources,
            "demands": self.demands,
            "goals": self.goals,
            "current_university": self.current_university,
            "university_email": self.university_email,
            "university_verified": self.university_verified,
            "wechat_id": self.wechat_id,
            "wechat_verified": self.wechat_verified,
            "is_profile_complete": self.is_profile_complete,
            "profile_visibility": self.profile_visibility,
            "project_count": self.project_count,
            "institution_count": self.institution_count,
            "last_active": self.last_active.isoformat() if self.last_active else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
