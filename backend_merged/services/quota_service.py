"""
Comprehensive quota management service for project idea generation
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import text

from models.subscriptions import UserSubscription, ProjectIdeaRequest
from dependencies.db import SessionLocal

logger = logging.getLogger(__name__)

class QuotaService:
    """Service for managing user quotas and subscriptions"""
    
    # Quota limits by subscription type (per month)
    QUOTA_LIMITS = {
        "basic": 30,
        "pro": 300,
        "ai-powered": 1000
    }
    
    @classmethod
    def get_or_create_subscription(cls, user_id: int, db: Session) -> UserSubscription:
        """Get existing subscription or create a new free subscription"""
        try:
            # Try to get existing subscription
            subscription = db.query(UserSubscription).filter(
                UserSubscription.user_id == user_id
            ).first()
            
            if subscription:
                # Reset period if needed
                subscription.reset_period_if_needed()
                db.commit()
                return subscription
            
            # Create new basic subscription
            subscription = UserSubscription(
                user_id=user_id, 
                subscription_type="basic"
            )
            db.add(subscription)
            db.commit()
            db.refresh(subscription)
            
            logger.info(f"Created new basic subscription for user {user_id}")
            return subscription
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error getting/creating subscription for user {user_id}: {e}")
            raise
    
    @classmethod
    def check_quota(cls, user_id: int) -> Tuple[bool, Dict[str, Any]]:
        """
        Check if user has quota remaining
        
        Returns:
            Tuple of (has_quota, quota_info)
        """
        db = SessionLocal()
        try:
            subscription = cls.get_or_create_subscription(user_id, db)
            
            quota_info = {
                "user_id": user_id,
                "subscription_type": subscription.subscription_type,
                "monthly_limit": subscription.monthly_quota_limit,
                "current_usage": subscription.current_period_usage,
                "remaining_quota": subscription.remaining_quota,
                "quota_reset_date": subscription.quota_reset_date.isoformat(),
                "is_quota_exceeded": subscription.is_quota_exceeded,
                "period_start": subscription.current_period_start.isoformat(),
                "period_end": subscription.current_period_end.isoformat()
            }
            
            has_quota = not subscription.is_quota_exceeded and subscription.is_active
            
            return has_quota, quota_info
            
        except Exception as e:
            logger.error(f"Error checking quota for user {user_id}: {e}")
            # Default to allowing request if there's an error
            return True, {
                "user_id": user_id,
                "subscription_type": "free",
                "monthly_limit": 30,
                "current_usage": 0,
                "remaining_quota": 30,
                "error": f"Quota check failed: {str(e)}"
            }
        finally:
            db.close()
    
    @classmethod
    def consume_quota(cls, user_id: int, query: str, success: bool = True, 
                     error_message: Optional[str] = None,
                     processing_time: Optional[float] = None,
                     sources_found: Optional[int] = None,
                     ideas_extracted: Optional[int] = None) -> bool:
        """
        Consume quota for a request and log the request
        
        Returns:
            True if quota was successfully consumed, False otherwise
        """
        db = SessionLocal()
        try:
            # Get subscription and check quota
            subscription = cls.get_or_create_subscription(user_id, db)
            
            if subscription.is_quota_exceeded:
                logger.warning(f"Quota exceeded for user {user_id}")
                return False
            
            # Increment usage
            subscription.increment_usage(1)
            
            # Log the request
            request_log = ProjectIdeaRequest(
                user_id=user_id,
                subscription_id=subscription.id,
                query=query,
                success=success,
                error_message=error_message,
                processing_time_seconds=int(processing_time) if processing_time else None,
                total_sources_found=sources_found,
                total_ideas_extracted=ideas_extracted
            )
            
            db.add(request_log)
            db.commit()
            
            logger.info(f"Quota consumed for user {user_id}. Remaining: {subscription.remaining_quota}")
            return True
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error consuming quota for user {user_id}: {e}")
            return False
        finally:
            db.close()
    
    @classmethod
    def upgrade_subscription(cls, user_id: int, new_type: str) -> bool:
        """Upgrade user subscription"""
        db = SessionLocal()
        try:
            subscription = cls.get_or_create_subscription(user_id, db)
            subscription.upgrade_subscription(new_type)
            db.commit()
            
            logger.info(f"Upgraded user {user_id} to {new_type}")
            return True
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error upgrading subscription for user {user_id}: {e}")
            return False
        finally:
            db.close()
    
    @classmethod
    def get_quota_status(cls, user_id: int) -> Dict[str, Any]:
        """Get detailed quota status for a user"""
        has_quota, quota_info = cls.check_quota(user_id)
        
        # Add additional status information
        quota_info.update({
            "has_quota": has_quota,
            "service_status": "operational",
            "quota_percentage_used": (
                quota_info["current_usage"] / quota_info["monthly_limit"] * 100
                if quota_info["monthly_limit"] > 0 else 0
            )
        })
        
        return quota_info
    
    @classmethod
    def get_usage_history(cls, user_id: int, days: int = 30) -> Dict[str, Any]:
        """Get usage history for a user"""
        db = SessionLocal()
        try:
            # Get requests from the last N days
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            requests = db.query(ProjectIdeaRequest).filter(
                ProjectIdeaRequest.user_id == user_id,
                ProjectIdeaRequest.created_at >= cutoff_date
            ).order_by(ProjectIdeaRequest.created_at.desc()).all()
            
            # Calculate statistics
            total_requests = len(requests)
            successful_requests = sum(1 for req in requests if req.success)
            failed_requests = total_requests - successful_requests
            
            # Group by date
            daily_usage = {}
            for req in requests:
                date_key = req.created_at.strftime('%Y-%m-%d')
                if date_key not in daily_usage:
                    daily_usage[date_key] = 0
                daily_usage[date_key] += 1
            
            return {
                "user_id": user_id,
                "period_days": days,
                "total_requests": total_requests,
                "successful_requests": successful_requests,
                "failed_requests": failed_requests,
                "success_rate": (successful_requests / total_requests * 100) if total_requests > 0 else 0,
                "daily_usage": daily_usage,
                "recent_requests": [
                    {
                        "id": req.request_id,
                        "query": req.query[:100] + "..." if len(req.query) > 100 else req.query,
                        "successful": req.success,
                        "created_at": req.created_at.isoformat(),
                        "processing_time": req.processing_time_seconds,
                        "sources_found": req.total_sources_found,
                        "ideas_extracted": req.total_ideas_extracted
                    }
                    for req in requests[:10]  # Last 10 requests
                ]
            }
            
        except Exception as e:
            logger.error(f"Error getting usage history for user {user_id}: {e}")
            return {
                "user_id": user_id,
                "error": f"Failed to get usage history: {str(e)}"
            }
        finally:
            db.close()
    
    @classmethod
    def reset_quota(cls, user_id: int) -> bool:
        """Reset quota for a user (admin function)"""
        db = SessionLocal()
        try:
            subscription = cls.get_or_create_subscription(user_id, db)
            subscription.current_period_usage = 0
            subscription.updated_at = datetime.utcnow()
            db.commit()
            
            logger.info(f"Reset quota for user {user_id}")
            return True
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error resetting quota for user {user_id}: {e}")
            return False
        finally:
            db.close()

# Legacy function for backward compatibility
def check_quota(user_id: int) -> bool:
    """Legacy quota check function for backward compatibility"""
    has_quota, _ = QuotaService.check_quota(user_id)
    return has_quota
