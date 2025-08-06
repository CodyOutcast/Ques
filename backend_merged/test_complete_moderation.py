"""
Test the complete content moderation service
Validates both text and image moderation capabilities
"""
import asyncio
import json
import sys
import os

# Add the backend path to sys.path to import modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.content_moderation import (
    content_moderation_service,
    moderate_text_content,
    moderate_image_content,
    moderate_profile
)

# Test data
TEST_PROFILES = [
    {
        "bio": "I love hiking and photography. Looking for someone who shares my passion for adventure!",
        "profile_picture": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400",
        "interests": "outdoor activities, travel, books"
    },
    {
        "bio": "Let's have sex tonight. I do drugs and party hard. Want to hook up?",
        "profile_picture": "https://example.com/suspicious-image.jpg",
        "occupation": "Adult entertainment"
    }
]

TEST_MESSAGES = [
    "Hi there! How was your weekend?",
    "You look beautiful in your photos!",
    "Let's meet tonight for sex and do some cocaine",
    "Want to see my naked photos? Send me yours!",
    "I work in finance and love traveling. What about you?"
]

TEST_IMAGES = [
    "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400",  # Normal portrait
    "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=400",  # Beach photo
    "https://invalid-url-for-testing.com/image.jpg"  # Invalid URL
]


async def test_text_moderation():
    """Test text content moderation"""
    print("\n🔤 TESTING TEXT MODERATION")
    print("=" * 50)
    
    for i, message in enumerate(TEST_MESSAGES, 1):
        print(f"\nTest {i}: {message[:50]}{'...' if len(message) > 50 else ''}")
        
        result = await moderate_text_content(message, f"test_user_{i}")
        
        status = "✅ APPROVED" if result.is_approved else "❌ BLOCKED"
        confidence = f"{result.confidence:.2f}"
        
        print(f"  Status: {status}")
        print(f"  Confidence: {confidence}")
        print(f"  Suggestion: {result.suggestion}")
        print(f"  Mode: {result.mode}")
        
        if result.reason:
            print(f"  Reason: {result.reason}")
        
        if result.blocked_words:
            print(f"  Blocked words: {result.blocked_words}")
        
        if result.scores:
            print(f"  Scores: {result.scores}")


async def test_image_moderation():
    """Test image content moderation"""
    print("\n🖼️ TESTING IMAGE MODERATION")
    print("=" * 50)
    
    for i, image_url in enumerate(TEST_IMAGES, 1):
        print(f"\nTest {i}: {image_url}")
        
        result = await moderate_image_content(image_url, f"test_user_{i}")
        
        status = "✅ APPROVED" if result.is_approved else "❌ BLOCKED"
        confidence = f"{result.confidence:.2f}"
        
        print(f"  Status: {status}")
        print(f"  Confidence: {confidence}")
        print(f"  Suggestion: {result.suggestion}")
        print(f"  Mode: {result.mode}")
        
        if result.reason:
            print(f"  Reason: {result.reason}")
        
        if result.image_labels:
            print(f"  Image labels: {result.image_labels}")
        
        if result.detected_objects:
            print(f"  Detected objects: {result.detected_objects}")
        
        if result.ocr_text:
            print(f"  OCR text: {result.ocr_text}")
        
        if result.scores:
            print(f"  Scores: {result.scores}")


async def test_profile_moderation():
    """Test complete profile moderation"""
    print("\n👤 TESTING PROFILE MODERATION")
    print("=" * 50)
    
    for i, profile in enumerate(TEST_PROFILES, 1):
        print(f"\nProfile {i}:")
        print(f"  Bio: {profile.get('bio', '')[:50]}{'...' if len(profile.get('bio', '')) > 50 else ''}")
        print(f"  Profile Picture: {profile.get('profile_picture', '')}")
        
        results = await moderate_profile(profile, f"test_user_{i}")
        
        print(f"  Moderation Results:")
        for field, result in results.items():
            status = "✅ APPROVED" if result.is_approved else "❌ BLOCKED"
            print(f"    {field}: {status} (confidence: {result.confidence:.2f})")
            
            if result.reason:
                print(f"      Reason: {result.reason}")
        
        # Overall profile status
        all_approved = all(result.is_approved for result in results.values())
        overall_status = "✅ PROFILE APPROVED" if all_approved else "❌ PROFILE BLOCKED"
        print(f"  Overall: {overall_status}")


async def test_service_methods():
    """Test service helper methods"""
    print("\n🔧 TESTING SERVICE METHODS")
    print("=" * 50)
    
    # Test with a blocked content result
    blocked_result = await moderate_text_content("Let's have sex and do drugs", "test_user")
    
    print(f"Should block: {content_moderation_service.should_block_content(blocked_result)}")
    print(f"Summary: {content_moderation_service.get_moderation_summary(blocked_result)}")
    
    # Test with approved content
    approved_result = await moderate_text_content("Hello, how are you?", "test_user")
    
    print(f"Should block: {content_moderation_service.should_block_content(approved_result)}")
    print(f"Summary: {content_moderation_service.get_moderation_summary(approved_result)}")


async def main():
    """Run all tests"""
    print("🚀 STARTING COMPLETE CONTENT MODERATION TESTS")
    print("=" * 60)
    
    try:
        await test_text_moderation()
        await test_image_moderation()
        await test_profile_moderation()
        await test_service_methods()
        
        print("\n✅ ALL TESTS COMPLETED SUCCESSFULLY!")
        
    except Exception as e:
        print(f"\n❌ TEST ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Clean up
        await content_moderation_service.close()


if __name__ == "__main__":
    asyncio.run(main())
