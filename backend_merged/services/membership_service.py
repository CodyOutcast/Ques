"""
Membership service for managing user limits and membership tiers
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, func, desc
from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import json

from models.users import User
from models.user_membership import UserMembership, UserUsageLog, MembershipType


class MembershipService:
    """Service for handling membership limits and usage tracking"""
    
    # Membership limits configuration
    LIMITS = {
        MembershipType.FREE: {
            "swipes_per_day": 30,
            "project_cards_max": 2,
            "project_cards_per_day": 2,
            "messages_per_day": 50,
            "project_ideas_per_day": 1,  # Free users: 1 AI project idea generation per day
            "rate_limit_enabled": True
        },
        MembershipType.PAID: {
            "swipes_per_day": -1,  # Unlimited
            "swipes_per_hour": 30,  # Rate limiting to prevent botting
            "project_cards_max": -1,  # Unlimited
            "project_cards_per_day": 10,
            "messages_per_day": -1,  # Unlimited
            "project_ideas_per_day": -1,  # Unlimited
            "project_ideas_per_hour": 30,  # Rate limiting to prevent abuse
            "rate_limit_enabled": True
        }
    }
    
    @staticmethod
    def get_or_create_membership(db: Session, user_id: int) -> UserMembership:
        """
        Get user membership or create a free membership if none exists
        """
        membership = db.query(UserMembership).filter(
            UserMembership.user_id == user_id
        ).first()
        
        if not membership:
            # Create free membership for new users
            membership = UserMembership(
                user_id=user_id,
                membership_type=MembershipType.FREE,
                is_active=True,
                start_date=datetime.utcnow()
            )
            db.add(membership)
            db.commit()
            db.refresh(membership)
        
        return membership
    
    @staticmethod
    def check_swipe_limit(db: Session, user_id: int) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Check if user can perform a swipe action
        Returns: (can_swipe, message, usage_info)
        """
        membership = MembershipService.get_or_create_membership(db, user_id)
        limits = MembershipService.LIMITS[membership.membership_type]
        
        now = datetime.utcnow()
        today = UserUsageLog.get_day_timestamp(now)
        current_hour = UserUsageLog.get_hour_timestamp(now)
        
        # Check daily limit for free users
        if membership.membership_type == MembershipType.FREE:
            daily_swipes = db.query(func.sum(UserUsageLog.action_count)).filter(
                UserUsageLog.user_id == user_id,
                UserUsageLog.action_type == "swipe",
                UserUsageLog.day_timestamp == today
            ).scalar() or 0
            
            if daily_swipes >= limits["swipes_per_day"]:
                return False, f"Daily swipe limit reached ({limits['swipes_per_day']} swipes per day for free users)", {
                    "daily_swipes": daily_swipes,
                    "limit": limits["swipes_per_day"],
                    "membership_type": membership.membership_type.value
                }
        
        # Check hourly rate limit for paid users (anti-botting)
        elif membership.membership_type == MembershipType.PAID:
            hourly_swipes = db.query(func.sum(UserUsageLog.action_count)).filter(
                UserUsageLog.user_id == user_id,
                UserUsageLog.action_type == "swipe",
                UserUsageLog.hour_timestamp == current_hour
            ).scalar() or 0
            
            if hourly_swipes >= limits["swipes_per_hour"]:
                return False, f"Hourly rate limit reached ({limits['swipes_per_hour']} swipes per hour to prevent botting)", {
                    "hourly_swipes": hourly_swipes,
                    "limit": limits["swipes_per_hour"],
                    "membership_type": membership.membership_type.value
                }
        
        return True, "Swipe allowed", {
            "membership_type": membership.membership_type.value,
            "is_paid": membership.is_paid
        }
    
    @staticmethod
    def check_project_card_limit(db: Session, user_id: int) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Check if user can create a project card
        Returns: (can_create, message, usage_info)
        """
        membership = MembershipService.get_or_create_membership(db, user_id)
        limits = MembershipService.LIMITS[membership.membership_type]
        
        now = datetime.utcnow()
        today = UserUsageLog.get_day_timestamp(now)
        
        # Import here to avoid circular imports
        from services.project_card_service import ProjectCardService
        
        # Check maximum cards limit
        current_cards = ProjectCardService.get_user_card_count(db, user_id)
        max_cards = limits["project_cards_max"]
        
        if max_cards != -1 and current_cards >= max_cards:
            return False, f"Maximum project cards limit reached ({max_cards} cards for {membership.membership_type.value} users)", {
                "current_cards": current_cards,
                "max_cards": max_cards,
                "membership_type": membership.membership_type.value
            }
        
        # Check daily creation limit
        daily_cards = db.query(func.sum(UserUsageLog.action_count)).filter(
            UserUsageLog.user_id == user_id,
            UserUsageLog.action_type == "project_card_create",
            UserUsageLog.day_timestamp == today
        ).scalar() or 0
        
        daily_limit = limits["project_cards_per_day"]
        if daily_limit != -1 and daily_cards >= daily_limit:
            return False, f"Daily project card creation limit reached ({daily_limit} cards per day)", {
                "daily_cards": daily_cards,
                "daily_limit": daily_limit,
                "current_cards": current_cards,
                "membership_type": membership.membership_type.value
            }
        
        return True, "Project card creation allowed", {
            "current_cards": current_cards,
            "daily_cards": daily_cards,
            "membership_type": membership.membership_type.value,
            "is_paid": membership.is_paid
        }
    
    @staticmethod
    def check_project_ideas_limit(db: Session, user_id: int) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Check if user can generate project ideas based on membership limits
        Returns: (can_generate, message, usage_info)
        """
        membership = MembershipService.get_or_create_membership(db, user_id)
        limits = MembershipService.LIMITS[membership.membership_type]
        
        now = datetime.utcnow()
        today = UserUsageLog.get_day_timestamp(now)
        current_hour = UserUsageLog.get_hour_timestamp(now)
        
        # Check daily limit for free users
        if membership.membership_type == MembershipType.FREE:
            daily_ideas = db.query(func.sum(UserUsageLog.action_count)).filter(
                UserUsageLog.user_id == user_id,
                UserUsageLog.action_type == "project_ideas_generate",
                UserUsageLog.day_timestamp == today
            ).scalar() or 0
            
            daily_limit = limits["project_ideas_per_day"]
            if daily_limit != -1 and daily_ideas >= daily_limit:
                return False, f"Daily project ideas generation limit reached ({daily_limit} per day for free users)", {
                    "daily_ideas": daily_ideas,
                    "daily_limit": daily_limit,
                    "membership_type": membership.membership_type.value
                }
        
        # Check hourly rate limit for paid users (anti-abuse)
        elif membership.membership_type == MembershipType.PAID:
            hourly_ideas = db.query(func.sum(UserUsageLog.action_count)).filter(
                UserUsageLog.user_id == user_id,
                UserUsageLog.action_type == "project_ideas_generate",
                UserUsageLog.hour_timestamp == current_hour
            ).scalar() or 0
            
            hourly_limit = limits.get("project_ideas_per_hour")
            if hourly_limit and hourly_limit != -1 and hourly_ideas >= hourly_limit:
                return False, f"Hourly project ideas generation limit reached ({hourly_limit} per hour to prevent abuse)", {
                    "hourly_ideas": hourly_ideas,
                    "hourly_limit": hourly_limit,
                    "membership_type": membership.membership_type.value
                }
        
        return True, "Project ideas generation allowed", {
            "membership_type": membership.membership_type.value,
            "is_paid": membership.is_paid
        }
    
    @staticmethod
    def log_usage(db: Session, user_id: int, action_type: str, count: int = 1, metadata: Dict = None) -> UserUsageLog:
        """
        Log user action for usage tracking
        """
        membership = MembershipService.get_or_create_membership(db, user_id)
        
        now = datetime.utcnow()
        hour_timestamp = UserUsageLog.get_hour_timestamp(now)
        day_timestamp = UserUsageLog.get_day_timestamp(now)
        
        # Check if there's already a log for this hour/day/action combination
        existing_log = db.query(UserUsageLog).filter(
            UserUsageLog.user_id == user_id,
            UserUsageLog.action_type == action_type,
            UserUsageLog.hour_timestamp == hour_timestamp
        ).first()
        
        if existing_log:
            # Update existing log
            existing_log.action_count += count
            existing_log.action_metadata = json.dumps(metadata) if metadata else None
            db.commit()
            return existing_log
        else:
            # Create new log
            usage_log = UserUsageLog(
                user_id=user_id,
                membership_id=membership.membership_id,
                action_type=action_type,
                action_count=count,
                hour_timestamp=hour_timestamp,
                day_timestamp=day_timestamp,
                action_metadata=json.dumps(metadata) if metadata else None
            )
            db.add(usage_log)
            db.commit()
            db.refresh(usage_log)
            return usage_log
    
    @staticmethod
    def get_usage_stats(db: Session, user_id: int) -> Dict[str, Any]:
        """
        Get current usage statistics for a user
        """
        membership = MembershipService.get_or_create_membership(db, user_id)
        limits = MembershipService.LIMITS[membership.membership_type]
        
        now = datetime.utcnow()
        today = UserUsageLog.get_day_timestamp(now)
        current_hour = UserUsageLog.get_hour_timestamp(now)
        
        # Get daily stats
        daily_swipes = db.query(func.sum(UserUsageLog.action_count)).filter(
            UserUsageLog.user_id == user_id,
            UserUsageLog.action_type == "swipe",
            UserUsageLog.day_timestamp == today
        ).scalar() or 0
        
        daily_cards = db.query(func.sum(UserUsageLog.action_count)).filter(
            UserUsageLog.user_id == user_id,
            UserUsageLog.action_type == "project_card_create",
            UserUsageLog.day_timestamp == today
        ).scalar() or 0
        
        # Get hourly stats (for paid users)
        hourly_swipes = db.query(func.sum(UserUsageLog.action_count)).filter(
            UserUsageLog.user_id == user_id,
            UserUsageLog.action_type == "swipe",
            UserUsageLog.hour_timestamp == current_hour
        ).scalar() or 0
        
        # Get current project cards count
        from services.project_card_service import ProjectCardService
        current_cards = ProjectCardService.get_user_card_count(db, user_id)
        
        return {
            "membership_type": membership.membership_type.value,
            "is_paid": membership.is_paid,
            "days_remaining": membership.days_remaining,
            "limits": limits,
            "usage": {
                "daily_swipes": daily_swipes,
                "hourly_swipes": hourly_swipes,
                "daily_cards_created": daily_cards,
                "total_cards": current_cards
            },
            "can_swipe": MembershipService.check_swipe_limit(db, user_id)[0],
            "can_create_card": MembershipService.check_project_card_limit(db, user_id)[0]
        }
    
    @staticmethod
    def upgrade_to_paid(db: Session, user_id: int, duration_days: int = 30, payment_method: str = None, subscription_id: str = None) -> UserMembership:
        """
        Upgrade user to paid membership
        """
        membership = MembershipService.get_or_create_membership(db, user_id)
        
        membership.membership_type = MembershipType.PAID
        membership.is_active = True
        membership.start_date = datetime.utcnow()
        membership.end_date = datetime.utcnow() + timedelta(days=duration_days)
        membership.payment_method = payment_method
        membership.subscription_id = subscription_id
        membership.auto_renew = True
        membership.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(membership)
        
        return membership
    
    @staticmethod
    def downgrade_to_free(db: Session, user_id: int, reason: str = "expired") -> UserMembership:
        """
        Downgrade user to free membership
        """
        membership = MembershipService.get_or_create_membership(db, user_id)
        
        membership.membership_type = MembershipType.FREE
        membership.is_active = True
        membership.end_date = None
        membership.auto_renew = False
        membership.updated_at = datetime.utcnow()
        
        # Log the downgrade
        MembershipService.log_usage(db, user_id, "membership_downgrade", 1, {"reason": reason})
        
        db.commit()
        db.refresh(membership)
        
        return membership
