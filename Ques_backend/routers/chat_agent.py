"""
Chat Mechanism System with Intent Detection and Service Routing
Based on SearchAgent algorithm from intelligent_search_original.py
Routes users to appropriate services based on GLM-4 LLM intent analysis
"""

import json
import os
from typing import Dict, List, Optional, Any
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field

# Import services and dependencies
from services.intention_detection import IntentionDetector, IntentionType, IntentionResult
from dependencies.auth import get_current_user
from models.casual_requests import CasualRequest
from routers.casual_requests import get_my_casual_request, search_casual_requests
from schemas.casual_requests import CasualRequestCreate

# Chat request/response schemas
class ChatMessage(BaseModel):
    message: str = Field(..., description="User's chat message")
    context: Optional[Dict] = Field(None, description="Additional context or referenced user info")

class ChatResponse(BaseModel):
    response_type: str = Field(..., description="Type of response: search_result, casual_match, inquiry_answer, chat_reply")
    content: str = Field(..., description="Main response content")
    intent: str = Field(..., description="Detected user intent")
    confidence: float = Field(..., description="Confidence score of intent detection")
    actions: Optional[List[Dict]] = Field(None, description="Suggested actions for the user")
    data: Optional[Dict] = Field(None, description="Additional structured data")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())

class SearchResult(BaseModel):
    users: List[Dict] = Field(..., description="Matching users")
    total_count: int = Field(..., description="Total matching users")
    search_query: str = Field(..., description="Processed search query")
    filters_applied: Dict = Field(..., description="Applied search filters")

class CasualMatch(BaseModel):
    matches: List[Dict] = Field(..., description="Casual activity matches")
    user_request: Optional[Dict] = Field(None, description="User's current request")
    suggestions: List[str] = Field(..., description="Activity suggestions")

router = APIRouter(prefix="/chat", tags=["chat"])

