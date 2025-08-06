"""
Test examples of content that would be BLOCKED by Tencent Cloud CMS/TMS
This demonstrates the content moderation system with realistic examples
"""
import asyncio
import sys
import os

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.content_moderation import content_moderation_service, ModerationResult


async def test_blocked_content_examples():
    """
    Test content that would be blocked by Tencent Cloud moderation
    NOTE: These are example patterns - actual blocking depends on Tencent's AI models
    """
    
    print("🚫 TESTING CONTENT THAT WOULD BE BLOCKED")
    print("=" * 60)
    print("⚠️  NOTE: This demonstrates fallback mode since credentials aren't configured.")
    print("   With real Tencent Cloud credentials, these would likely be REJECTED.\n")
    
    # Examples of text content that would typically be blocked
    blocked_text_examples = [
        {
            "content": "你是个白痴，我恨你",  # Chinese hate speech
            "category": "Hate Speech (Chinese)",
            "reason": "Contains insulting language and hate speech"
        },
        {
            "content": "Let's meet at my place tonight for some fun 😉🔥💋",
            "category": "Sexual Content",
            "reason": "Suggestive sexual content with provocative emojis"
        },
        {
            "content": "I'm going to hurt you if you don't give me your number",
            "category": "Threats/Violence",
            "reason": "Contains threatening language and intimidation"
        },
        {
            "content": "Buy cheap drugs here! Contact WhatsApp +1234567890",
            "category": "Illegal Activities/Spam",
            "reason": "Promoting illegal drug sales with contact information"
        },
        {
            "content": "Send me nude photos or I'll share your personal info",
            "category": "Sexual Harassment/Blackmail",
            "reason": "Sexual coercion and threats of doxxing"
        },
        {
            "content": "Click this link to get rich quick! bit.ly/scam123 💰💰💰",
            "category": "Scam/Fraud",
            "reason": "Fraudulent get-rich-quick scheme with suspicious links"
        },
        {
            "content": "My real name is John Smith, I live at 123 Main St, call me at 555-0123",
            "category": "Personal Information",
            "reason": "Contains full name, address, and phone number (privacy risk)"
        },
        {
            "content": "I want to kill all people from [country name]",
            "category": "Hate Speech/Violence",
            "reason": "Violent hate speech targeting ethnic groups"
        },
        {
            "content": "卖肾联系微信：xxx-xxx-xxx",  # Chinese organ selling
            "category": "Illegal Activities (Chinese)",
            "reason": "Illegal organ trafficking advertisement"
        },
        {
            "content": "🍆🍑💦👅 looking for some action tonight",
            "category": "Sexual Content (Emoji)",
            "reason": "Sexual emoji combination with explicit intent"
        }
    ]
    
    print("📝 Testing Text Content That Would Be Blocked:")
    print("-" * 50)
    
    for i, example in enumerate(blocked_text_examples, 1):
        print(f"\n{i}. {example['category']}")
        print(f"   Content: '{example['content']}'")
        print(f"   Why blocked: {example['reason']}")
        
        try:
            result = await content_moderation_service.moderate_text(
                content=example['content'],
                user_id=999,  # Test user ID
                data_id=f"blocked_test_{i}"
            )
            
            if result.result == ModerationResult.REJECTED:
                print(f"   🚫 RESULT: BLOCKED ✅")
                print(f"   Violations: {result.violations}")
            elif result.result == ModerationResult.APPROVED:
                print(f"   ✅ RESULT: APPROVED (fallback mode)")
                print(f"   Note: With real credentials, this would likely be BLOCKED")
            else:
                print(f"   ⏳ RESULT: {result.result.upper()}")
            
            print(f"   Confidence: {result.confidence}")
            print(f"   Suggestion: {result.suggestion}")
            
        except Exception as e:
            print(f"   ❌ ERROR: {str(e)}")
    
    print("\n" + "=" * 60)
    print("🖼️  Examples of Images That Would Be Blocked:")
    print("-" * 50)
    
    # Examples of image URLs that would typically be blocked
    blocked_image_examples = [
        {
            "url": "https://example.com/explicit-content.jpg",
            "category": "Adult Content",
            "reason": "Contains explicit sexual imagery"
        },
        {
            "url": "https://example.com/violence-graphic.png",
            "category": "Violence/Gore",
            "reason": "Contains graphic violent content"
        },
        {
            "url": "https://example.com/hate-symbol.jpg",
            "category": "Hate Symbols",
            "reason": "Contains hate speech symbols or imagery"
        },
        {
            "url": "https://example.com/drug-paraphernalia.png",
            "category": "Illegal Drugs",
            "reason": "Shows drug use or paraphernalia"
        },
        {
            "url": "https://example.com/personal-documents.jpg",
            "category": "Privacy Violation",
            "reason": "Contains personal documents or ID information"
        }
    ]
    
    for i, example in enumerate(blocked_image_examples, 1):
        print(f"\n{i}. {example['category']}")
        print(f"   Image URL: {example['url']}")
        print(f"   Why blocked: {example['reason']}")
        
        try:
            result = await content_moderation_service.moderate_image(
                image_url=example['url'],
                user_id=999,
                data_id=f"blocked_image_test_{i}"
            )
            
            if result.result == ModerationResult.REJECTED:
                print(f"   🚫 RESULT: BLOCKED ✅")
                print(f"   Violations: {result.violations}")
            elif result.result == ModerationResult.APPROVED:
                print(f"   ✅ RESULT: APPROVED (fallback mode)")
                print(f"   Note: With real credentials, this would likely be BLOCKED")
            else:
                print(f"   ⏳ RESULT: {result.result.upper()}")
                
            print(f"   Confidence: {result.confidence}")
            print(f"   Suggestion: {result.suggestion}")
            
        except Exception as e:
            print(f"   ❌ ERROR: {str(e)}")
    
    print("\n" + "=" * 60)
    print("👤 Testing Profile Content That Would Be Blocked:")
    print("-" * 50)
    
    # Example of a user profile that would have multiple violations
    problematic_profile = {
        "user_id": 999,
        "username": "SexyHotBabe69",  # Inappropriate username
        "display_name": "💋 Call me for fun 💋",  # Sexual display name
        "bio": "Looking for sugar daddy. Send money first! WhatsApp: +1234567890",  # Solicitation
        "location": "红灯区",  # Red light district in Chinese
        "occupation": "Adult entertainer 🔞",  # Adult content
        "education": "School of hard knocks, if you know what I mean 😉",  # Sexual innuendo
        "interests": "Making easy money, scamming people, selling fake products",  # Fraud
        "avatar_url": "https://example.com/inappropriate-avatar.jpg",
        "cover_image_url": "https://example.com/explicit-cover.png"
    }
    
    print("Testing problematic user profile:")
    print(f"Username: {problematic_profile['username']}")
    print(f"Display Name: {problematic_profile['display_name']}")
    print(f"Bio: {problematic_profile['bio']}")
    print("")
    
    try:
        profile_results = await content_moderation_service.moderate_user_profile(problematic_profile)
        
        blocked_fields = []
        approved_fields = []
        
        for field_name, result in profile_results.items():
            if result.result == ModerationResult.REJECTED:
                blocked_fields.append(field_name)
                print(f"   🚫 {field_name}: BLOCKED")
                print(f"      Violations: {result.violations}")
            elif result.result == ModerationResult.APPROVED:
                approved_fields.append(field_name)
                print(f"   ✅ {field_name}: APPROVED (fallback mode)")
            else:
                print(f"   ⏳ {field_name}: {result.result.upper()}")
        
        print(f"\nProfile Summary:")
        print(f"   Fields that would be blocked: {len(blocked_fields)}")
        print(f"   Fields approved: {len(approved_fields)}")
        print(f"   Note: With real credentials, most of these would be BLOCKED")
        
    except Exception as e:
        print(f"   ❌ ERROR: {str(e)}")
    
    print("\n" + "=" * 60)
    print("📱 Testing Chat Messages That Would Be Blocked:")
    print("-" * 50)
    
    problematic_messages = [
        "Hey sexy, want to meet up tonight? 😘💋",
        "I'll give you $500 for your phone number",
        "你长得真丑，没人会喜欢你的",  # Chinese insult
        "Check out my OnlyFans: onlyfans.com/user123",
        "I know where you live, be careful...",
        "Send me your bank details for a 'loan'"
    ]
    
    for i, message in enumerate(problematic_messages, 1):
        print(f"\n{i}. Message: '{message}'")
        
        try:
            result = await content_moderation_service.moderate_message(
                message_content=message,
                sender_id=999,
                chat_id=123
            )
            
            if result.result == ModerationResult.REJECTED:
                print(f"   🚫 RESULT: BLOCKED ✅")
                print(f"   Violations: {result.violations}")
            elif result.result == ModerationResult.APPROVED:
                print(f"   ✅ RESULT: APPROVED (fallback mode)")
                print(f"   Note: With real credentials, this would likely be BLOCKED")
            else:
                print(f"   ⏳ RESULT: {result.result.upper()}")
                
        except Exception as e:
            print(f"   ❌ ERROR: {str(e)}")
    
    print("\n" + "=" * 60)
    print("🔧 How to Enable Real Content Moderation:")
    print("-" * 50)
    print("1. Get Tencent Cloud account and create CMS/TMS services")
    print("2. Add credentials to .env file:")
    print("   TENCENT_SECRET_ID=your_actual_secret_id")
    print("   TENCENT_SECRET_KEY=your_actual_secret_key")
    print("   ENABLE_CONTENT_MODERATION=true")
    print("3. Restart the application")
    print("4. The examples above would then be properly blocked!")
    print("")
    print("📊 Current Status: Running in fallback mode (approves all content)")
    print("🔒 Production Status: Would block inappropriate content automatically")


if __name__ == "__main__":
    print("🛡️  TENCENT CLOUD CONTENT MODERATION - BLOCKED CONTENT EXAMPLES")
    print("=" * 70)
    print("This test demonstrates content that would be blocked in production")
    print("=" * 70)
    
    # Run the async test
    asyncio.run(test_blocked_content_examples())
