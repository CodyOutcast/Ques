"""
Compare different explicit texts to understand Tencent moderation behavior
"""
import asyncio
import sys
import os

# Add the backend path to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.content_moderation import moderate_text_content

async def compare_texts():
    """Compare different explicit texts"""
    
    test_texts = [
        "Let's have sex tonight. I do drugs and party hard. Want to hook up?",  # Profile 2 bio
        "Let's meet tonight for sex and do some cocaine",  # Previously blocked text
        "Want to see my naked photos? Send me yours!",      # Previously blocked text
        "Let's have sex",
        "I do cocaine", 
        "I do drugs",
        "Want to hook up",
        "Let's do cocaine tonight",
        "Adult entertainment",
        "sex tonight",
        "cocaine",
        "drugs"
    ]
    
    print("🔍 COMPARING DIFFERENT EXPLICIT TEXTS:")
    print("=" * 80)
    
    for text in test_texts:
        result = await moderate_text_content(text, "compare_user")
        
        status = "✅ APPROVED" if result.is_approved else "❌ BLOCKED"
        confidence = result.confidence
        
        print(f"\nText: '{text}'")
        print(f"  Status: {status} (confidence: {confidence:.2f}, suggestion: {result.suggestion})")
        
        if result.reason:
            print(f"  Reason: {result.reason}")
        
        if result.blocked_words:
            print(f"  Blocked words: {result.blocked_words}")
        
        # Show highest scoring categories
        if result.scores:
            high_scores = {k: v for k, v in result.scores.items() if v > 0}
            if high_scores:
                print(f"  High scores: {high_scores}")

if __name__ == "__main__":
    asyncio.run(compare_texts())