class ChatAgent:
    """
    Main chat agent that handles intent detection and service routing
    Based on SearchAgent from intelligent_search_original.py
    """
    
    def __init__(self):
        """Initialize chat agent with GLM-4 powered intention detector"""
        self.intention_detector = IntentionDetector()
        self.stats = {
            "total_messages": 0,
            "search_requests": 0,
            "casual_requests": 0,
            "inquiry_requests": 0,
            "chat_requests": 0
        }
        print(f"🤖 ChatAgent initialized with GLM-4 support: {self.intention_detector.has_llm}")
    
    async def process_message(
        self, 
        message: str, 
        current_user: Dict,
        context: Optional[Dict] = None
    ) -> ChatResponse:
        """
        Process user message and route to appropriate service
        
        Args:
            message: User's message
            current_user: Current authenticated user
            context: Additional context (referenced users, etc.)
            
        Returns:
            ChatResponse with appropriate service response
        """
        self.stats["total_messages"] += 1
        
        # Step 1: Detect user intent using GLM-4
        referenced_user = context.get("referenced_user") if context else None
        intent_result = self.intention_detector.analyze_user_intent(
            user_input=message,
            referenced_user=referenced_user,
            current_user=current_user
        )
        
        print(f"🎯 Intent detected: {intent_result.intention.value} (confidence: {intent_result.confidence:.2f})")
        print(f"📝 Reasoning: {intent_result.reasoning}")
        
        # Step 2: Route to appropriate service based on intent
        try:
            if intent_result.intention == IntentionType.SEARCH:
                return await self._handle_search_request(message, current_user, intent_result)
            elif intent_result.intention == IntentionType.CASUAL:
                return await self._handle_casual_request(message, current_user, intent_result)
            elif intent_result.intention == IntentionType.INQUIRY:
                return await self._handle_inquiry_request(message, current_user, referenced_user, intent_result)
            else:
                return self._handle_general_chat(message, current_user, intent_result)
                
        except Exception as e:
            print(f"❌ Service routing failed: {e}")
            return ChatResponse(
                response_type="error",
                content=f"Sorry, I encountered an error processing your request: {str(e)}",
                intent=intent_result.intention.value,
                confidence=intent_result.confidence,
                actions=[{"type": "retry", "label": "Try again"}]
            )
    
    async def _handle_search_request(
        self, 
        message: str, 
        current_user: Dict, 
        intent_result: IntentionResult
    ) -> ChatResponse:
        """Handle search requests - find people/activities"""
        self.stats["search_requests"] += 1
        
        # TODO: Implement user search functionality
        # This would integrate with vector database and user matching
        
        # For now, provide a structured response
        return ChatResponse(
            response_type="search_result",
            content=f"I understand you're looking for: {message}. Let me search for relevant people or activities.",
            intent="search",
            confidence=intent_result.confidence,
            actions=[
                {"type": "refine_search", "label": "Refine search criteria"},
                {"type": "view_profiles", "label": "View matching profiles"},
                {"type": "save_search", "label": "Save this search"}
            ],
            data={
                "search_query": message,
                "reasoning": intent_result.reasoning,
                "status": "processing"
            }
        )
    
    async def _handle_casual_request(
        self, 
        message: str, 
        current_user: Dict, 
        intent_result: IntentionResult
    ) -> ChatResponse:
        """Handle casual requests - social activities and greetings"""
        self.stats["casual_requests"] += 1
        
        # Check if user is looking for activities or just casual chat
        activity_keywords = ['partner', 'buddy', 'activity', 'join', 'together', 'meet']
        is_activity_request = any(keyword in message.lower() for keyword in activity_keywords)
        
        if is_activity_request:
            # Route to casual requests system
            try:
                # Check user's current casual request
                from routers.casual_requests import get_my_casual_request
                # This would need to be adapted for direct function call
                
                return ChatResponse(
                    response_type="casual_match",
                    content="I see you're interested in activities! Let me help you find or create activity requests.",
                    intent="casual",
                    confidence=intent_result.confidence,
                    actions=[
                        {"type": "create_request", "label": "Create activity request"},
                        {"type": "browse_activities", "label": "Browse available activities"},
                        {"type": "join_activity", "label": "Join existing activity"}
                    ],
                    data={
                        "activity_type": "general",
                        "reasoning": intent_result.reasoning
                    }
                )
                
            except Exception as e:
                print(f"Casual request handling error: {e}")
        
        # Handle general casual conversation
        return ChatResponse(
            response_type="chat_reply",
            content=self._generate_casual_response(message, current_user),
            intent="casual",
            confidence=intent_result.confidence,
            actions=[
                {"type": "explore_features", "label": "Explore app features"},
                {"type": "find_activities", "label": "Find activities"}
            ]
        )
    
    async def _handle_inquiry_request(
        self, 
        message: str, 
        current_user: Dict,
        referenced_user: Optional[Dict],
        intent_result: IntentionResult
    ) -> ChatResponse:
        """Handle inquiry requests - questions about users or system"""
        self.stats["inquiry_requests"] += 1
        
        if referenced_user:
            # User is asking about a specific person
            return ChatResponse(
                response_type="inquiry_answer",
                content=f"Based on the user profile, I can provide insights about their background and compatibility.",
                intent="inquiry",
                confidence=intent_result.confidence,
                actions=[
                    {"type": "view_full_profile", "label": "View full profile"},
                    {"type": "contact_user", "label": "Send connection request"},
                    {"type": "compare_compatibility", "label": "Check compatibility"}
                ],
                data={
                    "referenced_user": referenced_user,
                    "inquiry_type": "user_profile",
                    "reasoning": intent_result.reasoning
                }
            )
        else:
            # General inquiry about the system or features
            return ChatResponse(
                response_type="inquiry_answer", 
                content=self._generate_system_info_response(message),
                intent="inquiry",
                confidence=intent_result.confidence,
                actions=[
                    {"type": "learn_more", "label": "Learn more"},
                    {"type": "get_help", "label": "Get help"},
                    {"type": "contact_support", "label": "Contact support"}
                ]
            )
    
    def _handle_general_chat(
        self, 
        message: str, 
        current_user: Dict, 
        intent_result: IntentionResult
    ) -> ChatResponse:
        """Handle general chat when intent is unclear"""
        self.stats["chat_requests"] += 1
        
        return ChatResponse(
            response_type="chat_reply",
            content="I'm here to help! You can search for people, find activities, or ask questions. What would you like to do?",
            intent="chat",
            confidence=intent_result.confidence,
            actions=[
                {"type": "find_people", "label": "Find people"},
                {"type": "discover_activities", "label": "Discover activities"}, 
                {"type": "ask_question", "label": "Ask a question"}
            ],
            data={
                "suggestions": [
                    "Try: 'Looking for hiking partners'",
                    "Try: 'What activities are available?'", 
                    "Try: 'Tell me about user profiles'"
                ]
            }
        )
    
    def _generate_casual_response(self, message: str, current_user: Dict) -> str:
        """Generate friendly casual response"""
        casual_responses = {
            "hello": f"Hello {current_user.get('name', 'there')}! How can I help you today?",
            "hi": f"Hi {current_user.get('name', 'there')}! What would you like to explore?", 
            "thanks": "You're welcome! Is there anything else I can help you with?",
            "good": "That's great to hear! How can I assist you further?"
        }
        
        message_lower = message.lower()
        for key, response in casual_responses.items():
            if key in message_lower:
                return response
                
        return f"Nice to chat with you, {current_user.get('name', 'there')}! How can I help?"
    
    def _generate_system_info_response(self, message: str) -> str:
        """Generate informative response about system features"""
        if any(word in message.lower() for word in ['how', 'work', 'use']):
            return "This app helps you connect with people for activities, work, or socializing. You can search for specific types of people, create activity requests, or browse what others are looking for."
        elif any(word in message.lower() for word in ['feature', 'can', 'do']):
            return "Key features include: people search, activity matching, profile browsing, and smart recommendations. You can find study partners, workout buddies, project collaborators, or social activities."
        else:
            return "I'm here to help you navigate the app and connect with the right people. What specific information would you like to know?"
    
    def get_stats(self) -> Dict:
        """Get chat agent statistics"""
        return {
            **self.stats,
            "intention_detector_stats": self.intention_detector.get_statistics()
        }

