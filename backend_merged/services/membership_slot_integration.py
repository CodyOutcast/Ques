"""
Membership Slot Integration Service
Handles slot allocation changes when user membership changes
"""

import logging
from typing import Optional
from datetime import datetime, timedelta

from services.project_slots_service import ProjectSlotsService
from services.membership_service import MembershipService
from models.user_membership import MembershipType
from models.project_slots import UserSlotConfiguration

logger = logging.getLogger(__name__)

class MembershipSlotIntegrationService:
    """
    Service to integrate membership changes with slot allocations
    """
    
    def __init__(self):
        self.slots_service = ProjectSlotsService()
        self.membership_service = MembershipService()
    
    def handle_membership_upgrade(
        self,
        user_id: int, 
        old_membership: str,
        new_membership: str,
        subscription_end_date: Optional[datetime] = None
    ) -> bool:
        """
        Handle user membership upgrade - increase slot allocation
        
        Args:
            user_id: ID of the user
            old_membership: Previous membership type
            new_membership: New membership type  
            subscription_end_date: When subscription ends (None for permanent)
        
        Returns:
            True if handled successfully
        """
        try:
            logger.info(f"Processing membership upgrade for user {user_id}: {old_membership} → {new_membership}")
            
            # Determine if upgrade is permanent
            permanent = subscription_end_date is None
            
            # Update slot allocation
            success = self.slots_service.update_user_membership_slots(
                user_id=user_id,
                membership_type=new_membership,
                expires_at=subscription_end_date,
                permanent=permanent
            )
            
            if success:
                logger.info(f"Upgraded slot allocation for user {user_id} to {new_membership}")
            else:
                logger.error(f"Failed to upgrade slot allocation for user {user_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error handling membership upgrade for user {user_id}: {str(e)}")
            return False
    
    def handle_membership_downgrade(
        self,
        user_id: int,
        old_membership: str,
        new_membership: str
    ) -> bool:
        """
        Handle user membership downgrade - reduce slot allocation
        
        Args:
            user_id: ID of the user
            old_membership: Previous membership type
            new_membership: New membership type (usually "basic")
        
        Returns:
            True if handled successfully
        """
        try:
            logger.info(f"Processing membership downgrade for user {user_id}: {old_membership} → {new_membership}")
            
            # Update slot allocation (this will automatically deactivate excess slots)
            success = self.slots_service.update_user_membership_slots(
                user_id=user_id,
                membership_type=new_membership,
                expires_at=None,
                permanent=False
            )
            
            if success:
                logger.info(f"Downgraded slot allocation for user {user_id} to {new_membership}")
            else:
                logger.error(f"Failed to downgrade slot allocation for user {user_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error handling membership downgrade for user {user_id}: {str(e)}")
            return False
    
    def handle_membership_expiration(self, user_id: int) -> bool:
        """
        Handle membership expiration - reduce slots to basic level
        
        Args:
            user_id: ID of the user
        
        Returns:
            True if handled successfully
        """
        try:
            logger.info(f"Processing membership expiration for user {user_id}")
            
            # Downgrade to basic membership
            return self.handle_membership_downgrade(
                user_id=user_id,
                old_membership="pro",  # Assume was premium
                new_membership="basic"
            )
            
        except Exception as e:
            logger.error(f"Error handling membership expiration for user {user_id}: {str(e)}")
            return False
    
    def handle_subscription_purchase(
        self,
        user_id: int,
        membership_type: str,
        duration_months: int
    ) -> bool:
        """
        Handle new subscription purchase
        
        Args:
            user_id: ID of the user
            membership_type: Type of membership purchased
            duration_months: Duration in months
        
        Returns:
            True if handled successfully
        """
        try:
            # Calculate subscription end date
            subscription_end = datetime.utcnow() + timedelta(days=duration_months * 30)
            
            # Get current membership
            current_membership = self.membership_service.get_user_membership_type(user_id)
            current_membership_str = current_membership.value if current_membership else "basic"
            
            return self.handle_membership_upgrade(
                user_id=user_id,
                old_membership=current_membership_str,
                new_membership=membership_type,
                subscription_end_date=subscription_end
            )
            
        except Exception as e:
            logger.error(f"Error handling subscription purchase for user {user_id}: {str(e)}")
            return False
    
    def handle_subscription_cancellation(self, user_id: int) -> bool:
        """
        Handle subscription cancellation - set expiration date
        
        Args:
            user_id: ID of the user
        
        Returns:
            True if handled successfully
        """
        try:
            logger.info(f"Processing subscription cancellation for user {user_id}")
            
            # Get current subscription end date from membership service
            # For now, we'll let the membership expire naturally
            # The check_and_expire_memberships method will handle the actual slot reduction
            
            logger.info(f"Subscription cancelled for user {user_id}, will expire naturally")
            return True
            
        except Exception as e:
            logger.error(f"Error handling subscription cancellation for user {user_id}: {str(e)}")
            return False
    
    def run_daily_membership_check(self) -> dict:
        """
        Daily job to check for expired memberships and update slot allocations
        
        Returns:
            Dictionary with processing results
        """
        try:
            logger.info("Running daily membership expiration check")
            
            # Check for expired memberships and reduce slots
            expired_count = self.slots_service.check_and_expire_memberships()
            
            results = {
                "expired_memberships": expired_count,
                "timestamp": datetime.utcnow().isoformat(),
                "status": "success"
            }
            
            logger.info(f"Daily membership check complete: {expired_count} memberships expired")
            return results
            
        except Exception as e:
            logger.error(f"Error in daily membership check: {str(e)}")
            return {
                "expired_memberships": 0,
                "timestamp": datetime.utcnow().isoformat(),
                "status": "error",
                "error": str(e)
            }
    
    def get_user_slot_info(self, user_id: int) -> dict:
        """
        Get comprehensive slot information for a user
        
        Args:
            user_id: ID of the user
        
        Returns:
            Dictionary with slot information
        """
        try:
            # Get slot statistics
            stats = self.slots_service.get_slot_statistics(user_id)
            
            # Get membership info
            membership_type = self.membership_service.get_user_membership_type(user_id)
            membership_str = membership_type.value if membership_type else "basic"
            
            # Get slot configuration
            from dependencies.db import get_db_connection
            
            # This should be injected in a real implementation
            db = get_db_connection()
            try:
                config = db.query(UserSlotConfiguration).filter(
                    UserSlotConfiguration.user_id == user_id
                ).first()
            finally:
                db.close()
            
            info = {
                "user_id": user_id,
                "current_membership": membership_str,
                "slot_statistics": stats,
                "membership_benefits": {
                    "basic": {"max_slots": 2, "description": "Basic users get 2 project slots"},
                    "pro": {"max_slots": 10, "description": "Pro users get 10 project slots"},
                    "ai-powered": {"max_slots": 10, "description": "AI-Powered users get 10 project slots"}
                }
            }
            
            return info
            
        except Exception as e:
            logger.error(f"Error getting slot info for user {user_id}: {str(e)}")
            return {
                "user_id": user_id,
                "error": str(e)
            }
