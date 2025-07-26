from sqlalchemy import Column, Integer, DateTime, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base

class Chat(Base):
    __tablename__ = "chats"

    id = Column(Integer, primary_key=True, index=True)
    user1_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)  # One participant
    user2_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)  # Other participant
    like_id = Column(Integer, ForeignKey("likes.id"), nullable=False)  # Ties to the original like
    started_at = Column(DateTime, default=datetime.utcnow)

    messages = relationship("Message", back_populates="chat")  # All messages in this chat

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(Integer, ForeignKey("chats.id"), nullable=False)
    sender_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    content = Column(String, nullable=False)  # The message text
    timestamp = Column(DateTime, default=datetime.utcnow)
    read = Column(Boolean, default=False)  # Has it been read?

    chat = relationship("Chat", back_populates="messages")  # Link back to chat