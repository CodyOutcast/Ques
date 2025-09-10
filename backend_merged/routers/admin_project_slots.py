"""
Admin Project Slots Router
Administrative endpoints for managing slot system and membership integration
"""

import logging
from typing import Dict, Any, List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from dependencies.db import get_db
from dependencies.auth import get_current_admin_user
from services.membership_slot_integration import MembershipSlotIntegrationService
from services.task_scheduler import get_task_scheduler
from services.project_slots_service import ProjectSlotsService
from models.users import User

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/admin/slots", tags=["Admin - Project Slots"])

@router.get("/statistics/global", response_model=Dict[str, Any])
async def get_global_slot_statistics(
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Get global slot system statistics (admin only)
    """
    try:
        service = ProjectSlotsService()
        service.db_session = db
        
        # Get overall statistics
        stats = service.get_global_slot_statistics()
        
        return {
            "status": "success",
            "data": stats,
            "admin_user": current_user.username
        }
        
    except Exception as e:
        logger.error(f"Error getting global slot statistics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get slot statistics: {str(e)}"
        )

@router.get("/users/{user_id}/info")
async def get_user_slot_info(
    user_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Get detailed slot information for a specific user (admin only)
    """
    try:
        integration_service = MembershipSlotIntegrationService()
        
        # Get comprehensive user slot info
        info = integration_service.get_user_slot_info(user_id)
        
        return info
        
    except Exception as e:
        logger.error(f"Error getting user slot info for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user slot info: {str(e)}"
        )

@router.post("/membership/check", response_model=Dict[str, Any])
async def run_membership_check(
    current_user: User = Depends(get_current_admin_user)
):
    """
    Manually trigger membership expiration check (admin only)
    """
    try:
        scheduler = get_task_scheduler()
        
        # Run membership check immediately
        results = await scheduler.run_membership_check_now()
        
        return {
            "status": "success",
            "message": "Membership check completed",
            "results": results,
            "admin_user": current_user.username
        }
        
    except Exception as e:
        logger.error(f"Error running manual membership check: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to run membership check: {str(e)}"
        )

@router.post("/users/{user_id}/membership/update")
async def update_user_membership_slots(
    user_id: int,
    membership_type: str,
    permanent: bool = False,
    expires_in_days: int = 30,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Manually update a user's membership slots (admin only)
    """
    try:
        from datetime import datetime, timedelta
        
        integration_service = MembershipSlotIntegrationService()
        
        # Calculate expiration date
        expires_at = None if permanent else datetime.utcnow() + timedelta(days=expires_in_days)
        
        # Update membership slots
        success = integration_service.handle_membership_upgrade(
            user_id=user_id,
            old_membership="basic",  # We don't know the old one, assume basic
            new_membership=membership_type,
            subscription_end_date=expires_at
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to update user membership slots"
            )
        
        return {
            "status": "success",
            "message": f"Updated membership slots for user {user_id}",
            "membership_type": membership_type,
            "permanent": permanent,
            "expires_at": expires_at.isoformat() if expires_at else None,
            "admin_user": current_user.username
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating membership slots for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update membership slots: {str(e)}"
        )

@router.get("/users/with-active-memberships")
async def get_users_with_active_memberships(
    limit: int = 100,
    offset: int = 0,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Get list of users with active premium memberships (admin only)
    """
    try:
        from models.project_slots import UserSlotConfiguration
        
        # Query users with active bonus slots
        configs = db.query(UserSlotConfiguration).filter(
            UserSlotConfiguration.bonus_slots > 0,
            UserSlotConfiguration.bonus_expires_at > datetime.utcnow()
        ).offset(offset).limit(limit).all()
        
        users_info = []
        for config in configs:
            user_info = {
                "user_id": config.user_id,
                "base_slots": config.base_slots,
                "bonus_slots": config.bonus_slots,
                "total_slots": config.current_max_slots,
                "bonus_expires_at": config.bonus_expires_at.isoformat() if config.bonus_expires_at else None,
                "permanent": config.permanent
            }
            users_info.append(user_info)
        
        return {
            "status": "success",
            "users": users_info,
            "count": len(users_info),
            "offset": offset,
            "limit": limit
        }
        
    except Exception as e:
        logger.error(f"Error getting users with active memberships: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get users with memberships: {str(e)}"
        )

@router.post("/maintenance/clean-expired-slots")
async def clean_expired_slots(
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Clean up expired slots and deactivate excess slots (admin only)
    """
    try:
        service = ProjectSlotsService()
        service.db_session = db
        
        # Run cleanup
        expired_count = service.check_and_expire_memberships()
        
        return {
            "status": "success",
            "message": "Slot cleanup completed",
            "expired_memberships": expired_count,
            "admin_user": current_user.username
        }
        
    except Exception as e:
        logger.error(f"Error cleaning expired slots: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to clean expired slots: {str(e)}"
        )
