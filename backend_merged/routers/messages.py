"""
Messages router
Handles chat messages, conversations, and messaging features
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func
from typing import List, Optional
import logging

from dependencies.db import get_db
from models.users import User
from models.messages import Message
from models.matches import Match
from services.auth_service import AuthService
from schemas.messages import (
    MessageSearchResponse, MessageContextResponse, SendMessageRequest,
    MessageResponse, ConversationResponse, DeleteMessageResponse
)

router = APIRouter()
security = HTTPBearer()
logger = logging.getLogger(__name__)
auth_service = AuthService()

@router.get("/conversations")
async def get_conversations(
    token: str = Depends(security),
    db: Session = Depends(get_db)
):
    """Get user's conversations (matches with messages)"""
    current_user = auth_service.get_current_user(db, token.credentials)
    if not current_user:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # Get matches
    matches = db.query(Match).filter(
        (Match.user1_id == current_user.user_id) | (Match.user2_id == current_user.user_id),
        Match.is_active == True
    ).all()
    
    conversations = []
    for match in matches:
        other_user_id = match.user2_id if match.user1_id == current_user.user_id else match.user1_id
        other_user = db.query(User).filter(User.user_id == other_user_id).first()
        
        # Get latest message
        latest_message = db.query(Message).filter(
            Message.match_id == match.match_id
        ).order_by(Message.timestamp.desc()).first()
        
        conversations.append({
            "match_id": match.match_id,
            "user": {
                "id": other_user.user_id,
                "username": other_user.username,
                "display_name": other_user.display_name,
                "avatar_url": other_user.avatar_url
            } if other_user else None,
            "latest_message": {
                "content": latest_message.text if latest_message else None,
                "created_at": latest_message.timestamp if latest_message else None,
                "sender_id": latest_message.sender_id if latest_message else None
            } if latest_message else None,
            "matched_at": match.timestamp
        })
    
    return conversations

@router.get("/{match_id}/messages")
async def get_messages(
    match_id: int,
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0),
    token: str = Depends(security),
    db: Session = Depends(get_db)
):
    """Get messages for a specific match/conversation"""
    current_user = auth_service.get_current_user(db, token.credentials)
    if not current_user:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # Verify user is part of this match
    match = db.query(Match).filter(
        Match.match_id == match_id,
        (Match.user1_id == current_user.user_id) | (Match.user2_id == current_user.user_id)
    ).first()
    
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    
    messages = db.query(Message).filter(
        Message.match_id == match_id
    ).order_by(Message.timestamp.desc()).offset(offset).limit(limit).all()
    
    return [
        {
            "id": msg.message_id,
            "content": msg.text,
            "sender_id": msg.sender_id,
            "created_at": msg.timestamp,
            "message_type": "text"
        }
        for msg in reversed(messages)  # Return in chronological order
    ]

