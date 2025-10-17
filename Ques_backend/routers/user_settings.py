"""
User settings router - implements all settings endpoints from frontend API documentation
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, func, desc
from typing import Optional
from datetime import datetime, timedelta
import logging

from dependencies.db import get_db
from dependencies.auth import get_current_user
from models.user_settings import UserSettings, SearchMode, Theme
from models.users import User
from models.user_profiles import UserProfile
from models.memberships import Membership
from models.user_quotas import UserQuota
from models.whispers import Whisper
from schemas.user_settings import (
    UserSettingsResponse,
    UpdateNotificationSettings,
    UpdateUserPreferences,
    UpdateWhisperSettings,
    WhisperSettings,
    UserStatistics,
    LogoutRequest,
    DeleteAccountRequest,
    DeleteAccountResponse,
    ExportDataResponse,
    AccountInfo,
    NotificationSettings,
    UserPreferences,
    Plan
)

router = APIRouter(prefix="/settings", tags=["Settings Management"])
logger = logging.getLogger(__name__)

# ============================================================================
# Helper Functions
# ============================================================================

async def get_or_create_user_settings(db: Session, user_id: int) -> UserSettings:
    """Get existing user settings or create default ones"""
    settings = db.query(UserSettings).filter(UserSettings.user_id == user_id).first()
    
    if not settings:
        settings = UserSettings(user_id=user_id)
        db.add(settings)
        db.commit()
        db.refresh(settings)
    
    return settings

async def build_settings_response(db: Session, user_id: int, settings: UserSettings) -> UserSettingsResponse:
    """Build complete settings response with data from multiple tables"""
    
    # Get user with related data
    user = db.query(User).options(
        joinedload(User.profile),
        joinedload(User.membership)
    ).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get plan and receives info from membership
    membership = user.membership
    plan = Plan.PRO if membership and membership.plan_type == "pro" else Plan.BASIC
    receives_left = membership.receives_remaining if membership else 0
    
    # Get whisper count from quotas or calculate
    quota = db.query(UserQuota).filter(UserQuota.user_id == user_id).first()
    whisper_count = quota.whispers_sent_today if quota else 0
    
    return UserSettingsResponse(
        id=str(settings.id),
        userId=str(user_id),
        plan=plan,
        receivesLeft=receives_left,
        whisperCount=whisper_count,
        notifications=NotificationSettings(
            emailNotifications=settings.email_notifications,
            pushNotifications=settings.push_notifications,
            whisperRequests=settings.whisper_requests,
            friendRequests=settings.friend_requests,
            matches=settings.matches_notifications,
            messages=settings.messages_notifications,
            system=settings.system_notifications,
            gifts=settings.gifts_notifications
        ),
        preferences=UserPreferences(
            searchMode=SearchMode(settings.search_mode),
            autoAcceptMatches=settings.auto_accept_matches,
            showOnlineStatus=settings.show_online_status
        ),
        createdAt=settings.created_at,
        updatedAt=settings.updated_at
    )

# ============================================================================
# API Endpoints - Matching Frontend Documentation Exactly
# ============================================================================

@router.get("", response_model=UserSettingsResponse)
async def get_user_settings(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get complete user settings
    Frontend API: GET /settings
    """
    try:
        user_id = current_user["id"]
        settings = await get_or_create_user_settings(db, user_id)
        return await build_settings_response(db, user_id, settings)
        
    except Exception as e:
        logger.error(f"Failed to get user settings: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get settings: {str(e)}")

