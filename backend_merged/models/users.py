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
    
    # Swipe relationships (using actual column names: swiper_id and swiped_user_id)
    sent_swipes = relationship("UserSwipe", foreign_keys="UserSwipe.swiper_id", back_populates="swiper")
    received_swipes = relationship("UserSwipe", foreign_keys="UserSwipe.swiped_user_id", back_populates="swiped_user")
    
    # Whisper relationships
    sent_whispers = relationship("Whisper", foreign_keys="Whisper.sender_id", back_populates="sender")
    received_whispers = relationship("Whisper", foreign_keys="Whisper.recipient_id", back_populates="recipient")
    
    # Report relationships
    reports_made = relationship("UserReport", foreign_keys="UserReport.reporter_id", back_populates="reporter")
    reports_received = relationship("UserReport", foreign_keys="UserReport.reported_user_id", back_populates="reported_user")
    moderated_reports = relationship("UserReport", foreign_keys="UserReport.moderator_id", back_populates="moderator")
    
    # University verification relationship
    university_verification = relationship("UniversityVerification", back_populates="user", uselist=False)
    
    # Settings relationships
    account_settings = relationship("UserAccountSettings", back_populates="user", uselist=False)
    security_settings = relationship("UserSecuritySettings", back_populates="user", uselist=False)
    account_actions = relationship("AccountAction", foreign_keys="AccountAction.user_id", back_populates="user")
    privacy_consents = relationship("PrivacyConsent", back_populates="user")
    data_export_requests = relationship("DataExportRequest", back_populates="user")
    
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
