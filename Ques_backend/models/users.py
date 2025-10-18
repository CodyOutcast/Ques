"""
User models matching the actual database schema
Updated to match production database: users table with id, phone_number, wechat_id, user_status
"""

from sqlalchemy import Column, BigInteger, String, Boolean, TIMESTAMP
from sqlalchemy.orm import relationship
from datetime import datetime, date
from .base import Base

class User(Base):
    """
    User model matching the actual production database schema
    
    Database schema:
    - id: BIGINT (primary key)
    - phone_number: VARCHAR(20) - UNIQUE
    - wechat_id: VARCHAR(50) - UNIQUE
    - user_status: VARCHAR(20) - default 'inactive'
    - created_at: TIMESTAMP - default CURRENT_TIMESTAMP
    - updated_at: TIMESTAMP - default CURRENT_TIMESTAMP
    """
    __tablename__ = "users"

    # Primary key - actual column name is 'id' not 'user_id'
    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    
    # Authentication fields
    phone_number = Column(String(20), unique=True, nullable=True, index=True)
    wechat_id = Column(String(50), unique=True, nullable=True, index=True)
    
    # Status field
    user_status = Column(String(20), nullable=False, default='inactive', index=True)
    
    # Timestamps
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow, index=True)
    updated_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships to other tables
    # Profile relationship (one-to-one with user_profiles table)
    profile = relationship("UserProfile", back_populates="user", uselist=False)
    
    # Legacy swipes removed - replaced by agent card swipes and AI recommendation swipes
    
    # Whisper relationships
    sent_whispers = relationship("Whisper", foreign_keys="Whisper.sender_id", back_populates="sender")
    received_whispers = relationship("Whisper", foreign_keys="Whisper.recipient_id", back_populates="recipient")
    
    # Report relationships
    reports_made = relationship("UserReport", foreign_keys="UserReport.reporter_id", back_populates="reporter")
    reports_received = relationship("UserReport", foreign_keys="UserReport.reported_user_id", back_populates="reported_user")
    moderated_reports = relationship("UserReport", foreign_keys="UserReport.moderator_id", back_populates="moderator")
    
    # University verification is handled through UserProfile model
    # (user_profile.university_email, user_profile.university_verified)
    
    # Settings relationships (removed outdated models)
    
    # Swipe relationships
    swipe_records = relationship("SwipeRecord", back_populates="user")  # New swipe system
    
    # Institution relationships  
    institutions = relationship("UserInstitution", back_populates="user")
    
    # Project relationships
    projects = relationship("UserProject", back_populates="user")
    
    # Membership and payment relationships
    membership = relationship("Membership", back_populates="user", uselist=False)
    transactions = relationship("MembershipTransaction", back_populates="user")
    payment_methods = relationship("PaymentMethod", back_populates="user")
    
    # Settings relationship
    settings = relationship("UserSettings", back_populates="user", uselist=False)
    
    # Chat relationships
    chat_sessions = relationship("ChatSession", back_populates="user", cascade="all, delete-orphan")

    
    # Compatibility properties - delegate to user_profiles table
    @property
    def user_id(self):
        """Alias for id for backward compatibility"""
        return self.id
    
    @property
    def name(self):
        """Get name from profile"""
        return self.profile.name if self.profile else None
    
    @property
    def username(self):
        """Get name from profile as username"""
        return self.profile.name if self.profile else f"user_{self.id}"
    
    @property
    def display_name(self):
        """Get display name from profile"""
        return self.profile.name if self.profile else f"User {self.id}"
    
    @property
    def bio(self):
        """Get bio from profile one_sentence_intro"""
        return self.profile.one_sentence_intro if self.profile else None
    
    @property
    def age(self):
        """Get age from profile"""
        return self.profile.age if self.profile else None
    
    @property
    def birthday(self):
        """Get birthday from profile"""
        return self.profile.birthday if self.profile else None
    
    @property
    def gender(self):
        """Get gender from profile"""
        return self.profile.gender if self.profile else None
    
    @property
    def location(self):
        """Get location from profile"""
        return self.profile.location if self.profile else None
    
    @property
    def avatar_url(self):
        """Get avatar URL from profile"""
        if self.profile and self.profile.profile_photo:
            return self.profile.profile_photo
        return f"https://api.dicebear.com/7.x/avataaars/svg?seed={self.id}"
    
    @property
    def is_verified(self):
        """Check if user's university is verified"""
        return self.profile.university_verified if self.profile else False
    
    @property
    def is_active(self):
        """Check if user status is active"""
        return self.user_status == 'active'
    
    def __repr__(self):
        return f"<User(id={self.id}, phone={self.phone_number}, wechat={self.wechat_id}, status={self.user_status})>"
