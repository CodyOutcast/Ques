"""
Test if the adapter correctly integrates the new UniFuncs API with the existing interface
"""

import asyncio
import os
import sys
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import original function and adapter function
from services.project_idea_agent import generate_project_ideas as original_generate
from services.project_idea_agent_adapter import generate_project_ideas as adapted_generate

def test_adapter_functionality():
    """Test the equivalence of adapter functionality to the original function"""
    query = "Develop an AI-based health diet recommendation app"
    user_id = 1  # Test user ID
    
    print(f"\n===== Testing output format of original API vs adapter API =====")
    
    # Use adapter call
    try:
        print(f"\n----- Using adapter call -----")
        adapted_result = adapted_generate(query, user_id)
        
        print(f"Found {adapted_result['total_sources_found']} relevant sources")
        print(f"Generated {adapted_result['total_ideas_extracted']} project ideas")
        print(f"Processing time: {adapted_result['processing_time_seconds']} seconds")
        
        for i, idea in enumerate(adapted_result['project_ideas']):
            print(f"\n----- Idea {i+1}: {idea['project_idea_title']} -----")
            print(f"Description: {idea['description']}")
            print(f"Key features: {', '.join(idea['key_features'][:3])}...")
            print(f"Difficulty: {idea['difficulty_level']}")
            print(f"Timeline: {idea['estimated_timeline']}")
            
        # Save to JSON file for detailed comparison
        with open("adapted_result.json", "w", encoding="utf-8") as f:
            json.dump(adapted_result, f, ensure_ascii=False, indent=2)
            print(f"\nResults saved to adapted_result.json")
    
    except Exception as e:
        print(f"Adapter call failed: {str(e)}")
    
    # Original call commented out to avoid duplicate quota consumption
    # try:
    #     print(f"\n----- Using original implementation call -----")
    #     original_result = original_generate(query, user_id)
    #     
    #     print(f"Found {original_result['total_sources_found']} relevant sources")
    #     print(f"Generated {original_result['total_ideas_extracted']} project ideas")
    #     print(f"Processing time: {original_result['processing_time_seconds']} seconds")
    #     
    #     for i, idea in enumerate(original_result['project_ideas']):
    #         print(f"\n----- Idea {i+1}: {idea['project_idea_title']} -----")
    #         print(f"Description: {idea['description']}")
    #         print(f"Key features: {', '.join(idea['key_features'][:3])}...")
    #         print(f"Difficulty: {idea['difficulty_level']}")
    #         print(f"Timeline: {idea['estimated_timeline']}")
    #         
    #     # Save to JSON file for detailed comparison
    #     with open("original_result.json", "w", encoding="utf-8") as f:
    #         json.dump(original_result, f, ensure_ascii=False, indent=2)
    #         print(f"\nResults saved to original_result.json")
    # except Exception as e:
    #     print(f"Original implementation call failed: {str(e)}")

if __name__ == "__main__":
    test_adapter_functionality()
