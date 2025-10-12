"""
Intelligent Agent API Router
Provides AI-powered interactions with 3 paths: Search, Inquiry, Chat
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import os
import logging

from dependencies.auth import get_current_user
from services.intelligent_search.intelligent_search_agent import SearchAgent
from services.intelligent_search.tencent_vectordb_adapter import TencentVectorDBAdapter

# Setup logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v1/intelligent", tags=["Intelligent Agent"])

# Pydantic models for request/response
class IntelligentConversationRequest(BaseModel):
    """Request model for intelligent conversation"""
    user_input: str = Field(..., description="User's natural language input")
    referenced_ids: Optional[List[str]] = Field(None, description="List of user IDs being referenced (for inquiry mode)")
    viewed_user_ids: Optional[List[str]] = Field(None, description="List of already viewed user IDs to exclude from search")
    
    class Config:
        schema_extra = {
            "example": {
                "user_input": "find me a student based in shenzhen who have interest in developing mobile apps",
                "referenced_ids": None,
                "viewed_user_ids": []
            }
        }


class SearchResultUser(BaseModel):
    """User result in search response"""
    user_id: str
    name: str
    avatar_url: Optional[str]
    location: Optional[str]
    role: Optional[str]
    skills: Optional[List[str]]
    interests: Optional[List[str]]
    bio: Optional[str]
    match_score: float
    match_reason: str


class SearchResponse(BaseModel):
    """Response for search intent"""
    type: str = "search_results"
    intent: str = "search"
    query_understanding: str
    total_results: int
    results: List[SearchResultUser]
    search_strategy: str
    language: str
    processing_time: float


class InquiryResponse(BaseModel):
    """Response for inquiry intent"""
    type: str = "inquiry_response"
    intent: str = "inquiry"
    user_input: str
    referenced_user: Dict[str, Any]
    answer: str
    analysis: str
    suggestions: Optional[List[str]]
    language: str
    processing_time: float


class ChatResponse(BaseModel):
    """Response for chat intent"""
    type: str = "chat_response"
    intent: str = "chat"
    user_input: str
    response: str
    clarification_needed: bool = False
    suggestions: Optional[List[str]]
    language: str
    processing_time: float


class IntentAnalysisResponse(BaseModel):
    """Response for intent analysis only"""
    intent: str = Field(..., description="Detected intent: search, inquiry, or chat")
    confidence: float = Field(..., description="Confidence score (0-1)")
    reasoning: str = Field(..., description="Explanation of why this intent was detected")
    clarification_needed: bool = Field(False, description="Whether user input needs clarification")
    uncertainty_reason: Optional[str] = Field(None, description="Reason for uncertainty")


# Global search agent instance (initialized lazily)
_search_agent: Optional[SearchAgent] = None


def get_search_agent() -> SearchAgent:
    """
    Get or create the global search agent instance
    """
    global _search_agent
    
    if _search_agent is None:
        # Get environment variables
        glm_api_key = os.getenv("GLM_API_KEY")
        if not glm_api_key:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="GLM_API_KEY not configured"
            )
        
        # Initialize Tencent VectorDB adapter
        try:
            vectordb_adapter = TencentVectorDBAdapter(
                url=os.getenv("TENCENT_VECTORDB_URL", "http://lb-beofq7pb-lf9vj28fmr5hnf4m.clb.ap-guangzhou.tencentclb.com:20000"),
                username=os.getenv("TENCENT_VECTORDB_USERNAME", "root"),
                key=os.getenv("TENCENT_VECTORDB_KEY", "CiNRD4rMCEJVSjUYqr9w3hYvdOVFMUF8p60R2xr2"),
                database_name="intelligent_search",
                collection_name="user_vectors_1024",
                timeout=30
            )
            logger.info("✅ TencentVectorDB adapter initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize TencentVectorDB: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to initialize vector database: {str(e)}"
            )
        
        # Create search agent
        try:
            _search_agent = SearchAgent(
                glm_api_key=glm_api_key,
                vectordb_adapter=vectordb_adapter,
                collection_name="user_vectors_1024",
                glm_model="glm-4-flash",
                api_base_url=os.getenv("API_BASE_URL", "http://localhost:8000")
            )
            logger.info("✅ SearchAgent initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize SearchAgent: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to initialize search agent: {str(e)}"
            )
    
    return _search_agent


@router.post("/conversation", response_model=Dict[str, Any])
async def intelligent_conversation(
    request: IntelligentConversationRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Main entry point for intelligent agent interaction
    
    Automatically detects intent and routes to:
    - **Search**: Find matching users based on criteria
    - **Inquiry**: Answer questions about specific users
    - **Chat**: General conversation and guidance
    
    **Examples:**
    
    Search: "find me a student in shenzhen interested in AI"
    
    Inquiry: "tell me more about this user" (with referenced_ids)
    
    Chat: "how does this platform work?"
    """
    try:
        agent = get_search_agent()
        
        # Call the unified intelligent_conversation method
        result = await agent.intelligent_conversation(
            user_input=request.user_input,
            user_id=str(current_user.get("id")),
            referenced_ids=request.referenced_ids,
            viewed_user_ids=request.viewed_user_ids
        )
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Intelligent conversation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process request: {str(e)}"
        )


