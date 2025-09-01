"""
Enhanced Profile Service with Auto Tag Generation
"""

from typing import Dict, Any
from sqlalchemy.orm import Session
from models.users import User
from services.auto_tag_service import AutoTagService
import logging

logger = logging.getLogger(__name__)

class EnhancedProfileService:
    """Enhanced profile service that auto-generates tags from bio updates"""
    
    @staticmethod
    def update_user_profile(
        db: Session, 
        user_id: int, 
        profile_data: Dict[str, Any], 
        auto_generate_tags: bool = True
    ) -> Dict[str, Any]:
        """
        Update user profile with optional auto tag generation
        
        Args:
            db: Database session
            user_id: User ID to update
            profile_data: Dictionary of profile fields to update
            auto_generate_tags: Whether to auto-generate tags from bio
            
        Returns:
            Dictionary with update status and any generated tags
        """
        try:
            # Get user
            user = db.query(User).filter(User.user_id == user_id).first()
            if not user:
                return {"success": False, "error": "User not found"}
            
            # Track if bio was updated
            bio_updated = False
            old_bio = user.bio
            
            # Update allowed fields
            allowed_fields = [
                'name', 'bio', 'location', 'age', 'gender', 
                'avatar_url', 'interests', 'occupation', 'education',
                'display_name', 'about_me'
            ]
            
            updated_fields = []
            for field in allowed_fields:
                if field in profile_data:
                    setattr(user, field, profile_data[field])
                    updated_fields.append(field)
                    if field == 'bio':
                        bio_updated = True
            
            # Save profile updates
            db.commit()
            
            result = {
                "success": True,
                "updated_fields": updated_fields,
                "auto_tags_generated": False,
                "generated_tags": []
            }
            
            # Auto-generate tags if bio was updated and user doesn't have tags
            if auto_generate_tags and bio_updated and profile_data.get('bio'):
                logger.info(f"Bio updated for user {user_id}, checking for auto tag generation")
                
                # Check if user needs tags
                needs_tags = not user.feature_tags or (
                    isinstance(user.feature_tags, list) and len(user.feature_tags) == 0
                ) or (
                    isinstance(user.feature_tags, str) and len(user.feature_tags.strip()) <= 2
                )
                
                if needs_tags:
                    logger.info(f"User {user_id} needs tags, attempting auto-generation")
                    
                    # Try to generate tags from the new bio
                    extracted_tags = AutoTagService.extract_tags_from_bio(profile_data['bio'])
                    
                    if extracted_tags:
                        user.feature_tags = extracted_tags
                        db.commit()
                        
                        result["auto_tags_generated"] = True
                        result["generated_tags"] = extracted_tags
                        
                        logger.info(f"Auto-generated {len(extracted_tags)} tags for user {user_id}: {extracted_tags}")
                    else:
                        logger.warning(f"Failed to auto-generate tags for user {user_id}")
                else:
                    logger.info(f"User {user_id} already has tags, skipping auto-generation")
            
            return result
            
        except Exception as e:
            logger.error(f"Error updating profile for user {user_id}: {e}")
            db.rollback()
            return {"success": False, "error": str(e)}
    
    @staticmethod
    def ensure_user_has_tags(db: Session, user_id: int) -> bool:
        """
        Ensure a user has feature tags, generating them if necessary
        
        Args:
            db: Database session
            user_id: User ID to check
            
        Returns:
            True if user has tags (existing or newly generated)
        """
        try:
            user = db.query(User).filter(User.user_id == user_id).first()
            if not user:
                return False
            
            # Check if user already has meaningful tags
            has_tags = user.feature_tags and (
                (isinstance(user.feature_tags, list) and len(user.feature_tags) > 0) or
                (isinstance(user.feature_tags, str) and len(user.feature_tags.strip()) > 2)
            )
            
            if has_tags:
                return True
            
            # Try to generate tags from bio
            if user.bio and len(user.bio.strip()) >= 10:
                return AutoTagService.auto_generate_user_tags(db, user_id)
            
            return False
            
        except Exception as e:
            logger.error(f"Error ensuring tags for user {user_id}: {e}")
            return False
