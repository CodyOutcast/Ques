"""
Contact Management Router
Complete contact management system for maintaining user connections,
contact history, and reporting functionality.
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
from services.monitoring import log_security_event

router = APIRouter()
security = HTTPBearer()
logger = logging.getLogger(__name__)
auth_service = AuthService()

# ==================== Pydantic Models ====================

class ContactResponse(BaseModel):
    """Response model for a contact"""
    id: str
    user_id: str
    user_name: str
    user_avatar: Optional[str] = None
    contact_type: str = Field(..., description="Type: friend, blocked, favorite")
    notes: Optional[str] = None
    connection_date: datetime
    last_interaction: Optional[datetime] = None
    mutual_connections: int = 0
    match_score: Optional[float] = None
    is_online: bool = False
    last_seen: Optional[datetime] = None

class ContactsListResponse(BaseModel):
    """Response model for contacts list"""
    contacts: List[ContactResponse]
    total_count: int
    page: int
    limit: int
    has_more: bool

class AddContactRequest(BaseModel):
    """Request model for adding a contact"""
    userId: str
    contactType: str = Field(..., regex="^(friend|blocked|favorite)$")
    notes: Optional[str] = Field(None, max_length=500)

class UpdateContactRequest(BaseModel):
    """Request model for updating a contact"""
    contactType: Optional[str] = Field(None, regex="^(friend|blocked|favorite)$")
    notes: Optional[str] = Field(None, max_length=500)

class ReportContactRequest(BaseModel):
    """Request model for reporting a contact"""
    contactId: str
    reason: str = Field(..., regex="^(spam|harassment|inappropriate_content|fake_profile|other)$")
    description: Optional[str] = Field(None, max_length=1000)
    evidence: Optional[List[str]] = None  # URLs to evidence (screenshots, etc.)

class ContactHistoryItem(BaseModel):
    """Contact history item model"""
    id: str
    contact_id: str
    action_type: str = Field(..., description="Type: added, updated, blocked, unblocked, reported")
    action_details: Optional[Dict[str, Any]] = None
    timestamp: datetime
    notes: Optional[str] = None

class ContactHistoryResponse(BaseModel):
    """Response model for contact history"""
    history: List[ContactHistoryItem]
    total_count: int
    page: int
    limit: int
    has_more: bool

class RecommendedContact(BaseModel):
    """Recommended contact model"""
    user_id: str
    user_name: str
    user_avatar: Optional[str] = None
    match_score: float
    mutual_connections: int
    shared_interests: List[str]
    reason: str  # Why recommended
    location_distance: Optional[float] = None

class RecommendedContactsResponse(BaseModel):
    """Response model for recommended contacts"""
    recommendations: List[RecommendedContact]
    total_count: int

class ContactStatsResponse(BaseModel):
    """Contact statistics response"""
    total_contacts: int
    friends: int
    blocked: int
    favorites: int
    recent_additions: int
    mutual_connections_avg: float

# ==================== Endpoints ====================

@router.get("/contacts", response_model=ContactsListResponse)
async def get_contacts(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    type: Optional[str] = Query(None, description="Filter by type: friend, blocked, favorite"),
    search: Optional[str] = Query(None, description="Search by name"),
    sort_by: str = Query("connection_date", description="Sort by: name, connection_date, last_interaction"),
    sort_order: str = Query("desc", regex="^(asc|desc)$"),
    token: str = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Get paginated list of user contacts with filtering and search
    """
    try:
        current_user = auth_service.get_current_user(db, token.credentials)
        if not current_user:
            raise HTTPException(status_code=401, detail="Invalid token")

        # Calculate offset
        offset = (page - 1) * limit
        
        # Mock contacts data (in real implementation, query from database)
        mock_contacts = []
        for i in range(1, 51):  # 50 mock contacts
            contact_types = ["friend", "blocked", "favorite"]
            contact_type = contact_types[i % 3]
            
            mock_contacts.append({
                "id": f"contact_{i}",
                "user_id": f"user_{i}",
                "user_name": f"Contact User {i}",
                "user_avatar": f"https://avatar.example.com/user_{i}",
                "contact_type": contact_type,
                "notes": f"Notes for contact {i}" if i % 4 == 0 else None,
                "connection_date": datetime.now() - timedelta(days=i),
                "last_interaction": datetime.now() - timedelta(hours=i*2) if i % 3 == 0 else None,
                "mutual_connections": max(0, 10 - i // 5),
                "match_score": min(100, 50 + i * 1.5),
                "is_online": i % 5 == 0,
                "last_seen": datetime.now() - timedelta(minutes=i*10) if i % 5 != 0 else None
            })
        
        # Apply filters
        filtered_contacts = mock_contacts
        if type:
            filtered_contacts = [c for c in filtered_contacts if c["contact_type"] == type]
        if search:
            filtered_contacts = [c for c in filtered_contacts if search.lower() in c["user_name"].lower()]
        
        # Apply sorting
        reverse_order = sort_order == "desc"
        if sort_by == "name":
            filtered_contacts.sort(key=lambda x: x["user_name"], reverse=reverse_order)
        elif sort_by == "connection_date":
            filtered_contacts.sort(key=lambda x: x["connection_date"], reverse=reverse_order)
        elif sort_by == "last_interaction":
            # Handle None values in sorting
            filtered_contacts.sort(
                key=lambda x: x["last_interaction"] or datetime.min, 
                reverse=reverse_order
            )
        
        # Apply pagination
        total_count = len(filtered_contacts)
        paginated_contacts = filtered_contacts[offset:offset + limit]
        
        return ContactsListResponse(
            contacts=[ContactResponse(**c) for c in paginated_contacts],
            total_count=total_count,
            page=page,
            limit=limit,
            has_more=offset + limit < total_count
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting contacts: {e}")
        raise HTTPException(status_code=500, detail="Failed to get contacts")

@router.post("/contacts")
async def add_contact(
    request: AddContactRequest,
    token: str = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Add a new contact to user's contact list
    """
    try:
        current_user = auth_service.get_current_user(db, token.credentials)
        if not current_user:
            raise HTTPException(status_code=401, detail="Invalid token")

        # Check if target user exists
        target_user = db.query(User).filter(User.id == request.userId).first()
        if not target_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        if current_user.id == request.userId:
            raise HTTPException(status_code=400, detail="Cannot add yourself as contact")

        # Mock implementation - in real app, create database record
        contact_id = f"contact_{current_user.id}_{request.userId}_{int(datetime.now().timestamp())}"
        
        # Log security event for blocking
        if request.contactType == "blocked":
            log_security_event(
                current_user.id,
                "user_blocked",
                {"blocked_user_id": request.userId, "reason": request.notes}
            )
        
        logger.info(f"Added contact: {request.userId} as {request.contactType} by {current_user.id}")
        
        return {
            "id": contact_id,
            "message": f"Successfully added {target_user.display_name or target_user.username} as {request.contactType}",
            "contact_type": request.contactType
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding contact: {e}")
        raise HTTPException(status_code=500, detail="Failed to add contact")

@router.put("/contacts/{contactId}")
async def update_contact(
    contactId: str,
    request: UpdateContactRequest,
    token: str = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Update an existing contact's information
    """
    try:
        current_user = auth_service.get_current_user(db, token.credentials)
        if not current_user:
            raise HTTPException(status_code=401, detail="Invalid token")

        # Mock implementation - in real app, update database record
        logger.info(f"Updated contact {contactId} by user {current_user.id}")
        
        # Log security event if contact type changed to blocked
        if request.contactType == "blocked":
            log_security_event(
                current_user.id,
                "user_blocked",
                {"contact_id": contactId, "reason": request.notes}
            )
        
        return {
            "message": "Contact updated successfully",
            "contact_id": contactId,
            "updated_fields": {
                k: v for k, v in request.dict().items() if v is not None
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating contact: {e}")
        raise HTTPException(status_code=500, detail="Failed to update contact")

@router.delete("/contacts/{contactId}")
async def delete_contact(
    contactId: str,
    token: str = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Remove a contact from user's contact list
    """
    try:
        current_user = auth_service.get_current_user(db, token.credentials)
        if not current_user:
            raise HTTPException(status_code=401, detail="Invalid token")

        # Mock implementation - in real app, delete from database
        logger.info(f"Deleted contact {contactId} by user {current_user.id}")
        
        return {
            "message": "Contact removed successfully",
            "contact_id": contactId
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting contact: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete contact")

@router.post("/contacts/report")
async def report_contact(
    request: ReportContactRequest,
    token: str = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Report a contact for inappropriate behavior
    """
    try:
        current_user = auth_service.get_current_user(db, token.credentials)
        if not current_user:
            raise HTTPException(status_code=401, detail="Invalid token")

        # Mock implementation - in real app, create report record
        report_id = f"report_{current_user.id}_{request.contactId}_{int(datetime.now().timestamp())}"
        
        # Log security event
        log_security_event(
            current_user.id,
            "user_reported",
            {
                "reported_contact_id": request.contactId,
                "reason": request.reason,
                "description": request.description
            }
        )
        
        logger.info(f"Contact {request.contactId} reported by user {current_user.id} for {request.reason}")
        
        return {
            "report_id": report_id,
            "message": "Contact reported successfully. Our team will review this report.",
            "status": "submitted"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error reporting contact: {e}")
        raise HTTPException(status_code=500, detail="Failed to report contact")

@router.get("/contacts/history", response_model=ContactHistoryResponse)
async def get_contact_history(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    contact_id: Optional[str] = Query(None, description="Filter by specific contact ID"),
    action_type: Optional[str] = Query(None, description="Filter by action type"),
    token: str = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Get history of contact-related actions
    """
    try:
        current_user = auth_service.get_current_user(db, token.credentials)
        if not current_user:
            raise HTTPException(status_code=401, detail="Invalid token")

        # Calculate offset
        offset = (page - 1) * limit
        
        # Mock history data
        action_types = ["added", "updated", "blocked", "unblocked", "reported"]
        mock_history = []
        
        for i in range(1, 31):  # 30 mock history items
            action = action_types[i % len(action_types)]
            mock_history.append({
                "id": f"history_{i}",
                "contact_id": f"contact_{i % 10 + 1}",
                "action_type": action,
                "action_details": {
                    "previous_type": "friend" if action == "updated" else None,
                    "new_type": "blocked" if action in ["updated", "blocked"] else None,
                    "reason": f"Reason for {action}" if action in ["blocked", "reported"] else None
                },
                "timestamp": datetime.now() - timedelta(hours=i),
                "notes": f"Action notes for {action} #{i}" if i % 3 == 0 else None
            })
        
        # Apply filters
        filtered_history = mock_history
        if contact_id:
            filtered_history = [h for h in filtered_history if h["contact_id"] == contact_id]
        if action_type:
            filtered_history = [h for h in filtered_history if h["action_type"] == action_type]
        
        # Apply pagination
        total_count = len(filtered_history)
        paginated_history = filtered_history[offset:offset + limit]
        
        return ContactHistoryResponse(
            history=[ContactHistoryItem(**h) for h in paginated_history],
            total_count=total_count,
            page=page,
            limit=limit,
            has_more=offset + limit < total_count
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting contact history: {e}")
        raise HTTPException(status_code=500, detail="Failed to get contact history")

@router.get("/contacts/recommendations", response_model=RecommendedContactsResponse)
async def get_contact_recommendations(
    limit: int = Query(10, ge=1, le=50, description="Number of recommendations"),
    token: str = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Get recommended contacts based on mutual connections and interests
    """
    try:
        current_user = auth_service.get_current_user(db, token.credentials)
        if not current_user:
            raise HTTPException(status_code=401, detail="Invalid token")

        # Mock recommendations
        mock_recommendations = []
        reasons = [
            "High mutual connections",
            "Similar interests in technology",
            "Same university",
            "Location proximity",
            "Similar project experience"
        ]
        
        for i in range(1, limit + 1):
            mock_recommendations.append({
                "user_id": f"recommended_user_{i}",
                "user_name": f"Recommended User {i}",
                "user_avatar": f"https://avatar.example.com/rec_{i}",
                "match_score": max(60, 100 - i * 2),
                "mutual_connections": max(1, 8 - i),
                "shared_interests": ["AI", "Mobile Development", "Startups"][:max(1, 4-i)],
                "reason": reasons[i % len(reasons)],
                "location_distance": round(i * 1.5, 1) if i % 3 == 0 else None
            })
        
        return RecommendedContactsResponse(
            recommendations=[RecommendedContact(**r) for r in mock_recommendations],
            total_count=len(mock_recommendations)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting contact recommendations: {e}")
        raise HTTPException(status_code=500, detail="Failed to get contact recommendations")

@router.get("/contacts/stats", response_model=ContactStatsResponse)
async def get_contact_stats(
    token: str = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Get contact statistics for the current user
    """
    try:
        current_user = auth_service.get_current_user(db, token.credentials)
        if not current_user:
            raise HTTPException(status_code=401, detail="Invalid token")

        # Mock statistics - in real app, calculate from database
        return ContactStatsResponse(
            total_contacts=47,
            friends=35,
            blocked=2,
            favorites=10,
            recent_additions=5,  # Added in last 7 days
            mutual_connections_avg=3.2
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting contact stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get contact stats")