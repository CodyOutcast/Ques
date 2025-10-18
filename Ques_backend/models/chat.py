"""
Chat system models for AI-powered user discovery conversations
Simplified design based on frontend API requirements
"""

from sqlalchemy import Column, String, Text, Boolean, Integer, TIMESTAMP, ForeignKey, ARRAY, UUID, Numeric
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from models.base import Base


class ChatSession(Base):
    """
    Chat sessions for user-AI conversations
    Simplified for AI chat only - no multi-user conversations
    """
    __tablename__ = "chat_sessions"
    
    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=True)  # Optional session title
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    last_message_at = Column(TIMESTAMP, nullable=True)
    message_count = Column(Integer, default=0, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="chat_sessions")
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<ChatSession {self.id}: {self.title or 'Untitled'} ({self.message_count} messages)>"


class ChatMessage(Base):
    """
    Individual messages in chat sessions
    Supports both user messages and AI responses with metadata
    """
    __tablename__ = "chat_messages"
    
    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(PostgresUUID(as_uuid=True), ForeignKey("chat_sessions.id", ondelete="CASCADE"), nullable=False)
    message_text = Column(Text, nullable=False)
    message_type = Column(String(20), default="user", nullable=False)  # 'user' or 'ai'
    
    # Search context (for AI responses)
    search_query = Column(String(500), nullable=True)
    search_mode = Column(String(20), nullable=True)  # 'inside' or 'global'
    quoted_contacts = Column(ARRAY(String), nullable=True)  # Array of contact IDs mentioned
    
    # AI response metadata (only for AI messages)
    response_time_ms = Column(Integer, nullable=True)
    confidence_score = Column(Numeric(3, 2), nullable=True)  # 0.00 to 1.00
    
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    
    # Relationships
    session = relationship("ChatSession", back_populates="messages")
    recommendations = relationship("MessageRecommendation", back_populates="message", cascade="all, delete-orphan", uselist=False)  # One batch per message
    suggested_queries = relationship("SuggestedQuery", back_populates="message", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<ChatMessage {self.id}: {self.message_type} - {self.message_text[:50]}...>"


class MessageRecommendation(Base):
    """
    User recommendations batch linked to AI chat messages
    Stores arrays of users recommended by AI in response to queries
    Each record represents a batch of recommendations for one message
    """
    __tablename__ = "message_recommendations"
    
    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    message_id = Column(PostgresUUID(as_uuid=True), ForeignKey("chat_messages.id", ondelete="CASCADE"), nullable=False)
    
    # Array of recommended user IDs - stores multiple users per message
    recommended_user_ids = Column(ARRAY(Integer), nullable=False)  # [101, 102, 103, ...]
    
    # Batch metadata
    batch_id = Column(String(100), nullable=True)  # Optional batch identifier for frontend
    search_context = Column(Text, nullable=True)  # Search query/context that generated these recommendations
    total_found = Column(Integer, nullable=True)  # Total users found (may be more than returned)
    
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    
    # Relationships
    message = relationship("ChatMessage", back_populates="recommendations")
    
    def __repr__(self):
        user_count = len(self.recommended_user_ids) if self.recommended_user_ids else 0
        return f"<MessageRecommendation {self.id}: {user_count} users for message {self.message_id}>"


class SuggestedQuery(Base):
    """
    AI-generated follow-up query suggestions for chat messages
    Helps users refine their search and continue conversations
    """
    __tablename__ = "suggested_queries"
    
    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    message_id = Column(PostgresUUID(as_uuid=True), ForeignKey("chat_messages.id", ondelete="CASCADE"), nullable=False)
    query_text = Column(String(500), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    
    # Relationships
    message = relationship("ChatMessage", back_populates="suggested_queries")
    
    def __repr__(self):
        return f"<SuggestedQuery {self.id}: {self.query_text}>"