@router.post("/{match_id}/messages")
async def send_message(
    match_id: int,
    message_data: dict,
    token: str = Depends(security),
    db: Session = Depends(get_db)
):
    """Send a message in a conversation"""
    current_user = auth_service.get_current_user(db, token.credentials)
    if not current_user:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # Verify user is part of this match
    match = db.query(Match).filter(
        Match.match_id == match_id,
        (Match.user1_id == current_user.user_id) | (Match.user2_id == current_user.user_id),
        Match.is_active == True
    ).first()
    
    if not match:
        raise HTTPException(status_code=404, detail="Match not found or inactive")
    
    content = message_data.get("content", "").strip()
    if not content:
        raise HTTPException(status_code=400, detail="Message content is required")
    
    # Create message
    message = Message(
        match_id=match_id,
        sender_id=current_user.user_id,
        text=content
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    
    return {
        "id": message.message_id,
        "content": message.text,
        "sender_id": message.sender_id,
        "created_at": message.timestamp,
        "message_type": "text"
    }

@router.delete("/{message_id}")
async def delete_message(
    message_id: int,
    token: str = Depends(security),
    db: Session = Depends(get_db)
):
    """Delete a message (only sender can delete)"""
    current_user = auth_service.get_current_user(db, token.credentials)
    if not current_user:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    message = db.query(Message).filter(
        Message.message_id == message_id,
        Message.sender_id == current_user.user_id
    ).first()
    
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    
    db.delete(message)
    db.commit()
    
    return {"message": "Message deleted successfully"}

@router.get("/{match_id}/search", response_model=MessageSearchResponse)
async def search_messages(
    match_id: int,
    query: str = Query(..., min_length=2, description="Search query (minimum 2 characters)"),
    limit: int = Query(20, le=100, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    token: str = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Search messages within a specific conversation
    Returns messages containing the search query with context
    """
    current_user = auth_service.get_current_user(db, token.credentials)
    if not current_user:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # Verify user is part of this match
    match = db.query(Match).filter(
        Match.match_id == match_id,
        or_(Match.user1_id == current_user.user_id, Match.user2_id == current_user.user_id)
    ).first()
    
    if not match:
        raise HTTPException(status_code=404, detail="Match not found or access denied")
    
    # Search messages containing the query (case-insensitive)
    search_filter = func.lower(Message.text).contains(func.lower(query))
    
    # Get total count for pagination
    total_count = db.query(Message).filter(
        Message.match_id == match_id,
        search_filter
    ).count()
    
    # Get search results ordered by most recent first
    messages = db.query(Message).filter(
        Message.match_id == match_id,
        search_filter
    ).order_by(Message.timestamp.desc()).offset(offset).limit(limit).all()
    
    # Format results with sender information
    results = []
    for message in messages:
        sender = db.query(User).filter(User.user_id == message.sender_id).first()
        results.append({
            "message_id": message.message_id,
            "content": message.text,
            "sender": {
                "id": sender.user_id,
                "username": sender.username,
                "display_name": sender.display_name,
                "avatar_url": sender.avatar_url
            } if sender else None,
            "timestamp": message.timestamp,
            "is_read": message.is_read,
            "match_id": message.match_id
        })
    
    return {
        "query": query,
        "results": results,
        "total_count": total_count,
        "limit": limit,
        "offset": offset,
        "has_more": total_count > offset + limit
    }

@router.get("/search/global", response_model=MessageSearchResponse)
async def search_all_messages(
    query: str = Query(..., min_length=2, description="Search query (minimum 2 characters)"),
    limit: int = Query(20, le=100, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    token: str = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Search messages across all user's conversations
    Returns messages containing the search query from all accessible matches
    """
    current_user = auth_service.get_current_user(db, token.credentials)
    if not current_user:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # Get all matches for the current user
    user_matches = db.query(Match).filter(
        or_(Match.user1_id == current_user.user_id, Match.user2_id == current_user.user_id),
        Match.is_active == True
    ).all()
    
    match_ids = [match.match_id for match in user_matches]
    
    if not match_ids:
        return {
            "query": query,
            "results": [],
            "total_count": 0,
            "limit": limit,
            "offset": offset,
            "has_more": False
        }
    
    # Search messages containing the query across all user's matches
    search_filter = and_(
        Message.match_id.in_(match_ids),
        func.lower(Message.text).contains(func.lower(query))
    )
    
    # Get total count for pagination
    total_count = db.query(Message).filter(search_filter).count()
    
    # Get search results ordered by most recent first
    messages = db.query(Message).filter(search_filter).order_by(
        Message.timestamp.desc()
    ).offset(offset).limit(limit).all()
    
    # Format results with sender and match information
    results = []
    for message in messages:
        sender = db.query(User).filter(User.user_id == message.sender_id).first()
        match = db.query(Match).filter(Match.match_id == message.match_id).first()
        
        # Get the other user in the match
        other_user_id = match.user2_id if match.user1_id == current_user.user_id else match.user1_id
        other_user = db.query(User).filter(User.user_id == other_user_id).first()
        
        results.append({
            "message_id": message.message_id,
            "content": message.text,
            "sender": {
                "id": sender.user_id,
                "username": sender.username,
                "display_name": sender.display_name,
                "avatar_url": sender.avatar_url
            } if sender else None,
            "match": {
                "id": match.match_id,
                "other_user": {
                    "id": other_user.user_id,
                    "username": other_user.username,
                    "display_name": other_user.display_name,
                    "avatar_url": other_user.avatar_url
                } if other_user else None
            },
            "timestamp": message.timestamp,
            "is_read": message.is_read
        })
    
    return {
        "query": query,
        "results": results,
        "total_count": total_count,
        "limit": limit,
        "offset": offset,
        "has_more": total_count > offset + limit
    }

@router.get("/{match_id}/message/{message_id}/context", response_model=MessageContextResponse)
async def get_message_context(
    match_id: int,
    message_id: int,
    before: int = Query(5, ge=0, le=20, description="Number of messages before the target message"),
    after: int = Query(5, ge=0, le=20, description="Number of messages after the target message"),
    token: str = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Get context around a specific message (useful for "jump to message" functionality)
    Returns messages before and after the target message for context
    """
    current_user = auth_service.get_current_user(db, token.credentials)
    if not current_user:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # Verify user is part of this match
    match = db.query(Match).filter(
        Match.match_id == match_id,
        or_(Match.user1_id == current_user.user_id, Match.user2_id == current_user.user_id)
    ).first()
    
    if not match:
        raise HTTPException(status_code=404, detail="Match not found or access denied")
    
    # Get the target message
    target_message = db.query(Message).filter(
        Message.message_id == message_id,
        Message.match_id == match_id
    ).first()
    
    if not target_message:
        raise HTTPException(status_code=404, detail="Message not found")
    
    # Get messages before the target message
    messages_before = db.query(Message).filter(
        Message.match_id == match_id,
        Message.timestamp < target_message.timestamp
    ).order_by(Message.timestamp.desc()).limit(before).all()
    
    # Get messages after the target message
    messages_after = db.query(Message).filter(
        Message.match_id == match_id,
        Message.timestamp > target_message.timestamp
    ).order_by(Message.timestamp.asc()).limit(after).all()
    
    # Format all messages
    def format_message(msg):
        sender = db.query(User).filter(User.user_id == msg.sender_id).first()
        return {
            "message_id": msg.message_id,
            "content": msg.text,
            "sender": {
                "id": sender.user_id,
                "username": sender.username,
                "display_name": sender.display_name,
                "avatar_url": sender.avatar_url
            } if sender else None,
            "timestamp": msg.timestamp,
            "is_read": msg.is_read,
            "is_target": msg.message_id == message_id
        }
    
    # Combine and sort all messages
    all_messages = messages_before[::-1] + [target_message] + messages_after
    formatted_messages = [format_message(msg) for msg in all_messages]
    
    return {
        "target_message_id": message_id,
        "context_messages": formatted_messages,
        "total_context": len(formatted_messages)
    }
