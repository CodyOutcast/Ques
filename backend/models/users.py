from sqlalchemy import Column, Integer, String, JSON
from .base import Base  # This imports the Base from base.py
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"  # The name of the table in the DB

    id = Column(Integer, primary_key=True, index=True)  # Primary key column
    name = Column(String)  # User's name
    bio = Column(String)  # User's bio
    feature_tags = Column(JSON)  # JSON field for tags
    vector_id = Column(String)  # String field for vector ID
    likes_sent = relationship("Like", back_populates="liker")  # Likes this user has given