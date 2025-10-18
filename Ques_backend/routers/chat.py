"""
Chat API Router - AI-powered chat system with user recommendations

Provides endpoints for chat sessions and AI-powered user discovery.
Integrates with the user recommendation system to return user cards
based on AI conversation context.

Endpoints align with frontend API documentation section 7.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime

from dependencies.db import get_db
from dependencies.auth import get_current_user
from models.users import User
from models.chat import ChatSession, ChatMessage, MessageRecommendation, SuggestedQuery
from schemas.chat import (
    SendMessageRequest,
    SendMessageResponse,
    UserRecommendation,
    CreateSessionRequest,
    CreateSessionResponse,
    GetSessionResponse,
    ChatSession,
    ChatMessage,
    ChatHistoryResponse,
    SessionDetailsResponse,
    ChatMessageWithRecommendations
)
from services.intelligent_user_search import get_search_service

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/message", response_model=SendMessageResponse)
async def send_message(
    request: SendMessageRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Send a message to AI and receive response with user recommendations.
    
    This endpoint processes the user's message, generates an AI response,
    and returns a batch of recommended users as cards that match the
    conversation context.
    
    Returns:
        - AI response message
        - Array of user recommendations (UserRecommendation[])
        - Suggested follow-up queries
    """
    try:
        # Get or create chat session
        session = None
        if request.session_id:
            session = db.query(ChatSession).filter(
                ChatSession.id == request.session_id,
                ChatSession.user_id == current_user.id
            ).first()
            
            if not session:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Chat session not found"
                )
        else:
            # Create new session
            session = ChatSession(
                user_id=current_user.id,
                title=request.message[:50] + "..." if len(request.message) > 50 else request.message,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.add(session)
            db.flush()  # Get the ID

        # Save user message
        user_message = ChatMessage(
            session_id=session.id,
            content=request.message,
            is_ai_response=False,
            timestamp=datetime.utcnow()
        )
        db.add(user_message)
        db.flush()

        # AI-powered user search and response generation
        search_service = await get_search_service()
        
        # Get current user context for personalized search
        current_user_context = {
            "name": current_user.name or f"User {current_user.id}",
            "skills": [],  # TODO: Get from user profile
            "bio": current_user.bio if hasattr(current_user, 'bio') else ""
        }
        
        # Perform intelligent user search
        search_results = await search_service.search_users(
            query=request.message,
            current_user_id=current_user.id,
            current_user_context=current_user_context
        )
        
        # Generate AI response based on search results
        recommendations_count = len(search_results.get("recommendations", []))
        intent = search_results.get("search_metadata", {}).get("intent", "search")
        
        if intent == "search" and recommendations_count > 0:
            ai_response_text = f"I found {recommendations_count} great matches for your search! Here are users I think would be perfect connections for you based on your interests and goals."
        elif intent == "search" and recommendations_count == 0:
            ai_response_text = "I couldn't find any exact matches for your search, but let me help you refine your criteria. Try being more specific about the skills or interests you're looking for."
        else:
            ai_response_text = f"I understand you're asking about: '{request.message}'. While I'm designed to help you find great people to connect with, I can also have conversations! What would you like to know?"
        
        # Save AI response message
        ai_message = ChatMessage(
            session_id=session.id,
            content=ai_response_text,
            is_ai_response=True,
            timestamp=datetime.utcnow()
        )
        db.add(ai_message)
        db.flush()

        # Get recommended user IDs and create recommendation batch
        recommended_user_ids = search_results.get("user_ids", [])
        
        if recommended_user_ids:
            recommendation_batch = MessageRecommendation(
                message_id=ai_message.id,
                recommended_user_ids=recommended_user_ids,
                batch_id=str(uuid.uuid4()),
                search_context=request.message,
                total_found=len(recommended_user_ids),
                created_at=datetime.utcnow()
            )
            db.add(recommendation_batch)

        # Build user recommendation cards from search results
        user_recommendations = await build_user_recommendation_cards_from_search(
            search_recommendations=search_results.get("recommendations", []),
            context_user_id=current_user.id,
            db=db
        )

        # Get AI-generated suggested queries
        suggested_queries = search_results.get("suggested_queries", [
            "Tell me more about users who share my interests",
            "Find people in my area",
            "Show me users with similar goals"
        ])

        # Save suggested queries
        for query_text in suggested_queries:
            suggested_query = SuggestedQuery(
                message_id=ai_message.id,
                query_text=query_text,
                created_at=datetime.utcnow()
            )
            db.add(suggested_query)

        # Update session timestamp
        session.updated_at = datetime.utcnow()
        
        db.commit()

        return SendMessageResponse(
            message=ai_response_text,
            recommendations=user_recommendations,
            suggestedQueries=suggested_queries,
            sessionId=session.id
        )

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing message: {str(e)}"
        )


@router.post("/session", response_model=CreateSessionResponse)
async def create_session(
    request: CreateSessionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new chat session.
    
    Args:
        request: Session creation request with optional title
        
    Returns:
        New session ID and details
    """
    try:
        session = ChatSession(
            user_id=current_user.id,
            title=request.title or "New Chat",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.add(session)
        db.commit()
        db.refresh(session)
        
        return CreateSessionResponse(
            sessionId=session.id,
            title=session.title,
            createdAt=session.created_at
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating session: {str(e)}"
        )


@router.get("/session/{session_id}", response_model=GetSessionResponse)
async def get_session_details(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a specific chat session.
    
    Args:
        session_id: ID of the session to retrieve
        
    Returns:
        Session details with message count and latest activity
    """
    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found"
        )
    
    # Get message count
    message_count = db.query(ChatMessage).filter(
        ChatMessage.session_id == session_id
    ).count()
    
    return GetSessionResponse(
        sessionId=session.id,
        title=session.title,
        messageCount=message_count,
        createdAt=session.created_at,
        lastActivity=session.updated_at
    )


