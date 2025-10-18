"""
Basic Operations API Router
Provides core functionality: user creation, whispers, swiping, top profiles

Endpoints:
- POST /api/v1/basic/users - Create new user
- POST /api/v1/basic/whispers - Send whisper message
- POST /api/v1/basic/swipe - Swipe on user
- GET /api/v1/basic/top-profiles - Get top 10 recommended profiles
- GET /api/v1/basic/my-whispers - Get my whispers (sent/received)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field, EmailStr, validator
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func
import logging

from dependencies.db import get_db
from dependencies.auth import get_current_user
from models.users import User
from models.user_profiles import UserProfile
from models.whispers import Whisper
from models.user_swipes import UserSwipe, SwipeDirection
from services.auth_service import AuthService

# Setup logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v1/basic", tags=["Basic Operations"])

# ==================== Pydantic Models ====================

class UserCreateRequest(BaseModel):
    """Request model for creating a new user"""
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., min_length=8, description="Password (min 8 characters)")
    name: str = Field(..., min_length=2, max_length=100, description="User's full name")
    phone_number: Optional[str] = Field(None, description="Phone number (optional)")
    wechat_id: Optional[str] = Field(None, description="WeChat ID (optional)")
    
    # Profile fields
    role: Optional[str] = Field(None, description="Role: student, professional, entrepreneur")
    location: Optional[str] = Field(None, description="City/location")
    bio: Optional[str] = Field(None, max_length=500, description="Short bio")
    skills: Optional[List[str]] = Field(None, description="List of skills")
    interests: Optional[List[str]] = Field(None, description="List of interests")
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "email": "zhang.wei@example.com",
                "password": "SecurePass123",
                "name": "Zhang Wei",
                "phone_number": "+86 138 0000 0000",
                "role": "student",
                "location": "Shenzhen",
                "bio": "CS student interested in mobile development",
                "skills": ["Python", "React Native", "Flutter"],
                "interests": ["AI", "mobile apps", "startups"]
            }
        }


class UserCreateResponse(BaseModel):
    """Response model for user creation"""
    user_id: int
    email: str
    name: str
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    message: str = "User created successfully"


class WhisperSendRequest(BaseModel):
    """Request model for sending a whisper"""
    recipient_id: int = Field(..., description="User ID of the recipient")
    greeting_message: str = Field(..., min_length=1, max_length=500, description="Whisper message")
    sender_wechat_id: Optional[str] = Field(None, description="Optional WeChat ID to share")
    swipe_id: Optional[int] = Field(None, description="Related swipe ID if applicable")
    from_template: bool = Field(False, description="Whether this is from a template")
    
    class Config:
        schema_extra = {
            "example": {
                "recipient_id": 123,
                "greeting_message": "Hi! I saw your profile and I'm also interested in mobile app development. Would love to connect!",
                "sender_wechat_id": None,
                "from_template": False
            }
        }


class WhisperResponse(BaseModel):
    """Response model for whisper"""
    id: int
    sender_id: int
    recipient_id: int
    greeting_message: str
    is_read: bool
    created_at: datetime
    sender_name: Optional[str] = None
    recipient_name: Optional[str] = None


class SwipeRequest(BaseModel):
    """Request model for swiping"""
    target_user_id: int = Field(..., description="User ID to swipe on")
    direction: str = Field(..., description="Swipe direction: 'like', 'dislike', 'superlike'")
    
    @validator('direction')
    def validate_direction(cls, v):
        if v.lower() not in ['like', 'dislike', 'superlike']:
            raise ValueError("Direction must be 'like', 'dislike', or 'superlike'")
        return v.lower()
    
    class Config:
        schema_extra = {
            "example": {
                "target_user_id": 123,
                "direction": "like"
            }
        }


class SwipeResponse(BaseModel):
    """Response model for swipe"""
    swipe_id: int
    user_id: int
    target_user_id: int
    direction: str
    is_match: bool
    match_id: Optional[int] = None
    created_at: datetime
    message: str


class ProfileSummary(BaseModel):
    """Summary of a user profile"""
    user_id: int
    name: str
    role: Optional[str]
    location: Optional[str]
    bio: Optional[str]
    skills: Optional[List[str]]
    interests: Optional[List[str]]
    avatar_url: Optional[str]
    match_score: Optional[float] = None


class TopProfilesResponse(BaseModel):
    """Response model for top profiles"""
    total_count: int
    profiles: List[ProfileSummary]
    timestamp: datetime


class WhisperListResponse(BaseModel):
    """Response model for whisper list"""
    sent: List[WhisperResponse]
    received: List[WhisperResponse]
    total_sent: int
    total_received: int
    unread_count: int


# ==================== Endpoints ====================

@router.post("/users", response_model=UserCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    request: UserCreateRequest,
    db: Session = Depends(get_db)
):
    """
    Create a new user account with profile
    
    **Features:**
    - Email/password authentication
    - Optional phone and WeChat ID
    - Profile creation with skills and interests
    - Returns access and refresh tokens
    
    **Password Requirements:**
    - Minimum 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    """
    try:
        logger.info(f"Creating new user with email: {request.email}")
        
        # Check if user already exists
        existing_user = db.query(User).filter(
            or_(
                User.email == request.email,
                User.phone_number == request.phone_number if request.phone_number else False
            )
        ).first()
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email or phone already exists"
            )
        
        # Initialize auth service
        auth_service = AuthService(db)
        
        # Create user with auth service
        user, tokens = auth_service.register_user_email(
            email=request.email,
            password=request.password,
            name=request.name,
            phone_number=request.phone_number,
            wechat_id=request.wechat_id
        )
        
        # Update profile with additional fields
        if user.profile:
            if request.role:
                user.profile.role = request.role
            if request.location:
                user.profile.location = request.location
            if request.bio:
                user.profile.bio = request.bio
            if request.skills:
                user.profile.skills = request.skills
            if request.interests:
                user.profile.interests = request.interests
            
            db.commit()
            db.refresh(user)
        
        logger.info(f"✅ User created successfully: {user.id}")
        
        return UserCreateResponse(
            user_id=user.id,
            email=user.email,
            name=user.profile.name if user.profile else request.name,
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
            message="User created successfully. Welcome!"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to create user: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create user: {str(e)}"
        )


@router.post("/whispers", response_model=WhisperResponse, status_code=status.HTTP_201_CREATED)
async def send_whisper(
    request: WhisperSendRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Send a whisper (greeting message) to another user
    
    **Features:**
    - Anonymous or revealed messages
    - Optional WeChat ID sharing
    - Link to swipe context
    - Template support
    
    **Limits:**
    - Free users: 5 whispers per day
    - Premium users: Unlimited
    """
    try:
        sender_id = current_user["id"]
        logger.info(f"User {sender_id} sending whisper to user {request.recipient_id}")
        
        # Check if recipient exists
        recipient = db.query(User).filter(User.id == request.recipient_id).first()
        if not recipient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Recipient user not found"
            )
        
        # Check if sender is trying to send to themselves
        if sender_id == request.recipient_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot send whisper to yourself"
            )
        
        # TODO: Check whisper limits based on membership
        # For now, just create the whisper
        
        # Create whisper
        whisper = Whisper(
            sender_id=sender_id,
            recipient_id=request.recipient_id,
            greeting_message=request.greeting_message,
            sender_wechat_id=request.sender_wechat_id,
            swipe_id=request.swipe_id,
            from_template=request.from_template,
            is_read=False
        )
        
        db.add(whisper)
        db.commit()
        db.refresh(whisper)
        
        # Get sender and recipient names
        sender = db.query(User).filter(User.id == sender_id).first()
        sender_name = sender.profile.name if sender and sender.profile else None
        recipient_name = recipient.profile.name if recipient and recipient.profile else None
        
        logger.info(f"✅ Whisper sent successfully: {whisper.id}")
        
        return WhisperResponse(
            id=whisper.id,
            sender_id=whisper.sender_id,
            recipient_id=whisper.recipient_id,
            greeting_message=whisper.greeting_message,
            is_read=whisper.is_read,
            created_at=whisper.created_at,
            sender_name=sender_name,
            recipient_name=recipient_name
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to send whisper: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send whisper: {str(e)}"
        )


