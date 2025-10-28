"""
Casual Request Optimizer
As specified in casual_request_integration_guide_en.md
"""

import json
from typing import Dict
from services.glm4_client import GLM4Client


class CasualRequestOptimizer:
    """Casual request optimizer"""
    
    def __init__(self, glm_api_key: str = None, glm_model: str = "glm-4-flash"):
        """Initialize optimizer"""
        self.glm_client = GLM4Client(
            api_key=glm_api_key,
            model=glm_model
        )
    
    def optimize_query(self, user_input: str) -> Dict:
        """Optimize casual request expression"""
        # Build optimization prompt
        system_prompt = """
        You are a specialist in optimizing casual social requests. Your task is to analyze user input, extract key information and optimize the expression to make it easier to match with others.
        
        Please extract the following information:
        1. Activity type - what activity the user wants to do (e.g., coffee, movies, hiking)
        2. Time information - when the activity is expected to occur (e.g., weekend, next week, every Thursday night)
        3. Location information - if there is any mentioned activity location
        4. Special preferences - any special requirements or preferences of the user
        
        Please return results in the following JSON format:
        {
            "optimized_query": "",     // Optimized query text, more suitable for matching
            "activity_type": "",       // Activity type
            "time_info": "",           // Time information
            "location": "",            // Location information
            "preferences": []          // List of special preferences
        }
        
        Return only JSON format results, do not add extra explanations.
        """
        
        # Build user request
        user_message = f"Please optimize this social request: \"{user_input}\""
        
        try:
            # Call LLM for optimization using GLM4Client interface
            response = self.glm_client.chat_completion(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.3,
                response_format="json_object"
            )
            
            # Parse results
            result_text = response["choices"][0]["message"]["content"]
            result = json.loads(result_text)
            return result
        except Exception as e:
            print(f"Error optimizing request: {e}")
            # Return default result
            return {
                "optimized_query": user_input,
                "activity_type": "",
                "time_info": "",
                "location": "",
                "preferences": []
            }