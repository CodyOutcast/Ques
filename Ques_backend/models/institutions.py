"""
Institution models following DATABASE_STRUCTURE_UPDATE.md
"""

from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, Boolean, VARCHAR, ForeignKey, BIGINT, Date
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base

class Institution(Base):
    """
    Institution/organization information
    """
    __tablename__ = "institutions"

    id = Column(BIGINT, primary_key=True, index=True)
    name = Column(VARCHAR(255), nullable=False)
    name_en = Column(VARCHAR(255), nullable=True)
    type = Column(VARCHAR(50), nullable=False)  # university, company, government, ngo, startup, other
    city_id = Column(Integer, ForeignKey("cities.id"), nullable=True)
    province_id = Column(Integer, ForeignKey("provinces.id"), nullable=True)
    description = Column(Text, nullable=True)
    website = Column(VARCHAR(512), nullable=True)
    logo_url = Column(VARCHAR(512), nullable=True)
    is_verified = Column(Boolean, nullable=False, default=False)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    city = relationship("City", back_populates="institutions")
    province = relationship("Province", back_populates="institutions")
    user_institutions = relationship("UserInstitution", back_populates="institution")

class UserInstitution(Base):
    """
    User-institution relationships
    """
    __tablename__ = "user_institutions"

    user_id = Column(BIGINT, ForeignKey("users.id"), primary_key=True)
    institution_id = Column(BIGINT, ForeignKey("institutions.id"), primary_key=True)
    role = Column(VARCHAR(100), nullable=True)  # student, employee, volunteer, intern, researcher, professor, manager, other
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    is_current = Column(Boolean, nullable=False, default=True)
    position = Column(VARCHAR(100), nullable=True)  # Job title, degree, etc.
    department = Column(VARCHAR(100), nullable=True)  # Department or major
    description = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="user_institutions")
    institution = relationship("Institution", back_populates="user_institutions")