@router.post("/search", response_model=Dict[str, Any])
async def intelligent_search(
    request: IntelligentConversationRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Direct search endpoint (bypasses intent detection)
    
    Use this when you know the user wants to search for people.
    
    **Example:**
    ```json
    {
        "user_input": "find students in shenzhen who want to build mobile apps",
        "viewed_user_ids": ["123", "456"]
    }
    ```
    """
    try:
        agent = get_search_agent()
        
        # Fetch current user details
        from sqlalchemy.orm import Session
        from dependencies.db import get_db
        from models.users import User, UserProfile
        
        db: Session = next(get_db())
        try:
            user = db.query(User).filter(User.id == int(current_user.get("id"))).first()
            current_user_info = None
            if user and user.profile:
                current_user_info = {
                    "id": str(user.id),
                    "name": user.profile.name or "Unknown",
                    "role": user.profile.role,
                    "skills": user.profile.skills or [],
                    "interests": user.profile.interests or [],
                    "bio": user.profile.bio or "",
                    "demands": user.profile.demands or "",
                    "goals": user.profile.goals or ""
                }
        finally:
            db.close()
        
        # Call intelligent_search directly
        result = await agent.intelligent_search(
            user_query=request.user_input,
            current_user=current_user_info,
            referenced_users=None,
            viewed_user_ids=request.viewed_user_ids
        )
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Intelligent search failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}"
        )


@router.post("/analyze-intent", response_model=IntentAnalysisResponse)
async def analyze_intent(
    request: IntelligentConversationRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Analyze user input to determine intent without executing the action
    
    Useful for UI/UX to show appropriate interface before processing.
    
    **Returns:**
    - intent: "search", "inquiry", or "chat"
    - confidence: 0.0 to 1.0
    - reasoning: explanation of detected intent
    """
    try:
        agent = get_search_agent()
        
        # Fetch referenced users if provided
        referenced_users = None
        if request.referenced_ids:
            from sqlalchemy.orm import Session
            from dependencies.db import get_db
            from models.users import User, UserProfile
            
            db: Session = next(get_db())
            try:
                users = db.query(User).join(UserProfile).filter(
                    User.id.in_([int(uid) for uid in request.referenced_ids])
                ).all()
                
                referenced_users = []
                for user in users:
                    if user.profile:
                        referenced_users.append({
                            "id": str(user.id),
                            "name": user.profile.name or "Unknown",
                            "role": user.profile.role,
                            "skills": user.profile.skills or [],
                            "interests": user.profile.interests or [],
                            "bio": user.profile.bio or ""
                        })
            finally:
                db.close()
        
        # Analyze intent
        intent_result = agent.analyze_user_intent(
            user_input=request.user_input,
            referenced_user=referenced_users[0] if referenced_users else None,
            current_user=None  # Not needed for intent analysis
        )
        
        return IntentAnalysisResponse(**intent_result)
        
    except Exception as e:
        logger.error(f"❌ Intent analysis failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Intent analysis failed: {str(e)}"
        )


@router.get("/stats")
async def get_agent_stats(current_user: dict = Depends(get_current_user)):
    """
    Get search agent statistics
    
    Returns performance metrics and usage statistics.
    """
    try:
        agent = get_search_agent()
        stats = agent.get_search_stats()
        
        return {
            "stats": stats,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to get stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve statistics: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """
    Health check for intelligent agent service
    
    No authentication required.
    """
    try:
        agent = get_search_agent()
        
        return {
            "status": "healthy",
            "service": "intelligent_agent",
            "vector_db": "connected",
            "llm": "connected",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"❌ Health check failed: {e}")
        return {
            "status": "unhealthy",
            "service": "intelligent_agent",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