@router.post("/swipe", response_model=SwipeResponse)
async def swipe_user(
    request: SwipeRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Swipe on a user profile (like, dislike, or superlike)
    
    **Directions:**
    - `like`: Show interest in the user
    - `dislike`: Pass on the user
    - `superlike`: Strong interest (may require premium)
    
    **Match Detection:**
    - If both users liked each other, a match is created
    - Match ID is returned if match occurs
    """
    try:
        user_id = current_user["id"]
        logger.info(f"User {user_id} swiping {request.direction} on user {request.target_user_id}")
        
        # Check if target user exists
        target_user = db.query(User).filter(User.id == request.target_user_id).first()
        if not target_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Target user not found"
            )
        
        # Check if user is trying to swipe themselves
        if user_id == request.target_user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot swipe on yourself"
            )
        
        # Check if swipe already exists
        existing_swipe = db.query(UserSwipe).filter(
            and_(
                UserSwipe.user_id == user_id,
                UserSwipe.swiped_user_id == request.target_user_id
            )
        ).first()
        
        if existing_swipe:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You have already swiped on this user"
            )
        
        # Map direction to enum
        direction_map = {
            'like': SwipeDirection.LIKE,
            'dislike': SwipeDirection.DISLIKE,
            'superlike': SwipeDirection.SUPERLIKE
        }
        
        # Create swipe
        swipe = UserSwipe(
            user_id=user_id,
            swiped_user_id=request.target_user_id,
            direction=direction_map[request.direction]
        )
        
        db.add(swipe)
        db.commit()
        db.refresh(swipe)
        
        # Check for match (if this is a like)
        is_match = False
        match_id = None
        message = f"You {request.direction}d this user"
        
        if request.direction in ['like', 'superlike']:
            # Check if target user also liked current user
            reverse_swipe = db.query(UserSwipe).filter(
                and_(
                    UserSwipe.user_id == request.target_user_id,
                    UserSwipe.swiped_user_id == user_id,
                    UserSwipe.direction.in_([SwipeDirection.LIKE, SwipeDirection.SUPERLIKE])
                )
            ).first()
            
            if reverse_swipe:
                is_match = True
                # TODO: Create match record in matches table
                message = "🎉 It's a match! You can now send messages."
                logger.info(f"✅ Match created between user {user_id} and user {request.target_user_id}")
        
        logger.info(f"✅ Swipe recorded: {swipe.id}")
        
        return SwipeResponse(
            swipe_id=swipe.id,
            user_id=user_id,
            target_user_id=request.target_user_id,
            direction=request.direction,
            is_match=is_match,
            match_id=match_id,
            created_at=swipe.created_at,
            message=message
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to swipe: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to swipe: {str(e)}"
        )


@router.get("/top-profiles", response_model=TopProfilesResponse)
async def get_top_profiles(
    limit: int = 10,
    exclude_seen: bool = True,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get top recommended profiles for the current user
    
    **Parameters:**
    - `limit`: Number of profiles to return (default: 10, max: 50)
    - `exclude_seen`: Exclude already swiped users (default: true)
    
    **Algorithm:**
    - Filters out users already swiped
    - Returns active users with complete profiles
    - Ordered by relevance (can be enhanced with ML)
    """
    try:
        user_id = current_user["id"]
        logger.info(f"Getting top {limit} profiles for user {user_id}")
        
        # Limit the limit
        if limit > 50:
            limit = 50
        if limit < 1:
            limit = 10
        
        # Build base query
        query = db.query(User).join(UserProfile).filter(
            User.id != user_id,
            User.user_status == 'active',
            UserProfile.name.isnot(None)
        )
        
        # Exclude seen users if requested
        if exclude_seen:
            seen_user_ids = db.query(UserSwipe.swiped_user_id).filter(
                UserSwipe.user_id == user_id
            ).all()
            seen_ids = [swipe[0] for swipe in seen_user_ids]
            
            if seen_ids:
                query = query.filter(User.id.notin_(seen_ids))
        
        # Get users (ordered by created_at for now, can add ML ranking later)
        users = query.order_by(User.created_at.desc()).limit(limit).all()
        
        # Build profile summaries
        profiles = []
        for user in users:
            if user.profile:
                profiles.append(ProfileSummary(
                    user_id=user.id,
                    name=user.profile.name or "Unknown",
                    role=user.profile.role,
                    location=user.profile.location,
                    bio=user.profile.bio,
                    skills=user.profile.skills or [],
                    interests=user.profile.interests or [],
                    avatar_url=user.profile.avatar_url,
                    match_score=None  # Can add ML-based scoring later
                ))
        
        logger.info(f"✅ Returned {len(profiles)} profiles")
        
        return TopProfilesResponse(
            total_count=len(profiles),
            profiles=profiles,
            timestamp=datetime.now()
        )
        
    except Exception as e:
        logger.error(f"❌ Failed to get top profiles: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get profiles: {str(e)}"
        )


@router.get("/my-whispers", response_model=WhisperListResponse)
async def get_my_whispers(
    type: str = "all",
    limit: int = 50,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get whispers sent and received by the current user
    
    **Parameters:**
    - `type`: Filter by type - 'sent', 'received', or 'all' (default: all)
    - `limit`: Maximum whispers per category (default: 50)
    
    **Returns:**
    - Sent whispers
    - Received whispers
    - Unread count
    """
    try:
        user_id = current_user["id"]
        logger.info(f"Getting whispers for user {user_id} (type: {type})")
        
        sent_whispers = []
        received_whispers = []
        
        # Get sent whispers
        if type in ['all', 'sent']:
            sent = db.query(Whisper).filter(
                Whisper.sender_id == user_id
            ).order_by(desc(Whisper.created_at)).limit(limit).all()
            
            for whisper in sent:
                recipient = db.query(User).filter(User.id == whisper.recipient_id).first()
                recipient_name = recipient.profile.name if recipient and recipient.profile else None
                
                sent_whispers.append(WhisperResponse(
                    id=whisper.id,
                    sender_id=whisper.sender_id,
                    recipient_id=whisper.recipient_id,
                    greeting_message=whisper.greeting_message,
                    is_read=whisper.is_read,
                    created_at=whisper.created_at,
                    sender_name=None,
                    recipient_name=recipient_name
                ))
        
        # Get received whispers
        if type in ['all', 'received']:
            received = db.query(Whisper).filter(
                Whisper.recipient_id == user_id
            ).order_by(desc(Whisper.created_at)).limit(limit).all()
            
            for whisper in received:
                sender = db.query(User).filter(User.id == whisper.sender_id).first()
                sender_name = sender.profile.name if sender and sender.profile else None
                
                received_whispers.append(WhisperResponse(
                    id=whisper.id,
                    sender_id=whisper.sender_id,
                    recipient_id=whisper.recipient_id,
                    greeting_message=whisper.greeting_message,
                    is_read=whisper.is_read,
                    created_at=whisper.created_at,
                    sender_name=sender_name,
                    recipient_name=None
                ))
        
        # Count unread
        unread_count = db.query(func.count(Whisper.id)).filter(
            Whisper.recipient_id == user_id,
            Whisper.is_read == False
        ).scalar()
        
        logger.info(f"✅ Returned {len(sent_whispers)} sent, {len(received_whispers)} received whispers")
        
        return WhisperListResponse(
            sent=sent_whispers,
            received=received_whispers,
            total_sent=len(sent_whispers),
            total_received=len(received_whispers),
            unread_count=unread_count or 0
        )
        
    except Exception as e:
        logger.error(f"❌ Failed to get whispers: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get whispers: {str(e)}"
        )


@router.patch("/whispers/{whisper_id}/read")
async def mark_whisper_read(
    whisper_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Mark a whisper as read
    
    Only the recipient can mark a whisper as read.
    """
    try:
        user_id = current_user["id"]
        
        whisper = db.query(Whisper).filter(Whisper.id == whisper_id).first()
        if not whisper:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Whisper not found"
            )
        
        # Check if current user is the recipient
        if whisper.recipient_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only mark your own received whispers as read"
            )
        
        # Mark as read
        whisper.is_read = True
        whisper.read_at = datetime.now()
        
        db.commit()
        
        logger.info(f"✅ Whisper {whisper_id} marked as read by user {user_id}")
        
        return {"message": "Whisper marked as read", "whisper_id": whisper_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to mark whisper as read: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to mark whisper as read: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """Health check for basic operations service"""
    return {
        "status": "healthy",
        "service": "basic_operations",
        "timestamp": datetime.now().isoformat()
    }
