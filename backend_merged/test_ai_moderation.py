"""
Test AI-Enhanced Content Moderation with DeepSeek
Tests the triple-layer moderation system: Custom Keywords + AI Analysis + Tencent Cloud
"""
import asyncio
import sys
import os

# Add the backend path to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.enhanced_moderation import moderate_text_enhanced, moderate_profile_enhanced

async def test_ai_enhanced_moderation():
    """Test AI-enhanced moderation on various content types"""
    
    print("🤖 TESTING AI-ENHANCED MODERATION SERVICE")
    print("=" * 70)
    
    # Test cases with varying levels of explicitness
    test_cases = [
        # Clearly inappropriate (should be caught by all layers)
        "Let's have sex tonight. I do drugs and party hard. Want to hook up?",
        
        # Subtle inappropriate (should be caught by AI)
        "Looking for someone to Netflix and chill with. I'm very open-minded and adventurous.",
        
        # Borderline cases (AI should provide nuanced analysis)
        "I'm a massage therapist who loves to help people relax and feel good.",
        "I work in adult entertainment industry as a lighting technician.",
        "I'm 420 friendly and love good vibes.",
        
        # Scam-like content (should be caught)
        "I'm a successful crypto trader. DM me to learn my secrets!",
        "Contact me on WhatsApp for business opportunities.",
        
        # Normal dating content (should pass)
        "I love hiking, cooking, and meaningful conversations. Looking for someone genuine.",
        "Software engineer who enjoys weekend adventures and good coffee.",
        
        # Edge cases with context
        "I'm a pharmaceutical researcher working on drug development.",
        "I'm writing a book about adult relationships and intimacy.",
    ]
    
    print("🔍 TESTING VARIOUS CONTENT TYPES:")
    print("-" * 70)
    
    for i, text in enumerate(test_cases, 1):
        print(f"\n{i}. Text: {text[:60]}{'...' if len(text) > 60 else ''}")
        
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
    
    # Test the problematic Profile 2 with AI enhancement
    print(f"\n🔍 TESTING PROFILE 2 WITH AI ENHANCEMENT:")
    print("-" * 70)
    
    profile_2 = {
        "bio": "Let's have sex tonight. I do drugs and party hard. Want to hook up?",
        "occupation": "Adult entertainment",
        "interests": "Netflix and chill, 420 friendly, good vibes"
    }
    
    profile_results = await moderate_profile_enhanced(profile_2, "ai_test_user")
    
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
    
    # Test edge cases that might fool keyword filters but not AI
    print(f"\n🔍 TESTING SUBTLE CASES (AI vs Keywords):")
    print("-" * 70)
    
    subtle_cases = [
        "I'm very generous and looking for mutually beneficial arrangements 😉",
        "Let's skip the small talk and get straight to the fun part",
        "I know how to have a good time and show appreciation",
        "Looking for someone who understands the finer things in life 💰",
        "DM me for special content and exclusive experiences"
    ]
    
    for text in subtle_cases:
        result = await moderate_text_enhanced(text, "subtle_test")
        status = "✅ APPROVED" if result.is_approved else "❌ BLOCKED"
        print(f"'{text[:50]}...' → {status} (mode: {result.mode})")
        if result.reason:
            print(f"  Reason: {result.reason}")

if __name__ == "__main__":
    asyncio.run(test_ai_enhanced_moderation())
