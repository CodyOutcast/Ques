"""
Auto Tag Generation Service
Automatically generates feature tags from user bios when they don't have any
"""

import json
import logging
import requests
import os
from typing import List, Optional
from sqlalchemy.orm import Session
from models.users import User

logger = logging.getLogger(__name__)

# Get DeepSeek API key from environment
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_URL = "https://api.deepseek.com/v1/chat/completions"

class AutoTagService:
    """Service for automatically generating tags from user bios"""
    
    @staticmethod
    def extract_tags_from_bio(bio: str) -> Optional[List[str]]:
        """
        Extract feature tags from user's bio using DeepSeek AI
        
        Args:
            bio: User's biography text
            
        Returns:
            List of extracted tags or None if extraction fails
        """
        if not DEEPSEEK_API_KEY:
            logger.warning("DeepSeek API key not configured, cannot auto-generate tags")
            return None
            
        if not bio or len(bio.strip()) < 10:
            logger.info("Bio too short for tag extraction")
            return None
        
        try:
            logger.info(f"Extracting tags from bio: {bio[:100]}...")
            
            prompt = (
                f"Extract 3-7 professional feature tags from this user's biography: '{bio}'. "
                "Focus on skills, roles, industries, technologies, and professional interests. "
                "Examples: 'Data Scientist', 'Full-stack Developer', 'Blockchain', 'AI/ML', "
                "'Product Manager', 'Startup Founder', 'Venture Capital', 'Healthcare', 'Fintech'. "
                "Make tags specific and professionally relevant. "
                "Output only a JSON list of tags, e.g., [\"tag1\", \"tag2\", \"tag3\"]."
            )
            
            payload = {
                "model": "deepseek-chat",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.3,  # Lower temperature for more consistent results
                "max_tokens": 300
            }
            headers = {
                "Authorization": f"Bearer {DEEPSEEK_API_KEY}", 
                "Content-Type": "application/json"
            }
            
            response = requests.post(DEEPSEEK_URL, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            content = response.json()['choices'][0]['message']['content']
            
            # Clean the content and parse JSON
            content = content.strip()
            if content.startswith('```json'):
                content = content[7:]
            if content.endswith('```'):
                content = content[:-3]
            content = content.strip()
            
            tags = json.loads(content)
            
            # Validate tags
            if not isinstance(tags, list) or len(tags) < 1 or len(tags) > 10:
                logger.warning(f"Invalid tag count: {len(tags) if isinstance(tags, list) else 'not a list'}")
                return None
                
            # Clean and validate individual tags
            clean_tags = []
            for tag in tags:
                if isinstance(tag, str) and len(tag.strip()) > 1 and len(tag.strip()) < 50:
                    clean_tags.append(tag.strip())
            
            if len(clean_tags) < 1:
                logger.warning("No valid tags extracted")
                return None
                
            logger.info(f"Extracted {len(clean_tags)} tags from bio: {clean_tags}")
            return clean_tags[:7]  # Limit to 7 tags max
            
        except requests.exceptions.RequestException as e:
            logger.error(f"DeepSeek API request error: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse DeepSeek response as JSON: {e}")
            return None
        except Exception as e:
            logger.error(f"Error extracting tags from bio: {e}")
            return None
    
    @staticmethod
    def auto_generate_user_tags(db: Session, user_id: int, force_update: bool = False) -> bool:
        """
        Automatically generate and save tags for a user if they don't have any
        
        Args:
            db: Database session
            user_id: User ID to generate tags for
            force_update: Whether to update tags even if user already has some
            
        Returns:
            True if tags were generated and saved, False otherwise
        """
        try:
            # Get user
            user = db.query(User).filter(User.user_id == user_id).first()
            if not user:
                logger.error(f"User {user_id} not found")
                return False
            
            # Check if user already has tags (unless force_update is True)
            has_existing_tags = user.feature_tags and (
                (isinstance(user.feature_tags, list) and len(user.feature_tags) > 0) or
                (isinstance(user.feature_tags, str) and len(user.feature_tags.strip()) > 2)
            )
            
            if has_existing_tags and not force_update:
                logger.info(f"User {user_id} already has tags, skipping auto-generation")
                return False
            
            # Check if user has a bio to extract from
            if not user.bio or len(user.bio.strip()) < 10:
                logger.info(f"User {user_id} bio too short for tag extraction")
                return False
            
            # Extract tags from bio
            extracted_tags = AutoTagService.extract_tags_from_bio(user.bio)
            if not extracted_tags:
                logger.warning(f"Failed to extract tags from bio for user {user_id}")
                return False
            
            # Save tags to user
            user.feature_tags = extracted_tags
            db.commit()
            
            logger.info(f"Successfully auto-generated {len(extracted_tags)} tags for user {user_id}: {extracted_tags}")
            return True
            
        except Exception as e:
            logger.error(f"Error auto-generating tags for user {user_id}: {e}")
            db.rollback()
            return False
    
    @staticmethod
    def auto_generate_tags_for_users_without_tags(db: Session, limit: int = 10) -> int:
        """
        Batch process to auto-generate tags for users who don't have any
        
        Args:
            db: Database session
            limit: Maximum number of users to process in one batch
            
        Returns:
            Number of users that got new tags
        """
        try:
            # Find users without tags but with bios
            users_without_tags = db.query(User).filter(
                User.bio.isnot(None),
                User.bio != "",
                (User.feature_tags.is_(None) | (User.feature_tags == "[]") | (User.feature_tags == ""))
            ).limit(limit).all()
            
            logger.info(f"Found {len(users_without_tags)} users without tags to process")
            
            success_count = 0
            for user in users_without_tags:
                if AutoTagService.auto_generate_user_tags(db, user.user_id):
                    success_count += 1
            
            logger.info(f"Successfully generated tags for {success_count}/{len(users_without_tags)} users")
            return success_count
            
        except Exception as e:
            logger.error(f"Error in batch tag generation: {e}")
            return 0
