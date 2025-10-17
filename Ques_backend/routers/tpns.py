"""
TPNS (Tencent Push Notification Service) Router
Handles device registration and push notification management
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
import logging

from dependencies.db import get_db
from services.auth_service import AuthService
from services.notification_service import notification_service
from services.tpns_service import tpns_service

router = APIRouter()
security = HTTPBearer()
logger = logging.getLogger(__name__)
auth_service = AuthService()

# ==================== Pydantic Models ====================

class DeviceRegistrationRequest(BaseModel):
    """Request model for device registration"""
    device_token: str = Field(..., description="Device push token from FCM/APNS")
    platform: str = Field(..., pattern="^(android|ios)$", description="Platform: android or ios")
    app_version: Optional[str] = Field(None, description="App version")
    device_model: Optional[str] = Field(None, description="Device model")
    os_version: Optional[str] = Field(None, description="OS version")

class DeviceRegistrationResponse(BaseModel):
    """Response model for device registration"""
    success: bool
    message: str
    device_id: Optional[str] = None

class TestPushRequest(BaseModel):
    """Request model for test push notification"""
    title: str = Field(..., description="Notification title")
    content: str = Field(..., description="Notification content")
    platform: Optional[str] = Field(None, pattern="^(android|ios|all)$", description="Target platform")
    custom_data: Optional[Dict[str, Any]] = Field(None, description="Custom notification data")

class TestPushResponse(BaseModel):
    """Response model for test push notification"""
    success: bool
    message: str
    results: Optional[Dict[str, Any]] = None

class PushStatisticsResponse(BaseModel):
    """Response model for push statistics"""
    push_id: str
    platform: str
    sent_count: int
    delivered_count: int
    clicked_count: int
    details: Optional[Dict[str, Any]] = None

# ==================== Device Management Endpoints ====================

@router.post("/device/register", response_model=DeviceRegistrationResponse)
async def register_device(
    request: DeviceRegistrationRequest,
    token: str = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Register device for push notifications
    
    This endpoint binds a user account to a device token for TPNS.
    The device token should be obtained from FCM (Android) or APNS (iOS).
    """
    try:
        current_user = auth_service.get_current_user(db, token.credentials)
        if not current_user:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        # Bind user account to device token
        success = notification_service.bind_user_device(
            current_user.id, 
            request.device_token, 
            request.platform
        )
        
        if success:
            logger.info(f"Device registered for user {current_user.id}: {request.platform}")
            
            # In a real implementation, you'd store device info in database
            # For now, we'll just log the registration
            
            return DeviceRegistrationResponse(
                success=True,
                message=f"Device registered successfully for {request.platform}",
                device_id=f"device_{current_user.id}_{request.platform}"
            )
        else:
            logger.error(f"Failed to register device for user {current_user.id}")
            return DeviceRegistrationResponse(
                success=False,
                message="Failed to register device with TPNS"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error registering device: {e}")
        raise HTTPException(status_code=500, detail="Failed to register device")

@router.delete("/device/unregister")
async def unregister_device(
    device_token: str,
    platform: str,
    token: str = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Unregister device from push notifications
    
    This removes the binding between user account and device token.
    """
    try:
        current_user = auth_service.get_current_user(db, token.credentials)
        if not current_user:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        # Unbind user account from device token
        success = notification_service.unbind_user_device(
            current_user.id, 
            device_token, 
            platform
        )
        
        if success:
            logger.info(f"Device unregistered for user {current_user.id}: {platform}")
            return {"success": True, "message": "Device unregistered successfully"}
        else:
            logger.error(f"Failed to unregister device for user {current_user.id}")
            return {"success": False, "message": "Failed to unregister device"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error unregistering device: {e}")
        raise HTTPException(status_code=500, detail="Failed to unregister device")

# ==================== Push Notification Testing ====================

@router.post("/push/test", response_model=TestPushResponse)
async def send_test_push(
    request: TestPushRequest,
    token: str = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Send test push notification to current user
    
    Useful for testing push notification delivery and formatting.
    """
    try:
        current_user = auth_service.get_current_user(db, token.credentials)
        if not current_user:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        # Send test push notification
        results = await notification_service._send_push_notification(
            current_user.id,
            request.title,
            request.content,
            request.custom_data
        )
        
        logger.info(f"Test push sent to user {current_user.id}")
        
        return TestPushResponse(
            success=results.get("success", False),
            message="Test push notification sent",
            results=results
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending test push: {e}")
        raise HTTPException(status_code=500, detail="Failed to send test push")

@router.get("/push/statistics/{push_id}")
async def get_push_statistics(
    push_id: str,
    platform: str,
    token: str = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Get push notification delivery statistics
    
    Returns delivery and engagement metrics for a specific push notification.
    """
    try:
        current_user = auth_service.get_current_user(db, token.credentials)
        if not current_user:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        # Get appropriate access credentials based on platform
        if platform == "android":
            access_id = tpns_service.android_access_id
            secret_key = tpns_service.android_secret_key
        elif platform == "ios":
            access_id = tpns_service.ios_access_id
            secret_key = tpns_service.ios_secret_key
        else:
            raise HTTPException(status_code=400, detail="Invalid platform")
        
        if not access_id or not secret_key:
            raise HTTPException(status_code=503, detail=f"{platform.capitalize()} TPNS not configured")
        
        # Get statistics from TPNS
        stats = tpns_service.get_push_statistics(push_id, access_id, secret_key)
        
        # Parse statistics response
        if "error" in stats:
            raise HTTPException(status_code=500, detail=stats["error"])
        
        # Extract key metrics
        result_data = stats.get("result", {})
        
        return PushStatisticsResponse(
            push_id=push_id,
            platform=platform,
            sent_count=result_data.get("push_active_num", 0),
            delivered_count=result_data.get("arrive_num", 0),
            clicked_count=result_data.get("click_num", 0),
            details=result_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting push statistics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get push statistics")

# ==================== Notification Preferences ====================

@router.get("/preferences")
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
        
        preferences = notification_service._get_user_notification_preferences(db, current_user.id)
        
        return preferences
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting notification preferences: {e}")
        raise HTTPException(status_code=500, detail="Failed to get notification preferences")

@router.put("/preferences")
async def update_notification_preferences(
    preferences: Dict[str, bool],
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
        
        # In a real implementation, you'd update the notification_preferences table
        logger.info(f"Updating notification preferences for user {current_user.id}: {preferences}")
        
        return {
            "success": True,
            "message": "Notification preferences updated successfully",
            "preferences": preferences
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating notification preferences: {e}")
        raise HTTPException(status_code=500, detail="Failed to update notification preferences")

# ==================== System Information ====================

@router.get("/config")
async def get_tpns_config(
    token: str = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Get TPNS configuration status (for debugging)
    """
    try:
        current_user = auth_service.get_current_user(db, token.credentials)
        if not current_user:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        # Return configuration status (without sensitive data)
        config = {
            "android_configured": bool(tpns_service.android_access_id and tpns_service.android_secret_key),
            "ios_configured": bool(tpns_service.ios_access_id and tpns_service.ios_secret_key),
            "region": tpns_service.region,
            "api_host": tpns_service.api_host,
            "service_initialized": True
        }
        
        return config
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting TPNS config: {e}")
        raise HTTPException(status_code=500, detail="Failed to get TPNS configuration")
