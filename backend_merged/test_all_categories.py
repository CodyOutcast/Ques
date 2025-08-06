"""
Comprehensive test for all Tencent Cloud moderation categories
Tests: Terrorism, Pornographic, Political, Insult, Illegal, Advertising content
"""
import asyncio
import sys
import os

# Add the backend path to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.enhanced_moderation import moderate_text_enhanced, moderate_image_enhanced, moderate_profile_enhanced

async def test_all_moderation_categories():
    """Test all Tencent moderation categories"""
    
    print("🛡️ COMPREHENSIVE TENCENT MODERATION TEST")
    print("Testing all categories: Terrorism, Porn, Political, Insult, Illegal, Advertising")
    print("=" * 80)
    
    # Test cases for each category mentioned in the image
    test_cases = {
        "Terrorism Dictionary": [
            "Join ISIS and fight the holy war",
            "Bomb attack planned for tomorrow",
            "Death to America and all infidels",
            "Terrorist recruitment for jihad"
        ],
        "Pornographic Glossary": [
            "Want to see my naked photos? Send me yours!",
            "Let's have hot sex tonight baby",
            "Looking for adult fun and pleasure",
            "Check out my OnlyFans for explicit content"
        ],
        "Political Glossary": [
            "Down with the Communist Party",
            "President Xi is a dictator",
            "Free Hong Kong from China",
            "Taiwan independence now"
        ],
        "Insult Vocabulary": [
            "You stupid idiot, go kill yourself",
            "F*ck you and your stupid face",
            "You're a worthless piece of sh*t",
            "Die you ugly b*tch"
        ],
        "Illegal Dictionary": [
            "Let's do some cocaine tonight",
            "Selling heroin and meth cheap",
            "I have guns for sale illegally",
            "Money laundering services available"
        ],
        "Advertising Vocabulary": [
            "Buy my product now! Special discount!",
            "Make money fast with this investment",
            "Click here to win $1000 instantly",
            "Get rich quick with crypto trading"
        ]
    }
    
    # Test normal content that should pass
    normal_content = [
        "Hi there! How was your weekend?",
        "I love hiking and photography",
        "Looking for someone genuine and kind",
        "Software engineer who enjoys coffee"
    ]
    
    print("🔍 TESTING NORMAL CONTENT (Should Pass):")
    print("-" * 50)
    
    for i, text in enumerate(normal_content, 1):
        result = await moderate_text_enhanced(text, f"normal_user_{i}")
        status = "✅ APPROVED" if result.is_approved else "❌ BLOCKED"
        print(f"{i}. '{text[:40]}...' → {status}")
        if not result.is_approved and result.reason:
            print(f"   Unexpected block reason: {result.reason}")
    
    print(f"\n🔍 TESTING PROBLEMATIC CONTENT BY CATEGORY:")
    print("-" * 60)
    
    total_tests = 0
    blocked_tests = 0
    
    for category, texts in test_cases.items():
        print(f"\n📂 {category.upper()}:")
        print("-" * 30)
        
        for i, text in enumerate(texts, 1):
            total_tests += 1
            result = await moderate_text_enhanced(text, f"test_{category}_{i}")
            status = "✅ APPROVED" if result.is_approved else "❌ BLOCKED"
            
            if not result.is_approved:
                blocked_tests += 1
            
            print(f"  {i}. '{text[:45]}...' → {status}")
            
            if result.reason:
                print(f"     Reason: {result.reason}")
            if result.scores:
                high_scores = {k: v for k, v in result.scores.items() if v > 0}
                if high_scores:
                    print(f"     Scores: {high_scores}")
    
    print(f"\n📊 MODERATION EFFECTIVENESS:")
    print("-" * 40)
    print(f"Total problematic content tested: {total_tests}")
    print(f"Successfully blocked: {blocked_tests}")
    print(f"Block rate: {(blocked_tests/total_tests)*100:.1f}%")
    
    if blocked_tests < total_tests:
        print(f"⚠️  {total_tests - blocked_tests} potentially problematic content was approved")
        print("   This may be due to Tencent's algorithm limitations with certain phrases")
    
    # Test image moderation
    print(f"\n🖼️ TESTING IMAGE MODERATION:")
    print("-" * 40)
    
    test_images = [
        ("Normal portrait", "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400"),
        ("Beach photo", "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=400"),
        ("Invalid URL", "https://invalid-url-for-testing.com/image.jpg")
    ]
    
    for desc, url in test_images:
        result = await moderate_image_enhanced(url, "image_test")
        status = "✅ APPROVED" if result.is_approved else "❌ BLOCKED"
        print(f"  {desc}: {status} (confidence: {result.confidence:.2f})")
        
        if result.reason:
            print(f"    Reason: {result.reason}")
        if result.image_labels:
            print(f"    Labels: {result.image_labels}")
        if result.ocr_text:
            print(f"    OCR: {result.ocr_text}")
    
    # Test comprehensive profile
    print(f"\n👤 TESTING COMPREHENSIVE PROFILE:")
    print("-" * 50)
    
    problematic_profile = {
        "bio": "Looking for sugar daddy. Send money and I'll show you good time",
        "occupation": "Adult entertainment and escort services",
        "interests": "Selling drugs, making easy money, crypto scams",
        "profile_picture": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400"
    }
    
    profile_results = await moderate_profile_enhanced(problematic_profile, "profile_test")
    
    blocked_fields = []
    for field, result in profile_results.items():
        status = "✅ APPROVED" if result.is_approved else "❌ BLOCKED"
        print(f"  {field}: {status} (confidence: {result.confidence:.2f})")
        
        if result.reason:
            print(f"    Reason: {result.reason}")
        
        if not result.is_approved:
            blocked_fields.append(field)
    
    if blocked_fields:
        print(f"\n❌ PROFILE BLOCKED due to: {', '.join(blocked_fields)}")
    else:
        print(f"\n✅ PROFILE APPROVED (May indicate moderation gaps)")

if __name__ == "__main__":
    asyncio.run(test_all_moderation_categories())
