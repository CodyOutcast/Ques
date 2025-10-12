"""
Notification System Router
Complete notification management for the dating app including friend requests,
system notifications, receives management, and user preferences.
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
from services.auth_service import AuthService
from services.email_service import EmailService

router = APIRouter()
security = HTTPBearer()
logger = logging.getLogger(__name__)
auth_service = AuthService()
email_service = EmailService()

# ==================== Pydantic Models ====================

class NotificationResponse(BaseModel):
    """Response model for a notification"""
    id: str
    type: str = Field(..., description="Notification type: friend_request, message, match, system, gift")
    title: str
    message: str
    data: Optional[Dict[str, Any]] = None
    is_read: bool = False
    created_at: datetime
    expires_at: Optional[datetime] = None

class NotificationsListResponse(BaseModel):
    """Response model for notifications list"""
    notifications: List[NotificationResponse]
    total_count: int
    unread_count: int
    page: int
    limit: int
    has_more: bool

class MarkAsReadRequest(BaseModel):
    """Request model for marking notifications as read"""
    notificationIds: List[str]

class FriendRequestResponse(BaseModel):
    """Response model for friend request"""
    id: str
    sender_id: str
    sender_name: str
    sender_avatar: Optional[str] = None
    recipient_id: str
    message: Optional[str] = None
    status: str = Field(..., description="Status: pending, accepted, declined, expired")
    gift_receives: Optional[int] = None
    created_at: datetime
    expires_at: Optional[datetime] = None

class FriendRequestsListResponse(BaseModel):
    """Response model for friend requests list"""
    friend_requests: List[FriendRequestResponse]
    total_count: int
    page: int
    limit: int
    has_more: bool

class SendFriendRequestRequest(BaseModel):
    """Request model for sending friend request"""
    recipientId: str
    message: Optional[str] = None
    giftReceives: Optional[int] = Field(None, ge=0, le=100, description="Gift receives amount")

class RespondFriendRequestRequest(BaseModel):
    """Request model for responding to friend request"""
    requestId: str
    action: str = Field(..., regex="^(accept|decline)$")
    message: Optional[str] = None

class UnreadCountResponse(BaseModel):
    """Response model for unread count"""
    total: int
    friendRequests: int
    messages: int
    matches: int
    system: int
    gifts: int

class NotificationPreferences(BaseModel):
    """Notification preferences model"""
    emailNotifications: bool = True
    pushNotifications: bool = True
    friendRequests: bool = True
    matches: bool = True
    messages: bool = True
    system: bool = True
    gifts: bool = True

class ReceivesStatus(BaseModel):
    """Receives status response model"""
    remaining: int
    total: int
    resetDate: str
    plan: str = Field(..., regex="^(basic|pro)$")

class TopUpRequest(BaseModel):
    """Top up receives request"""
    amount: int = Field(..., ge=1, le=1000)
    paymentMethod: Optional[str] = None

class GiftRequest(BaseModel):
    """Gift receives request"""
    recipientId: str
    amount: int = Field(..., ge=1, le=100)
    message: Optional[str] = None

class ReceivesHistoryItem(BaseModel):
    """Receives history item"""
    id: str
    type: str = Field(..., regex="^(purchase|gift_sent|gift_received|usage)$")
    amount: int
    description: str
    relatedUserId: Optional[str] = None
    relatedUserName: Optional[str] = None
    timestamp: datetime

class ReceivesHistoryResponse(BaseModel):
    """Receives history response"""
    items: List[ReceivesHistoryItem]
    total_count: int
    page: int
    limit: int
    has_more: bool

# ==================== Endpoints ====================

@router.get("/notifications", response_model=NotificationsListResponse)
async def get_notifications(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    type: Optional[str] = Query(None, description="Filter by type: friend_request, message, match, system, gift"),
    unreadOnly: bool = Query(False, description="Only return unread notifications"),
    token: str = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Get paginated list of user notifications
    """
    try:
        current_user = auth_service.get_current_user(db, token.credentials)
        if not current_user:
            raise HTTPException(status_code=401, detail="Invalid token")

        # Calculate offset
        offset = (page - 1) * limit
        
        # Mock notifications data (in real implementation, query from database)
        mock_notifications = [
            {
                "id": f"notif_{i}",
                "type": "friend_request" if i % 3 == 0 else "match" if i % 3 == 1 else "system",
                "title": f"New {'friend request' if i % 3 == 0 else 'match' if i % 3 == 1 else 'system notification'}",
                "message": f"You have a new notification #{i}",
                "data": {"related_user_id": f"user_{i}"} if i % 3 != 2 else None,
                "is_read": i % 4 != 0,
                "created_at": datetime.now() - timedelta(hours=i),
                "expires_at": None
            }
            for i in range(1, 51)  # 50 mock notifications
        ]
        
        # Apply filters
        filtered_notifications = mock_notifications
        if type:
            filtered_notifications = [n for n in filtered_notifications if n["type"] == type]
        if unreadOnly:
            filtered_notifications = [n for n in filtered_notifications if not n["is_read"]]
        
        # Apply pagination
        total_count = len(filtered_notifications)
        paginated_notifications = filtered_notifications[offset:offset + limit]
        unread_count = len([n for n in mock_notifications if not n["is_read"]])
        
        return NotificationsListResponse(
            notifications=[NotificationResponse(**n) for n in paginated_notifications],
            total_count=total_count,
            unread_count=unread_count,
            page=page,
            limit=limit,
            has_more=offset + limit < total_count
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting notifications: {e}")
        raise HTTPException(status_code=500, detail="Failed to get notifications")

@router.post("/notifications/read")
async def mark_notifications_as_read(
    request: MarkAsReadRequest,
    token: str = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Mark multiple notifications as read
    """
    try:
        current_user = auth_service.get_current_user(db, token.credentials)
        if not current_user:
            raise HTTPException(status_code=401, detail="Invalid token")

        # Mock implementation - in real app, update database records
        logger.info(f"Marking notifications as read: {request.notificationIds}")
        
        return {"message": f"Marked {len(request.notificationIds)} notifications as read"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error marking notifications as read: {e}")
        raise HTTPException(status_code=500, detail="Failed to mark notifications as read")

@router.delete("/notifications/{notificationId}")
async def delete_notification(
    notificationId: str,
    token: str = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Delete a specific notification
    """
    try:
        current_user = auth_service.get_current_user(db, token.credentials)
        if not current_user:
            raise HTTPException(status_code=401, detail="Invalid token")

        # Mock implementation - in real app, delete from database
        logger.info(f"Deleting notification: {notificationId}")
        
        return {"message": "Notification deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting notification: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete notification")

@router.get("/notifications/friend-requests", response_model=FriendRequestsListResponse)
async def get_friend_requests(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    status: Optional[str] = Query(None, description="Filter by status: pending, accepted, declined, expired"),
    direction: Optional[str] = Query(None, description="Filter by direction: sent, received, all"),
    token: str = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Get paginated list of friend requests
    """
    try:
        current_user = auth_service.get_current_user(db, token.credentials)
        if not current_user:
            raise HTTPException(status_code=401, detail="Invalid token")

        # Calculate offset
        offset = (page - 1) * limit
        
        # Mock friend requests data
        mock_requests = [
            {
                "id": f"req_{i}",
                "sender_id": f"user_{i}",
                "sender_name": f"User {i}",
                "sender_avatar": f"https://avatar.example.com/{i}",
                "recipient_id": current_user.id,
                "message": f"Hi! I'd like to connect with you. Request #{i}",
                "status": "pending" if i % 3 == 0 else "accepted" if i % 3 == 1 else "declined",
                "gift_receives": 5 if i % 4 == 0 else None,
                "created_at": datetime.now() - timedelta(days=i),
                "expires_at": datetime.now() + timedelta(days=7-i) if i % 3 == 0 else None
            }
            for i in range(1, 21)  # 20 mock requests
        ]
        
        # Apply filters
        filtered_requests = mock_requests
        if status:
            filtered_requests = [r for r in filtered_requests if r["status"] == status]
        
        # Apply pagination
        total_count = len(filtered_requests)
        paginated_requests = filtered_requests[offset:offset + limit]
        
        return FriendRequestsListResponse(
            friend_requests=[FriendRequestResponse(**r) for r in paginated_requests],
            total_count=total_count,
            page=page,
            limit=limit,
            has_more=offset + limit < total_count
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting friend requests: {e}")
        raise HTTPException(status_code=500, detail="Failed to get friend requests")

@router.post("/notifications/friend-requests")
async def send_friend_request(
    request: SendFriendRequestRequest,
    token: str = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Send a friend request to another user
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
            raise HTTPException(status_code=400, detail="Cannot send friend request to yourself")

        # Mock implementation - in real app, create database record
        friend_request_id = f"req_{current_user.id}_{request.recipientId}_{int(datetime.now().timestamp())}"
        
        logger.info(f"Friend request sent from {current_user.id} to {request.recipientId}")
        
        return {
            "id": friend_request_id,
            "message": "Friend request sent successfully",
            "recipient_name": recipient.display_name or recipient.username
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending friend request: {e}")
        raise HTTPException(status_code=500, detail="Failed to send friend request")

@router.post("/notifications/friend-requests/respond")
async def respond_to_friend_request(
    request: RespondFriendRequestRequest,
    token: str = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Respond to a friend request (accept or decline)
    """
    try:
        current_user = auth_service.get_current_user(db, token.credentials)
        if not current_user:
            raise HTTPException(status_code=401, detail="Invalid token")

        # Mock implementation - in real app, update database record
        logger.info(f"Friend request {request.requestId} {request.action}ed by {current_user.id}")
        
        return {
            "message": f"Friend request {request.action}ed successfully",
            "new_status": request.action + "ed"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error responding to friend request: {e}")
        raise HTTPException(status_code=500, detail="Failed to respond to friend request")

@router.get("/notifications/unread-count", response_model=UnreadCountResponse)
async def get_unread_count(
    token: str = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Get count of unread notifications by category
    """
    try:
        current_user = auth_service.get_current_user(db, token.credentials)
        if not current_user:
            raise HTTPException(status_code=401, detail="Invalid token")

        # Mock implementation - in real app, count from database
        unread_counts = {
            "friendRequests": 3,
            "messages": 5,
            "matches": 2,
            "system": 1,
            "gifts": 1
        }
        
        return UnreadCountResponse(
            total=sum(unread_counts.values()),
            **unread_counts
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting unread count: {e}")
        raise HTTPException(status_code=500, detail="Failed to get unread count")

@router.post("/notifications/batch")
async def batch_operate_notifications(
    operation: str = Query(..., regex="^(read|delete)$"),
    notification_ids: List[str] = Query(...),
    token: str = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Batch operation on notifications (read or delete multiple)
    """
    try:
        current_user = auth_service.get_current_user(db, token.credentials)
        if not current_user:
            raise HTTPException(status_code=401, detail="Invalid token")

        # Mock implementation
        logger.info(f"Batch {operation} operation on {len(notification_ids)} notifications")
        
        return {
            "message": f"Successfully {operation} {len(notification_ids)} notifications",
            "operation": operation,
            "count": len(notification_ids)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in batch operation: {e}")
        raise HTTPException(status_code=500, detail="Failed to perform batch operation")

@router.put("/notifications/preferences")
async def update_notification_preferences(
    preferences: NotificationPreferences,
    token: str = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Update user notification preferences
    """
    try:
        current_user = auth_service.get_current_user(db, token.credentials)
        if not current_user:
            raise HTTPException(status_code=401, detail="Invalid token")

        # Mock implementation - in real app, save to database
        logger.info(f"Updated notification preferences for user {current_user.id}")
        
        return {"message": "Notification preferences updated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating notification preferences: {e}")
        raise HTTPException(status_code=500, detail="Failed to update notification preferences")

@router.get("/notifications/preferences", response_model=NotificationPreferences)
async def get_notification_preferences(
    token: str = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Get user notification preferences
    """
    try:
        current_user = auth_service.get_current_user(db, token.credentials)
        if not current_user:
            raise HTTPException(status_code=401, detail="Invalid token")

        # Mock implementation - in real app, load from database
        return NotificationPreferences()
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting notification preferences: {e}")
        raise HTTPException(status_code=500, detail="Failed to get notification preferences")

@router.get("/receives/status", response_model=ReceivesStatus)
async def get_receives_status(
    token: str = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Get current receives status for user
    """
    try:
        current_user = auth_service.get_current_user(db, token.credentials)
        if not current_user:
            raise HTTPException(status_code=401, detail="Invalid token")

        # Mock implementation
        return ReceivesStatus(
            remaining=45,
            total=100,
            resetDate=(datetime.now() + timedelta(days=30)).isoformat(),
            plan="basic"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting receives status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get receives status")

@router.post("/receives/top-up")
async def top_up_receives(
    request: TopUpRequest,
    token: str = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Top up receives balance
    """
    try:
        current_user = auth_service.get_current_user(db, token.credentials)
        if not current_user:
            raise HTTPException(status_code=401, detail="Invalid token")

        # Mock implementation - in real app, process payment and update balance
        logger.info(f"Top up {request.amount} receives for user {current_user.id}")
        
        return {
            "message": f"Successfully topped up {request.amount} receives",
            "new_balance": 100 + request.amount,
            "transaction_id": f"topup_{int(datetime.now().timestamp())}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error topping up receives: {e}")
        raise HTTPException(status_code=500, detail="Failed to top up receives")

@router.post("/receives/gift")
async def gift_receives(
    request: GiftRequest,
    token: str = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Gift receives to another user
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
            raise HTTPException(status_code=400, detail="Cannot gift to yourself")

        # Mock implementation - in real app, transfer receives between users
        logger.info(f"Gift {request.amount} receives from {current_user.id} to {request.recipientId}")
        
        return {
            "message": f"Successfully gifted {request.amount} receives to {recipient.display_name or recipient.username}",
            "transaction_id": f"gift_{int(datetime.now().timestamp())}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error gifting receives: {e}")
        raise HTTPException(status_code=500, detail="Failed to gift receives")

@router.get("/receives/history", response_model=ReceivesHistoryResponse)
async def get_receives_history(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    type: Optional[str] = Query(None, description="Filter by type: purchase, gift_sent, gift_received, usage"),
    token: str = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Get receives transaction history
    """
    try:
        current_user = auth_service.get_current_user(db, token.credentials)
        if not current_user:
            raise HTTPException(status_code=401, detail="Invalid token")

        # Calculate offset
        offset = (page - 1) * limit
        
        # Mock history data
        mock_history = [
            {
                "id": f"trans_{i}",
                "type": ["purchase", "gift_sent", "gift_received", "usage"][i % 4],
                "amount": [50, -10, 15, -5][i % 4],
                "description": [
                    "Purchased receives pack",
                    "Gifted to User ABC",
                    "Received gift from User XYZ", 
                    "Used for friend request"
                ][i % 4],
                "relatedUserId": f"user_{i}" if i % 4 != 0 else None,
                "relatedUserName": f"User {i}" if i % 4 != 0 else None,
                "timestamp": datetime.now() - timedelta(days=i)
            }
            for i in range(1, 31)  # 30 mock transactions
        ]
        
        # Apply filters
        filtered_history = mock_history
        if type:
            filtered_history = [h for h in filtered_history if h["type"] == type]
        
        # Apply pagination
        total_count = len(filtered_history)
        paginated_history = filtered_history[offset:offset + limit]
        
        return ReceivesHistoryResponse(
            items=[ReceivesHistoryItem(**h) for h in paginated_history],
            total_count=total_count,
            page=page,
            limit=limit,
            has_more=offset + limit < total_count
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting receives history: {e}")
        raise HTTPException(status_code=500, detail="Failed to get receives history")