"""
Security and audit models following DATABASE_STRUCTURE_UPDATE.md
"""

from sqlalchemy import Column, Integer, String, TIMESTAMP, Boolean, VARCHAR, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base

# SecurityLog already defined in user_auth.py

class BlockedUser(Base):
    """
    Blocked user relationships
    """
    __tablename__ = "blocked_users"

    block_id = Column(Integer, primary_key=True, index=True)
    blocker_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    blocked_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    reason = Column(VARCHAR(100), nullable=True)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)
    is_active = Column(Boolean, nullable=False, default=True)

    # Relationships
    blocker = relationship("User", foreign_keys=[blocker_id], back_populates="blocked_users")
    blocked = relationship("User", foreign_keys=[blocked_id], back_populates="blocked_by_users")

class DeviceToken(Base):
    """
    Device tokens for push notifications
    """
    __tablename__ = "device_tokens"

    token_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    device_token = Column(VARCHAR(255), nullable=False, unique=True)
    device_type = Column(VARCHAR(20), nullable=False)  # ios, android, web
    device_info = Column(JSON, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)
    last_used_at = Column(TIMESTAMP, nullable=True)

    # Relationships
    user = relationship("User", back_populates="device_tokens")

class AuditLog(Base):
    """
    System audit logging
    """
    __tablename__ = "audit_logs"

    audit_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(VARCHAR(50), nullable=False)  # create, update, delete, login, logout
    table_name = Column(VARCHAR(50), nullable=True)
    record_id = Column(Integer, nullable=True)
    old_values = Column(JSON, nullable=True)
    new_values = Column(JSON, nullable=True)
    ip_address = Column(VARCHAR(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    timestamp = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="audit_logs")

class APIKey(Base):
    """
    API keys for external integrations
    """
    __tablename__ = "api_keys"

    key_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    key_hash = Column(VARCHAR(255), nullable=False, unique=True)
    name = Column(VARCHAR(100), nullable=False)
    permissions = Column(JSON, nullable=True)
    rate_limit = Column(Integer, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)
    last_used_at = Column(TIMESTAMP, nullable=True)
    expires_at = Column(TIMESTAMP, nullable=True)

    # Relationships
    user = relationship("User", back_populates="api_keys")