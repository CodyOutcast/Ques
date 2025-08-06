"""
Simple Content Moderation Service
Uses only Tencent Cloud moderation for content filtering
"""
from typing import Dict
from services.content_moderation import (
    ModerationResult, 
    TencentContentModerationService,
    moderate_text_content,
    moderate_image_content,
    moderate_profile
)

# Just use the standard Tencent moderation service
enhanced_moderation_service = TencentContentModerationService()

# Simple convenience functions that use standard Tencent moderation
async def moderate_text_enhanced(text: str, user_id: str = None) -> ModerationResult:
    """Enhanced text moderation (uses standard Tencent moderation)"""
    return await moderate_text_content(text, user_id)

async def moderate_image_enhanced(image_url: str, user_id: str = None) -> ModerationResult:
    """Enhanced image moderation (uses standard Tencent moderation)"""
    return await moderate_image_content(image_url, user_id)

async def moderate_profile_enhanced(profile_data: Dict[str, any], user_id: str = None) -> Dict[str, ModerationResult]:
    """Enhanced profile moderation (uses standard Tencent moderation)"""
    return await moderate_profile(profile_data, user_id)
