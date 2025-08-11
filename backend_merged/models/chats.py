"""
Chat and messaging models with greeting/acceptance flow
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from .base import Base

class ChatStatus(enum.Enum):
    """Chat status enumeration"""
    PENDING = "pending"  # Greeting sent, waiting for acceptance
    ACTIVE = "active"    # Greeting accepted, chat is active
    REJECTED = "rejected"  # Greeting rejected
    BLOCKED = "blocked"   # One user blocked the other

class Chat(Base):
    """
    Chat model with greeting/acceptance flow
    """
    __tablename__ = "chats"
    
    chat_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    initiator_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)  # User who sent greeting
    recipient_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)  # User who received greeting
    status = Column(Enum(ChatStatus), nullable=False, default=ChatStatus.PENDING)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    accepted_at = Column(DateTime, nullable=True)  # When greeting was accepted
    last_message_at = Column(DateTime, nullable=True)
    
    # Greeting message
    greeting_message = Column(Text, nullable=True)  # The initial greeting sent
    
    # Relationships
    initiator = relationship("User", foreign_keys=[initiator_id])
    recipient = relationship("User", foreign_keys=[recipient_id])
    messages = relationship("ChatMessage", back_populates="chat", cascade="all, delete-orphan")
    
    # Compatibility properties
    @property
    def id(self):
        return self.chat_id
    
    @property
    def is_active(self):
        return self.status == ChatStatus.ACTIVE
    
    @property
    def is_pending(self):
        return self.status == ChatStatus.PENDING
    
    @property
    def is_rejected(self):
        return self.status == ChatStatus.REJECTED
    
    def get_other_user_id(self, user_id: int) -> int:
        """Get the ID of the other user in the chat"""
        return self.recipient_id if user_id == self.initiator_id else self.initiator_id
    
    def can_send_message(self, user_id: int) -> bool:
        """Check if user can send messages in this chat"""
        if self.status == ChatStatus.ACTIVE:
            return True
        elif self.status == ChatStatus.PENDING and user_id == self.initiator_id:
            return False  # Can't send more messages until greeting is accepted
        return False

class ChatMessage(Base):
    """
    ChatMessage model for chat messages
    """
    __tablename__ = "chat_messages"
    
    message_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    chat_id = Column(Integer, ForeignKey("chats.chat_id", ondelete="CASCADE"), nullable=False)
    sender_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    content = Column(Text, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True, onupdate=datetime.utcnow)
    
    # Message status
    is_read = Column(Boolean, nullable=False, default=False)
    is_greeting = Column(Boolean, nullable=False, default=False)  # True for initial greeting message
    
    # Relationships
    chat = relationship("Chat", back_populates="messages")
    sender = relationship("User")
    
    # Compatibility properties
    @property
    def id(self):
        return self.message_id
    
    @property
    def text(self):
        return self.content
    
    @property
    def timestamp(self):
        return self.created_at
