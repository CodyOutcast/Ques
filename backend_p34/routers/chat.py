"""
Page 4: Chat Router
Handles messaging between matched users, chat history, and match management
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, desc
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from dependencies.db import get_db
from models.users import User
from models.matches import Match
from models.messages import Message

router = APIRouter()

# Pydantic models for API requests/responses
class MessageSendRequest(BaseModel):
    match_id: int
    message_text: str

class MessageResponse(BaseModel):
    message_id: int
    match_id: int
    sender_id: int
    sender_name: str
    message_text: str
    sent_at: datetime
    is_read: bool

    class Config:
        from_attributes = True

class ChatHistoryResponse(BaseModel):
    match_id: int
    other_user_id: int
    other_user_name: str
    other_user_bio: Optional[str]
    messages: List[MessageResponse]
    last_message_at: Optional[datetime]

class MatchResponse(BaseModel):
    match_id: int
    other_user_id: int
    other_user_name: str
    other_user_bio: Optional[str]
    matched_at: datetime
    last_message: Optional[str]
    last_message_at: Optional[datetime]
    unread_count: int

    class Config:
        from_attributes = True

@router.get("/matches/{user_id}", response_model=List[MatchResponse])
def get_user_matches(user_id: int, db: Session = Depends(get_db)):
    """
    Page 4: Get list of all matches for a user with last message preview
    """
    # Check if user exists
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Get all matches for this user
    matches = db.query(Match).filter(
        and_(
            or_(Match.user1_id == user_id, Match.user2_id == user_id),
            Match.is_active == True
        )
    ).all()
    
    match_list = []
    for match in matches:
        # Determine the other user
        other_user_id = match.user2_id if match.user1_id == user_id else match.user1_id
        other_user = db.query(User).filter(User.user_id == other_user_id).first()
        
        if not other_user:
            continue
        
        # Get the last message in this match
        last_message = db.query(Message).filter(
            Message.match_id == match.match_id
        ).order_by(desc(Message.sent_at)).first()
        
        # Count unread messages for this user
        unread_count = db.query(Message).filter(
            and_(
                Message.match_id == match.match_id,
                Message.sender_id != user_id,
                Message.is_read == False
            )
        ).count()
        
        match_response = MatchResponse(
            match_id=match.match_id,
            other_user_id=other_user_id,
            other_user_name=other_user.name,
            other_user_bio=other_user.bio,
            matched_at=match.matched_at,
            last_message=last_message.message_text if last_message else None,
            last_message_at=last_message.sent_at if last_message else None,
            unread_count=unread_count
        )
        match_list.append(match_response)
    
    # Sort by last message time (most recent first)
    match_list.sort(key=lambda x: x.last_message_at or x.matched_at, reverse=True)
    
    return match_list

@router.get("/chat/{match_id}", response_model=ChatHistoryResponse)
def get_chat_history(match_id: int, user_id: int, db: Session = Depends(get_db)):
    """
    Page 4: Get full chat history for a specific match
    """
    # Verify the match exists and user is part of it
    match = db.query(Match).filter(
        and_(
            Match.match_id == match_id,
            or_(Match.user1_id == user_id, Match.user2_id == user_id),
            Match.is_active == True
        )
    ).first()
    
    if not match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Match not found or user not authorized"
        )
    
    # Get the other user
    other_user_id = match.user2_id if match.user1_id == user_id else match.user1_id
    other_user = db.query(User).filter(User.user_id == other_user_id).first()
    
    # Get all messages for this match
    messages = db.query(Message).filter(
        Message.match_id == match_id
    ).order_by(Message.sent_at).all()
    
    # Convert messages to response format
    message_responses = []
    for message in messages:
        sender = db.query(User).filter(User.user_id == message.sender_id).first()
        message_response = MessageResponse(
            message_id=message.message_id,
            match_id=message.match_id,
            sender_id=message.sender_id,
            sender_name=sender.name if sender else "Unknown",
            message_text=message.message_text,
            sent_at=message.sent_at,
            is_read=message.is_read
        )
        message_responses.append(message_response)
    
    # Mark messages from other user as read
    db.query(Message).filter(
        and_(
            Message.match_id == match_id,
            Message.sender_id != user_id,
            Message.is_read == False
        )
    ).update({Message.is_read: True})
    db.commit()
    
    return ChatHistoryResponse(
        match_id=match_id,
        other_user_id=other_user_id,
        other_user_name=other_user.name,
        other_user_bio=other_user.bio,
        messages=message_responses,
        last_message_at=messages[-1].sent_at if messages else None
    )

@router.post("/send", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
def send_message(message_data: MessageSendRequest, user_id: int, db: Session = Depends(get_db)):
    """
    Page 4: Send a message in a chat
    """
    # Verify the match exists and user is part of it
    match = db.query(Match).filter(
        and_(
            Match.match_id == message_data.match_id,
            or_(Match.user1_id == user_id, Match.user2_id == user_id),
            Match.is_active == True
        )
    ).first()
    
    if not match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Match not found or user not authorized"
        )
    
    # Create the message
    try:
        new_message = Message(
            match_id=message_data.match_id,
            sender_id=user_id,
            message_text=message_data.message_text,
            is_read=False
        )
        
        db.add(new_message)
        db.commit()
        db.refresh(new_message)
        
        # Get sender info for response
        sender = db.query(User).filter(User.user_id == user_id).first()
        
        return MessageResponse(
            message_id=new_message.message_id,
            match_id=new_message.match_id,
            sender_id=new_message.sender_id,
            sender_name=sender.name if sender else "Unknown",
            message_text=new_message.message_text,
            sent_at=new_message.sent_at,
            is_read=new_message.is_read
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to send message: {str(e)}"
        )

@router.put("/messages/{message_id}/read")
def mark_message_read(message_id: int, user_id: int, db: Session = Depends(get_db)):
    """
    Mark a specific message as read
    """
    message = db.query(Message).filter(Message.message_id == message_id).first()
    
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )
    
    # Verify user is part of the match
    match = db.query(Match).filter(
        and_(
            Match.match_id == message.match_id,
            or_(Match.user1_id == user_id, Match.user2_id == user_id)
        )
    ).first()
    
    if not match:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not authorized to access this message"
        )
    
    # Only allow marking as read if user is not the sender
    if message.sender_id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot mark your own message as read"
        )
    
    message.is_read = True
    db.commit()
    
    return {"message": "Message marked as read"}

@router.get("/unread-count/{user_id}")
def get_unread_message_count(user_id: int, db: Session = Depends(get_db)):
    """
    Get total count of unread messages for a user across all chats
    """
    # Get all match IDs where user is involved
    user_matches = db.query(Match.match_id).filter(
        and_(
            or_(Match.user1_id == user_id, Match.user2_id == user_id),
            Match.is_active == True
        )
    ).subquery()
    
    # Count unread messages from other users
    unread_count = db.query(Message).filter(
        and_(
            Message.match_id.in_(user_matches),
            Message.sender_id != user_id,
            Message.is_read == False
        )
    ).count()
    
    return {"unread_count": unread_count}

@router.delete("/match/{match_id}")
def unmatch_user(match_id: int, user_id: int, db: Session = Depends(get_db)):
    """
    Unmatch with another user (deactivate the match)
    """
    match = db.query(Match).filter(
        and_(
            Match.match_id == match_id,
            or_(Match.user1_id == user_id, Match.user2_id == user_id),
            Match.is_active == True
        )
    ).first()
    
    if not match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Match not found or user not authorized"
        )
    
    match.is_active = False
    db.commit()
    
    return {"message": "Successfully unmatched"}
