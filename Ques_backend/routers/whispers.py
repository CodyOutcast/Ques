"""
Whisper Messaging Router
Complete whisper messaging system extending the basic operations
with advanced features like settings, detailed history, and batch operations.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
import logging

from dependencies.db import get_db
from models.users import User
from models.whispers import Whisper
from services.auth_service import AuthService
from services.monitoring import log_security_event

router = APIRouter()
security = HTTPBearer()
logger = logging.getLogger(__name__)
auth_service = AuthService()

# ==================== Pydantic Models ====================

class WhisperMessageResponse(BaseModel):
    """Response model for a whisper message"""
    id: str
    sender_id: str
    recipient_id: str
    message: Optional[str] = None
    sender_profile: Optional[Dict[str, Any]] = None
    context: Optional[Dict[str, Any]] = None
    status: str = Field(..., description="Status: pending, accepted, declined, expired")
    is_read: bool = False
    created_at: datetime
    expires_at: Optional[datetime] = None
    response_message: Optional[str] = None
    responded_at: Optional[datetime] = None

class WhispersListResponse(BaseModel):
    """Response model for whispers list"""
    whispers: List[WhisperMessageResponse]
    total_count: int
    unread_count: int
    page: int
    limit: int
    has_more: bool

class SendWhisperRequest(BaseModel):
    """Request model for sending whisper"""
    recipientId: str
    message: Optional[str] = Field(None, max_length=500)
    senderProfile: Optional[Dict[str, Any]] = None
    context: Optional[Dict[str, Any]] = None

class RespondWhisperRequest(BaseModel):
    """Request model for responding to whisper"""
    whisperId: str
    action: str = Field(..., pattern="^(accept|decline)$")
    responseMessage: Optional[str] = Field(None, max_length=500)

class WhisperSettings(BaseModel):
    """Whisper settings model"""
    wechatId: Optional[str] = None
    customMessage: Optional[str] = Field(None, max_length=200)
    autoAccept: bool = False
    showOnlineStatus: bool = True
    enableNotifications: bool = True
    allowFromStrangers: bool = True
    requireGift: bool = False
    minimumGiftAmount: Optional[int] = Field(None, ge=1, le=100)

class BatchReadRequest(BaseModel):
    """Request model for batch marking whispers as read"""
    whisperIds: List[str]

class WhisperStatsResponse(BaseModel):
    """Whisper statistics response"""
    total_sent: int
    total_received: int
    pending_received: int
    accepted_count: int
    declined_count: int
    response_rate: float
    avg_response_time_hours: Optional[float] = None

# ==================== Endpoints ====================

@router.post("/whispers/send", response_model=WhisperMessageResponse)
async def send_whisper(
    request: SendWhisperRequest,
    token: str = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Send a whisper message to another user
    """
    try:
        current_user = auth_service.get_current_user(db, token.credentials)
        if not current_user:
            raise HTTPException(status_code=401, detail="Invalid token")

        # Check if recipient exists
        recipient = db.query(User).filter(User.id == request.recipientId).first()
        if not recipient:
            raise HTTPException(status_code=404, detail="Recipient not found")
        
        if current_user.id == request.recipientId:
            raise HTTPException(status_code=400, detail="Cannot send whisper to yourself")

        # Mock implementation - in real app, create database record
        whisper_id = f"whisper_{current_user.id}_{request.recipientId}_{int(datetime.now().timestamp())}"
        
        logger.info(f"Whisper sent from {current_user.id} to {request.recipientId}")
        
        return WhisperMessageResponse(
            id=whisper_id,
            sender_id=current_user.id,
            recipient_id=request.recipientId,
            message=request.message,
            sender_profile=request.senderProfile,
            context=request.context,
            status="pending",
            is_read=False,
            created_at=datetime.now(),
            expires_at=datetime.now() + timedelta(days=7)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending whisper: {e}")
        raise HTTPException(status_code=500, detail="Failed to send whisper")

@router.get("/whispers", response_model=WhispersListResponse)
async def get_received_whispers(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    status: Optional[str] = Query(None, description="Filter by status: pending, accepted, declined, expired"),
    unread_only: bool = Query(False, description="Only return unread whispers"),
    token: str = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Get received whispers with pagination and filtering
    """
    try:
        current_user = auth_service.get_current_user(db, token.credentials)
        if not current_user:
            raise HTTPException(status_code=401, detail="Invalid token")

        # Calculate offset
        offset = (page - 1) * limit
        
        # Mock received whispers data
        mock_whispers = []
        statuses = ["pending", "accepted", "declined", "expired"]
        
        for i in range(1, 51):  # 50 mock whispers
            whisper_status = statuses[i % len(statuses)]
            is_read = i % 3 != 0
            
            mock_whispers.append({
                "id": f"received_whisper_{i}",
                "sender_id": f"sender_{i}",
                "recipient_id": current_user.id,
                "message": f"Hi! I'd love to connect with you. Whisper #{i}",
                "sender_profile": {
                    "name": f"Sender {i}",
                    "avatar": f"https://avatar.example.com/sender_{i}",
                    "location": "San Francisco",
                    "matchScore": 85 + (i % 15)
                },
                "context": {
                    "searchQuery": "AI developers" if i % 4 == 0 else None,
                    "giftReceives": 5 if i % 5 == 0 else None
                },
                "status": whisper_status,
                "is_read": is_read,
                "created_at": datetime.now() - timedelta(hours=i),
                "expires_at": datetime.now() + timedelta(days=7-i) if whisper_status == "pending" else None,
                "response_message": f"Thank you for reaching out!" if whisper_status == "accepted" else None,
                "responded_at": datetime.now() - timedelta(hours=i//2) if whisper_status in ["accepted", "declined"] else None
            })
        
        # Apply filters
        filtered_whispers = mock_whispers
        if status:
            filtered_whispers = [w for w in filtered_whispers if w["status"] == status]
        if unread_only:
            filtered_whispers = [w for w in filtered_whispers if not w["is_read"]]
        
        # Apply pagination
        total_count = len(filtered_whispers)
        paginated_whispers = filtered_whispers[offset:offset + limit]
        unread_count = len([w for w in mock_whispers if not w["is_read"]])
        
        return WhispersListResponse(
            whispers=[WhisperMessageResponse(**w) for w in paginated_whispers],
            total_count=total_count,
            unread_count=unread_count,
            page=page,
            limit=limit,
            has_more=offset + limit < total_count
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting received whispers: {e}")
        raise HTTPException(status_code=500, detail="Failed to get received whispers")

@router.get("/whispers/sent", response_model=WhispersListResponse)
async def get_sent_whispers(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    status: Optional[str] = Query(None, description="Filter by status: pending, accepted, declined, expired"),
    token: str = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Get sent whispers with pagination and filtering
    """
    try:
        current_user = auth_service.get_current_user(db, token.credentials)
        if not current_user:
            raise HTTPException(status_code=401, detail="Invalid token")

        # Calculate offset
        offset = (page - 1) * limit
        
        # Mock sent whispers data
        mock_whispers = []
        statuses = ["pending", "accepted", "declined", "expired"]
        
        for i in range(1, 31):  # 30 mock sent whispers
            whisper_status = statuses[i % len(statuses)]
            
            mock_whispers.append({
                "id": f"sent_whisper_{i}",
                "sender_id": current_user.id,
                "recipient_id": f"recipient_{i}",
                "message": f"Hello! I saw your profile and would love to connect. Message #{i}",
                "sender_profile": None,  # Not needed for sent whispers
                "context": {
                    "searchQuery": "Mobile developers" if i % 3 == 0 else None
                },
                "status": whisper_status,
                "is_read": i % 2 == 0,  # Whether recipient read it
                "created_at": datetime.now() - timedelta(days=i),
                "expires_at": datetime.now() + timedelta(days=7-i) if whisper_status == "pending" else None,
                "response_message": f"Thanks for reaching out!" if whisper_status == "accepted" else "Not interested" if whisper_status == "declined" else None,
                "responded_at": datetime.now() - timedelta(days=i//2) if whisper_status in ["accepted", "declined"] else None
            })
        
        # Apply filters
        filtered_whispers = mock_whispers
        if status:
            filtered_whispers = [w for w in filtered_whispers if w["status"] == status]
        
        # Apply pagination
        total_count = len(filtered_whispers)
        paginated_whispers = filtered_whispers[offset:offset + limit]
        
        return WhispersListResponse(
            whispers=[WhisperMessageResponse(**w) for w in paginated_whispers],
            total_count=total_count,
            unread_count=0,  # Not applicable for sent whispers
            page=page,
            limit=limit,
            has_more=offset + limit < total_count
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting sent whispers: {e}")
        raise HTTPException(status_code=500, detail="Failed to get sent whispers")

@router.post("/whispers/respond")
async def respond_to_whisper(
    request: RespondWhisperRequest,
    token: str = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Respond to a received whisper (accept or decline)
    """
    try:
        current_user = auth_service.get_current_user(db, token.credentials)
        if not current_user:
            raise HTTPException(status_code=401, detail="Invalid token")

        # Mock implementation - in real app, update database record
        logger.info(f"Whisper {request.whisperId} {request.action}ed by {current_user.id}")
        
        return {
            "message": f"Whisper {request.action}ed successfully",
            "whisper_id": request.whisperId,
            "action": request.action,
            "response_message": request.responseMessage
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error responding to whisper: {e}")
        raise HTTPException(status_code=500, detail="Failed to respond to whisper")

@router.get("/whispers/settings", response_model=WhisperSettings)
async def get_whisper_settings(
    token: str = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Get user's whisper settings
    """
    try:
        current_user = auth_service.get_current_user(db, token.credentials)
        if not current_user:
            raise HTTPException(status_code=401, detail="Invalid token")

        # Mock implementation - in real app, load from database
        return WhisperSettings(
            wechatId="user_wechat_123",
            customMessage="Hello! I'm interested in connecting with like-minded people.",
            autoAccept=False,
            showOnlineStatus=True,
            enableNotifications=True,
            allowFromStrangers=True,
            requireGift=False,
            minimumGiftAmount=None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting whisper settings: {e}")
        raise HTTPException(status_code=500, detail="Failed to get whisper settings")

@router.put("/whispers/settings")
async def update_whisper_settings(
    settings: WhisperSettings,
    token: str = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Update user's whisper settings
    """
    try:
        current_user = auth_service.get_current_user(db, token.credentials)
        if not current_user:
            raise HTTPException(status_code=401, detail="Invalid token")

        # Mock implementation - in real app, save to database
        logger.info(f"Updated whisper settings for user {current_user.id}")
        
        return {
            "message": "Whisper settings updated successfully",
            "settings": settings.dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating whisper settings: {e}")
        raise HTTPException(status_code=500, detail="Failed to update whisper settings")

@router.get("/whispers/{whisperId}", response_model=WhisperMessageResponse)
async def get_whisper_details(
    whisperId: str,
    token: str = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a specific whisper
    """
    try:
        current_user = auth_service.get_current_user(db, token.credentials)
        if not current_user:
            raise HTTPException(status_code=401, detail="Invalid token")

        # Mock implementation - in real app, query from database
        mock_whisper = {
            "id": whisperId,
            "sender_id": "sender_123",
            "recipient_id": current_user.id,
            "message": "Hi there! I noticed we have similar interests in AI and would love to connect.",
            "sender_profile": {
                "name": "John Doe",
                "avatar": "https://avatar.example.com/john",
                "location": "San Francisco",
                "skills": ["AI", "Python", "Machine Learning"],
                "bio": "AI enthusiast and software developer",
                "matchScore": 92,
                "wechatId": "john_wechat"
            },
            "context": {
                "searchQuery": "AI developers",
                "searchMode": "global",
                "matchExplanation": "High compatibility based on shared interests in AI and technology",
                "giftReceives": 10
            },
            "status": "pending",
            "is_read": False,
            "created_at": datetime.now() - timedelta(hours=2),
            "expires_at": datetime.now() + timedelta(days=5),
            "response_message": None,
            "responded_at": None
        }
        
        return WhisperMessageResponse(**mock_whisper)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting whisper details: {e}")
        raise HTTPException(status_code=500, detail="Failed to get whisper details")

@router.delete("/whispers/{whisperId}")
async def delete_whisper(
    whisperId: str,
    token: str = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Delete a whisper message
    """
    try:
        current_user = auth_service.get_current_user(db, token.credentials)
        if not current_user:
            raise HTTPException(status_code=401, detail="Invalid token")

        # Mock implementation - in real app, delete from database
        logger.info(f"Deleted whisper {whisperId} by user {current_user.id}")
        
        return {
            "message": "Whisper deleted successfully",
            "whisper_id": whisperId
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting whisper: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete whisper")

@router.patch("/whispers/{whisperId}/read")
async def mark_whisper_as_read(
    whisperId: str,
    token: str = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Mark a specific whisper as read
    """
    try:
        current_user = auth_service.get_current_user(db, token.credentials)
        if not current_user:
            raise HTTPException(status_code=401, detail="Invalid token")

        # Mock implementation - in real app, update database record
        logger.info(f"Marked whisper {whisperId} as read by user {current_user.id}")
        
        return {
            "message": "Whisper marked as read",
            "whisper_id": whisperId
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error marking whisper as read: {e}")
        raise HTTPException(status_code=500, detail="Failed to mark whisper as read")

@router.post("/whispers/batch-read")
async def batch_mark_whispers_as_read(
    request: BatchReadRequest,
    token: str = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Mark multiple whispers as read in batch
    """
    try:
        current_user = auth_service.get_current_user(db, token.credentials)
        if not current_user:
            raise HTTPException(status_code=401, detail="Invalid token")

        # Mock implementation - in real app, batch update database records
        logger.info(f"Batch marked {len(request.whisperIds)} whispers as read by user {current_user.id}")
        
        return {
            "message": f"Successfully marked {len(request.whisperIds)} whispers as read",
            "count": len(request.whisperIds)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error batch marking whispers as read: {e}")
        raise HTTPException(status_code=500, detail="Failed to batch mark whispers as read")

@router.get("/whispers/stats", response_model=WhisperStatsResponse)
async def get_whisper_stats(
    token: str = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Get whisper statistics for the current user
    """
    try:
        current_user = auth_service.get_current_user(db, token.credentials)
        if not current_user:
            raise HTTPException(status_code=401, detail="Invalid token")

        # Mock statistics - in real app, calculate from database
        total_sent = 25
        total_received = 40
        accepted_count = 15
        declined_count = 8
        
        return WhisperStatsResponse(
            total_sent=total_sent,
            total_received=total_received,
            pending_received=7,  # Current pending
            accepted_count=accepted_count,
            declined_count=declined_count,
            response_rate=round((accepted_count + declined_count) / total_received * 100, 1),
            avg_response_time_hours=4.5
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting whisper stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get whisper stats")
