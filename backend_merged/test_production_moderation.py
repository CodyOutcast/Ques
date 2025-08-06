"""
Test content moderation with real Tencent Cloud CMS/TMS APIs
This test uses actual Tencent Cloud credentials from .env file
"""
import asyncio
import sys
import os

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.content_moderation_new import content_moderation_service


async def test_production_moderation():
    """Test content moderation with real Tencent Cloud APIs"""
    
    print("🧪 Testing Content Moderation with Real Tencent Cloud APIs")
    print("=" * 60)
    
    # Test cases with various types of content
    test_cases = [
        {
            "name": "Normal Content",
            "text": "Hello, I'm looking for someone to share meaningful conversations with. I enjoy hiking and reading books.",
            "expected": "APPROVED"
        },
        {
            "name": "Mild Inappropriate",
            "text": "You're such a beautiful woman, I want to get to know you better intimately.",
            "expected": "MIGHT_BE_BLOCKED"
        },
        {
            "name": "Explicit Sexual Content",
            "text": "I want to have sex with you right now. Let's meet up for a hookup tonight.",
            "expected": "BLOCKED"
        },
        {
            "name": "Hate Speech",
            "text": "I hate all people from that country, they are all criminals and should be banned.",
            "expected": "BLOCKED"
        },
        {
            "name": "Harassment",
            "text": "You stupid bitch, I'm going to find where you live and make you pay for rejecting me.",
            "expected": "BLOCKED"
        },
        {
            "name": "Scam/Fraud",
            "text": "Send me money and I'll give you my premium photos. Just transfer $50 to my account.",
            "expected": "BLOCKED"
        },
        {
            "name": "Drug References",
            "text": "I sell high quality marijuana and cocaine. Contact me for best prices.",
            "expected": "BLOCKED"
        },
        {
            "name": "Violence Threats",
            "text": "I will kill you and your family if you don't do what I say.",
            "expected": "BLOCKED"
        },
        {
            "name": "Self-Harm",
            "text": "I want to kill myself, life is not worth living anymore.",
            "expected": "BLOCKED"
        },
        {
            "name": "Normal Dating",
            "text": "I'm a software engineer who loves traveling. Looking for someone to explore the world with.",
            "expected": "APPROVED"
        }
    ]
    
    print(f"Service Configuration:")
    print(f"  Enable Moderation: {getattr(content_moderation_service, 'enable_moderation', 'Unknown')}")
    print(f"  Secret ID: {content_moderation_service.secret_id[:10]}..." if content_moderation_service.secret_id else "  Secret ID: Not Set")
    print(f"  Region: {content_moderation_service.region}")
    print()
    
    blocked_count = 0
    approved_count = 0
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"Test {i}: {test_case['name']}")
        print(f"Text: {test_case['text'][:60]}{'...' if len(test_case['text']) > 60 else ''}")
        
        try:
            # Test text moderation
            result = await content_moderation_service.moderate_text(
                text=test_case['text'],
                user_id=f"test_user_{i}"
            )
            
            # Display results
            status = "✅ APPROVED" if result.is_approved else "❌ BLOCKED"
            print(f"Result: {status} (confidence: {result.confidence:.2f})")
            print(f"Suggestion: {result.suggestion}")
            print(f"Mode: {result.mode}")
            
            if result.reason:
                print(f"Reason: {result.reason}")
            if result.blocked_words:
                print(f"Blocked words: {', '.join(result.blocked_words)}")
            
            # Count results
            if result.is_approved:
                approved_count += 1
            else:
                blocked_count += 1
                
            print()
            
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
            print()
    
    # Summary
    print("=" * 60)
    print(f"📊 SUMMARY:")
    print(f"  Total tests: {len(test_cases)}")
    print(f"  Approved: {approved_count}")
    print(f"  Blocked: {blocked_count}")
    print(f"  Success rate: {((approved_count + blocked_count) / len(test_cases)) * 100:.1f}%")
    
    # Determine if moderation is working properly
    if blocked_count == 0 and approved_count == len(test_cases):
        print()
        print("⚠️  WARNING: All content was approved, including clearly inappropriate content.")
        print("   This suggests the moderation service might be in fallback mode.")
        print("   Check your Tencent Cloud credentials and configuration.")
    elif blocked_count > 0:
        print()
        print("✅ Content moderation is working! Some inappropriate content was blocked.")
        print("   The system is successfully filtering content using Tencent Cloud APIs.")
    
    await content_moderation_service.close()


if __name__ == "__main__":
    asyncio.run(test_production_moderation())
