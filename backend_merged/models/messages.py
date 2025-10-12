"""
Messages model matching actual database schema
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base

class Message(Base):
    """
    Message model matching the actual database schema
    """
    __tablename__ = "messages"
    
    message_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    match_id = Column(Integer, ForeignKey("matches.match_id"), nullable=False)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    text = Column(Text, nullable=False)
    timestamp = Column(DateTime, nullable=True, default=datetime.utcnow)
    is_read = Column(Boolean, nullable=True, default=False)
    
    # Relationships
    match = relationship("Match", back_populates="messages")
    sender = relationship("User", back_populates="sent_messages")
    
    # Compatibility properties
    @property
    def id(self):
        return self.message_id
    
    @property
    def content(self):
        return self.text
    
    @property
    def created_at(self):
        return self.timestamp
