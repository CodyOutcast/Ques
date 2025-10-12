"""
Swipe History Service

Handles querying user swipe history for search filtering and other swipe-related operations.
Provides functions to retrieve swiped user IDs for filtering search results.

Created to support intelligent search filtering based on user interaction history.
Updated to match production database schema (swiped_user_id, swipe_direction as string)
"""

from typing import List, Set, Optional
from sqlalchemy.orm import Session
from models.likes import UserSwipe
from models.users import User


class SwipeService:
    """Service for handling swipe history and filtering operations"""
    
    @staticmethod
    def get_swiped_user_ids(db: Session, user_id: int, direction: Optional[str] = None) -> List[int]:
        """
        Get list of user IDs that the current user has swiped on.
        
        Args:
            db: Database session
            user_id: ID of the user whose swipe history to fetch
            direction: Optional filter by swipe direction ('like'/'dislike'). If None, returns all swipes.
        
        Returns:
            List of user IDs that have been swiped on
        """
        query = db.query(UserSwipe.swiped_user_id).filter(
            UserSwipe.swiper_id == user_id
        )
        
        if direction:
            query = query.filter(UserSwipe.swipe_direction == direction)
        
        result = query.all()
        return [row[0] for row in result]
    
    @staticmethod
    def get_all_swiped_user_ids(db: Session, user_id: int) -> List[int]:
        """
        Get all user IDs that the current user has swiped on (both likes and dislikes).
        This is the main function for search filtering - we want to exclude all previously swiped users.
        
        Args:
            db: Database session
            user_id: ID of the user whose swipe history to fetch
        
        Returns:
            List of all user IDs that have been swiped on (like or dislike)
        """
        return SwipeService.get_swiped_user_ids(db, user_id)
    
    @staticmethod
    def get_liked_user_ids(db: Session, user_id: int) -> List[int]:
        """
        Get list of user IDs that the current user has liked.
        
        Args:
            db: Database session
            user_id: ID of the user whose like history to fetch
        
        Returns:
            List of user IDs that have been liked
        """
        return SwipeService.get_swiped_user_ids(db, user_id, 'like')
    
    @staticmethod
    def get_disliked_user_ids(db: Session, user_id: int) -> List[int]:
        """
        Get list of user IDs that the current user has disliked.
        
        Args:
            db: Database session
            user_id: ID of the user whose dislike history to fetch
        
        Returns:
            List of user IDs that have been disliked
        """
        return SwipeService.get_swiped_user_ids(db, user_id, 'dislike')
    
    @staticmethod
    def get_mutual_likes(db: Session, user_id: int) -> List[int]:
        """
        Get list of user IDs where there are mutual likes (both users liked each other).
        
        Args:
            db: Database session
            user_id: ID of the user to check for mutual likes
        
        Returns:
            List of user IDs with mutual likes
        """
        # Get users that current user has liked
        liked_by_user = db.query(UserSwipe.swiped_user_id).filter(
            UserSwipe.swiper_id == user_id,
            UserSwipe.swipe_direction == 'right'
        ).subquery()
        
        # Get users that have liked the current user back
        mutual_likes = db.query(UserSwipe.swiper_id).filter(
            UserSwipe.swiped_user_id == user_id,
            UserSwipe.swipe_direction == 'right',
            UserSwipe.swiper_id.in_(liked_by_user)
        ).all()
        
        return [row[0] for row in mutual_likes]
    
    @staticmethod
    def has_swiped_on_user(db: Session, swiper_id: int, target_id: int) -> bool:
        """
        Check if a user has already swiped on another user.
        
        Args:
            db: Database session
            swiper_id: ID of the user who swiped
            target_id: ID of the user being swiped on
        
        Returns:
            True if swipe exists, False otherwise
        """
        swipe = db.query(UserSwipe).filter(
            UserSwipe.swiper_id == swiper_id,
            UserSwipe.target_id == target_id
        ).first()
        
        return swipe is not None
    
    @staticmethod
    def get_swipe_direction(db: Session, swiper_id: int, target_id: int) -> Optional[str]:
        """
        Get the direction of a swipe between two users.
        
        Args:
            db: Database session
            swiper_id: ID of the user who swiped
            target_id: ID of the user being swiped on
        
        Returns:
            'like' or 'dislike' if swipe exists, None otherwise
        """
        swipe = db.query(UserSwipe).filter(
            UserSwipe.swiper_id == swiper_id,
            UserSwipe.swiped_user_id == target_id
        ).first()
        
        return swipe.swipe_direction if swipe else None
    
    @staticmethod
    def get_swipe_stats(db: Session, user_id: int) -> dict:
        """
        Get comprehensive swipe statistics for a user.
        
        Args:
            db: Database session
            user_id: ID of the user to get stats for
        
        Returns:
            Dictionary with swipe statistics
        """
        total_swipes = db.query(UserSwipe).filter(UserSwipe.swiper_id == user_id).count()
        total_likes = db.query(UserSwipe).filter(
            UserSwipe.swiper_id == user_id,
            UserSwipe.swipe_direction == 'right'
        ).count()
        total_dislikes = db.query(UserSwipe).filter(
            UserSwipe.swiper_id == user_id,
            UserSwipe.swipe_direction == 'left'
        ).count()
        
        # Get mutual likes count
        mutual_likes = SwipeService.get_mutual_likes(db, user_id)
        mutual_likes_count = len(mutual_likes)
        
        # Get users who liked current user
        received_likes = db.query(UserSwipe).filter(
            UserSwipe.swiped_user_id == user_id,
            UserSwipe.swipe_direction == 'right'
        ).count()
        
        return {
            "total_swipes": total_swipes,
            "total_likes": total_likes,
            "total_dislikes": total_dislikes,
            "mutual_likes": mutual_likes_count,
            "received_likes": received_likes,
            "like_rate": (total_likes / total_swipes * 100) if total_swipes > 0 else 0,
            "mutual_like_rate": (mutual_likes_count / total_likes * 100) if total_likes > 0 else 0
        }


# Legacy function names for backward compatibility
def get_viewed_user_ids(db: Session, user_id: int) -> List[int]:
    """
    Legacy function name - redirects to get_all_swiped_user_ids
    
    Args:
        db: Database session
        user_id: ID of the user whose swipe history to fetch
    
    Returns:
        List of all user IDs that have been swiped on
    """
    return SwipeService.get_all_swiped_user_ids(db, user_id)
