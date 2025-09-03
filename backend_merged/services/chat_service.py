"""
Chat service handling greeting/acceptance flow and messaging with content moderation
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
from typing import List, Optional, Tuple
from datetime import datetime

from models.chats import Chat, ChatMessage, ChatStatus
from models.users import User
from models.likes import UserSwipe, Like, SwipeDirection
from schemas.chats import (
    GreetingCreate, GreetingResponse, MessageCreate, 
    ChatResponse, MessageResponse, ChatWithMessages, ChatListResponse
)
from services.content_moderation import content_moderation_service, ModerationResult

class ChatService:
    """Service for handling chat operations with greeting/acceptance flow"""
    
    @staticmethod
    async def send_greeting(db: Session, sender_id: int, greeting_data: GreetingCreate) -> ChatResponse:
        """
        Send a greeting message to start a chat with content moderation
        Only allowed if sender has liked the recipient
        """
        # Moderate greeting message content first
        moderation_result = await content_moderation_service.moderate_message(
            message_content=greeting_data.greeting_message,
            sender_id=sender_id,
            chat_id=0  # No chat ID yet
        )
        
        # Check if content should be blocked
        if content_moderation_service.should_block_content(moderation_result):
            raise ValueError(f"Greeting message violates community guidelines: {', '.join(moderation_result.violations)}")
        
        # Check if sender has liked the recipient
        like_exists = db.query(UserSwipe).filter(
            UserSwipe.swiper_id == sender_id,
            UserSwipe.target_id == greeting_data.recipient_id,
            UserSwipe.direction == SwipeDirection.like
        ).first()
        
        if not like_exists:
            raise ValueError("You must like this user before sending a greeting")
        
        # Check if chat already exists
        existing_chat = db.query(Chat).filter(
            or_(
                and_(Chat.initiator_id == sender_id, Chat.recipient_id == greeting_data.recipient_id),
                and_(Chat.initiator_id == greeting_data.recipient_id, Chat.recipient_id == sender_id)
            )
        ).first()
        
        if existing_chat:
            if existing_chat.status == ChatStatus.REJECTED:
                raise ValueError("Your greeting was rejected. You cannot send another greeting.")
            elif existing_chat.status == ChatStatus.PENDING:
                raise ValueError("You have already sent a greeting. Please wait for a response.")
            else:
                raise ValueError("Chat already exists with this user")
        
        # Create new chat
        new_chat = Chat(
            initiator_id=sender_id,
            recipient_id=greeting_data.recipient_id,
            status=ChatStatus.PENDING,
            greeting_message=greeting_data.greeting_message,
            created_at=datetime.utcnow()
        )
        
        db.add(new_chat)
        db.commit()
        db.refresh(new_chat)
        
        # Create initial greeting message
        greeting_message = ChatMessage(
            chat_id=new_chat.chat_id,
            sender_id=sender_id,
            content=greeting_data.greeting_message,
            is_greeting=True,
            created_at=datetime.utcnow()
        )
        
        db.add(greeting_message)
        db.commit()
        
        # Update chat's last_message_at
        new_chat.last_message_at = greeting_message.created_at
        db.commit()
        
        return ChatService._build_chat_response(db, new_chat, sender_id)
    
    @staticmethod
    def respond_to_greeting(db: Session, recipient_id: int, response: GreetingResponse) -> ChatResponse:
        """
        Accept or reject a greeting
        """
        chat = db.query(Chat).filter(
            Chat.chat_id == response.chat_id,
            Chat.recipient_id == recipient_id,
            Chat.status == ChatStatus.PENDING
        ).first()
        
        if not chat:
            raise ValueError("Greeting not found or already responded to")
        
        if response.accept:
            chat.status = ChatStatus.ACTIVE
            chat.accepted_at = datetime.utcnow()
            
            # Send acceptance message
            acceptance_message = ChatMessage(
                chat_id=chat.chat_id,
                sender_id=recipient_id,
                content="👋 Greeting accepted! Let's start chatting!",
                created_at=datetime.utcnow()
            )
            db.add(acceptance_message)
            chat.last_message_at = acceptance_message.created_at
        else:
            chat.status = ChatStatus.REJECTED
        
        db.commit()
        db.refresh(chat)
        
        return ChatService._build_chat_response(db, chat, recipient_id)
    
    @staticmethod
    async def send_message(db: Session, sender_id: int, chat_id: int, message_data: MessageCreate) -> MessageResponse:
        """
        Send a message in an active chat with content moderation
        """
        # Moderate message content first
        moderation_result = await content_moderation_service.moderate_message(
            message_content=message_data.content,
            sender_id=sender_id,
            chat_id=chat_id
        )
        
        # Check if content should be blocked
        if content_moderation_service.should_block_content(moderation_result):
            raise ValueError(f"Message violates community guidelines: {', '.join(moderation_result.violations)}")
        
        chat = db.query(Chat).filter(Chat.chat_id == chat_id).first()
        
        if not chat:
            raise ValueError("Chat not found")
        
        # Check if user is part of this chat
        if sender_id not in [chat.initiator_id, chat.recipient_id]:
            raise ValueError("You are not part of this chat")
        
        # Check if chat allows messaging
        if not chat.can_send_message(sender_id):
            if chat.status == ChatStatus.PENDING:
                raise ValueError("Wait for the greeting to be accepted before sending messages")
            elif chat.status == ChatStatus.REJECTED:
                raise ValueError("Cannot send messages in a rejected chat")
            else:
                raise ValueError("Cannot send messages in this chat")
        
        # Determine moderation status based on result
        moderation_status = content_moderation_service.get_moderation_status(moderation_result)
        
        # Create message with moderation status
        new_message = ChatMessage(
            chat_id=chat_id,
            sender_id=sender_id,
            content=message_data.content,
            moderation_status=moderation_status,
            created_at=datetime.utcnow()
        )
        
        db.add(new_message)
        
        # Update chat's last message time
        chat.last_message_at = new_message.created_at
        db.commit()
        db.refresh(new_message)
        
        return MessageResponse.from_orm(new_message)
    
    @staticmethod
    def get_user_chats(db: Session, user_id: int, limit: int = 50, offset: int = 0) -> ChatListResponse:
        """
        Get all chats for a user
        """
        chats = db.query(Chat).filter(
            or_(Chat.initiator_id == user_id, Chat.recipient_id == user_id)
        ).order_by(desc(Chat.last_message_at), desc(Chat.created_at)).offset(offset).limit(limit).all()
        
        # Count pending greetings (received, not sent)
        pending_greetings = db.query(Chat).filter(
            Chat.recipient_id == user_id,
            Chat.status == ChatStatus.PENDING
        ).count()
        
        chat_responses = []
        for chat in chats:
            chat_response = ChatService._build_chat_response(db, chat, user_id)
            chat_responses.append(chat_response)
        
        total = db.query(Chat).filter(
            or_(Chat.initiator_id == user_id, Chat.recipient_id == user_id)
        ).count()
        
        return ChatListResponse(
            chats=chat_responses,
            total=total,
            pending_greetings=pending_greetings
        )
    
    @staticmethod
    def get_chat_with_messages(db: Session, user_id: int, chat_id: int, limit: int = 50, 
                             offset: int = 0, search_query: Optional[str] = None) -> ChatWithMessages:
        """
        Get a specific chat with its messages
        If search_query is provided, highlights matching text in messages
        """
        chat = db.query(Chat).filter(Chat.chat_id == chat_id).first()
        
        if not chat:
            raise ValueError("Chat not found")
        
        # Check if user is part of this chat
        if user_id not in [chat.initiator_id, chat.recipient_id]:
            raise ValueError("You are not part of this chat")
        
        # Get messages
        messages = db.query(ChatMessage).filter(
            ChatMessage.chat_id == chat_id
        ).order_by(ChatMessage.created_at).offset(offset).limit(limit).all()
        
        # Build message responses with optional highlighting
        message_responses = []
        for msg in messages:
            msg_response = MessageResponse.from_orm(msg)
            
            # Add highlighting if search query provided
            if search_query and search_query.strip():
                msg_response.highlighted_content = ChatService._highlight_text(msg.content, search_query)
            
            message_responses.append(msg_response)
        
        # Build chat response with messages
        other_user_id = chat.get_other_user_id(user_id)
        other_user = db.query(User).filter(User.user_id == other_user_id).first()
        
        return ChatWithMessages(
            chat_id=chat.chat_id,
            initiator_id=chat.initiator_id,
            recipient_id=chat.recipient_id,
            status=chat.status,
            created_at=chat.created_at,
            accepted_at=chat.accepted_at,
            last_message_at=chat.last_message_at,
            greeting_message=chat.greeting_message,
            messages=message_responses,
            other_user_name=other_user.name if other_user else "Unknown",
            other_user_bio=other_user.bio if other_user else None
        )
    
    @staticmethod
    def mark_messages_as_read(db: Session, user_id: int, message_ids: List[int]) -> int:
        """
        Mark messages as read
        Returns number of messages marked as read
        """
        # Only mark messages where the user is the recipient
        messages = db.query(ChatMessage).join(Chat).filter(
            ChatMessage.message_id.in_(message_ids),
            ChatMessage.sender_id != user_id,  # Don't mark own messages as read
            or_(Chat.initiator_id == user_id, Chat.recipient_id == user_id)  # User must be part of chat
        ).all()
        
        count = 0
        for message in messages:
            if not message.is_read:
                message.is_read = True
                count += 1
        
        db.commit()
        return count
    
    @staticmethod
    def get_pending_greetings(db: Session, user_id: int) -> List[ChatResponse]:
        """
        Get all pending greetings for a user
        """
        pending_chats = db.query(Chat).filter(
            Chat.recipient_id == user_id,
            Chat.status == ChatStatus.PENDING
        ).order_by(desc(Chat.created_at)).all()
        
        return [ChatService._build_chat_response(db, chat, user_id) for chat in pending_chats]
    
    @staticmethod
    def _build_chat_response(db: Session, chat: Chat, current_user_id: int) -> ChatResponse:
        """
        Build a ChatResponse with other user information
        """
        other_user_id = chat.get_other_user_id(current_user_id)
        other_user = db.query(User).filter(User.user_id == other_user_id).first()
        
        return ChatResponse(
            chat_id=chat.chat_id,
            initiator_id=chat.initiator_id,
            recipient_id=chat.recipient_id,
            status=chat.status,
            created_at=chat.created_at,
            accepted_at=chat.accepted_at,
            last_message_at=chat.last_message_at,
            greeting_message=chat.greeting_message,
            other_user_name=other_user.name if other_user else "Unknown",
            other_user_bio=other_user.bio if other_user else None
        )

    @staticmethod
    def search_chats_and_messages(db: Session, user_id: int, query: str, search_messages: bool = True, 
                                search_users: bool = True, limit: int = 20):
        """
        Search through user's chats and messages
        Returns both matching chats and messages
        """
        from schemas.chats import ChatSearchResult, MessageSearchResult, SearchResponse
        
        # Get user's chats
        user_chats = db.query(Chat).filter(
            or_(Chat.initiator_id == user_id, Chat.recipient_id == user_id),
            Chat.status.in_([ChatStatus.ACTIVE, ChatStatus.PENDING])
        ).all()
        
        chat_ids = [chat.chat_id for chat in user_chats]
        
        matching_chats = []
        matching_messages = []
        
        # Search in messages if enabled
        if search_messages and chat_ids:
            message_query = db.query(ChatMessage).filter(
                ChatMessage.chat_id.in_(chat_ids),
                ChatMessage.content.ilike(f"%{query}%")
            ).order_by(desc(ChatMessage.created_at)).limit(limit)
            
            for message in message_query:
                sender = db.query(User).filter(User.user_id == message.sender_id).first()
                
                # Highlight the search term in content
                highlighted_content = ChatService._highlight_text(message.content, query)
                
                matching_messages.append(MessageSearchResult(
                    message_id=message.message_id,
                    chat_id=message.chat_id,
                    sender_id=message.sender_id,
                    sender_name=sender.name if sender else "Unknown",
                    content=message.content,
                    created_at=message.created_at,
                    highlighted_content=highlighted_content
                ))
        
        # Search in user names/bios if enabled
        if search_users:
            for chat in user_chats:
                other_user_id = chat.get_other_user_id(user_id)
                other_user = db.query(User).filter(User.user_id == other_user_id).first()
                
                if other_user:
                    match_reason = None
                    
                    # Check if username matches
                    if other_user.username and query.lower() in other_user.username.lower():
                        match_reason = "Username match"
                    # Check if display name matches
                    elif other_user.display_name and query.lower() in other_user.display_name.lower():
                        match_reason = "Display name match"
                    # Check if bio matches
                    elif other_user.bio and query.lower() in other_user.bio.lower():
                        match_reason = "Bio match"
                    
                    if match_reason:
                        # Get recent messages for context
                        recent_messages = db.query(ChatMessage).filter(
                            ChatMessage.chat_id == chat.chat_id
                        ).order_by(desc(ChatMessage.created_at)).limit(3).all()
                        
                        recent_msg_responses = []
                        for msg in recent_messages:
                            msg_response = MessageResponse(
                                message_id=msg.message_id,
                                chat_id=msg.chat_id,
                                sender_id=msg.sender_id,
                                content=msg.content,
                                created_at=msg.created_at,
                                is_read=msg.is_read,
                                is_greeting=msg.is_greeting,
                                highlighted_content=None  # No highlighting in recent context
                            )
                            recent_msg_responses.append(msg_response)
                        
                        matching_chats.append(ChatSearchResult(
                            chat_id=chat.chat_id,
                            other_user_id=other_user_id,
                            other_user_name=other_user.display_name or other_user.username,
                            other_user_bio=other_user.bio,
                            status=chat.status,
                            last_message_at=chat.last_message_at,
                            match_reason=match_reason,
                            recent_messages=recent_msg_responses
                        ))
        
        return SearchResponse(
            query=query,
            total_chats=len(matching_chats),
            total_messages=len(matching_messages),
            chats=matching_chats[:limit],
            messages=matching_messages[:limit]
        )
    
    @staticmethod
    def _highlight_text(text: str, query: str, max_length: int = 150) -> str:
        """
        Highlight search query in text and truncate for preview
        """
        if not query or not text:
            return text[:max_length] + "..." if len(text) > max_length else text
        
        # Find the position of the query in text (case insensitive)
        text_lower = text.lower()
        query_lower = query.lower()
        
        pos = text_lower.find(query_lower)
        if pos == -1:
            return text[:max_length] + "..." if len(text) > max_length else text
        
        # Calculate excerpt bounds
        start = max(0, pos - 50)
        end = min(len(text), pos + len(query) + 50)
        
        excerpt = text[start:end]
        
        # Add ellipsis if needed
        if start > 0:
            excerpt = "..." + excerpt
        if end < len(text):
            excerpt = excerpt + "..."
        
        # Highlight the query term (simple HTML-like markup)
        highlighted = excerpt.replace(
            text[pos:pos + len(query)], 
            f"**{text[pos:pos + len(query)]}**"
        )
        
        return highlighted