@router.get("/session/{session_id}/history", response_model=ChatHistoryResponse)
async def get_chat_history(
    session_id: int,
    limit: Optional[int] = 50,
    offset: Optional[int] = 0,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get chat history for a session with pagination.
    
    Args:
        session_id: ID of the session
        limit: Maximum number of messages to return (default: 50)
        offset: Number of messages to skip for pagination (default: 0)
        
    Returns:
        List of messages with recommendations and metadata
    """
    # Verify session ownership
    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found"
        )
    
    # Get messages with pagination
    messages = db.query(ChatMessage).filter(
        ChatMessage.session_id == session_id
    ).order_by(ChatMessage.timestamp).offset(offset).limit(limit).all()
    
    # Build response with recommendations
    message_list = []
    for message in messages:
        message_data = ChatMessageWithRecommendations(
            id=message.id,
            content=message.content,
            isAiResponse=message.is_ai_response,
            timestamp=message.timestamp,
            recommendations=[]
        )
        
        # Add recommendations for AI messages
        if message.is_ai_response and message.recommendations:
            user_recommendations = await build_user_recommendation_cards(
                user_ids=message.recommendations.recommended_user_ids,
                context_user_id=current_user.id,
                db=db
            )
            message_data.recommendations = user_recommendations
        
        message_list.append(message_data)
    
    total_messages = db.query(ChatMessage).filter(
        ChatMessage.session_id == session_id
    ).count()
    
    return ChatHistoryResponse(
        sessionId=session_id,
        messages=message_list,
        totalMessages=total_messages,
        hasMore=offset + limit < total_messages
    )


@router.delete("/session/{session_id}")
async def delete_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a chat session and all associated messages.
    
    Args:
        session_id: ID of the session to delete
        
    Returns:
        Success confirmation
    """
    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found"
        )
    
    try:
        db.delete(session)
        db.commit()
        
        return {"message": "Chat session deleted successfully"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting session: {str(e)}"
        )


# Helper functions

async def build_user_recommendation_cards_from_search(
    search_recommendations: List[Dict[str, Any]],
    context_user_id: int,
    db: Session
) -> List[UserRecommendation]:
    """
    Build UserRecommendation cards from intelligent search results.
    
    Args:
        search_recommendations: List of recommendation dicts from search service
        context_user_id: Current user ID for context
        db: Database session
        
    Returns:
        List of UserRecommendation objects
    """
    if not search_recommendations:
        return []
    
    recommendations = []
    
    for rec in search_recommendations:
        user_id = rec.get('user_id')
        if not user_id:
            continue
            
        # Get additional user data from database if needed
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            continue
        
        # TODO: Calculate actual online status, mutual connections, response rate
        # For now using search data + basic database info
        
        recommendation = UserRecommendation(
            userId=user_id,
            name=rec.get('name') or user.name or f"User {user_id}",
            age=user.age if hasattr(user, 'age') else None,
            bio=rec.get('bio') or (user.bio if hasattr(user, 'bio') else ""),
            profilePicture=user.profile_picture_url if hasattr(user, 'profile_picture_url') else None,
            matchScore=min(max(rec.get('match_score', 0.5), 0.0), 1.0),  # Ensure 0-1 range
            whyMatch=rec.get('why_match', 'AI-powered match based on your interests'),
            isOnline=False,  # TODO: Implement real-time online status
            mutualConnections=0  # TODO: Calculate actual mutual connections
        )
        recommendations.append(recommendation)
    
    return recommendations


async def get_recommended_users(
    user_id: int,
    context: str,
    db: Session,
    limit: int = 10
) -> List[int]:
    """
    Get recommended user IDs (fallback method for non-AI searches).
    
    Args:
        user_id: Current user ID
        context: Search context
        db: Database session
        limit: Maximum number of users to recommend
        
    Returns:
        List of recommended user IDs
    """
    # Simple fallback - get random active users excluding current user
    users = db.query(User.id).filter(
        User.id != user_id,
        User.is_active == True
    ).limit(limit).all()
    
    return [user.id for user in users]


async def build_user_recommendation_cards(
    user_ids: List[int],
    context_user_id: int,
    db: Session
) -> List[UserRecommendation]:
    """
    Build UserRecommendation cards from user IDs (fallback method).
    
    Args:
        user_ids: List of user IDs to build cards for
        context_user_id: Current user ID for context
        db: Database session
        
    Returns:
        List of UserRecommendation objects
    """
    if not user_ids:
        return []
    
    users = db.query(User).filter(User.id.in_(user_ids)).all()
    recommendations = []
    
    for user in users:
        recommendation = UserRecommendation(
            userId=user.id,
            name=user.name or f"User {user.id}",
            age=user.age if hasattr(user, 'age') else None,
            bio=user.bio if hasattr(user, 'bio') else "",
            profilePicture=user.profile_picture_url if hasattr(user, 'profile_picture_url') else None,
            matchScore=0.75,  # Default score for fallback recommendations
            whyMatch="Suggested based on your profile and preferences",
            isOnline=False,  # TODO: Implement real-time online status
            mutualConnections=0  # TODO: Calculate actual mutual connections
        )
        recommendations.append(recommendation)
    
    return recommendations