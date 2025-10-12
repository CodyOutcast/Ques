"""
User settings and configuration models following DATABASE_STRUCTURE_UPDATE.md
"""

from sqlalchemy import Column, Integer, String, TIMESTAMP, Boolean, VARCHAR, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base

class UserAccountSettings(Base):
    """
    User account settings and preferences
    """
    __tablename__ = "user_account_settings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    language = Column(VARCHAR(10), nullable=False, default='en')
    timezone = Column(VARCHAR(50), nullable=False, default='UTC')
    notifications_enabled = Column(Boolean, nullable=False, default=True)
    email_notifications = Column(Boolean, nullable=False, default=True)
    push_notifications = Column(Boolean, nullable=False, default=True)
    sms_notifications = Column(Boolean, nullable=False, default=False)
    profile_visibility = Column(VARCHAR(20), nullable=False, default='public')  # public, friends, private
    allow_messages = Column(Boolean, nullable=False, default=True)
    allow_whispers = Column(Boolean, nullable=False, default=True)
    show_age = Column(Boolean, nullable=False, default=True)
    show_location = Column(Boolean, nullable=False, default=True)
    auto_accept_chats = Column(Boolean, nullable=False, default=False)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, nullable=True)

    # Relationships
    user = relationship("User", back_populates="account_settings")

class UserSecuritySettings(Base):
    """
    User security and privacy settings
    """
    __tablename__ = "user_security_settings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    two_factor_enabled = Column(Boolean, nullable=False, default=False)
    login_notifications = Column(Boolean, nullable=False, default=True)
    suspicious_activity_alerts = Column(Boolean, nullable=False, default=True)
    data_sharing_consent = Column(Boolean, nullable=False, default=False)
    marketing_consent = Column(Boolean, nullable=False, default=False)
    location_tracking = Column(Boolean, nullable=False, default=False)
    session_timeout = Column(Integer, nullable=False, default=3600)  # seconds
    ip_whitelist = Column(JSON, nullable=True)  # Array of allowed IPs
    device_limit = Column(Integer, nullable=False, default=5)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, nullable=True)

    # Relationships
    user = relationship("User", back_populates="security_settings")

class PrivacyConsent(Base):
    """
    User privacy consent tracking
    """
    __tablename__ = "privacy_consents"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    consent_type = Column(VARCHAR(50), nullable=False)  # data_processing, marketing, analytics, etc.
    consent_given = Column(Boolean, nullable=False)
    consent_text = Column(Text, nullable=True)  # Text that was consented to
    ip_address = Column(VARCHAR(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)
    withdrawn_at = Column(TIMESTAMP, nullable=True)

    # Relationships
    user = relationship("User", back_populates="privacy_consents")

class DataExportRequest(Base):
    """
    User data export requests (GDPR compliance)
    """
    __tablename__ = "data_export_requests"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    request_type = Column(VARCHAR(20), nullable=False, default='full')  # full, partial, specific
    status = Column(VARCHAR(20), nullable=False, default='pending')  # pending, processing, completed, failed
    data_categories = Column(JSON, nullable=True)  # Specific data categories requested
    export_format = Column(VARCHAR(10), nullable=False, default='json')  # json, csv, pdf
    file_path = Column(VARCHAR(500), nullable=True)  # Path to generated export file
    download_url = Column(VARCHAR(500), nullable=True)  # Temporary download URL
    expires_at = Column(TIMESTAMP, nullable=True)  # When download link expires
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)
    processed_at = Column(TIMESTAMP, nullable=True)
    downloaded_at = Column(TIMESTAMP, nullable=True)

    # Relationships
    user = relationship("User", back_populates="data_export_requests")

class AccountAction(Base):
    """
    Account actions and lifecycle events
    """
    __tablename__ = "account_actions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    action_type = Column(VARCHAR(30), nullable=False)  # registration, verification, deactivation, deletion
    status = Column(VARCHAR(20), nullable=False, default='pending')  # pending, completed, failed, cancelled
    reason = Column(Text, nullable=True)
    ip_address = Column(VARCHAR(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    action_metadata = Column(JSON, nullable=True)  # Additional action-specific data
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)
    processed_at = Column(TIMESTAMP, nullable=True)
    expires_at = Column(TIMESTAMP, nullable=True)

    # Relationships
    user = relationship("User", back_populates="account_actions")