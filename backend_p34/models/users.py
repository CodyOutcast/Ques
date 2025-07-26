from sqlalchemy import Column, Integer, String, ForeignKey, Enum, DateTime, Boolean
from sqlalchemy.orm import relationship
from models.base import Base
import enum
from datetime import datetime

class SwipeDirection(enum.Enum):
    like = "like"
    dislike = "dislike"

class VerificationStatus(enum.Enum):
    unverified = "unverified"
    pending = "pending"
    verified = "verified"

class User(Base):
    __tablename__ = "users"
    
    user_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    bio = Column(String(500))
    verification_status = Column(String(50), default="pending")  # Changed to String to match migration
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    features = relationship("UserFeature", back_populates="user", cascade="all, delete-orphan")
    swipes_sent = relationship("UserSwipe", foreign_keys="[UserSwipe.swiper_id]", back_populates="swiper", cascade="all, delete-orphan")
    swipes_received = relationship("UserSwipe", foreign_keys="[UserSwipe.target_id]", back_populates="target", cascade="all, delete-orphan")
    links = relationship("UserLink", back_populates="user", cascade="all, delete-orphan")

class UserFeature(Base):
    __tablename__ = "user_features"
    
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), primary_key=True)
    feature_name = Column(String(50), primary_key=True)  # Changed from 'tags' to 'feature_name'
    user = relationship("User", back_populates="features")

class UserSwipe(Base):
    __tablename__ = "user_swipes"
    
    swipe_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    swiper_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    target_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    direction = Column(String(50), nullable=False)  # Changed to String to match migration
    timestamp = Column(DateTime, default=datetime.utcnow)

    swiper = relationship("User", foreign_keys=[swiper_id], back_populates="swipes_sent")
    target = relationship("User", foreign_keys=[target_id], back_populates="swipes_received")

class UserLink(Base):
    __tablename__ = "user_links"
    
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), primary_key=True)
    link_url = Column(String(255), primary_key=True)  # Changed from 'links' to 'link_url'
    user = relationship("User", back_populates="links")
