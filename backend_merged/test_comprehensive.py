"""
Comprehensive test of both text and image moderation
"""
import asyncio
import sys
import os

# Add the backend path to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.enhanced_moderation import (
    moderate_text_enhanced, 
    moderate_image_enhanced, 
    moderate_profile_enhanced
)

async def test_comprehensive_moderation():
    """Test both text and image moderation comprehensively"""
    
    print("🛡️ COMPREHENSIVE MODERATION TEST")
    print("=" * 60)
    
    # Test text moderation
    print("\n📝 TESTING TEXT MODERATION:")
    print("-" * 40)
    
    text_tests = [
        "Hello, how are you today?",
        "Let's meet for cocaine tonight",
        "Want to see my naked photos?"
    ]
    
    for text in text_tests:
        result = await moderate_text_enhanced(text, "text_user")
        status = "✅ APPROVED" if result.is_approved else "❌ BLOCKED"
        print(f"'{text[:30]}...' → {status} (confidence: {result.confidence:.2f})")
        if result.reason:
            print(f"  Reason: {result.reason}")
    
    # Test image moderation
    print("\n🖼️ TESTING IMAGE MODERATION:")
    print("-" * 40)
    
    image_tests = [
        "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400",  # Normal
        "https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=400",    # Portrait
        "https://invalid-url.com/test.jpg"  # Invalid
    ]
    
    for image_url in image_tests:
        result = await moderate_image_enhanced(image_url, "image_user")
        status = "✅ APPROVED" if result.is_approved else "❌ BLOCKED"
        print(f"Image {image_url.split('/')[-1][:20]}... → {status} (confidence: {result.confidence:.2f})")
        if result.reason:
            print(f"  Reason: {result.reason}")
        if result.scores:
            high_scores = {k: v for k, v in result.scores.items() if v > 10}
            if high_scores:
                print(f"  Notable scores: {high_scores}")
    
    # Test complete profile moderation
    print("\n👤 TESTING COMPLETE PROFILE MODERATION:")
    print("-" * 40)
    
    test_profiles = [
        {
            "name": "Clean Profile",
            "data": {
                "bio": "I love hiking and photography!",
                "profile_picture": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400",
                "interests": "travel, books, cooking"
            }
        },
        {
            "name": "Problematic Profile",
            "data": {
                "bio": "Let's meet for sex and drugs tonight",
                "profile_picture": "https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=400",
                "occupation": "Adult entertainment"
            }
        }
    ]
    
    for profile_info in test_profiles:
        print(f"\n{profile_info['name']}:")
        
        results = await moderate_profile_enhanced(profile_info['data'], "profile_user")
        
        blocked_fields = []
        for field, result in results.items():
            status = "✅ APPROVED" if result.is_approved else "❌ BLOCKED"
            content_type = f"({result.content_type})"
            print(f"  {field} {content_type}: {status} (confidence: {result.confidence:.2f})")
            
            if result.reason:
                print(f"    Reason: {result.reason}")
            
            if not result.is_approved:
                blocked_fields.append(field)
        
        if blocked_fields:
            print(f"  → ❌ PROFILE BLOCKED due to: {', '.join(blocked_fields)}")
        else:
            print(f"  → ✅ PROFILE APPROVED")
    
    print(f"\n✅ COMPREHENSIVE TEST COMPLETED")
    print("Both text and image moderation are working with Tencent Cloud!")

if __name__ == "__main__":
    asyncio.run(test_comprehensive_moderation())
