"""
Advanced Intention Detection System using GLM-4 LLM Analysis
Based on SearchAgent algorithm from intelligent_search_original.py
Analyzes user messages to determine if they are search, casual, or inquiry intentions
"""

import re
import enum
import json
import os
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import GLM4Client from local services directory
try:
    from .glm4_client import GLM4Client, GLM4Model, ResponseFormat
except ImportError:
    try:
        from glm4_client import GLM4Client, GLM4Model, ResponseFormat
    except ImportError:
        print("Warning: GLM4Client not found, using fallback system")
        GLM4Client = None

class IntentionType(enum.Enum):
    SEARCH = "search"
    CASUAL = "casual" 
    INQUIRY = "inquiry"

@dataclass
class IntentionResult:
    intention: IntentionType
    confidence: float
    keywords_matched: List[str]
    reasoning: str
    clarification_needed: bool = False
    uncertainty_reason: str = ""
    


class IntentionDetector:
    """
    Advanced intention detection system using GLM-4 LLM analysis
    Implements the SearchAgent algorithm approach from intelligent_search_original.py
    """
    
    def __init__(self, glm_api_key: str = None):
        """Initialize the intention detector with GLM-4 client"""
        if GLM4Client:
            try:
                api_key = glm_api_key or os.getenv('ZHIPUAI_API_KEY')
                model = os.getenv('GLM4_MODEL', 'glm-4-flash')  # Use glm-4-flash as default
                
                self.glm_client = GLM4Client(
                    api_key=api_key,
                    model=model
                )
                self.has_llm = True
                print(f"✅ GLM-4 client initialized successfully with model: {model}")
            except Exception as e:
                print(f"❌ GLM-4 client initialization failed: {e}")
                self.glm_client = None
                self.has_llm = False
        else:
            self.glm_client = None
            self.has_llm = False
            print("⚠️ GLM-4 client not available, using fallback analysis")
            
        self.stats = {
            "analysis_count": 0,
            "llm_calls": 0,
            "search_detections": 0,
            "casual_detections": 0,
            "inquiry_detections": 0
        }
    
    def analyze_user_intent(
        self, 
        user_input: str, 
        referenced_user: Dict = None, 
        current_user: Dict = None
    ) -> IntentionResult:
        """
        Analyze user intent using GLM-4 LLM analysis
        Based on SearchAgent.analyze_user_intent() method from intelligent_search_original.py
        
        Args:
            user_input: User input text
            referenced_user: Referenced user information (if any)
            current_user: Current user information (if any)
            
        Returns:
            IntentionResult with detected intention and details
        """
        self.stats["analysis_count"] += 1
        
        # Build referenced user information
        referenced_info = ""
        if referenced_user:
            referenced_info = f"""
Referenced user information:
{json.dumps(referenced_user, ensure_ascii=False, indent=2)}
"""
        
        # Build current user information
        current_user_info = ""
        if current_user:
            current_user_info = f"""
Current user information:
{json.dumps(current_user, ensure_ascii=False, indent=2)}
"""
        
        # System prompt from SearchAgent (exactly as in intelligent_search_original.py)
        system_prompt = """
You are a professional user intent analysis expert. Your task is to accurately identify user intent types and provide detailed analysis.

Intent Type Definitions:

1. **Search**: User wants to find talents or users that meet specific criteria
   - Key features: Contains verbs like find, search, look for people
   - Describes conditions: Skills, experience, location, industry filtering criteria
   - Typical expressions: "Help me find a Python engineer", "Looking for product managers in Beijing"

2. **Inquiry**: User asks questions about specific referenced users or needs detailed information
   - Key features: Questions targeting specific users
   - Requires referenced user: Must have a clear target user
   - Typical expressions: "How are this person's skills?", "Is he suitable for our project?", "Can you introduce in detail?"

3. **Chat**: General conversation, consultation, or unclear communication
   - Key features: No clear search or inquiry target
   - Includes greetings, general consultation, feature understanding, etc.
   - Typical expressions: "Hello", "How to use this system?", "Any suggestions?"

Analysis Requirements:
- Carefully analyze the semantics and context of user input
- Consider whether there is referenced user information to assist judgment
- If intent is unclear, mark as needing clarification
- Provide clear reasoning process

Return JSON format:
{
    "intent": "search|inquiry|chat",
    "confidence": 0.0-1.0,
    "reasoning": "Detailed analysis reasoning process",
    "clarification_needed": boolean,
    "uncertainty_reason": "If clarification needed, explain reason"
}
"""
        
        user_prompt = f"""
User input: "{user_input}"

{referenced_info}

{current_user_info}

Please analyze the user's intent type. Pay special attention to:
- If there is a referenced user and the user is asking related questions, it's likely inquiry type
- If the user is describing search criteria, it's likely search type  
- If intent is unclear or general conversation, it's likely chat type

Please provide detailed intent analysis.
"""
        
        if self.has_llm and self.glm_client:
            try:
                self.stats["llm_calls"] += 1
                
                # Call GLM-4 API (following original implementation)
                result = self.glm_client.json_chat(
                    content=user_prompt,
                    system_prompt=system_prompt,
                    temperature=0.1,
                    max_tokens=500
                )
                
                # Validate and standardize result (from original)
                intent = result.get("intent", "chat").lower()
                if intent not in ["search", "inquiry", "chat"]:
                    intent = "chat"
                
                # Map "chat" to "casual" for our enum
                if intent == "chat":
                    intent = "casual"
                
                confidence = float(result.get("confidence", 0.5))
                confidence = max(0.0, min(1.0, confidence))  # Ensure in 0-1 range
                
                # Update statistics
                self.stats[f"{intent}_detections"] += 1
                
                return IntentionResult(
                    intention=IntentionType(intent),
                    confidence=confidence,
                    keywords_matched=[],  # GLM-4 doesn't return keywords in this format
                    reasoning=result.get("reasoning", "Unable to get analysis reasoning"),
                    clarification_needed=result.get("clarification_needed", False),
                    uncertainty_reason=result.get("uncertainty_reason", "")
                )
                
            except Exception as e:
                print(f"❌ GLM-4 Intent analysis failed: {e}")
                # Return conservative default when GLM-4 fails
                return IntentionResult(
                    intention=IntentionType.CASUAL,
                    confidence=0.2,
                    keywords_matched=[],
                    reasoning=f"GLM-4 analysis failed: {str(e)}. Defaulting to casual intent.",
                    clarification_needed=True,
                    uncertainty_reason="GLM-4 LLM analysis unavailable - please try again"
                )
        
        # When GLM-4 is not available at all
        print("⚠️ GLM-4 not available - intent analysis not possible")
        return IntentionResult(
            intention=IntentionType.CASUAL,
            confidence=0.1,
            keywords_matched=[],
            reasoning="GLM-4 LLM not available. Cannot perform intent analysis.",
            clarification_needed=True,
            uncertainty_reason="GLM-4 API not configured - please set ZHIPUAI_API_KEY"
        )
    
    def detect_intention(self, message: str) -> IntentionResult:
        """Legacy method name for backward compatibility"""
        return self.analyze_user_intent(message)
    
    def detect_language(self, text: str) -> Tuple[str, float]:
        """Detect text language (from SearchAgent)"""
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
        total_chars = len(text.strip())
        
        if total_chars == 0:
            return "zh", 0.5
        
        chinese_ratio = chinese_chars / total_chars
        
        if chinese_ratio > 0.2:
            return "zh", min(0.9, 0.5 + chinese_ratio)
        else:
            return "en", min(0.9, 0.5 + (1 - chinese_ratio))
    
    def get_statistics(self) -> Dict:
        """Get detection statistics"""
        return self.stats.copy()

