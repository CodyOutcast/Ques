"""
Casual Request Classifier
As specified in casual_request_integration_guide_en.md
"""

import json
from typing import Dict
from services.glm4_client import GLM4Client


class CasualRequestClassifier:
    """Casual request classifier"""
    
    def __init__(self, glm_api_key: str = None, glm_model: str = "glm-4-flash"):
        """Initialize classifier"""
        self.glm_client = GLM4Client(
            api_key=glm_api_key,
            model=glm_model
        )
    
    def is_casual_request(self, user_input: str) -> Dict:
        """Determine if the input is a casual request"""
        # Build classification prompt
        system_prompt = """
        You are a specialist in analyzing casual requests. Your task is to determine whether the user input is a casual social request and, if so, to further identify its specific type.

        Casual request characteristics:
        1. Looking for partners for social activities, such as eating together, watching movies, traveling, sports, etc.
        2. Initiating invitations for interest groups or gatherings
        3. Primarily focused on social interaction and shared interests, not professional capabilities
        4. Not seeking professional services or recruiting talent
        5. May contain time and location information, time-sensitive descriptions

        Please analyze the user input and return results in the following JSON format:
        {
            "is_casual": true/false,  // Whether it's a casual request
            "confidence": 0.0-1.0,    // Confidence score
            "type": "",               // If yes, fill in type: social_activity, gathering, interest_group, or other specific type
            "reasoning": ""           // Brief explanation of the judgment reason
        }
        
        Return only JSON format results, do not add extra explanations.
        """
        
        # Build user request
        user_message = f"Please analyze whether this user input is a casual social request: \"{user_input}\""
        
        try:
            # Call LLM for classification using GLM4Client interface
            response = self.glm_client.chat_completion(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.1,
                response_format="json_object"
            )
            
            # Parse results
            result_text = response["choices"][0]["message"]["content"]
            result = json.loads(result_text)
            return result
        except Exception as e:
            print(f"Error classifying request: {e}")
            # Return default result
            return {
                "is_casual": False,
                "confidence": 0.0,
                "type": "",
                "reasoning": f"Classification process error: {str(e)}"
            }