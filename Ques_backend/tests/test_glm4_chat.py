#!/usr/bin/env python3
"""
Test GLM-4 Chat System
"""

from services.intention_detection import IntentionDetector

def test_glm4_chat():
    print('🚀 Testing GLM-4 Chat System')
    print('=' * 40)
    
    detector = IntentionDetector()
    print(f'GLM-4 Status: {"✅ Available" if detector.has_llm else "❌ Fallback"}')
    
    # Test messages for different intents
    test_cases = [
        "Looking for Python developers in Beijing",
        "Hello! How are you doing today?",
        "What time does the meeting start?",
        "Need hiking partners this weekend",
        "Can you tell me about this user's skills?"
    ]
    
    print('\nTesting Intent Detection:')
    print('-' * 30)
    
    for message in test_cases:
        print(f'\nMessage: "{message}"')
        result = detector.analyze_user_intent(message)
        print(f'  Intent: {result.intention.value}')
        print(f'  Confidence: {result.confidence:.2f}')
        print(f'  Reasoning: {result.reasoning}')
        if result.clarification_needed:
            print(f'  ⚠️ Clarification: {result.uncertainty_reason}')
    
    # Show statistics
    stats = detector.get_statistics()
    print(f'\nStatistics:')
    print(f'  Total analyses: {stats["analysis_count"]}')
    print(f'  LLM calls: {stats["llm_calls"]}')
    print(f'  Search detections: {stats["search_detections"]}')
    print(f'  Casual detections: {stats["casual_detections"]}')
    print(f'  Inquiry detections: {stats["inquiry_detections"]}')
    
    print('\n✅ GLM-4 Chat System Test Complete!')

if __name__ == "__main__":
    test_glm4_chat()