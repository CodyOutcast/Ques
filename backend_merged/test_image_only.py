"""
Test image moderation with the simplified service
"""
import asyncio
import sys
import os

# Add the backend path to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.enhanced_moderation import enhanced_moderation_service

async def test_image_moderation():
    """Test image moderation functionality"""
    
    print("🖼️ TESTING IMAGE MODERATION")
    print("=" * 50)
    
    # Test various image URLs
    test_images = [
        "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400",  # Normal portrait
        "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=400",  # Beach photo
        "https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=400",    # Another portrait
        "https://invalid-url-for-testing.com/image.jpg"  # Invalid URL
    ]
    
    for i, image_url in enumerate(test_images, 1):
        print(f"\n{i}. Testing image: {image_url}")
        
        try:
            result = await enhanced_moderation_service.moderate_image_url(image_url, f"test_user_{i}")
            
            status = "✅ APPROVED" if result.is_approved else "❌ BLOCKED"
            print(f"   Status: {status}")
            print(f"   Confidence: {result.confidence:.2f}")
            print(f"   Mode: {result.mode}")
            print(f"   Content Type: {result.content_type}")
            
            if result.reason:
                print(f"   Reason: {result.reason}")
            
            if result.image_labels:
                print(f"   Image Labels: {result.image_labels}")
            
            if result.detected_objects:
                print(f"   Detected Objects: {result.detected_objects}")
            
            if result.ocr_text:
                print(f"   OCR Text: {result.ocr_text}")
            
            if result.scores:
                print(f"   Scores: {result.scores}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    # Test profile with images
    print(f"\n🔍 TESTING PROFILE WITH IMAGES:")
    print("-" * 50)
    
    profile_with_images = {
        "bio": "I love photography and outdoor adventures!",
        "profile_picture": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400",
        "interests": "hiking, photography, travel"
    }
    
    try:
        from services.enhanced_moderation import moderate_profile_enhanced
        profile_results = await moderate_profile_enhanced(profile_with_images, "image_test_user")
        
        for field, result in profile_results.items():
            status = "✅ APPROVED" if result.is_approved else "❌ BLOCKED"
            content_type = result.content_type
            print(f"{field} ({content_type}): {status} (confidence: {result.confidence:.2f})")
            
            if result.reason:
                print(f"  Reason: {result.reason}")
            
            if result.content_type == "image":
                if result.ocr_text:
                    print(f"  OCR: {result.ocr_text}")
                if result.scores:
                    print(f"  Image Scores: {result.scores}")
    
    except Exception as e:
        print(f"❌ Profile test error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_image_moderation())
