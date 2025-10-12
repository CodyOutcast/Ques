"""
Profile Photo Router
Handles profile photo upload and AI description generation
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from typing import Optional
import logging
import os
import base64
from PIL import Image
import io

from dependencies.db import get_db
from models.users import User
from models.user_profiles import UserProfile
from services.auth_service import AuthService
from services.glm_image_service import get_image_service

router = APIRouter()
security = HTTPBearer()
logger = logging.getLogger(__name__)
auth_service = AuthService()

# Configuration
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./uploads/profile_photos")

# Ensure upload directory exists
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload-photo")
async def upload_profile_photo(
    file: UploadFile = File(...),
    generate_description: bool = Form(True),
    custom_prompt: Optional[str] = Form(None),
    token: str = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Upload profile photo and optionally generate AI description
    
    Args:
        file: Image file to upload
        generate_description: Whether to generate AI description (default: True)
        custom_prompt: Custom prompt for image description
        token: Authentication token
        db: Database session
    
    Returns:
        Profile photo URL and AI-generated description
    """
    try:
        # Authenticate user
        current_user = auth_service.get_current_user(db, token.credentials)
        if not current_user:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        # Validate file extension
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
            )
        
        # Read file content
        file_content = await file.read()
        
        # Validate file size
        if len(file_content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Maximum size: {MAX_FILE_SIZE // (1024*1024)}MB"
            )
        
        # Validate it's a real image
        try:
            image = Image.open(io.BytesIO(file_content))
            image.verify()
            # Re-open after verify (verify closes the file)
            image = Image.open(io.BytesIO(file_content))
        except Exception as e:
            logger.error(f"Invalid image file: {e}")
            raise HTTPException(status_code=400, detail="Invalid image file")
        
        # Generate unique filename
        user_id = current_user.id
        filename = f"user_{user_id}_profile{file_ext}"
        file_path = os.path.join(UPLOAD_DIR, filename)
        
        # Save file
        with open(file_path, 'wb') as f:
            f.write(file_content)
        
        # Generate public URL (adjust based on your setup)
        # This assumes you have a static file server serving UPLOAD_DIR
        photo_url = f"/static/profile_photos/{filename}"
        
        # Get or create user profile
        user_profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
        if not user_profile:
            raise HTTPException(status_code=404, detail="User profile not found. Please create profile first.")
        
        # Update user profile photo URL
        user_profile.profile_photo = photo_url
        
        # Generate AI description if requested
        description = None
        if generate_description:
            try:
                logger.info(f"Generating AI description for user {user_id} profile photo")
                
                # Convert image to base64 for GLM-4V
                image_base64 = base64.b64encode(file_content).decode('utf-8')
                image_format = file_ext.lstrip('.')
                if image_format == 'jpg':
                    image_format = 'jpeg'
                data_uri = f"data:image/{image_format};base64,{image_base64}"
                
                # Get image service and generate description
                image_service = get_image_service()
                description = image_service.describe_image_from_base64(
                    data_uri,
                    custom_prompt=custom_prompt
                )
                
                if description:
                    # Store description in user profile
                    user_profile.profile_image_description = description
                    logger.info(f"Successfully generated description for user {user_id}")
                else:
                    logger.warning(f"Failed to generate description for user {user_id}")
                    
            except Exception as e:
                logger.error(f"Error generating image description: {e}")
                # Don't fail the upload if description generation fails
                description = None
        
        # Commit changes
        db.commit()
        db.refresh(user_profile)
        
        return {
            "success": True,
            "message": "Profile photo uploaded successfully",
            "photo_url": photo_url,
            "description": description,
            "description_generated": description is not None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading profile photo: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to upload photo: {str(e)}")


@router.put("/update-photo-url")
async def update_profile_photo_url(
    photo_url: str = Form(...),
    generate_description: bool = Form(True),
    custom_prompt: Optional[str] = Form(None),
    token: str = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Update profile photo URL (for externally hosted images) and generate description
    
    Args:
        photo_url: URL of the profile photo
        generate_description: Whether to generate AI description
        custom_prompt: Custom prompt for image description
        token: Authentication token
        db: Database session
    """
    try:
        # Authenticate user
        current_user = auth_service.get_current_user(db, token.credentials)
        if not current_user:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        # Get user profile
        user_profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
        if not user_profile:
            raise HTTPException(status_code=404, detail="User profile not found. Please create profile first.")
        
        # Update photo URL
        user_profile.profile_photo = photo_url
        
        # Generate AI description if requested
        description = None
        if generate_description:
            try:
                logger.info(f"Generating AI description from URL for user {current_user.id}")
                
                # Get image service and generate description
                image_service = get_image_service()
                description = image_service.describe_image_from_url(
                    photo_url,
                    custom_prompt=custom_prompt
                )
                
                if description:
                    user_profile.profile_image_description = description
                    logger.info(f"Successfully generated description for user {current_user.id}")
                else:
                    logger.warning(f"Failed to generate description for user {current_user.id}")
                    
            except Exception as e:
                logger.error(f"Error generating image description from URL: {e}")
                description = None
        
        # Commit changes
        db.commit()
        db.refresh(user_profile)
        
        return {
            "success": True,
            "message": "Profile photo URL updated successfully",
            "photo_url": photo_url,
            "description": description,
            "description_generated": description is not None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating profile photo URL: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update photo URL: {str(e)}")


@router.post("/regenerate-description")
async def regenerate_photo_description(
    custom_prompt: Optional[str] = Form(None),
    token: str = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Regenerate AI description for existing profile photo
    
    Args:
        custom_prompt: Custom prompt for image description
        token: Authentication token
        db: Database session
    """
    try:
        # Authenticate user
        current_user = auth_service.get_current_user(db, token.credentials)
        if not current_user:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        # Get user profile
        user_profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
        if not user_profile:
            raise HTTPException(status_code=404, detail="User profile not found")
        
        # Check if user has a profile photo
        if not user_profile.profile_photo:
            raise HTTPException(status_code=400, detail="No profile photo found")
        
        # Generate AI description
        logger.info(f"Regenerating AI description for user {current_user.id}")
        
        # Get image service
        image_service = get_image_service()
        
        # Determine if it's a local file or URL
        if user_profile.profile_photo.startswith('http'):
            # External URL
            description = image_service.describe_image_from_url(
                user_profile.profile_photo,
                custom_prompt=custom_prompt
            )
        else:
            # Local file
            file_path = os.path.join(UPLOAD_DIR, os.path.basename(user_profile.profile_photo))
            if os.path.exists(file_path):
                description = image_service.describe_image_from_file(
                    file_path,
                    custom_prompt=custom_prompt
                )
            else:
                raise HTTPException(status_code=404, detail="Profile photo file not found")
        
        if description:
            user_profile.profile_image_description = description
            db.commit()
            db.refresh(user_profile)
            logger.info(f"Successfully regenerated description for user {current_user.id}")
            
            return {
                "success": True,
                "message": "Photo description regenerated successfully",
                "description": description
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to generate description")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error regenerating photo description: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to regenerate description: {str(e)}")


@router.get("/photo-description")
async def get_photo_description(
    token: str = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Get current profile photo description
    
    Args:
        token: Authentication token
        db: Database session
    """
    try:
        # Authenticate user
        current_user = auth_service.get_current_user(db, token.credentials)
        if not current_user:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        # Get user profile
        user_profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
        if not user_profile:
            raise HTTPException(status_code=404, detail="User profile not found")
        
        return {
            "photo_url": user_profile.profile_photo,
            "description": user_profile.profile_image_description
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting photo description: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get description: {str(e)}")
