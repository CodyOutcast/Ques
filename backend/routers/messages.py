"""
Messages router
Handles chat messages, conversations, and messaging features
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from typing import List
import logging

from dependencies.db import get_db
from models.users import User
from models.messages import Message
from models.matches import Match
from services.auth_service import AuthService

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
        (Match.user1_id == current_user.id) | (Match.user2_id == current_user.id),
        Match.status == "active"
    ).all()
    
    conversations = []
    for match in matches:
        other_user_id = match.user2_id if match.user1_id == current_user.id else match.user1_id
        other_user = db.query(User).filter(User.id == other_user_id).first()
        
        # Get latest message
        latest_message = db.query(Message).filter(
            Message.match_id == match.id
        ).order_by(Message.created_at.desc()).first()
        
        conversations.append({
            "match_id": match.id,
            "user": {
                "id": other_user.id,
                "username": other_user.username,
                "display_name": other_user.display_name,
                "avatar_url": other_user.avatar_url
            },
            "latest_message": {
                "content": latest_message.content if latest_message else None,
                "created_at": latest_message.created_at if latest_message else None,
                "sender_id": latest_message.sender_id if latest_message else None
            } if latest_message else None,
            "matched_at": match.created_at
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
        Match.id == match_id,
        (Match.user1_id == current_user.id) | (Match.user2_id == current_user.id)
    ).first()
    
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    
    messages = db.query(Message).filter(
        Message.match_id == match_id
    ).order_by(Message.created_at.desc()).offset(offset).limit(limit).all()
    
    return [
        {
            "id": msg.id,
            "content": msg.content,
            "sender_id": msg.sender_id,
            "created_at": msg.created_at,
            "message_type": msg.message_type
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
        Match.id == match_id,
        (Match.user1_id == current_user.id) | (Match.user2_id == current_user.id),
        Match.status == "active"
    ).first()
    
    if not match:
        raise HTTPException(status_code=404, detail="Match not found or inactive")
    
    content = message_data.get("content", "").strip()
    if not content:
        raise HTTPException(status_code=400, detail="Message content is required")
    
    # Create message
    message = Message(
        match_id=match_id,
        sender_id=current_user.id,
        content=content,
        message_type="text"
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    
    return {
        "id": message.id,
        "content": message.content,
        "sender_id": message.sender_id,
        "created_at": message.created_at,
        "message_type": message.message_type
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
        Message.id == message_id,
        Message.sender_id == current_user.id
    ).first()
    
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    
    db.delete(message)
    db.commit()
    
    return {"message": "Message deleted successfully"}
