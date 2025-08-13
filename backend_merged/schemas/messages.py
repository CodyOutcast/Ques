"""
Message schemas for API requests and responses
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class MessageSearchRequest(BaseModel):
    """Request schema for message search"""
    query: str = Field(..., min_length=2, description="Search query (minimum 2 characters)")
    limit: int = Field(20, le=100, description="Maximum number of results")
    offset: int = Field(0, ge=0, description="Number of results to skip")


class UserInfo(BaseModel):
    """User information for message responses"""
    id: int
    username: Optional[str]
    display_name: Optional[str]
    avatar_url: Optional[str]


class MatchInfo(BaseModel):
    """Match information for global search responses"""
    id: int
    other_user: Optional[UserInfo]


class MessageSearchResult(BaseModel):
    """Individual message search result"""
    message_id: int
    content: str
    sender: Optional[UserInfo]
    timestamp: datetime
    is_read: bool
    match_id: Optional[int] = None  # For conversation search
    match: Optional[MatchInfo] = None  # For global search


class MessageSearchResponse(BaseModel):
    """Response schema for message search"""
    query: str
    results: List[MessageSearchResult]
    total_count: int
    limit: int
    offset: int
    has_more: bool


class MessageContextResult(BaseModel):
    """Message with context information"""
    message_id: int
    content: str
    sender: Optional[UserInfo]
    timestamp: datetime
    is_read: bool
    is_target: bool = Field(description="True if this is the target message being searched for")


class MessageContextResponse(BaseModel):
    """Response schema for message context"""
    target_message_id: int
    context_messages: List[MessageContextResult]
    total_context: int


class SendMessageRequest(BaseModel):
    """Request schema for sending a message"""
    content: str = Field(..., min_length=1, max_length=2000, description="Message content")
    message_type: Optional[str] = Field("text", description="Type of message (text, image, etc.)")


class MessageResponse(BaseModel):
    """Response schema for a single message"""
    id: int
    content: str
    sender_id: int
    created_at: datetime
    message_type: Optional[str] = "text"
    is_read: bool = False
    match_id: int


class ConversationInfo(BaseModel):
    """User information in conversation list"""
    id: int
    username: Optional[str]
    display_name: Optional[str]
    avatar_url: Optional[str]


class LatestMessageInfo(BaseModel):
    """Latest message information in conversation"""
    content: Optional[str]
    created_at: Optional[datetime]
    sender_id: Optional[int]


class ConversationResponse(BaseModel):
    """Response schema for conversation list"""
    match_id: int
    user: ConversationInfo
    latest_message: Optional[LatestMessageInfo]
    matched_at: datetime


class DeleteMessageResponse(BaseModel):
    """Response schema for message deletion"""
    message: str = "Message deleted successfully"