# Initialize global chat agent
chat_agent = ChatAgent()

# API Endpoints
@router.post("/message", response_model=ChatResponse)
async def send_message(
    chat_message: ChatMessage,
    current_user: Dict = Depends(get_current_user)
):
    """
    Main chat endpoint - processes user messages and routes to appropriate services
    
    This endpoint:
    1. Analyzes user intent using GLM-4 LLM
    2. Routes to search, casual requests, or inquiry services
    3. Returns structured response with actions and data
    """
    try:
        response = await chat_agent.process_message(
            message=chat_message.message,
            current_user=current_user,
            context=chat_message.context
        )
        return response
        
    except Exception as e:
        print(f"❌ Chat processing error: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to process chat message: {str(e)}"
        )

@router.get("/stats")
async def get_chat_stats(current_user: Dict = Depends(get_current_user)):
    """Get chat system statistics"""
    return chat_agent.get_stats()

@router.post("/test-intent")
async def test_intent_detection(
    message: dict,
    current_user: Dict = Depends(get_current_user)
):
    """Test intent detection without full processing"""
    user_message = message.get("message", "")
    
    intent_result = chat_agent.intention_detector.analyze_user_intent(
        user_input=user_message,
        current_user=current_user
    )
    
    return {
        "message": user_message,
        "detected_intent": intent_result.intention.value,
        "confidence": intent_result.confidence,
        "reasoning": intent_result.reasoning,
        "clarification_needed": intent_result.clarification_needed,
        "uncertainty_reason": intent_result.uncertainty_reason
    }

# Health check for GLM-4 integration
@router.get("/health")
async def chat_system_health():
    """Check chat system health including GLM-4 availability"""
    return {
        "status": "healthy",
        "glm4_available": chat_agent.intention_detector.has_llm,
        "total_processed": chat_agent.stats["total_messages"],
        "timestamp": datetime.now().isoformat()
    }
