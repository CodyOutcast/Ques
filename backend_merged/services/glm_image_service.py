"""
GLM-4V Image-to-Text Service
Uses GLM-4V model to generate descriptions of profile images
"""

import os
import base64
import logging
from typing import Optional
from zhipuai import ZhipuAI

logger = logging.getLogger(__name__)


class GLMImageToTextService:
    """
    Service for generating text descriptions from images using GLM-4V
    """
    
    # Default prompt for profile image description
    DEFAULT_PROMPT = """Please analyze this profile image and provide a detailed description in the following format:

1. **Visual Appearance**: Describe the person's appearance, including gender, approximate age range, hair style, clothing style, and any distinctive features.

2. **Setting & Background**: Describe the environment or background of the photo - is it indoors/outdoors, professional setting, casual setting, nature, urban, etc.

3. **Mood & Expression**: Describe the person's facial expression, body language, and the overall mood conveyed by the image.

4. **Photo Quality & Style**: Comment on the photo quality, lighting, composition, and whether it appears to be a professional photo, selfie, or candid shot.

5. **Overall Impression**: Provide a brief overall impression that could help match this person with potential collaborators or friends.

Please be objective, respectful, and focus on details that would be helpful for social networking and professional collaboration purposes. Keep the description concise but informative."""

    def __init__(self, api_key: str = None):
        """
        Initialize GLM-4V service
        
        Args:
            api_key: ZhipuAI API key (uses GLM_API_KEY from env if not provided)
        """
        self.api_key = api_key or os.getenv("GLM_API_KEY")
        if not self.api_key:
            raise ValueError("GLM_API_KEY must be provided or set in environment")
        
        self.client = ZhipuAI(api_key=self.api_key)
        logger.info("GLM-4V Image-to-Text Service initialized")
    
    def describe_image_from_url(
        self,
        image_url: str,
        custom_prompt: Optional[str] = None
    ) -> Optional[str]:
        """
        Generate description from image URL
        
        Args:
            image_url: URL of the image to analyze
            custom_prompt: Custom prompt (uses default if not provided)
        
        Returns:
            Generated description text, or None if failed
        """
        try:
            prompt = custom_prompt or self.DEFAULT_PROMPT
            
            response = self.client.chat.completions.create(
                model="glm-4v",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": image_url
                                }
                            }
                        ]
                    }
                ],
                temperature=0.3,  # Lower temperature for more consistent descriptions
                max_tokens=800
            )
            
            description = response.choices[0].message.content
            logger.info(f"Generated image description from URL: {image_url[:50]}...")
            return description
            
        except Exception as e:
            logger.error(f"Error generating image description from URL: {e}")
            return None
    
    def describe_image_from_base64(
        self,
        image_base64: str,
        custom_prompt: Optional[str] = None
    ) -> Optional[str]:
        """
        Generate description from base64 encoded image
        
        Args:
            image_base64: Base64 encoded image string
            custom_prompt: Custom prompt (uses default if not provided)
        
        Returns:
            Generated description text, or None if failed
        """
        try:
            prompt = custom_prompt or self.DEFAULT_PROMPT
            
            # Ensure base64 string has proper data URI format
            if not image_base64.startswith('data:'):
                # Assume it's a JPEG if no format specified
                image_base64 = f"data:image/jpeg;base64,{image_base64}"
            
            response = self.client.chat.completions.create(
                model="glm-4v",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": image_base64
                                }
                            }
                        ]
                    }
                ],
                temperature=0.3,
                max_tokens=800
            )
            
            description = response.choices[0].message.content
            logger.info("Generated image description from base64 data")
            return description
            
        except Exception as e:
            logger.error(f"Error generating image description from base64: {e}")
            return None
    
    def describe_image_from_file(
        self,
        image_path: str,
        custom_prompt: Optional[str] = None
    ) -> Optional[str]:
        """
        Generate description from local image file
        
        Args:
            image_path: Path to local image file
            custom_prompt: Custom prompt (uses default if not provided)
        
        Returns:
            Generated description text, or None if failed
        """
        try:
            # Read and encode image
            with open(image_path, 'rb') as image_file:
                image_data = image_file.read()
                image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            # Determine image format from file extension
            ext = os.path.splitext(image_path)[1].lower()
            format_map = {
                '.jpg': 'jpeg',
                '.jpeg': 'jpeg',
                '.png': 'png',
                '.gif': 'gif',
                '.webp': 'webp'
            }
            image_format = format_map.get(ext, 'jpeg')
            
            # Create data URI
            data_uri = f"data:image/{image_format};base64,{image_base64}"
            
            return self.describe_image_from_base64(data_uri, custom_prompt)
            
        except Exception as e:
            logger.error(f"Error reading image file {image_path}: {e}")
            return None
    
    def describe_profile_image(
        self,
        image_source: str,
        source_type: str = "url"
    ) -> Optional[str]:
        """
        Convenience method for profile image description
        
        Args:
            image_source: Image URL, base64 string, or file path
            source_type: Type of source - "url", "base64", or "file"
        
        Returns:
            Generated description text, or None if failed
        """
        if source_type == "url":
            return self.describe_image_from_url(image_source)
        elif source_type == "base64":
            return self.describe_image_from_base64(image_source)
        elif source_type == "file":
            return self.describe_image_from_file(image_source)
        else:
            logger.error(f"Invalid source_type: {source_type}")
            return None


# Singleton instance
_image_service_instance = None


def get_image_service() -> GLMImageToTextService:
    """
    Get singleton instance of GLMImageToTextService
    
    Returns:
        GLMImageToTextService instance
    """
    global _image_service_instance
    if _image_service_instance is None:
        _image_service_instance = GLMImageToTextService()
    return _image_service_instance
