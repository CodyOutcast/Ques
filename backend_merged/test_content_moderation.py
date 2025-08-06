"""
Test Tencent Cloud Content Moderation Service Integration
"""
import asyncio
import json
from typing import Dict, Any

from services.content_moderation import (
    content_moderation_service,
    ModerationResult,
    moderate_text_content,
    moderate_image_content,
    moderate_user_profile_data,
    moderate_chat_message
)


async def test_text_moderation():
    """Test text content moderation"""
    print("🧪 Testing Text Moderation...")
    
    test_texts = [
        "Hello, how are you today?",  # Should pass
        "I love your profile!",       # Should pass
        "Let's meet up for coffee",   # Should pass
        "你好，很高兴认识你",           # Chinese - should pass
        "",                          # Empty - should pass
        "   ",                       # Whitespace - should pass
    ]
    
    for i, text in enumerate(test_texts, 1):
        try:
            result = await moderate_text_content(text, user_id=123)
            status = "✅ PASS" if result.result == ModerationResult.APPROVED else "❌ BLOCK"
            print(f"  Test {i}: {status}")
            print(f"    Text: '{text[:30]}{'...' if len(text) > 30 else ''}'")
            print(f"    Result: {result.result.value}")
            print(f"    Confidence: {result.confidence}")
            if result.violations:
                print(f"    Violations: {result.violations}")
            print()
        except Exception as e:
            print(f"  Test {i}: ⚠️  ERROR - {str(e)}")
            print()


async def test_image_moderation():
    """Test image content moderation"""
    print("🖼️  Testing Image Moderation...")
    
    test_images = [
        "https://example.com/profile1.jpg",
        "https://example.com/avatar.png",
        # Add more test URLs if you have them
    ]
    
    for i, image_url in enumerate(test_images, 1):
        try:
            result = await moderate_image_content(image_url, user_id=123)
            status = "✅ PASS" if result.result == ModerationResult.APPROVED else "❌ BLOCK"
            print(f"  Test {i}: {status}")
            print(f"    Image: {image_url}")
            print(f"    Result: {result.result.value}")
            print(f"    Confidence: {result.confidence}")
            if result.violations:
                print(f"    Violations: {result.violations}")
            print()
        except Exception as e:
            print(f"  Test {i}: ⚠️  ERROR - {str(e)}")
            print()


async def test_profile_moderation():
    """Test user profile moderation"""
    print("👤 Testing Profile Moderation...")
    
    test_profile = {
        "id": 123,
        "username": "testuser",
        "display_name": "Test User",
        "bio": "Love hiking and photography. Looking for meaningful connections.",
        "location": "San Francisco, CA",
        "occupation": "Software Engineer",
        "education": "UC Berkeley",
        "interests": "Travel, cooking, reading",
        "avatar_url": "https://example.com/avatar.jpg"
    }
    
    try:
        results = await moderate_user_profile_data(test_profile)
        print("  Profile moderation results:")
        
        all_approved = True
        for field, result in results.items():
            status = "✅ PASS" if result.result == ModerationResult.APPROVED else "❌ BLOCK"
            if result.result != ModerationResult.APPROVED:
                all_approved = False
            
            print(f"    {field}: {status}")
            print(f"      Result: {result.result.value}")
            print(f"      Confidence: {result.confidence}")
            if result.violations:
                print(f"      Violations: {result.violations}")
        
        print(f"\n  Overall: {'✅ Profile approved' if all_approved else '❌ Profile needs review'}")
        print()
        
    except Exception as e:
        print(f"  ⚠️  ERROR - {str(e)}")
        print()


async def test_message_moderation():
    """Test chat message moderation"""
    print("💬 Testing Message Moderation...")
    
    test_messages = [
        ("Hi there! How's your day going?", 1, 101),
        ("Would you like to grab coffee sometime?", 1, 101),
        ("I really enjoyed reading your profile", 2, 101),
        ("Thanks for the match! 😊", 2, 101),
    ]
    
    for i, (message, sender_id, chat_id) in enumerate(test_messages, 1):
        try:
            result = await moderate_chat_message(message, sender_id, chat_id)
            status = "✅ PASS" if result.result == ModerationResult.APPROVED else "❌ BLOCK"
            print(f"  Test {i}: {status}")
            print(f"    Message: '{message}'")
            print(f"    Sender: {sender_id}, Chat: {chat_id}")
            print(f"    Result: {result.result.value}")
            print(f"    Confidence: {result.confidence}")
            if result.violations:
                print(f"    Violations: {result.violations}")
            print()
        except Exception as e:
            print(f"  Test {i}: ⚠️  ERROR - {str(e)}")
            print()


async def test_service_availability():
    """Test if the moderation service is properly configured"""
    print("🔧 Testing Service Configuration...")
    
    try:
        # Test with minimal content
        result = await moderate_text_content("test", user_id=1)
        print("  ✅ Service is available and responding")
        print(f"    Test result: {result.result.value}")
        print(f"    Confidence: {result.confidence}")
        
        # Check if we have proper credentials
        if hasattr(content_moderation_service, 'secret_id') and content_moderation_service.secret_id:
            print("  ✅ Tencent Cloud credentials configured")
        else:
            print("  ⚠️  Tencent Cloud credentials not found - using fallback mode")
        
        print()
        
    except Exception as e:
        print(f"  ❌ Service configuration error: {str(e)}")
        print("  🔧 Check your .env file for:")
        print("     - TENCENT_SECRET_ID")
        print("     - TENCENT_SECRET_KEY")
        print("     - ENABLE_CONTENT_MODERATION=true")
        print()


async def main():
    """Run all content moderation tests"""
    print("🛡️  TENCENT CLOUD CONTENT MODERATION TESTING")
    print("=" * 50)
    print()
    
    # Test service availability first
    await test_service_availability()
    
    # Run all tests
    await test_text_moderation()
    await test_image_moderation()
    await test_profile_moderation()
    await test_message_moderation()
    
    print("🎉 Content moderation testing completed!")
    print()
    print("📝 Integration Notes:")
    print("   • All user-generated content is automatically moderated")
    print("   • Text messages in chats are filtered before sending")
    print("   • Profile information is checked during updates")
    print("   • Images are scanned for inappropriate content")
    print("   • Blocked content returns clear error messages")
    print("   • Service gracefully handles failures with fallback approval")


if __name__ == "__main__":
    asyncio.run(main())