def test_glm4_intent_detection():
    """Test GLM-4 LLM intent detection system"""
    detector = IntentionDetector()
    
    print("🤖 GLM-4 Intent Detection System Test")
    print("=" * 50)
    
    if not detector.has_llm:
        print("❌ GLM-4 not available - cannot run intent detection tests")
        print("Please set ZHIPUAI_API_KEY environment variable")
        return
    
    # Test core intent detection with GLM-4
    test_messages = [
        "Looking for Python developers in Beijing",
        "Hello! How are you doing today?",
        "Can you tell me about this user's background?",
        "Need hiking partners this weekend",
        "什么时候开始学习？"  # Chinese inquiry
    ]
    
    print(f"GLM-4 Status: ✅ Available (Model: {os.getenv('GLM4_MODEL', 'glm-4-flash')})")
    print()
    
    for i, message in enumerate(test_messages, 1):
        print(f"Test {i}: \"{message}\"")
        print("-" * 30)
        
        try:
            result = detector.analyze_user_intent(message)
            print(f"Intent: {result.intention.value}")
            print(f"Confidence: {result.confidence:.2f}")
            print(f"GLM-4 Reasoning: {result.reasoning}")
            
            if result.clarification_needed:
                print(f"⚠️ Clarification: {result.uncertainty_reason}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print()
    
    # Show statistics
    stats = detector.get_statistics()
    print("📊 GLM-4 Usage Statistics:")
    print(f"  Total analyses: {stats['analysis_count']}")
    print(f"  LLM API calls: {stats['llm_calls']}")
    print(f"  Search detections: {stats['search_detections']}")
    print(f"  Casual detections: {stats['casual_detections']}")
    print(f"  Inquiry detections: {stats['inquiry_detections']}")
    
    print("\n✅ GLM-4 Intent Detection Test Complete!")

if __name__ == "__main__":
    test_glm4_intent_detection()