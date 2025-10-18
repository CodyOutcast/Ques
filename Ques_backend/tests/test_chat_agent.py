#!/usr/bin/env python3
"""
Direct test of the chat system without FastAPI dependencies
"""

from services.intention_detection import IntentionDetector
import sys
import os
sys.path.append(os.path.dirname(__file__))

# Import ChatAgent directly from the file to avoid router init issues
import importlib.util
spec = importlib.util.spec_from_file_location("chat_agent", "./routers/chat_agent.py")
chat_agent_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(chat_agent_module)
ChatAgent = chat_agent_module.ChatAgent

import asyncio
import json

async def test_chat_agent():
    """Test the complete chat agent system"""
    print('🤖 Testing Complete Chat Agent System')
    print('=' * 50)
    
    # Initialize chat agent
    chat_agent = ChatAgent()
    
    # Mock user data
    current_user = {
        "id": 1,
        "name": "Test User",
        "email": "test@example.com"
    }
    
    # Test different types of messages
    test_scenarios = [
        {
            "message": "Looking for Python developers in Beijing",
            "description": "Search request"
        },
        {
            "message": "Hello! How are you?",
            "description": "Casual greeting"
        },
        {
            "message": "What time does the study session start?",
            "description": "Inquiry about information"
        },
        {
            "message": "Need hiking partners this weekend",
            "description": "Activity request"
        }
    ]
    
    print(f'Chat Agent GLM-4 Status: {"✅ Available" if chat_agent.intention_detector.has_llm else "❌ Fallback"}')
    print()
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f'Test {i}: {scenario["description"]}')
        print(f'Message: "{scenario["message"]}"')
        print('-' * 30)
        
        try:
            # Process the message
            response = await chat_agent.process_message(
                message=scenario["message"],
                current_user=current_user
            )
            
            print(f'Response Type: {response.response_type}')
            print(f'Intent Detected: {response.intent}')
            print(f'Confidence: {response.confidence:.2f}')
            print(f'Content: {response.content}')
            print(f'Actions Available: {len(response.actions or [])}')
            
            if response.actions:
                for action in response.actions:
                    print(f'  - {action.get("label", "N/A")}')
            
        except Exception as e:
            print(f'❌ Error processing message: {e}')
        
        print()
    
    # Show overall statistics
    stats = chat_agent.get_stats()
    print('📊 Chat Agent Statistics:')
    print(f'  Total messages: {stats["total_messages"]}')
    print(f'  Search requests: {stats["search_requests"]}')
    print(f'  Casual requests: {stats["casual_requests"]}')
    print(f'  Inquiry requests: {stats["inquiry_requests"]}')
    
    intention_stats = stats.get("intention_detector_stats", {})
    print(f'  LLM calls made: {intention_stats.get("llm_calls", 0)}')
    
    print('\n✅ Complete Chat Agent Test Finished!')

if __name__ == "__main__":
    asyncio.run(test_chat_agent())