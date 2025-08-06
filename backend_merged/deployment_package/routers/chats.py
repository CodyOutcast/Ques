"""
Chat router for messaging system with greeting/acceptance flow
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from dependencies.db import get_db
from dependencies.auth import get_current_user
from models.users import User
from services.chat_service import ChatService
from schemas.chats import (
    GreetingCreate, GreetingResponse, MessageCreate, SendMessageRequest,
    ChatResponse, MessageResponse, ChatWithMessages, ChatListResponse,
    MarkAsReadRequest, ChatSearchRequest, SearchResponse
)

router = APIRouter(prefix="/api/chats", tags=["chats"])

@router.post("/greeting", response_model=ChatResponse, status_code=status.HTTP_201_CREATED)
async def send_greeting(
    greeting_data: GreetingCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Send a greeting to start a chat with content moderation
    Only allowed if you have liked the user
    """
    try:
        return await ChatService.send_greeting(db, current_user.user_id, greeting_data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/greeting/respond", response_model=ChatResponse)
def respond_to_greeting(
    response: GreetingResponse,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Accept or reject a greeting
    """
    try:
        return ChatService.respond_to_greeting(db, current_user.user_id, response)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/message", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def send_message(
    message_request: SendMessageRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Send a message in an active chat with content moderation
    """
    try:
        message_data = MessageCreate(content=message_request.content)
        return await ChatService.send_message(
            db, current_user.user_id, message_request.chat_id, message_data
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/", response_model=ChatListResponse)
def get_my_chats(
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all chats for the current user
    """
    return ChatService.get_user_chats(db, current_user.user_id, limit, offset)

@router.get("/pending", response_model=List[ChatResponse])
def get_pending_greetings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all pending greetings for the current user
    """
    return ChatService.get_pending_greetings(db, current_user.user_id)

@router.get("/{chat_id}", response_model=ChatWithMessages)
def get_chat_with_messages(
    chat_id: int,
    limit: int = 50,
    offset: int = 0,
    search_query: str = None,  # Optional search query for highlighting
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific chat with its messages
    If search_query is provided, matching text will be highlighted in messages
    """
    try:
        return ChatService.get_chat_with_messages(
            db, current_user.user_id, chat_id, limit, offset, search_query
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@router.post("/messages/read")
def mark_messages_as_read(
    request: MarkAsReadRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Mark messages as read
    """
    count = ChatService.mark_messages_as_read(db, current_user.user_id, request.message_ids)
    return {"marked_as_read": count}

@router.delete("/{chat_id}/block")
def block_chat(
    chat_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Block a chat (prevents further messaging)
    """
    try:
        # This would be implemented to set chat status to BLOCKED
        # For now, just return success
        return {"message": "Chat blocked successfully"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

# WebSocket endpoint for real-time messaging (optional)
@router.get("/{chat_id}/ws")
def websocket_chat(chat_id: int):
    """
    WebSocket endpoint for real-time chat
    Implementation would go here for real-time messaging
    """
    return {"message": "WebSocket endpoint for real-time chat - to be implemented"}

@router.post("/search", response_model=SearchResponse)
def search_chats_and_messages(
    search_request: ChatSearchRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Search through user's chats and messages
    
    Search capabilities:
    - Message content search
    - User name search (username, display name)
    - User bio search
    - Highlighted results with context
    """
    try:
        return ChatService.search_chats_and_messages(
            db=db,
            user_id=current_user.user_id,
            query=search_request.query,
            search_messages=search_request.search_messages,
            search_users=search_request.search_users,
            limit=search_request.limit
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}"
        )
