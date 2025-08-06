"""
Test simplified moderation service using only Tencent Cloud
"""
import asyncio
import sys
import os

# Add the backend path to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.enhanced_moderation import moderate_text_enhanced, moderate_profile_enhanced

async def test_simple_moderation():
    """Test simplified moderation with only Tencent Cloud"""
    
    print("🛡️ TESTING SIMPLIFIED TENCENT-ONLY MODERATION")
    print("=" * 60)
    
    # Test the same problematic texts
    test_texts = [
        "Hi there! How was your weekend?",
        "Let's have sex tonight. I do drugs and party hard. Want to hook up?",
        "Let's meet tonight for sex and do some cocaine",
        "Want to see my naked photos? Send me yours!",
        "I work in finance and love traveling."
    ]
    
    print("🔍 TESTING TEXT MODERATION:")
    print("-" * 40)
    
    for i, text in enumerate(test_texts, 1):
        print(f"\n{i}. Text: {text[:50]}{'...' if len(text) > 50 else ''}")
        
        result = await moderate_text_enhanced(text, f"test_user_{i}")
        
        status = "✅ APPROVED" if result.is_approved else "❌ BLOCKED"
        print(f"   Status: {status}")
        print(f"   Confidence: {result.confidence:.2f}")
        print(f"   Mode: {result.mode}")
        
        if result.reason:
            print(f"   Reason: {result.reason}")
        
        if result.blocked_words:
            print(f"   Blocked words: {result.blocked_words}")
        
        if result.scores:
            print(f"   Scores: {result.scores}")
    
    # Test Profile 2 with simplified moderation
    print(f"\n🔍 TESTING PROFILE 2 WITH SIMPLIFIED MODERATION:")
    print("-" * 60)
    
    profile_2 = {
        "bio": "Let's have sex tonight. I do drugs and party hard. Want to hook up?",
        "occupation": "Adult entertainment",
        "interests": "outdoor activities, travel, books"
    }
    
    profile_results = await moderate_profile_enhanced(profile_2, "simple_test_user")
    
    blocked_fields = []
    for field, result in profile_results.items():
        status = "✅ APPROVED" if result.is_approved else "❌ BLOCKED"
        print(f"{field}: {status} (confidence: {result.confidence:.2f}, mode: {result.mode})")
        
        if result.reason:
            print(f"  Reason: {result.reason}")
        
        if not result.is_approved:
            blocked_fields.append(field)
    
    if blocked_fields:
        print(f"\n❌ PROFILE BLOCKED due to: {', '.join(blocked_fields)}")
    else:
        print(f"\n✅ PROFILE APPROVED")
        print("\nNote: Profile 2 bio contains explicit content but may be approved")
        print("by Tencent's moderation due to euphemistic language patterns.")

if __name__ == "__main__":
    asyncio.run(test_simple_moderation())
