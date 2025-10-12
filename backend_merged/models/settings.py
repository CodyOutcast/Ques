"""
Settings management models for account security and privacy
"""

from sqlalchemy import Column, BigInteger, String, Boolean, DateTime, Integer, Text, ARRAY, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, INET, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
import uuid
import json

from models.base import Base


class UserAccountSettings(Base):
    """Model for user account settings including privacy and security preferences"""
    
    __tablename__ = "user_account_settings"
    
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    
    # Privacy Settings
    profile_visibility = Column(String(20), default='public')  # public, private, friends
    show_online_status = Column(Boolean, default=True)
    allow_messages_from = Column(String(20), default='everyone')  # everyone, matches, friends, nobody
    show_location = Column(Boolean, default=True)
    show_university = Column(Boolean, default=True)
    show_age = Column(Boolean, default=True)
    
    # Safety Settings
    block_screenshots = Column(Boolean, default=False)
    require_verification = Column(Boolean, default=False)
    auto_reject_spam = Column(Boolean, default=True)
    content_filtering = Column(String(20), default='moderate')  # strict, moderate, off
    
    # Account Security
    two_factor_enabled = Column(Boolean, default=False)
    login_notifications = Column(Boolean, default=True)
    session_timeout_minutes = Column(Integer, default=60)
    password_change_required = Column(Boolean, default=False)
    
    # Communication Settings
    allow_whispers = Column(Boolean, default=True)
    allow_friend_requests = Column(Boolean, default=True)
    auto_accept_matches = Column(Boolean, default=False)
    message_read_receipts = Column(Boolean, default=True)
    typing_indicators = Column(Boolean, default=True)
    
    # Data & Privacy (GDPR Compliance)
    data_sharing_consent = Column(Boolean, default=False)
    analytics_tracking = Column(Boolean, default=True)
    personalized_ads = Column(Boolean, default=True)
    data_export_requested = Column(Boolean, default=False)
    marketing_emails = Column(Boolean, default=True)
    
    # Notification Preferences
    email_notifications = Column(Boolean, default=True)
    push_notifications = Column(Boolean, default=True)
    sms_notifications = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="account_settings")
    
    def to_dict(self):
        """Convert settings to dictionary"""
        return {
            'privacy': {
                'profile_visibility': self.profile_visibility,
                'show_online_status': self.show_online_status,
                'allow_messages_from': self.allow_messages_from,
                'show_location': self.show_location,
                'show_university': self.show_university,
                'show_age': self.show_age
            },
            'safety': {
                'block_screenshots': self.block_screenshots,
                'require_verification': self.require_verification,
                'auto_reject_spam': self.auto_reject_spam,
                'content_filtering': self.content_filtering
            },
            'security': {
                'two_factor_enabled': self.two_factor_enabled,
                'login_notifications': self.login_notifications,
                'session_timeout_minutes': self.session_timeout_minutes,
                'password_change_required': self.password_change_required
            },
            'communication': {
                'allow_whispers': self.allow_whispers,
                'allow_friend_requests': self.allow_friend_requests,
                'auto_accept_matches': self.auto_accept_matches,
                'message_read_receipts': self.message_read_receipts,
                'typing_indicators': self.typing_indicators
            },
            'data_privacy': {
                'data_sharing_consent': self.data_sharing_consent,
                'analytics_tracking': self.analytics_tracking,
                'personalized_ads': self.personalized_ads,
                'data_export_requested': self.data_export_requested,
                'marketing_emails': self.marketing_emails
            },
            'notifications': {
                'email_notifications': self.email_notifications,
                'push_notifications': self.push_notifications,
                'sms_notifications': self.sms_notifications
            }
        }


