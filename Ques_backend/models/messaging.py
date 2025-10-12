"""
Messaging and matching models following DATABASE_STRUCTURE_UPDATE.md
"""

from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, Boolean, VARCHAR, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base

class Match(Base):
    """
    User matches for communication
    """
    __tablename__ = "matches"

    match_id = Column(Integer, primary_key=True, index=True)
    user1_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user2_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    timestamp = Column(TIMESTAMP, nullable=True, default=datetime.utcnow)
    is_active = Column(Boolean, nullable=True, default=True)
    match_reason = Column(VARCHAR(200), nullable=True)
    chat_enabled = Column(Boolean, nullable=False, default=True)
    video_call_enabled = Column(Boolean, nullable=False, default=False)
    last_message_at = Column(TIMESTAMP, nullable=True)
    last_activity_at = Column(TIMESTAMP, nullable=True)
    compatibility_score = Column(Integer, nullable=True)

    # Relationships
    user1 = relationship("User", foreign_keys=[user1_id], back_populates="matches_as_user1")
    user2 = relationship("User", foreign_keys=[user2_id], back_populates="matches_as_user2")
    messages = relationship("Message", back_populates="match")

class Chat(Base):
    """
    Chat sessions between users
    """
    __tablename__ = "chats"

    chat_id = Column(Integer, primary_key=True, index=True)
    initiator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    recipient_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(VARCHAR(8), nullable=False, default='pending')  # pending, active, closed
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)
    accepted_at = Column(TIMESTAMP, nullable=True)
    last_message_at = Column(TIMESTAMP, nullable=True)
    greeting_message = Column(Text, nullable=True)

    # Relationships
    initiator = relationship("User", foreign_keys=[initiator_id], back_populates="initiated_chats")
    recipient = relationship("User", foreign_keys=[recipient_id], back_populates="received_chats")
    messages = relationship("ChatMessage", back_populates="chat")

class ChatMessage(Base):
    """
    Individual messages in chats
    """
    __tablename__ = "chat_messages"

    message_id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(Integer, ForeignKey("chats.chat_id"), nullable=False)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, nullable=True)
    is_read = Column(Boolean, nullable=False, default=False)
    is_greeting = Column(Boolean, nullable=False, default=False)

    # Relationships
    chat = relationship("Chat", back_populates="messages")
    sender = relationship("User", back_populates="chat_messages")

class Message(Base):
    """
    Legacy message system (alternative to chat_messages)
    """
    __tablename__ = "messages"

    message_id = Column(Integer, primary_key=True, index=True)
    match_id = Column(Integer, ForeignKey("matches.match_id"), nullable=False)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    text = Column(Text, nullable=False)
    timestamp = Column(TIMESTAMP, nullable=True, default=datetime.utcnow)
    is_read = Column(Boolean, nullable=True, default=False)

    # Relationships
    match = relationship("Match", back_populates="messages")
    sender = relationship("User", back_populates="sent_messages")