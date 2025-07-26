from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base  # Import from base.py

class Like(Base):
    __tablename__ = "likes"  # Table name in DB

    id = Column(Integer, primary_key=True, index=True)  # Unique ID
    liker_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)  # Who did the liking (links to users table)
    liked_item_id = Column(Integer, nullable=False)  # ID of the liked thing (profile or project)
    liked_item_type = Column(String, nullable=False)  # 'profile' or 'project'
    timestamp = Column(DateTime, default=datetime.utcnow)  # When it happened
    granted_chat_access = Column(Boolean, default=False)  # Permission for chat

    liker = relationship("User", back_populates="likes_sent")  # Link back to the User model