"""
Chat and messaging schemas
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class ChatStatus(str, Enum):
    PENDING = "pending"
    ACTIVE = "active"
    REJECTED = "rejected"
    BLOCKED = "blocked"

class MessageCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=1000)

class GreetingCreate(BaseModel):
    recipient_id: int
    greeting_message: str = Field(..., min_length=1, max_length=500)

class GreetingResponse(BaseModel):
    chat_id: int
    accept: bool  # True to accept, False to reject

class MessageResponse(BaseModel):
    message_id: int
    chat_id: int
    sender_id: int
    content: str
    created_at: datetime
    is_read: bool
    is_greeting: bool
    highlighted_content: Optional[str] = None  # Content with search terms highlighted
    
    class Config:
        from_attributes = True

class ChatResponse(BaseModel):
    chat_id: int
    initiator_id: int
    recipient_id: int
    status: ChatStatus
    created_at: datetime
    accepted_at: Optional[datetime] = None
    last_message_at: Optional[datetime] = None
    greeting_message: Optional[str] = None
    
    # Other user info (populated by service)
    other_user_name: Optional[str] = None
    other_user_bio: Optional[str] = None
    
    class Config:
        from_attributes = True

class ChatWithMessages(BaseModel):
    chat_id: int
    initiator_id: int
    recipient_id: int
    status: ChatStatus
    created_at: datetime
    accepted_at: Optional[datetime] = None
    last_message_at: Optional[datetime] = None
    greeting_message: Optional[str] = None
    messages: List[MessageResponse] = []
    
    # Other user info
    other_user_name: Optional[str] = None
    other_user_bio: Optional[str] = None
    
    class Config:
        from_attributes = True

class ChatListResponse(BaseModel):
    chats: List[ChatResponse]
    total: int
    pending_greetings: int  # Number of pending greetings for this user

class SendMessageRequest(BaseModel):
    chat_id: int
    content: str = Field(..., min_length=1, max_length=1000)

class MarkAsReadRequest(BaseModel):
    message_ids: List[int]

# Search schemas
class ChatSearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=100, description="Search query")
    search_messages: bool = Field(default=True, description="Search in message content")
    search_users: bool = Field(default=True, description="Search in user names")
    limit: int = Field(default=20, ge=1, le=100, description="Maximum results to return")

class MessageSearchResult(BaseModel):
    message_id: int
    chat_id: int
    sender_id: int
    sender_name: Optional[str] = None
    content: str
    created_at: datetime
    # Highlighted content with search term
    highlighted_content: Optional[str] = None
    
    class Config:
        from_attributes = True

class ChatSearchResult(BaseModel):
    chat_id: int
    other_user_id: int
    other_user_name: Optional[str] = None
    other_user_bio: Optional[str] = None
    status: ChatStatus
    last_message_at: Optional[datetime] = None
    # Why this chat matched (user name, bio, or messages)
    match_reason: str
    # Recent messages for context
    recent_messages: List[MessageResponse] = []
    
    class Config:
        from_attributes = True

class SearchResponse(BaseModel):
    query: str
    total_chats: int
    total_messages: int
    chats: List[ChatSearchResult] = []
    messages: List[MessageSearchResult] = []
