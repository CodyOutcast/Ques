"""
Settings management API router
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import Optional, List

from dependencies.db import get_db
from dependencies.auth import get_current_user
from models.users import User
from services.settings_service import SettingsService
from schemas.settings_schemas import (
    AccountSettingsResponse, UpdateAccountSettingsRequest,
    PrivacyConsentRequest, PrivacyConsentResponse,
    AccountActionRequest, AccountActionResponse,
    DataExportRequest, DataExportResponse,
    DeactivateAccountRequest, DeleteAccountRequest, AccountDeletionResponse,
    ChangePasswordRequest, PasswordChangeResponse,
    SessionManagementResponse, SettingsSummaryResponse
)
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


def get_client_ip(request: Request) -> str:
    """Extract client IP address from request"""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host


def get_user_agent(request: Request) -> str:
    """Extract user agent from request"""
    return request.headers.get("User-Agent", "")


@router.get("/account", response_model=AccountSettingsResponse)
async def get_account_settings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user account settings"""
    try:
        service = SettingsService(db)
        settings = service.get_account_settings(current_user.id)
        
        if not settings:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Settings not found"
            )
        
        return settings
        
    except Exception as e:
        logger.error(f"Error getting account settings for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve account settings"
        )


@router.put("/account", response_model=AccountSettingsResponse)
async def update_account_settings(
    updates: UpdateAccountSettingsRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user account settings"""
    try:
        service = SettingsService(db)
        
        success = service.update_account_settings(
            user_id=current_user.id,
            updates=updates,
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request)
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update settings"
            )
        
        # Return updated settings
        updated_settings = service.get_account_settings(current_user.id)
        return updated_settings
        
    except Exception as e:
        logger.error(f"Error updating account settings for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update account settings"
        )


@router.get("/privacy", response_model=AccountSettingsResponse)
async def get_privacy_settings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get privacy settings (alias for account settings)"""
    return await get_account_settings(current_user, db)


@router.put("/privacy", response_model=AccountSettingsResponse)
async def update_privacy_settings(
    updates: UpdateAccountSettingsRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update privacy settings (alias for account settings update)"""
    return await update_account_settings(updates, request, current_user, db)


@router.get("/security", response_model=dict)
async def get_security_settings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get security settings and security score"""
    try:
        service = SettingsService(db)
        settings = service.get_account_settings(current_user.id)
        security_score = service.get_security_score(current_user.id)
        
        if not settings:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Settings not found"
            )
        
        return {
            "security": settings.security,
            "two_factor_enabled": settings.security.two_factor_enabled,
            "security_score": security_score["score"],
            "recommendations": security_score["recommendations"]
        }
        
    except Exception as e:
        logger.error(f"Error getting security settings for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve security settings"
        )


@router.put("/security", response_model=dict)
async def update_security_settings(
    updates: UpdateAccountSettingsRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update security settings"""
    try:
        service = SettingsService(db)
        
        # Only allow security-related updates
        security_only_updates = UpdateAccountSettingsRequest(
            security=updates.security
        )
        
        success = service.update_account_settings(
            user_id=current_user.id,
            updates=security_only_updates,
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request)
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update security settings"
            )
        
        # Return updated security info
        return await get_security_settings(current_user, db)
        
    except Exception as e:
        logger.error(f"Error updating security settings for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update security settings"
        )


@router.post("/data-privacy/consent")
async def record_privacy_consent(
    consent_request: PrivacyConsentRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Record privacy consent for GDPR compliance"""
    try:
        service = SettingsService(db)
        
        success = service.record_privacy_consent(
            user_id=current_user.id,
            consent_request=consent_request,
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request)
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to record privacy consent"
            )
        
        return {"success": True, "message": "Privacy consent recorded successfully"}
        
    except Exception as e:
        logger.error(f"Error recording privacy consent for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to record privacy consent"
        )


@router.post("/data-privacy/export")
async def request_data_export(
    export_request: DataExportRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Request data export for GDPR compliance"""
    try:
        service = SettingsService(db)
        
        export_id = service.request_data_export(
            user_id=current_user.id,
            export_request=export_request
        )
        
        if not export_id:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create data export request"
            )
        
        return {
            "success": True,
            "export_id": export_id,
            "message": "Data export request created. You will receive an email when ready.",
            "estimated_completion": "24-48 hours"
        }
        
    except Exception as e:
        logger.error(f"Error creating data export request for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create data export request"
        )


@router.post("/account/deactivate")
async def deactivate_account(
    deactivate_request: DeactivateAccountRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Deactivate user account"""
    try:
        service = SettingsService(db)
        
        success = service.deactivate_account(
            user_id=current_user.id,
            reason=deactivate_request.reason,
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request)
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to deactivate account"
            )
        
        return {
            "success": True,
            "message": "Account has been deactivated. You can reactivate by logging in again.",
            "reactivation_instructions": "Simply log in again to reactivate your account"
        }
        
    except Exception as e:
        logger.error(f"Error deactivating account for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to deactivate account"
        )


@router.post("/account/delete", response_model=AccountDeletionResponse)
async def schedule_account_deletion(
    delete_request: DeleteAccountRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Schedule account deletion with 30-day grace period"""
    try:
        service = SettingsService(db)
        
        result = service.schedule_account_deletion(
            user_id=current_user.id,
            reason=delete_request.reason,
            confirmation_text=delete_request.confirmation_text,
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request)
        )
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to schedule account deletion"
            )
        
        return AccountDeletionResponse(**result)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error scheduling account deletion for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to schedule account deletion"
        )


@router.get("/summary", response_model=SettingsSummaryResponse)
async def get_settings_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive settings summary"""
    try:
        service = SettingsService(db)
        
        # Get account settings
        account_settings = service.get_account_settings(current_user.id)
        if not account_settings:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Settings not found"
            )
        
        # Get security score
        security_info = service.get_security_score(current_user.id)
        
        # TODO: Get privacy consents and pending actions from database
        # For now, return empty lists
        privacy_consents = []
        pending_actions = []
        
        return SettingsSummaryResponse(
            account_settings=account_settings,
            two_factor_enabled=account_settings.security.two_factor_enabled,
            privacy_consents=privacy_consents,
            pending_actions=pending_actions,
            security_score=security_info["score"],
            recommendations=security_info["recommendations"]
        )
        
    except Exception as e:
        logger.error(f"Error getting settings summary for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve settings summary"
        )


@router.get("/", response_model=AccountSettingsResponse)
async def get_user_settings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user settings (alias for account settings)"""
    return await get_account_settings(current_user, db)


@router.put("/", response_model=AccountSettingsResponse)
async def update_user_settings(
    updates: UpdateAccountSettingsRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user settings (alias for account settings update)"""
    return await update_account_settings(updates, request, current_user, db)