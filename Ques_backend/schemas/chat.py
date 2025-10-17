"""
Chat system Pydantic schemas matching frontend API requirements
Based on frontend API documentation section 7 (Chat System)
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Union
from datetime import datetime
from uuid import UUID

# ===== REQUEST SCHEMAS =====

class SendMessageRequest(BaseModel):
    """Request schema for POST /chat/message"""
    message: str = Field(..., min_length=1, max_length=1000, description="User message text")
    sessionId: Optional[str] = Field(None, description="Optional session ID to continue conversation")
    searchMode: Optional[str] = Field("global", description="Search mode: 'inside' or 'global'")
    quotedContacts: Optional[List[str]] = Field(default_factory=list, description="Array of contact IDs mentioned")
    
    @validator('searchMode')
    def validate_search_mode(cls, v):
        if v not in ['inside', 'global']:
            raise ValueError('searchMode must be "inside" or "global"')
        return v


class CreateSessionRequest(BaseModel):
    """Request schema for POST /chat/session"""
    title: Optional[str] = Field(None, max_length=255, description="Optional session title")


# ===== RESPONSE SCHEMAS =====

class ChatSession(BaseModel):
    """Chat session response schema"""
    id: str = Field(..., description="Session UUID")
    user_id: int = Field(..., description="User ID who owns the session")
    title: Optional[str] = Field(None, description="Session title")
    is_active: bool = Field(..., description="Whether session is active")
    created_at: datetime = Field(..., description="Session creation timestamp")
    last_message_at: Optional[datetime] = Field(None, description="Last message timestamp")
    message_count: int = Field(..., description="Number of messages in session")
    
    class Config:
        from_attributes = True


class UserRecommendation(BaseModel):
    """
    User recommendation schema matching frontend data type definition
    From frontend docs: User basic information, matchScore, whyMatch, receivesLeft, isOnline, mutualConnections, responseRate
    """
    id: int = Field(..., description="User ID")
    name: str = Field(..., description="User display name")
    avatar: Optional[str] = Field(None, description="User avatar URL")
    location: Optional[str] = Field(None, description="User location")
    skills: List[str] = Field(default_factory=list, description="User skills")
    bio: Optional[str] = Field(None, description="User bio/intro")
    matchScore: float = Field(..., ge=0, le=1, description="Match score (0-1)")
    whyMatch: str = Field(..., description="Explanation of why this user matches")
    receivesLeft: Optional[int] = Field(None, description="User's remaining receives")
    isOnline: bool = Field(False, description="Whether user is currently online")
    mutualConnections: int = Field(0, description="Number of mutual connections")
    responseRate: float = Field(0, ge=0, le=1, description="User's response rate")
    
    class Config:
        from_attributes = True


class ChatMessage(BaseModel):
    """Chat message response schema"""
    id: str = Field(..., description="Message UUID")
    session_id: str = Field(..., description="Session UUID")
    message_text: str = Field(..., description="Message content")
    message_type: str = Field(..., description="Message type: 'user' or 'ai'")
    search_query: Optional[str] = Field(None, description="Search query for AI messages")
    search_mode: Optional[str] = Field(None, description="Search mode used")
    quoted_contacts: Optional[List[str]] = Field(None, description="Mentioned contact IDs")
    response_time_ms: Optional[int] = Field(None, description="AI response time in milliseconds")
    confidence_score: Optional[float] = Field(None, ge=0, le=1, description="AI confidence score")
    created_at: datetime = Field(..., description="Message timestamp")
    
    class Config:
        from_attributes = True


class SendMessageResponse(BaseModel):
    """
    Response schema for POST /chat/message matching frontend API
    From frontend docs: { message: ChatMessage, sessionId: string, recommendations?: UserRecommendation[], suggestedQueries?: string[] }
    """
    message: ChatMessage = Field(..., description="The chat message object")
    sessionId: str = Field(..., description="Session ID")
    recommendations: Optional[List[UserRecommendation]] = Field(default_factory=list, description="User recommendations from AI")
    suggestedQueries: Optional[List[str]] = Field(default_factory=list, description="AI-generated follow-up queries")


class ChatHistoryResponse(BaseModel):
    """Response schema for GET /chat/history with pagination"""
    data: List[ChatSession] = Field(..., description="List of chat sessions")
    pagination: dict = Field(..., description="Pagination metadata")
    
    class Config:
        from_attributes = True


class MessageWithRecommendations(BaseModel):
    """Chat message with its recommendations and suggested queries"""
    message: ChatMessage = Field(..., description="The chat message")
    recommendations: List[UserRecommendation] = Field(default_factory=list, description="Message recommendations")
    suggested_queries: List[str] = Field(default_factory=list, description="Suggested follow-up queries")
    
    class Config:
        from_attributes = True


class SessionDetailsResponse(BaseModel):
    """Response schema for GET /chat/session/{sessionId}"""
    session: ChatSession = Field(..., description="Session information")
    messages: List[MessageWithRecommendations] = Field(default_factory=list, description="Session messages with recommendations")
    
    class Config:
        from_attributes = True


# ===== INTERNAL SCHEMAS =====

class MessageRecommendationCreate(BaseModel):
    """Schema for creating message recommendations"""
    message_id: UUID = Field(..., description="Message UUID")
    recommended_user_id: int = Field(..., description="Recommended user ID")
    match_score: Optional[float] = Field(None, ge=0, le=1, description="Match score")
    recommendation_reason: Optional[str] = Field(None, description="Why recommended")


class SuggestedQueryCreate(BaseModel):
    """Schema for creating suggested queries"""
    message_id: UUID = Field(..., description="Message UUID")
    query_text: str = Field(..., min_length=1, max_length=500, description="Suggested query text")


# ===== API RESPONSE WRAPPERS =====

class ChatApiResponse(BaseModel):
    """Standard API response wrapper for chat endpoints"""
    success: bool = Field(True, description="Request success status")
    data: Union[
        SendMessageResponse,
        ChatSession,
        SessionDetailsResponse,
        ChatHistoryResponse,
        dict
    ] = Field(..., description="Response data")
    error: Optional[str] = Field(None, description="Error message if success=false")
    message: Optional[str] = Field(None, description="Success message")


# ===== PAGINATION SCHEMAS =====

class PaginationParams(BaseModel):
    """Common pagination parameters"""
    page: int = Field(1, ge=1, description="Page number")
    limit: int = Field(20, ge=1, le=100, description="Items per page")
    sessionId: Optional[str] = Field(None, description="Filter by session ID")


class PaginationMeta(BaseModel):
    """Pagination metadata"""
    page: int = Field(..., description="Current page number")
    limit: int = Field(..., description="Items per page")
    total: int = Field(..., description="Total number of items")
    totalPages: int = Field(..., description="Total number of pages")


class CreateSessionResponse(BaseModel):
    """Response for creating a new chat session"""
    sessionId: int = Field(..., description="ID of the created session")
    title: str = Field(..., description="Session title")
    createdAt: datetime = Field(..., description="Session creation timestamp")
    
    class Config:
        from_attributes = True


class GetSessionResponse(BaseModel):
    """Response for getting session details"""
    sessionId: int = Field(..., description="Session ID")
    title: str = Field(..., description="Session title")
    messageCount: int = Field(..., description="Number of messages in session")
    createdAt: datetime = Field(..., description="Session creation timestamp")
    lastActivity: datetime = Field(..., description="Last activity timestamp")
    
    class Config:
        from_attributes = True


class ChatMessageWithRecommendations(BaseModel):
    """Chat message with associated recommendations"""
    id: int = Field(..., description="Message ID")
    content: str = Field(..., description="Message content")
    isAiResponse: bool = Field(..., description="Whether this is an AI response")
    timestamp: datetime = Field(..., description="Message timestamp")
    recommendations: List[UserRecommendation] = Field(default_factory=list, description="User recommendations for this message")
    
    class Config:
        from_attributes = True