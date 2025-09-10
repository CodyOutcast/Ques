"""
Online users tracking service for concurrent user analytics
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text, func, and_, or_
from models.user_auth import UserSession
from models.users import User
from dependencies.db import SessionLocal

logger = logging.getLogger(__name__)

class OnlineUsersService:
    """Service for tracking and managing online users"""
    
    @staticmethod
    def get_online_user_count(db: Session, active_threshold_minutes: int = 15) -> int:
        """
        Get count of users who were active within the threshold period
        
        Args:
            db: Database session
            active_threshold_minutes: Minutes to consider a user as online (default: 15)
        
        Returns:
            Number of online users
        """
        threshold_time = datetime.utcnow() - timedelta(minutes=active_threshold_minutes)
        
        try:
            count = db.query(UserSession).filter(
                and_(
                    UserSession.is_active == True,
                    UserSession.last_activity >= threshold_time
                )
            ).distinct(UserSession.user_id).count()
            
            return count
        except Exception as e:
            logger.error(f"Error getting online user count: {e}")
            return 0
    
    @staticmethod
    def get_online_users(db: Session, active_threshold_minutes: int = 15, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get list of online users with their details
        
        Args:
            db: Database session
            active_threshold_minutes: Minutes to consider a user as online
            limit: Maximum number of users to return
        
        Returns:
            List of online user details
        """
        threshold_time = datetime.utcnow() - timedelta(minutes=active_threshold_minutes)
        
        try:
            # Get online users with their latest session info
            results = db.query(
                User.user_id,
                User.name,
                User.profile_image_url,
                func.max(UserSession.last_activity).label('last_seen'),
                func.count(UserSession.id).label('session_count')
            ).join(
                UserSession, User.user_id == UserSession.user_id
            ).filter(
                and_(
                    UserSession.is_active == True,
                    UserSession.last_activity >= threshold_time
                )
            ).group_by(
                User.user_id, User.name, User.profile_image_url
            ).order_by(
                func.max(UserSession.last_activity).desc()
            ).limit(limit).all()
            
            online_users = []
            for result in results:
                online_users.append({
                    "user_id": result.user_id,
                    "username": result.name,  # Using name field as username
                    "display_name": result.name,  # Using name field as display_name
                    "avatar_url": result.profile_image_url,
                    "last_seen": result.last_seen.isoformat() if result.last_seen else None,
                    "session_count": result.session_count,
                    "status": "online"
                })
            
            return online_users
        except Exception as e:
            logger.error(f"Error getting online users: {e}")
            return []
    
    @staticmethod
    def get_user_sessions(db: Session, user_id: int) -> List[Dict[str, Any]]:
        """
        Get all active sessions for a specific user
        
        Args:
            db: Database session
            user_id: User ID to get sessions for
        
        Returns:
            List of user sessions
        """
        try:
            sessions = db.query(UserSession).filter(
                and_(
                    UserSession.user_id == user_id,
                    UserSession.is_active == True
                )
            ).order_by(UserSession.last_activity.desc()).all()
            
            session_list = []
            for session in sessions:
                session_list.append({
                    "session_id": session.id,
                    "device_name": session.device_name,
                    "ip_address": session.ip_address,
                    "user_agent": session.user_agent,
                    "location": session.location,
                    "created_at": session.created_at.isoformat() if session.created_at else None,
                    "last_activity": session.last_activity.isoformat() if session.last_activity else None,
                    "expires_at": session.expires_at.isoformat() if session.expires_at else None
                })
            
            return session_list
        except Exception as e:
            logger.error(f"Error getting user sessions: {e}")
            return []
    
    @staticmethod
    def cleanup_expired_sessions(db: Session) -> int:
        """
        Remove expired sessions from the database
        
        Args:
            db: Database session
        
        Returns:
            Number of sessions cleaned up
        """
        try:
            current_time = datetime.utcnow()
            
            # Mark expired sessions as inactive
            expired_count = db.query(UserSession).filter(
                or_(
                    UserSession.expires_at < current_time,
                    UserSession.last_activity < current_time - timedelta(days=7)  # 7 days inactive
                )
            ).update({"is_active": False}, synchronize_session=False)
            
            db.commit()
            logger.info(f"Cleaned up {expired_count} expired sessions")
            return expired_count
            
        except Exception as e:
            logger.error(f"Error cleaning up expired sessions: {e}")
            db.rollback()
            return 0
    
    @staticmethod
    def get_online_stats(db: Session) -> Dict[str, Any]:
        """
        Get comprehensive online user statistics
        
        Args:
            db: Database session
        
        Returns:
            Dictionary with online user statistics
        """
        try:
            current_time = datetime.utcnow()
            
            # Users online in last 5 minutes (very active)
            very_active_count = db.query(UserSession).filter(
                and_(
                    UserSession.is_active == True,
                    UserSession.last_activity >= current_time - timedelta(minutes=5)
                )
            ).distinct(UserSession.user_id).count()
            
            # Users online in last 15 minutes (online)
            online_count = db.query(UserSession).filter(
                and_(
                    UserSession.is_active == True,
                    UserSession.last_activity >= current_time - timedelta(minutes=15)
                )
            ).distinct(UserSession.user_id).count()
            
            # Users online in last hour (recently active)
            recent_count = db.query(UserSession).filter(
                and_(
                    UserSession.is_active == True,
                    UserSession.last_activity >= current_time - timedelta(hours=1)
                )
            ).distinct(UserSession.user_id).count()
            
            # Total active sessions
            total_sessions = db.query(UserSession).filter(
                UserSession.is_active == True
            ).count()
            
            # Peak activity time analysis (last 24 hours)
            peak_hour_query = text("""
                SELECT 
                    EXTRACT(HOUR FROM last_activity) as hour,
                    COUNT(DISTINCT user_id) as user_count
                FROM user_sessions 
                WHERE 
                    is_active = true 
                    AND last_activity >= :day_ago
                GROUP BY EXTRACT(HOUR FROM last_activity)
                ORDER BY user_count DESC
                LIMIT 1
            """)
            
            peak_result = db.execute(peak_hour_query, {
                "day_ago": current_time - timedelta(days=1)
            }).fetchone()
            
            peak_hour = peak_result[0] if peak_result else None
            peak_users = peak_result[1] if peak_result else 0
            
            return {
                "timestamp": current_time.isoformat(),
                "very_active_users": very_active_count,    # Last 5 minutes
                "online_users": online_count,              # Last 15 minutes  
                "recently_active_users": recent_count,     # Last hour
                "total_active_sessions": total_sessions,
                "peak_hour_today": peak_hour,
                "peak_users_today": peak_users,
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"Error getting online stats: {e}")
            return {
                "timestamp": datetime.utcnow().isoformat(),
                "very_active_users": 0,
                "online_users": 0,
                "recently_active_users": 0,
                "total_active_sessions": 0,
                "peak_hour_today": None,
                "peak_users_today": 0,
                "status": "error",
                "error": str(e)
            }
    
    @staticmethod
    def get_user_online_status(db: Session, user_id: int) -> Dict[str, Any]:
        """
        Get online status for a specific user
        
        Args:
            db: Database session
            user_id: User ID to check
        
        Returns:
            User's online status information
        """
        try:
            current_time = datetime.utcnow()
            
            # Get user's most recent session
            latest_session = db.query(UserSession).filter(
                and_(
                    UserSession.user_id == user_id,
                    UserSession.is_active == True
                )
            ).order_by(UserSession.last_activity.desc()).first()
            
            if not latest_session:
                return {
                    "user_id": user_id,
                    "status": "offline",
                    "last_seen": None,
                    "is_online": False
                }
            
            time_diff = current_time - latest_session.last_activity
            
            # Determine status based on last activity
            if time_diff <= timedelta(minutes=5):
                status = "very_active"
                is_online = True
            elif time_diff <= timedelta(minutes=15):
                status = "online"
                is_online = True
            elif time_diff <= timedelta(hours=1):
                status = "recently_active"
                is_online = False
            else:
                status = "offline"
                is_online = False
            
            return {
                "user_id": user_id,
                "status": status,
                "last_seen": latest_session.last_activity.isoformat(),
                "is_online": is_online,
                "session_count": db.query(UserSession).filter(
                    and_(
                        UserSession.user_id == user_id,
                        UserSession.is_active == True
                    )
                ).count()
            }
            
        except Exception as e:
            logger.error(f"Error getting user online status: {e}")
            return {
                "user_id": user_id,
                "status": "unknown",
                "last_seen": None,
                "is_online": False,
                "error": str(e)
            }

# Convenience function for getting online count without session management
def get_current_online_count() -> int:
    """Get current online user count (convenience function)"""
    try:
        db = SessionLocal()
        count = OnlineUsersService.get_online_user_count(db)
        return count
    except Exception as e:
        logger.error(f"Error in get_current_online_count: {e}")
        return 0
    finally:
        if 'db' in locals():
            db.close()
