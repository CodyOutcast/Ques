"""
Debug specific profile text that should have been blocked
"""
import asyncio
import sys
import os

# Add the backend path to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.content_moderation import moderate_text_content

async def test_specific_text():
    """Test the specific bio text that should have been blocked"""
    
    problem_bio = "Let's have sex tonight. I do drugs and party hard. Want to hook up?"
    
    print(f"🔍 TESTING PROBLEMATIC BIO:")
    print(f"Text: {problem_bio}")
    print("=" * 60)
    
    result = await moderate_text_content(problem_bio, "debug_user")
    
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
        print(f"Detailed scores: {result.scores}")
    
    print("\n🔍 ANALYSIS:")
    print("=" * 30)
    
    # Check individual components
    components = [
        "Let's have sex tonight",
        "I do drugs", 
        "party hard",
        "Want to hook up?"
    ]
    
    for component in components:
        comp_result = await moderate_text_content(component, "debug_comp")
        status = "✅ APPROVED" if comp_result.is_approved else "❌ BLOCKED"
        print(f"'{component}' → {status} (confidence: {comp_result.confidence:.2f})")
        if comp_result.reason:
            print(f"  Reason: {comp_result.reason}")
        if comp_result.scores:
            print(f"  Scores: {comp_result.scores}")

if __name__ == "__main__":
    asyncio.run(test_specific_text())
