"""
Enhanced Intention Detection Integration
Integrates intention detection with the casual requests system
"""

from typing import Dict, Optional
from services.intention_detection import IntentionDetector, IntentionType, IntentionResult

class CasualRequestIntentionHandler:
    """
    Enhanced handler that processes casual requests based on detected intention
    """
    
    def __init__(self):
        self.detector = IntentionDetector()
    
    def process_message(self, message: str, user_id: str) -> Dict:
        """
        Process a chat message and return appropriate response based on intention
        """
        # Detect intention
        result = self.detector.detect_intention(message)
        
        # Process based on intention type
        if result.intention == IntentionType.SEARCH:
            return self._handle_search_intention(message, user_id, result)
        elif result.intention == IntentionType.INQUIRY:
            return self._handle_inquiry_intention(message, user_id, result)
        else:  # CASUAL
            return self._handle_casual_intention(message, user_id, result)
    
    def _handle_search_intention(self, message: str, user_id: str, result: IntentionResult) -> Dict:
        """Handle search-type messages - likely casual requests"""
        return {
            'intention': 'search',
            'action': 'create_casual_request',
            'confidence': result.confidence,
            'suggestion': 'This looks like you want to find someone for an activity. Should I create a casual request?',
            'auto_create': result.confidence > 0.7,  # Auto-create if high confidence
            'optimized_query': self._optimize_for_search(message, result.keywords_matched),
            'extracted_data': self._extract_search_data(message),
            'reasoning': result.reasoning
        }
    
    def _handle_inquiry_intention(self, message: str, user_id: str, result: IntentionResult) -> Dict:
        """Handle inquiry-type messages - questions about platform/activities"""
        return {
            'intention': 'inquiry',
            'action': 'provide_information',
            'confidence': result.confidence,
            'suggestion': 'I can help answer your question or connect you with relevant people.',
            'response_type': 'informational',
            'query_type': self._classify_inquiry_type(message, result.keywords_matched),
            'related_searches': self._suggest_related_searches(message),
            'reasoning': result.reasoning
        }
    
    def _handle_casual_intention(self, message: str, user_id: str, result: IntentionResult) -> Dict:
        """Handle casual conversation - social interactions"""
        return {
            'intention': 'casual',
            'action': 'social_response',
            'confidence': result.confidence,
            'suggestion': 'Thanks for chatting! Let me know if you want to find people for activities.',
            'response_type': 'conversational',
            'mood': self._detect_mood(message, result.keywords_matched),
            'follow_up': self._suggest_follow_up(message),
            'reasoning': result.reasoning
        }
    
    def _optimize_for_search(self, message: str, keywords: list) -> str:
        """Optimize the message for better search matching"""
        # Basic optimization - in production, use NLP/AI
        optimized = message
        
        # Add location context if missing
        if not any(loc in message.lower() for loc in ['shenzhen', 'beijing', 'shanghai', 'guangzhou']):
            optimized += " (location flexible)"
        
        # Emphasize activity type
        if any(kw in keywords for kw in ['hiking', 'study', 'coffee', 'gym']):
            activity_keywords = [kw for kw in keywords if kw in ['hiking', 'study', 'coffee', 'gym']]
            optimized = f"[{activity_keywords[0].title()}] {optimized}"
        
        return optimized
    
    def _extract_search_data(self, message: str) -> Dict:
        """Extract structured data from search messages"""
        data = {
            'activity_type': None,
            'location': None,
            'timing': None,
            'preferences': {}
        }
        
        message_lower = message.lower()
        
        # Extract activity type
        activities = {
            'hiking': ['hiking', 'hike', 'mountain', 'trail'],
            'study': ['study', 'learning', 'homework', 'research'],
            'coffee': ['coffee', 'cafe', 'drink', 'chat'],
            'sports': ['gym', 'workout', 'fitness', 'exercise', 'sports'],
            'language': ['language', 'english', 'chinese', 'mandarin', 'conversation'],
            'social': ['meetup', 'hangout', 'friends', 'social']
        }
        
        for activity, keywords in activities.items():
            if any(kw in message_lower for kw in keywords):
                data['activity_type'] = activity
                break
        
        # Extract location
        locations = ['shenzhen', 'beijing', 'shanghai', 'guangzhou', 'downtown', 'nanshan']
        for location in locations:
            if location in message_lower:
                data['location'] = location.title()
                break
        
        # Extract timing
        timings = ['weekend', 'weekday', 'morning', 'evening', 'afternoon', 'tonight']
        for timing in timings:
            if timing in message_lower:
                data['timing'] = timing
                break
        
        return data
    
    def _classify_inquiry_type(self, message: str, keywords: list) -> str:
        """Classify the type of inquiry"""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ['where', 'location', 'place']):
            return 'location_inquiry'
        elif any(word in message_lower for word in ['when', 'time', 'schedule']):
            return 'timing_inquiry'
        elif any(word in message_lower for word in ['how', 'way', 'method']):
            return 'process_inquiry'
        elif any(word in message_lower for word in ['recommend', 'suggest', 'best']):
            return 'recommendation_inquiry'
        else:
            return 'general_inquiry'
    
    def _suggest_related_searches(self, message: str) -> list:
        """Suggest related casual request searches based on inquiry"""
        suggestions = []
        message_lower = message.lower()
        
        if 'coffee' in message_lower:
            suggestions.extend(['Coffee meetup partners', 'Cafe study buddies'])
        if 'gym' in message_lower or 'fitness' in message_lower:
            suggestions.extend(['Workout partners', 'Fitness accountability buddy'])
        if 'language' in message_lower or 'english' in message_lower:
            suggestions.extend(['Language exchange partners', 'Conversation practice'])
        if 'study' in message_lower or 'learning' in message_lower:
            suggestions.extend(['Study group members', 'Learning partners'])
        
        return suggestions[:3]  # Return top 3 suggestions
    
    def _detect_mood(self, message: str, keywords: list) -> str:
        """Detect the mood/emotion of casual messages"""
        positive_indicators = ['😊', '😄', '🎉', '✨', 'awesome', 'great', 'amazing', 'thanks', 'love']
        negative_indicators = ['😞', '😔', 'sad', 'tired', 'stressed', 'difficult']
        excited_indicators = ['!', 'omg', 'wow', '🔥', '💪', 'excited']
        
        message_lower = message.lower()
        
        if any(ind in message_lower or ind in keywords for ind in excited_indicators):
            return 'excited'
        elif any(ind in message_lower or ind in keywords for ind in positive_indicators):
            return 'positive'
        elif any(ind in message_lower or ind in keywords for ind in negative_indicators):
            return 'negative'
        else:
            return 'neutral'
    
    def _suggest_follow_up(self, message: str) -> str:
        """Suggest appropriate follow-up for casual messages"""
        mood = self._detect_mood(message, [])
        
        follow_ups = {
            'excited': "That's awesome! Want to share this excitement with others in a casual request?",
            'positive': "Glad to hear! Looking to connect with others for any activities?",
            'negative': "Hope things get better! Sometimes connecting with others helps - want to find some company?",
            'neutral': "Thanks for sharing! Let me know if you want to find people for any activities."
        }
        
        return follow_ups.get(mood, follow_ups['neutral'])

