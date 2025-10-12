"""
Whisper Model - matching actual database schema
Whispers are greeting messages sent between users
"""
from sqlalchemy import Column, BigInteger, Text, VARCHAR, Boolean, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base


class Whisper(Base):
    """Whisper messages between users"""
    __tablename__ = "whispers"
    
    # Primary key
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    
    # User relationships
    sender_id = Column(BigInteger, ForeignKey("users.id"), nullable=False, index=True)
    recipient_id = Column(BigInteger, ForeignKey("users.id"), nullable=False, index=True)
    
    # Message content
    greeting_message = Column(Text, nullable=False)
    sender_wechat_id = Column(VARCHAR(100), nullable=True)
    
    # Swipe context
    swipe_id = Column(BigInteger, ForeignKey("user_swipes.id"), nullable=True)
    
    # Status tracking
    is_read = Column(Boolean, default=False, nullable=False, index=True)
    read_at = Column(TIMESTAMP, nullable=True)
    
    # Threading
    reply_to_whisper_id = Column(BigInteger, ForeignKey("whispers.id"), nullable=True)
    
    # Template tracking
    from_template = Column(Boolean, default=False, nullable=False)
    
    # Expiration
    expires_at = Column(TIMESTAMP, nullable=True, index=True)
    
    # Timestamps
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.current_timestamp(), index=True)
    updated_at = Column(TIMESTAMP, nullable=False, server_default=func.current_timestamp(), onupdate=func.current_timestamp())
    
    # Relationships
    sender = relationship("User", foreign_keys=[sender_id], back_populates="sent_whispers")
    recipient = relationship("User", foreign_keys=[recipient_id], back_populates="received_whispers")
    swipe = relationship("UserSwipe", foreign_keys=[swipe_id], back_populates="whispers")
    
    # Self-referential relationship for replies
    reply_to = relationship("Whisper", remote_side=[id], foreign_keys=[reply_to_whisper_id])
    
    def __repr__(self):
        return f"<Whisper(id={self.id}, sender={self.sender_id}, recipient={self.recipient_id}, read={self.is_read})>"
    
    @property
    def is_expired(self) -> bool:
        """Check if whisper has expired"""
        from datetime import datetime, timezone
        if self.expires_at:
            return datetime.now(timezone.utc) > self.expires_at
        return False
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "sender_id": self.sender_id,
            "recipient_id": self.recipient_id,
            "greeting_message": self.greeting_message,
            "sender_wechat_id": self.sender_wechat_id,
            "swipe_id": self.swipe_id,
            "is_read": self.is_read,
            "read_at": self.read_at.isoformat() if self.read_at else None,
            "reply_to_whisper_id": self.reply_to_whisper_id,
            "from_template": self.from_template,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
