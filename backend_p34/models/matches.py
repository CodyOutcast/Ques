from sqlalchemy import Column, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from models.base import Base

class Match(Base):
    __tablename__ = "matches"

    match_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user1_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    user2_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    user1 = relationship("User", foreign_keys=[user1_id])
    user2 = relationship("User", foreign_keys=[user2_id])
    messages = relationship("Message", back_populates="match", cascade="all, delete-orphan")