def test_integration():
    """Test the integration with various scenarios"""
    handler = CasualRequestIntentionHandler()
    
    print("🔍 TESTING CASUAL REQUEST INTENTION INTEGRATION")
    print("=" * 60)
    
    test_scenarios = [
        {
            'message': 'Looking for hiking partners this weekend in Shenzhen',
            'user_id': 'user_123',
            'expected_action': 'create_casual_request'
        },
        {
            'message': 'What are the best coffee shops for studying?',
            'user_id': 'user_456', 
            'expected_action': 'provide_information'
        },
        {
            'message': 'Hey! Just finished an amazing workout! 💪',
            'user_id': 'user_789',
            'expected_action': 'social_response'
        },
        {
            'message': 'Need someone to practice English with',
            'user_id': 'user_101',
            'expected_action': 'create_casual_request'
        },
        {
            'message': 'How do I join study groups here?',
            'user_id': 'user_202',
            'expected_action': 'provide_information'
        }
    ]
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\\n{i}. Testing: \"{scenario['message']}\"")
        result = handler.process_message(scenario['message'], scenario['user_id'])
        
        print(f"   Intention: {result['intention'].upper()}")
        print(f"   Action: {result['action']}")
        print(f"   Confidence: {result['confidence']:.2f}")
        print(f"   Suggestion: {result['suggestion']}")
        
        if 'extracted_data' in result:
            print(f"   Extracted Data: {result['extracted_data']}")
        if 'query_type' in result:
            print(f"   Query Type: {result['query_type']}")
        if 'mood' in result:
            print(f"   Mood: {result['mood']}")
        
        expected_match = result['action'] == scenario['expected_action']
        status = "✅ CORRECT" if expected_match else "❌ MISMATCH"
        print(f"   Status: {status}")
    
    print(f"\\n🎉 Integration testing complete!")

if __name__ == "__main__":
    test_integration()