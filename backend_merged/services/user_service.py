"""
User Service for account management operations
"""
import logging
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from ..models.users import User

logger = logging.getLogger(__name__)


class UserService:
    """Service class for user account management operations"""
    
    @staticmethod
    def delete_user_account(db: Session, user_id: int) -> bool:
        """
        Delete a user account and all associated data
        
        This method will:
        1. Find the user by ID
        2. Delete the user record (CASCADE DELETE will handle related data)
        3. Commit the transaction
        
        Args:
            db: Database session
            user_id: ID of the user to delete
            
        Returns:
            bool: True if deletion was successful, False if user not found
            
        Raises:
            SQLAlchemyError: If database operation fails
        """
        try:
            # Find the user by ID
            user = db.query(User).filter(User.user_id == user_id).first()
            
            if not user:
                logger.warning(f"User not found for deletion: user_id={user_id}")
                return False
            
            # Log the deletion for audit purposes
            logger.info(f"Starting account deletion for user: user_id={user_id}, name={user.name}")
            
            # Delete the user (CASCADE DELETE will handle all related data)
            db.delete(user)
            db.commit()
            
            logger.info(f"User account deleted successfully: user_id={user_id}")
            return True
            
        except SQLAlchemyError as e:
            logger.error(f"Database error during user deletion: user_id={user_id}, error={str(e)}")
            db.rollback()
            raise
        except Exception as e:
            logger.error(f"Unexpected error during user deletion: user_id={user_id}, error={str(e)}")
            db.rollback()
            raise
    
    @staticmethod
    def soft_delete_user_account(db: Session, user_id: int) -> bool:
        """
        Soft delete a user account (mark as deleted but keep data)
        
        This is an alternative to hard deletion that preserves data for audit purposes.
        The user will be marked as deleted and hidden from the application,
        but data remains in the database.
        
        Note: The current User model doesn't have is_deleted/deleted_at fields.
        This method would require adding those fields to the database schema.
        
        Args:
            db: Database session
            user_id: ID of the user to soft delete
            
        Returns:
            bool: True if soft deletion was successful, False if user not found
            
        Raises:
            SQLAlchemyError: If database operation fails
        """
        try:
            # Find the user by ID
            user = db.query(User).filter(User.user_id == user_id).first()
            
            if not user:
                logger.warning(f"User not found for soft deletion: user_id={user_id}")
                return False
            
            # Log the soft deletion for audit purposes
            logger.info(f"Starting soft deletion for user: user_id={user_id}")
            
            # Mark user as inactive (since we don't have is_deleted field yet)
            user.is_active = False
            
            # Anonymize the name and bio
            user.name = f"Deleted User {user_id}"
            user.bio = None
            user.feature_tags = None
            
            db.commit()
            
            logger.info(f"User account soft deleted successfully: user_id={user_id}")
            return True
            
        except SQLAlchemyError as e:
            logger.error(f"Database error during user soft deletion: user_id={user_id}, error={str(e)}")
            db.rollback()
            raise
        except Exception as e:
            logger.error(f"Unexpected error during user soft deletion: user_id={user_id}, error={str(e)}")
            db.rollback()
            raise
    
    @staticmethod
    def get_user_deletion_preview(db: Session, user_id: int) -> dict:
        """
        Get a preview of what data will be deleted when a user account is removed
        
        This is useful for showing users what will be deleted before they confirm.
        
        Args:
            db: Database session
            user_id: ID of the user
            
        Returns:
            dict: Summary of data that will be deleted
        """
        try:
            # Import models here to avoid circular imports
            from ..models.users import User
            from ..models.matches import Match
            from ..models.messages import Message
            from ..models.projects import Project
            from ..models.user_reports import UserReport
            
            user = db.query(User).filter(User.user_id == user_id).first()
            if not user:
                return {"error": "User not found"}
            
            # Count related data
            matches_count = db.query(Match).filter(
                (Match.user1_id == user_id) | (Match.user2_id == user_id)
            ).count()
            
            messages_count = db.query(Message).filter(Message.sender_id == user_id).count()
            
            projects_count = db.query(Project).filter(Project.creator_id == user_id).count()
            
            reports_made_count = db.query(UserReport).filter(UserReport.reporter_id == user_id).count()
            
            return {
                "user_id": user_id,
                "name": user.name,
                "data_to_delete": {
                    "profile": "All profile information and photos",
                    "matches": f"{matches_count} matches and conversations",
                    "messages": f"{messages_count} messages sent",
                    "projects": f"{projects_count} projects created",
                    "reports": f"{reports_made_count} reports made",
                    "authentication": "All login sessions and tokens",
                    "preferences": "All app preferences and settings",
                    "activity": "All swipe history and interactions"
                },
                "warning": "This action cannot be undone. All data will be permanently deleted."
            }
            
        except Exception as e:
            logger.error(f"Error generating deletion preview: user_id={user_id}, error={str(e)}")
            return {"error": "Failed to generate deletion preview"}
