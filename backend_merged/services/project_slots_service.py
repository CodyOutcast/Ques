"""
Project Slots Service
Manages user project card slots for saving AI recommendations
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func
from datetime import datetime, timedelta

from models.project_slots import ProjectCardSlot, SlotStatus, SlotSource, UserSlotConfiguration
from models.users import User
from models.project_cards import ProjectCard
from dependencies.db import get_db

logger = logging.getLogger(__name__)

class ProjectSlotsService:
    """
    Service for managing user project card slots
    """
    
    def __init__(self):
        self.db_session = next(get_db())
    
    def initialize_user_slots(self, user_id: int, membership_type: str = "basic") -> bool:
        """
        Initialize slot configuration for a new user based on membership
        
        Args:
            user_id: ID of the user
            membership_type: "basic", "pro", or "ai-powered"
        
        Returns:
            True if initialized successfully
        """
        try:
            # Check if user already has configuration
            existing_config = self.db_session.query(UserSlotConfiguration).filter(
                UserSlotConfiguration.user_id == user_id
            ).first()
            
            if existing_config:
                logger.info(f"User {user_id} already has slot configuration")
                return True
            
            # Create new configuration based on membership
            config = UserSlotConfiguration(
                user_id=user_id,
                base_slots=2,  # All users get 2 base slots
                bonus_slots=8 if membership_type in ["pro", "ai-powered"] else 0,
                auto_save_recommendations=True,
                stop_recommendations_on_save=True
            )
            
            # Set membership expiration if not basic
            if membership_type != "basic":
                # For new premium users, set membership to permanent initially
                # This will be updated by the membership service when actual subscription is created
                config.membership_slots_permanent = True
            
            self.db_session.add(config)
            self.db_session.commit()
            
            max_slots = config.current_max_slots
            logger.info(f"Initialized slot configuration for user {user_id} with {max_slots} slots (membership: {membership_type})")
            return True
            
        except Exception as e:
            logger.error(f"Error initializing slots for user {user_id}: {str(e)}")
            self.db_session.rollback()
            return False
    
    def update_user_membership_slots(
        self, 
        user_id: int, 
        membership_type: str, 
        expires_at: Optional[datetime] = None,
        permanent: bool = False
    ) -> bool:
        """
        Update user's slot allocation based on membership changes
        
        Args:
            user_id: ID of the user
            membership_type: "basic", "pro", or "ai-powered"
            expires_at: When membership expires (None for permanent)
            permanent: Whether the membership is permanent
        
        Returns:
            True if updated successfully
        """
        try:
            # Get or create user configuration
            config = self.db_session.query(UserSlotConfiguration).filter(
                UserSlotConfiguration.user_id == user_id
            ).first()
            
            if not config:
                # Initialize if doesn't exist
                self.initialize_user_slots(user_id, membership_type)
                config = self.db_session.query(UserSlotConfiguration).filter(
                    UserSlotConfiguration.user_id == user_id
                ).first()
            
            # Update membership slots
            old_max = config.current_max_slots
            config.update_membership_slots(membership_type, expires_at, permanent)
            new_max = config.current_max_slots
            
            self.db_session.commit()
            
            # If slots reduced, handle deactivation of excess slots
            if new_max < old_max:
                self._deactivate_excess_slots(user_id, new_max)
            
            logger.info(f"Updated slots for user {user_id}: {old_max} → {new_max} (membership: {membership_type})")
            return True
            
        except Exception as e:
            logger.error(f"Error updating membership slots for user {user_id}: {str(e)}")
            self.db_session.rollback()
            return False
    
    def check_and_expire_memberships(self) -> int:
        """
        Check for expired memberships and reduce slot allocations
        
        Returns:
            Number of users whose slots were reduced
        """
        try:
            now = datetime.utcnow()
            expired_configs = self.db_session.query(UserSlotConfiguration).filter(
                and_(
                    UserSlotConfiguration.membership_expires_at <= now,
                    UserSlotConfiguration.membership_slots_permanent == False,
                    UserSlotConfiguration.bonus_slots > 0
                )
            ).all()
            
            count = 0
            for config in expired_configs:
                old_max = config.current_max_slots
                config.bonus_slots = 0  # Remove bonus slots
                config.membership_expires_at = None
                new_max = config.current_max_slots
                
                # Deactivate excess slots
                self._deactivate_excess_slots(config.user_id, new_max)
                
                count += 1
                logger.info(f"Expired membership for user {config.user_id}: {old_max} → {new_max} slots")
            
            if count > 0:
                self.db_session.commit()
                
            return count
            
        except Exception as e:
            logger.error(f"Error expiring memberships: {str(e)}")
            self.db_session.rollback()
            return 0
    
    def _deactivate_excess_slots(self, user_id: int, max_allowed: int) -> None:
        """
        Deactivate slots beyond the allowed limit
        Keeps the most recently updated slots active
        """
        try:
            # Get all occupied/activated slots ordered by last update (keep most recent)
            slots = self.db_session.query(ProjectCardSlot).filter(
                and_(
                    ProjectCardSlot.user_id == user_id,
                    or_(
                        ProjectCardSlot.status == SlotStatus.OCCUPIED.value,
                        ProjectCardSlot.status == SlotStatus.ACTIVATED.value
                    )
                )
            ).order_by(desc(ProjectCardSlot.updated_at)).all()
            
            # Deactivate excess slots (beyond max_allowed)
            excess_slots = slots[max_allowed:]
            for slot in excess_slots:
                if slot.status == SlotStatus.ACTIVATED.value:
                    # Deactivate but keep content
                    slot.status = SlotStatus.OCCUPIED.value
                    slot.is_activated = False
                    slot.activated_at = None
                    slot.updated_at = datetime.utcnow()
                    
                    logger.info(f"Deactivated excess slot {slot.slot_id} for user {user_id}")
            
        except Exception as e:
            logger.error(f"Error deactivating excess slots for user {user_id}: {str(e)}")
    
    def get_user_slots(self, user_id: int) -> List[Dict[str, Any]]:
        """
        Get all slots for a user
        
        Args:
            user_id: ID of the user
        
        Returns:
            List of slot dictionaries
        """
        try:
            slots = self.db_session.query(ProjectCardSlot).filter(
                ProjectCardSlot.user_id == user_id
            ).order_by(ProjectCardSlot.slot_number).all()
            
            slot_list = []
            for slot in slots:
                slot_data = {
                    "slot_id": slot.slot_id,
                    "slot_number": slot.slot_number,
                    "slot_name": slot.slot_name,
                    "status": slot.status.value,
                    "source": slot.source.value,
                    "created_at": slot.created_at.isoformat(),
                    "updated_at": slot.updated_at.isoformat()
                }
                
                # Add project data if slot is occupied
                if slot.status == SlotStatus.OCCUPIED:
                    slot_data.update({
                        "title": slot.title,
                        "description": slot.description,
                        "short_description": slot.short_description,
                        "category": slot.category,
                        "industry": slot.industry,
                        "project_type": slot.project_type,
                        "stage": slot.stage,
                        "looking_for": slot.looking_for,
                        "skills_needed": slot.skills_needed,
                        "image_urls": slot.image_urls,
                        "video_url": slot.video_url,
                        "demo_url": slot.demo_url,
                        "pitch_deck_url": slot.pitch_deck_url,
                        "funding_goal": slot.funding_goal,
                        "equity_offered": slot.equity_offered,
                        "current_valuation": slot.current_valuation,
                        "revenue": slot.revenue,
                        "ai_recommendation_id": slot.ai_recommendation_id,
                        "ai_confidence_score": slot.ai_confidence_score,
                        "ai_reasoning": slot.ai_reasoning,
                        "original_query": slot.original_query
                    })
                
                # Add publication info if published
                if slot.status == SlotStatus.PUBLISHED:
                    slot_data.update({
                        "published_project_id": slot.published_project_id,
                        "published_at": slot.published_at.isoformat() if slot.published_at else None
                    })
                
                slot_list.append(slot_data)
            
            return slot_list
            
        except Exception as e:
            logger.error(f"Error getting slots for user {user_id}: {str(e)}")
            return []
    
    def get_available_slot(self, user_id: int) -> Optional[int]:
        """
        Get the next available slot number for a user
        
        Args:
            user_id: ID of the user
        
        Returns:
            Available slot number or None if all slots are occupied
        """
        try:
            # Get user's configuration
            config = self.db_session.query(UserSlotConfiguration).filter(
                UserSlotConfiguration.user_id == user_id
            ).first()
            
            max_slots = config.max_slots if config else 5
            
            # Get occupied slot numbers
            occupied_slots = self.db_session.query(ProjectCardSlot.slot_number).filter(
                and_(
                    ProjectCardSlot.user_id == user_id,
                    ProjectCardSlot.status == SlotStatus.OCCUPIED
                )
            ).all()
            
            occupied_numbers = {slot[0] for slot in occupied_slots}
            
            # Find first available slot number
            for slot_num in range(1, max_slots + 1):
                if slot_num not in occupied_numbers:
                    return slot_num
            
            return None  # All slots are occupied
            
        except Exception as e:
            logger.error(f"Error finding available slot for user {user_id}: {str(e)}")
            return None
    
    def save_recommendation_to_slot(
        self,
        user_id: int,
        recommendation_data: Dict[str, Any],
        slot_number: Optional[int] = None,
        slot_name: Optional[str] = None
    ) -> Optional[int]:
        """
        Save an AI recommendation to a user's slot
        
        Args:
            user_id: ID of the user
            recommendation_data: Full recommendation data from AI service
            slot_number: Specific slot number to use (optional)
            slot_name: Custom name for the slot (optional)
        
        Returns:
            Slot ID if saved successfully, None otherwise
        """
        try:
            # Get available slot if not specified
            if slot_number is None:
                slot_number = self.get_available_slot(user_id)
                if slot_number is None:
                    logger.warning(f"No available slots for user {user_id}")
                    return None
            
            # Check if slot number is already occupied
            existing_slot = self.db_session.query(ProjectCardSlot).filter(
                and_(
                    ProjectCardSlot.user_id == user_id,
                    ProjectCardSlot.slot_number == slot_number,
                    ProjectCardSlot.status == SlotStatus.OCCUPIED
                )
            ).first()
            
            if existing_slot:
                logger.warning(f"Slot {slot_number} already occupied for user {user_id}")
                return None
            
            # Create new slot or update existing empty slot
            slot = self.db_session.query(ProjectCardSlot).filter(
                and_(
                    ProjectCardSlot.user_id == user_id,
                    ProjectCardSlot.slot_number == slot_number
                )
            ).first()
            
            if not slot:
                slot = ProjectCardSlot(
                    user_id=user_id,
                    slot_number=slot_number,
                    status=SlotStatus.OCCUPIED,
                    source=SlotSource.AI_RECOMMENDATION
                )
                self.db_session.add(slot)
            else:
                slot.status = SlotStatus.OCCUPIED
                slot.source = SlotSource.AI_RECOMMENDATION
                slot.updated_at = datetime.utcnow()
            
            # Set slot name
            if slot_name:
                slot.slot_name = slot_name
            elif not slot.slot_name:
                slot.slot_name = f"AI Recommendation {slot_number}"
            
            # Fill slot with recommendation data
            slot.title = recommendation_data.get("title")
            slot.description = recommendation_data.get("description")
            slot.short_description = recommendation_data.get("short_description")
            slot.category = recommendation_data.get("category")
            slot.industry = recommendation_data.get("industry")
            slot.project_type = recommendation_data.get("project_type")
            slot.stage = recommendation_data.get("stage")
            slot.looking_for = recommendation_data.get("looking_for", [])
            slot.skills_needed = recommendation_data.get("skills_needed", [])
            slot.image_urls = recommendation_data.get("image_urls", [])
            slot.video_url = recommendation_data.get("video_url")
            slot.demo_url = recommendation_data.get("demo_url")
            slot.pitch_deck_url = recommendation_data.get("pitch_deck_url")
            slot.funding_goal = recommendation_data.get("funding_goal")
            slot.equity_offered = recommendation_data.get("equity_offered")
            slot.current_valuation = recommendation_data.get("current_valuation")
            slot.revenue = recommendation_data.get("revenue")
            
            # AI metadata
            slot.ai_recommendation_id = recommendation_data.get("ai_recommendation_id")
            slot.ai_confidence_score = recommendation_data.get("confidence_score")
            slot.ai_reasoning = recommendation_data.get("ai_reasoning")
            slot.original_query = recommendation_data.get("original_query")
            
            self.db_session.commit()
            
            logger.info(f"Saved recommendation to slot {slot_number} for user {user_id}")
            return slot.slot_id
            
        except Exception as e:
            logger.error(f"Error saving recommendation to slot for user {user_id}: {str(e)}")
            self.db_session.rollback()
            return None
    
    def update_slot_content(
        self,
        user_id: int,
        slot_id: int,
        updates: Dict[str, Any]
    ) -> bool:
        """
        Update content of a user's slot
        
        Args:
            user_id: ID of the user
            slot_id: ID of the slot to update
            updates: Dictionary of fields to update
        
        Returns:
            True if updated successfully
        """
        try:
            slot = self.db_session.query(ProjectCardSlot).filter(
                and_(
                    ProjectCardSlot.slot_id == slot_id,
                    ProjectCardSlot.user_id == user_id,
                    ProjectCardSlot.status == SlotStatus.OCCUPIED
                )
            ).first()
            
            if not slot:
                logger.warning(f"Slot {slot_id} not found for user {user_id}")
                return False
            
            # Update allowed fields
            updatable_fields = [
                "slot_name", "title", "description", "short_description",
                "category", "industry", "project_type", "stage",
                "looking_for", "skills_needed", "image_urls",
                "video_url", "demo_url", "pitch_deck_url",
                "funding_goal", "equity_offered", "current_valuation", "revenue"
            ]
            
            for field, value in updates.items():
                if field in updatable_fields and hasattr(slot, field):
                    setattr(slot, field, value)
            
            slot.updated_at = datetime.utcnow()
            self.db_session.commit()
            
            logger.info(f"Updated slot {slot_id} for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating slot {slot_id} for user {user_id}: {str(e)}")
            self.db_session.rollback()
            return False
    
    def activate_slot(self, user_id: int, slot_id: int) -> bool:
        """
        Activate a slot's content (make it visible/published)
        The content stays in the same slot but becomes active
        
        Args:
            user_id: ID of the user
            slot_id: ID of the slot to activate
        
        Returns:
            True if activated successfully, False otherwise
        """
        try:
            slot = self.db_session.query(ProjectCardSlot).filter(
                and_(
                    ProjectCardSlot.slot_id == slot_id,
                    ProjectCardSlot.user_id == user_id,
                    ProjectCardSlot.status == SlotStatus.OCCUPIED.value
                )
            ).first()
            
            if not slot:
                logger.warning(f"Slot {slot_id} not found or not occupied for user {user_id}")
                return False
            
            # Check if user has room for more activated slots
            config = self.db_session.query(UserSlotConfiguration).filter(
                UserSlotConfiguration.user_id == user_id
            ).first()
            
            if not config:
                # Initialize configuration if missing
                self.initialize_user_slots(user_id)
                config = self.db_session.query(UserSlotConfiguration).filter(
                    UserSlotConfiguration.user_id == user_id
                ).first()
            
            # Count currently activated slots
            activated_count = self.db_session.query(ProjectCardSlot).filter(
                and_(
                    ProjectCardSlot.user_id == user_id,
                    ProjectCardSlot.status == SlotStatus.ACTIVATED.value
                )
            ).count()
            
            # Check if user can activate more slots
            max_slots = config.current_max_slots
            if activated_count >= max_slots:
                logger.warning(f"User {user_id} has reached activation limit ({activated_count}/{max_slots})")
                return False
            
            # Activate the slot
            slot.status = SlotStatus.ACTIVATED.value
            slot.is_activated = True
            slot.activated_at = datetime.utcnow()
            slot.updated_at = datetime.utcnow()
            
            self.db_session.commit()
            
            logger.info(f"Activated slot {slot_id} for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error activating slot {slot_id} for user {user_id}: {str(e)}")
            self.db_session.rollback()
            return False
    
    def deactivate_slot(self, user_id: int, slot_id: int) -> bool:
        """
        Deactivate a slot's content (keep content but make it inactive)
        
        Args:
            user_id: ID of the user
            slot_id: ID of the slot to deactivate
        
        Returns:
            True if deactivated successfully, False otherwise
        """
        try:
            slot = self.db_session.query(ProjectCardSlot).filter(
                and_(
                    ProjectCardSlot.slot_id == slot_id,
                    ProjectCardSlot.user_id == user_id,
                    ProjectCardSlot.status == SlotStatus.ACTIVATED.value
                )
            ).first()
            
            if not slot:
                logger.warning(f"Slot {slot_id} not found or not activated for user {user_id}")
                return False
            
            # Deactivate the slot but keep content
            slot.status = SlotStatus.OCCUPIED.value
            slot.is_activated = False
            slot.activated_at = None
            slot.updated_at = datetime.utcnow()
            
            self.db_session.commit()
            
            logger.info(f"Deactivated slot {slot_id} for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deactivating slot {slot_id} for user {user_id}: {str(e)}")
            self.db_session.rollback()
            return False
    
    def clear_slot(self, user_id: int, slot_id: int) -> bool:
        """
        Clear a slot's content
        
        Args:
            user_id: ID of the user
            slot_id: ID of the slot to clear
        
        Returns:
            True if cleared successfully
        """
        try:
            slot = self.db_session.query(ProjectCardSlot).filter(
                and_(
                    ProjectCardSlot.slot_id == slot_id,
                    ProjectCardSlot.user_id == user_id
                )
            ).first()
            
            if not slot:
                logger.warning(f"Slot {slot_id} not found for user {user_id}")
                return False
            
            # Clear all content but keep the slot
            slot.status = SlotStatus.EMPTY
            slot.title = None
            slot.description = None
            slot.short_description = None
            slot.category = None
            slot.industry = None
            slot.project_type = None
            slot.stage = None
            slot.looking_for = None
            slot.skills_needed = None
            slot.image_urls = None
            slot.video_url = None
            slot.demo_url = None
            slot.pitch_deck_url = None
            slot.funding_goal = None
            slot.equity_offered = None
            slot.current_valuation = None
            slot.revenue = None
            slot.ai_recommendation_id = None
            slot.ai_confidence_score = None
            slot.ai_reasoning = None
            slot.original_query = None
            slot.updated_at = datetime.utcnow()
            
            self.db_session.commit()
            
            logger.info(f"Cleared slot {slot_id} for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error clearing slot {slot_id} for user {user_id}: {str(e)}")
            self.db_session.rollback()
            return False
    
    def get_slot_statistics(self, user_id: int) -> Dict[str, Any]:
        """
        Get statistics about user's slots with membership-aware limits
        
        Args:
            user_id: ID of the user
        
        Returns:
            Dictionary with slot statistics
        """
        try:
            # Get configuration with membership awareness
            config = self.db_session.query(UserSlotConfiguration).filter(
                UserSlotConfiguration.user_id == user_id
            ).first()
            
            if not config:
                # Initialize if missing
                self.initialize_user_slots(user_id)
                config = self.db_session.query(UserSlotConfiguration).filter(
                    UserSlotConfiguration.user_id == user_id
                ).first()
            
            max_slots = config.current_max_slots
            
            # Count slots by status
            slot_counts = self.db_session.query(
                ProjectCardSlot.status,
                func.count(ProjectCardSlot.slot_id)
            ).filter(
                ProjectCardSlot.user_id == user_id
            ).group_by(ProjectCardSlot.status).all()
            
            counts = {status.value: 0 for status in SlotStatus}
            for status, count in slot_counts:
                counts[status.value] = count
            
            # Calculate usage with new status names
            occupied_count = counts.get("occupied", 0)
            activated_count = counts.get("activated", 0) 
            empty_count = counts.get("empty", 0)
            
            total_used_slots = occupied_count + activated_count
            available_slots = max_slots - total_used_slots
            
            stats = {
                "max_slots": max_slots,
                "base_slots": config.base_slots,
                "bonus_slots": config.bonus_slots,
                "membership_active": config.is_membership_active,
                "membership_expires_at": config.membership_expires_at.isoformat() if config.membership_expires_at else None,
                
                "occupied_slots": occupied_count,  # Has content but not activated
                "activated_slots": activated_count,  # Published/visible content
                "empty_slots": empty_count,
                "total_used_slots": total_used_slots,
                "available_slots": max(0, available_slots),
                
                "can_activate_more": activated_count < max_slots,
                "activation_limit_reached": activated_count >= max_slots,
                "utilization_percentage": round((total_used_slots / max_slots) * 100, 1) if max_slots > 0 else 0
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting slot statistics for user {user_id}: {str(e)}")
            return {
                "max_slots": 2,
                "base_slots": 2,
                "bonus_slots": 0,
                "membership_active": False,
                "membership_expires_at": None,
                "occupied_slots": 0,
                "activated_slots": 0,
                "empty_slots": 0,
                "total_used_slots": 0,
                "available_slots": 2,
                "can_activate_more": True,
                "activation_limit_reached": False,
                "utilization_percentage": 0.0
            }
    
    def update_slot_configuration(
        self,
        user_id: int,
        max_slots: Optional[int] = None,
        auto_save_recommendations: Optional[bool] = None,
        stop_recommendations_on_save: Optional[bool] = None
    ) -> bool:
        """
        Update user's slot configuration
        
        Args:
            user_id: ID of the user
            max_slots: Maximum number of slots
            auto_save_recommendations: Whether to auto-save right swipes
            stop_recommendations_on_save: Whether to stop recommendations after save
        
        Returns:
            True if updated successfully
        """
        try:
            config = self.db_session.query(UserSlotConfiguration).filter(
                UserSlotConfiguration.user_id == user_id
            ).first()
            
            if not config:
                # Initialize if doesn't exist
                self.initialize_user_slots(user_id, max_slots or 5)
                config = self.db_session.query(UserSlotConfiguration).filter(
                    UserSlotConfiguration.user_id == user_id
                ).first()
            
            # Update configuration
            if max_slots is not None:
                config.max_slots = max_slots
            if auto_save_recommendations is not None:
                config.auto_save_recommendations = auto_save_recommendations
            if stop_recommendations_on_save is not None:
                config.stop_recommendations_on_save = stop_recommendations_on_save
            
            config.updated_at = datetime.utcnow()
            self.db_session.commit()
            
            logger.info(f"Updated slot configuration for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating slot configuration for user {user_id}: {str(e)}")
            self.db_session.rollback()
            return False

    def get_global_slot_statistics(self) -> dict:
        """
        Get global statistics about the slot system
        
        Returns:
            Dictionary with global statistics
        """
        try:
            # Get total number of users with slot configurations
            total_users_with_configs = self.db_session.query(UserSlotConfiguration).count()
            
            # Get total number of slots
            total_slots = self.db_session.query(ProjectCardSlot).count()
            occupied_slots = self.db_session.query(ProjectCardSlot).filter(
                ProjectCardSlot.status != SlotStatus.EMPTY
            ).count()
            activated_slots = self.db_session.query(ProjectCardSlot).filter(
                ProjectCardSlot.status == SlotStatus.ACTIVATED
            ).count()
            
            # Get membership distribution
            basic_users = self.db_session.query(UserSlotConfiguration).filter(
                UserSlotConfiguration.bonus_slots == 0
            ).count()
            premium_users = self.db_session.query(UserSlotConfiguration).filter(
                UserSlotConfiguration.bonus_slots > 0
            ).count()
            
            # Get expiring memberships (next 7 days)
            from datetime import datetime, timedelta
            next_week = datetime.utcnow() + timedelta(days=7)
            expiring_soon = self.db_session.query(UserSlotConfiguration).filter(
                UserSlotConfiguration.bonus_expires_at.isnot(None),
                UserSlotConfiguration.bonus_expires_at <= next_week,
                UserSlotConfiguration.bonus_expires_at > datetime.utcnow()
            ).count()
            
            return {
                "total_users_with_configs": total_users_with_configs,
                "total_slots": total_slots,
                "occupied_slots": occupied_slots,
                "activated_slots": activated_slots,
                "empty_slots": total_slots - occupied_slots,
                "slot_utilization_rate": (occupied_slots / total_slots * 100) if total_slots > 0 else 0,
                "activation_rate": (activated_slots / occupied_slots * 100) if occupied_slots > 0 else 0,
                "membership_distribution": {
                    "basic_users": basic_users,
                    "premium_users": premium_users
                },
                "expiring_memberships_next_7_days": expiring_soon
            }
            
        except Exception as e:
            logger.error(f"Error getting global slot statistics: {str(e)}")
            return {
                "error": str(e),
                "total_users_with_configs": 0,
                "total_slots": 0,
                "occupied_slots": 0,
                "activated_slots": 0,
                "empty_slots": 0,
                "slot_utilization_rate": 0,
                "activation_rate": 0,
                "membership_distribution": {
                    "basic_users": 0,
                    "premium_users": 0
                },
                "expiring_memberships_next_7_days": 0
            }