@router.put("/notifications")
async def update_notification_settings(
    request: UpdateNotificationSettings,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update notification settings
    Frontend API: PUT /settings/notifications
    """
    try:
        user_id = current_user["id"]
        settings = await get_or_create_user_settings(db, user_id)
        
        # Update notification settings
        settings.email_notifications = request.notifications.emailNotifications
        settings.push_notifications = request.notifications.pushNotifications
        settings.whisper_requests = request.notifications.whisperRequests
        settings.friend_requests = request.notifications.friendRequests
        settings.matches_notifications = request.notifications.matches
        settings.messages_notifications = request.notifications.messages
        settings.system_notifications = request.notifications.system
        settings.gifts_notifications = request.notifications.gifts
        settings.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(settings)
        
        return await build_settings_response(db, user_id, settings)
        
    except Exception as e:
        logger.error(f"Failed to update notification settings: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update notifications: {str(e)}")

@router.put("/preferences")
async def update_user_preferences(
    request: UpdateUserPreferences,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update user preferences
    Frontend API: PUT /settings/preferences
    """
    try:
        user_id = current_user["id"]
        settings = await get_or_create_user_settings(db, user_id)
        
        # Update user preferences
        settings.search_mode = request.preferences.searchMode.value
        settings.auto_accept_matches = request.preferences.autoAcceptMatches
        settings.show_online_status = request.preferences.showOnlineStatus
        settings.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(settings)
        
        return await build_settings_response(db, user_id, settings)
        
    except Exception as e:
        logger.error(f"Failed to update user preferences: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update preferences: {str(e)}")

@router.get("/stats", response_model=UserStatistics)
async def get_user_statistics(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user statistics
    Frontend API: GET /settings/stats
    """
    try:
        user_id = current_user["id"]
        
        # Get user with profile
        user = db.query(User).options(joinedload(User.profile)).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Calculate whisper statistics
        whispers_sent = db.query(func.count(Whisper.id)).filter(Whisper.sender_id == user_id).scalar() or 0
        whispers_received = db.query(func.count(Whisper.id)).filter(Whisper.recipient_id == user_id).scalar() or 0
        
        # Get receives usage from membership
        membership = db.query(Membership).filter(Membership.user_id == user_id).first()
        receives_used = membership.receives_used if membership else 0
        
        return UserStatistics(
            totalWhispersSent=whispers_sent,
            totalWhispersReceived=whispers_received,
            totalMatches=0,  # Would need match calculation logic
            totalReceivesUsed=receives_used,
            joinDate=user.created_at,
            lastActiveDate=user.profile.last_active if user.profile else None
        )
        
    except Exception as e:
        logger.error(f"Failed to get user statistics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get statistics: {str(e)}")

# ============================================================================
# Whisper Settings (from WhisperService in frontend API)
# ============================================================================

@router.get("/whispers", response_model=WhisperSettings)
async def get_whisper_settings(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get whisper settings
    Frontend API: GET /whispers/settings
    """
    try:
        user_id = current_user["id"]
        settings = await get_or_create_user_settings(db, user_id)
        
        # Get WeChat ID from user profile
        profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
        wechat_id = profile.wechat_id if profile and profile.wechat_id else ""
        
        return WhisperSettings(
            wechatId=wechat_id,
            customMessage=settings.custom_message,
            autoAccept=settings.whisper_auto_accept,
            showOnlineStatus=settings.whisper_show_status,
            enableNotifications=settings.whisper_enable_notifications
        )
        
    except Exception as e:
        logger.error(f"Failed to get whisper settings: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get whisper settings: {str(e)}")

@router.put("/whispers")
async def update_whisper_settings(
    request: UpdateWhisperSettings,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update whisper settings
    Frontend API: PUT /whispers/settings
    """
    try:
        user_id = current_user["id"]
        settings = await get_or_create_user_settings(db, user_id)
        
        # Update whisper settings (only provided fields)
        if request.customMessage is not None:
            settings.custom_message = request.customMessage
        if request.autoAccept is not None:
            settings.whisper_auto_accept = request.autoAccept
        if request.showOnlineStatus is not None:
            settings.whisper_show_status = request.showOnlineStatus
        if request.enableNotifications is not None:
            settings.whisper_enable_notifications = request.enableNotifications
        
        settings.updated_at = datetime.utcnow()
        db.commit()
        
        return {"success": True, "message": "Whisper settings updated successfully"}
        
    except Exception as e:
        logger.error(f"Failed to update whisper settings: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update whisper settings: {str(e)}")

# ============================================================================
# Account Management
# ============================================================================

@router.post("/logout")
async def logout_user(
    request: LogoutRequest = None,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Logout user
    Frontend API: POST /auth/logout
    """
    try:
        # In a real implementation, you would invalidate tokens here
        # For now, just return success
        all_devices = request.allDevices if request else False
        
        logger.info(f"User {current_user['id']} logged out (all_devices: {all_devices})")
        
        return {"success": True, "message": "Logged out successfully"}
        
    except Exception as e:
        logger.error(f"Failed to logout user: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to logout: {str(e)}")

@router.post("/account/delete", response_model=DeleteAccountResponse)
async def delete_account(
    request: DeleteAccountRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete user account
    Frontend API: POST /account/delete
    """
    try:
        user_id = current_user["id"]
        
        # In a real implementation, you would:
        # 1. Verify password
        # 2. Mark account for deletion
        # 3. Schedule data anonymization
        # 4. Send confirmation email
        
        logger.warning(f"Account deletion requested for user {user_id}: {request.reason}")
        
        return DeleteAccountResponse(
            message="Account deletion scheduled. You have 30 days to recover your account.",
            deletedAt=datetime.utcnow(),
            dataRetentionDays=30
        )
        
    except Exception as e:
        logger.error(f"Failed to delete account: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete account: {str(e)}")

@router.post("/account/export", response_model=ExportDataResponse)
async def export_account_data(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Export user data
    Frontend API: POST /account/export
    """
    try:
        user_id = current_user["id"]
        
        # In a real implementation, you would:
        # 1. Generate data export
        # 2. Create secure download link
        # 3. Set expiration time
        
        logger.info(f"Data export requested for user {user_id}")
        
        return ExportDataResponse(
            downloadUrl=f"https://api.example.com/export/{user_id}/download",
            expiresAt=datetime.utcnow() + timedelta(hours=24)
        )
        
    except Exception as e:
        logger.error(f"Failed to export data: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to export data: {str(e)}")

@router.get("/account/info", response_model=AccountInfo)
async def get_account_info(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get account information
    Frontend API: GET /account/info
    """
    try:
        user_id = current_user["id"]
        
        # Get user data
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get profile for email info
        profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
        
        return AccountInfo(
            userId=str(user_id),
            email=profile.university_email if profile else None,
            phoneNumber=user.phone_number,
            createdAt=user.created_at,
            lastLoginAt=None,  # Would need session tracking
            dataRetentionDays=30
        )
        
    except Exception as e:
        logger.error(f"Failed to get account info: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get account info: {str(e)}")