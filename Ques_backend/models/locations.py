"""
Location models for provinces and cities based on location.json data
"""

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class Province(Base):
    """
    Province model for Chinese provinces and municipalities
    """
    __tablename__ = "provinces"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Province information
    name_en = Column(String(100), nullable=False)  # English name
    name_cn = Column(String(100), nullable=False)  # Chinese name
    
    # Relationships
    cities = relationship("City", back_populates="province")
    # Note: Users don't have direct province_id FK - location info is in user_profiles table
    user_profiles = relationship("UserProfile", foreign_keys="[UserProfile.province_id]", back_populates="province")

class City(Base):
    """
    City model for Chinese cities
    """
    __tablename__ = "cities"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign key to province
    province_id = Column(Integer, ForeignKey("provinces.id"), nullable=False)
    
    # City information
    name_en = Column(String(100), nullable=False)  # English name
    name_cn = Column(String(100), nullable=False)  # Chinese name
    
    # Relationships
    province = relationship("Province", back_populates="cities")
    # Note: Users don't have direct city_id FK - location info is in user_profiles table
    user_profiles = relationship("UserProfile", foreign_keys="[UserProfile.city_id]", back_populates="city")