class AccountAction(Base):
    """Model for tracking account actions and security events"""
    
    __tablename__ = "account_actions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    action_type = Column(String(30), nullable=False)  # deactivate, delete, reactivate, etc.
    reason = Column(Text, nullable=True)
    action_metadata = Column(JSONB, nullable=True)  # Additional action-specific data (renamed from 'metadata')
    ip_address = Column(INET, nullable=True)
    user_agent = Column(Text, nullable=True)
    scheduled_for = Column(DateTime, nullable=True)  # For delayed actions
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(BigInteger, ForeignKey("users.id"), nullable=True)  # For admin actions
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="account_actions")
    admin_user = relationship("User", foreign_keys=[created_by])
    
    def is_pending(self) -> bool:
        """Check if action is still pending"""
        return self.completed_at is None and (
            self.scheduled_for is None or self.scheduled_for > datetime.utcnow()
        )
    
    def mark_completed(self):
        """Mark action as completed"""
        self.completed_at = datetime.utcnow()


class UserSecuritySettings(Base):
    """Model for user security settings and two-factor authentication"""
    
    __tablename__ = "user_security_settings"
    
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    
    # Two-Factor Authentication
    two_factor_secret = Column(String(32), nullable=True)  # Base32 encoded TOTP secret
    two_factor_backup_codes = Column(ARRAY(Text), nullable=True)  # Backup codes array
    two_factor_enabled_at = Column(DateTime, nullable=True)
    
    # Login Security
    failed_login_attempts = Column(Integer, default=0)
    last_failed_login = Column(DateTime, nullable=True)
    account_locked_until = Column(DateTime, nullable=True)
    last_password_change = Column(DateTime, nullable=True)
    password_history = Column(JSONB, nullable=True)  # Hash history to prevent reuse
    
    # Session Management
    active_sessions = Column(JSONB, default=lambda: [])  # Track active session tokens
    max_concurrent_sessions = Column(Integer, default=3)
    
    # Security Events
    last_security_check = Column(DateTime, nullable=True)
    suspicious_activity_detected = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="security_settings")
    
    def is_account_locked(self) -> bool:
        """Check if account is currently locked"""
        return (
            self.account_locked_until is not None 
            and self.account_locked_until > datetime.utcnow()
        )
    
    def lock_account(self, duration_minutes: int = 30):
        """Lock account for specified duration"""
        self.account_locked_until = datetime.utcnow() + timedelta(minutes=duration_minutes)
        self.failed_login_attempts += 1
        self.last_failed_login = datetime.utcnow()
    
    def unlock_account(self):
        """Unlock account and reset failed attempts"""
        self.account_locked_until = None
        self.failed_login_attempts = 0


class PrivacyConsent(Base):
    """Model for tracking privacy consents for GDPR compliance"""
    
    __tablename__ = "privacy_consents"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    consent_type = Column(String(50), nullable=False)  # data_processing, marketing, analytics, cookies
    consent_given = Column(Boolean, nullable=False)
    consent_version = Column(String(20), nullable=False)  # Track policy version
    ip_address = Column(INET, nullable=True)
    user_agent = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)  # For time-limited consents
    
    # Relationships
    user = relationship("User", back_populates="privacy_consents")
    
    def is_expired(self) -> bool:
        """Check if consent has expired"""
        return self.expires_at is not None and self.expires_at < datetime.utcnow()
    
    def is_active(self) -> bool:
        """Check if consent is active and valid"""
        return self.consent_given and not self.is_expired()


class DataExportRequest(Base):
    """Model for handling data export requests (GDPR compliance)"""
    
    __tablename__ = "data_export_requests"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    request_type = Column(String(20), default='full')  # full, partial, delete
    status = Column(String(20), default='pending')  # pending, processing, completed, failed, cancelled
    export_format = Column(String(10), default='json')  # json, csv, xml
    export_url = Column(Text, nullable=True)  # S3 URL or file path
    expires_at = Column(DateTime, nullable=True)  # Export file expiration
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="data_export_requests")
    
    def is_completed(self) -> bool:
        """Check if export is completed"""
        return self.status == 'completed' and self.completed_at is not None
    
    def is_expired(self) -> bool:
        """Check if export file has expired"""
        return self.expires_at is not None and self.expires_at < datetime.utcnow()
    
    def mark_completed(self, export_url: str, expires_hours: int = 48):
        """Mark export as completed with download URL"""
        self.status = 'completed'
        self.export_url = export_url
        self.completed_at = datetime.utcnow()
        self.expires_at = datetime.utcnow() + timedelta(hours=expires_hours)