"""
User models matching the actual database schema
"""

from sqlalchemy import Column, Integer, String, Boolean, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base

class User(Base):
    """
    User model matching the actual database schema
    """
    __tablename__ = "users"

    # Primary key (actual column name is user_id)
    user_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    bio = Column(String(500), nullable=True)
    verification_status = Column(String(50), nullable=True)
    is_active = Column(Boolean, nullable=True, default=True)
    feature_tags = Column(JSON, nullable=True)
    vector_id = Column(String(255), nullable=True)
    profile_image_url = Column(String(512), nullable=True)
    
    # Location fields
    latitude = Column(String(20), nullable=True)  # e.g., "40.7128"
    longitude = Column(String(20), nullable=True)  # e.g., "-74.0060"
    city = Column(String(100), nullable=True)  # e.g., "New York"
    state = Column(String(100), nullable=True)  # e.g., "New York"
    country = Column(String(100), nullable=True)  # e.g., "United States"
    postal_code = Column(String(20), nullable=True)  # e.g., "10001"
    address = Column(String(500), nullable=True)  # Full address if needed
    
    # Relationships to other tables
    auth_records = relationship("UserAuth", back_populates="user")
    refresh_tokens = relationship("RefreshToken", back_populates="user")
    sessions = relationship("UserSession", back_populates="user")
    security_logs = relationship("SecurityLog", back_populates="user")
    features = relationship("UserFeature", back_populates="user", uselist=False)
    links = relationship("UserLink", back_populates="user", uselist=False)
    
    # User swipe relationships
    sent_swipes = relationship("UserSwipe", foreign_keys="UserSwipe.swiper_id", back_populates="swiper")
    received_swipes = relationship("UserSwipe", foreign_keys="UserSwipe.target_id", back_populates="target")
    
    # Like relationships
    given_likes = relationship("Like", foreign_keys="Like.liker_id", back_populates="liker")
    
    # Match relationships
    matches_as_user1 = relationship("Match", foreign_keys="Match.user1_id", back_populates="user1")
    matches_as_user2 = relationship("Match", foreign_keys="Match.user2_id", back_populates="user2")
    
    # Message relationships
    sent_messages = relationship("Message", back_populates="sender")
    
    # Project relationships
    user_projects = relationship("UserProject", back_populates="user")
    created_projects = relationship("ProjectCard", foreign_keys="ProjectCard.creator_id", back_populates="creator")
    
    # Membership relationship
    membership = relationship("UserMembership", back_populates="user", uselist=False)
    
    # Payment relationships
    membership_transactions = relationship("MembershipTransaction", back_populates="user")
    
    # Report relationships
    reports_made = relationship("UserReport", foreign_keys="UserReport.reporter_id", back_populates="reporter")
    reports_received = relationship("UserReport", foreign_keys="UserReport.reported_user_id", back_populates="reported_user")
    
    # Add commonly used fields for compatibility
    @property
    def id(self):
        """Alias for user_id for compatibility"""
        return self.user_id
    
    @property
    def username(self):
        """Alias for name for compatibility"""
        return self.name
    
    @property
    def display_name(self):
        """Use name as display name"""
        return self.name
    
    @property
    def email(self):
        """Email from auth table - placeholder"""
        return None
    
    @property
    def avatar_url(self):
        """Avatar URL from profile_image_url or generate default"""
        return getattr(self, 'profile_image_url', None) or f"https://api.dicebear.com/7.x/avataaars/svg?seed={self.name}"
    
    @property
    def location(self):
        """Location information"""
        if self.city and self.state:
            return f"{self.city}, {self.state}"
        elif self.city:
            return self.city
        elif self.latitude and self.longitude:
            return f"{self.latitude}, {self.longitude}"
        return None
    
    @property
    def age(self):
        """Age - placeholder"""
        return None
    
    @property
    def gender(self):
        """Gender - placeholder"""
        return None
    
    @property
    def is_verified(self):
        """Check if user is verified"""
        return self.verification_status == "verified"
    
    @property
    def created_at(self):
        """Created at - placeholder"""
        return datetime.utcnow()
    
    @property
    def updated_at(self):
        """Updated at - placeholder"""
        return datetime.utcnow()
