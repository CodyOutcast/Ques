"""
Test the enhanced moderation service that should catch Profile 2 issues
"""
import asyncio
import sys
import os

# Add the backend path to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.enhanced_moderation import moderate_text_enhanced, moderate_profile_enhanced

async def test_enhanced_moderation():
    """Test enhanced moderation on problematic content"""
    
    print("🚀 TESTING ENHANCED MODERATION SERVICE")
    print("=" * 60)
    
    # Test the problematic bio from Profile 2
    problem_bio = "Let's have sex tonight. I do drugs and party hard. Want to hook up?"
    
    print(f"\n🔍 TESTING PROBLEMATIC BIO:")
    print(f"Text: {problem_bio}")
    print("-" * 50)
    
    result = await moderate_text_enhanced(problem_bio, "test_user")
    
    status = "✅ APPROVED" if result.is_approved else "❌ BLOCKED"
    print(f"Status: {status}")
    print(f"Confidence: {result.confidence:.2f}")
    print(f"Suggestion: {result.suggestion}")
    print(f"Mode: {result.mode}")
    
    if result.reason:
        print(f"Reason: {result.reason}")
    
    if result.blocked_words:
        print(f"Blocked words: {result.blocked_words}")
    
    if result.scores:
        print(f"Scores: {result.scores}")
    
    # Test other problematic content
    test_texts = [
        "Adult entertainment professional",
        "Want to hook up tonight?",
        "I do drugs and party",
        "Looking for FWB relationship",
        "Send me money via Bitcoin",
        "Contact me on WhatsApp only"
    ]
    
    print(f"\n🔍 TESTING OTHER PROBLEMATIC CONTENT:")
    print("-" * 50)
    
    for text in test_texts:
        result = await moderate_text_enhanced(text, "test_user")
        status = "✅ APPROVED" if result.is_approved else "❌ BLOCKED"
        print(f"'{text[:30]}...' → {status} (confidence: {result.confidence:.2f})")
        if result.reason:
            print(f"  Reason: {result.reason}")
    
    # Test the complete Profile 2
    profile_2 = {
        "bio": "Let's have sex tonight. I do drugs and party hard. Want to hook up?",
        "profile_picture": "https://example.com/suspicious-image.jpg",
        "occupation": "Adult entertainment"
    }
    
    print(f"\n🔍 TESTING COMPLETE PROFILE 2:")
    print("-" * 50)
    
    profile_results = await moderate_profile_enhanced(profile_2, "profile_user")
    
    for field, result in profile_results.items():
        status = "✅ APPROVED" if result.is_approved else "❌ BLOCKED"
        print(f"{field}: {status} (confidence: {result.confidence:.2f})")
        if result.reason:
            print(f"  Reason: {result.reason}")
        if result.blocked_words:
            print(f"  Blocked words: {result.blocked_words}")
    
    # Overall profile decision
    blocked_fields = [field for field, result in profile_results.items() if not result.is_approved]
    if blocked_fields:
        print(f"\n❌ PROFILE BLOCKED due to: {', '.join(blocked_fields)}")
    else:
        print(f"\n✅ PROFILE APPROVED")

if __name__ == "__main__":
    asyncio.run(test_enhanced_moderation())
