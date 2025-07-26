from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from models.base import Base

class Message(Base):
    __tablename__ = "messages"

    message_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    match_id = Column(Integer, ForeignKey("matches.match_id"), nullable=False)
    sender_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    text = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    is_read = Column(Boolean, default=False)

    # Relationships
    match = relationship("Match", back_populates="messages")
    sender = relationship("User", foreign_keys=[sender_id])
