"""
Simple test to debug DeepSeek API integration
"""
import asyncio
import sys
import os
import httpx
import json

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ Environment variables loaded")
except ImportError:
    print("❌ dotenv not available")

# Add the backend path to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_deepseek_api():
    """Test DeepSeek API directly"""
    
    api_key = os.getenv('DEEPSEEK_API_KEY')
    print(f"API Key loaded: {'Yes' if api_key else 'No'}")
    if api_key:
        print(f"API Key starts with: {api_key[:10]}...")
    
    if not api_key:
        print("❌ No DeepSeek API key found")
        return
    
    try:
        client = httpx.AsyncClient(timeout=30.0)
        
        print("🔍 Testing DeepSeek API connection...")
        
        response = await client.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "deepseek-chat",
                "messages": [
                    {
                        "role": "user",
                        "content": "Is the text 'Hello world' appropriate for a dating app? Answer with just 'yes' or 'no'."
                    }
                ],
                "temperature": 0.1,
                "max_tokens": 10
            }
        )
        
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ API call successful!")
            print(f"Response: {result['choices'][0]['message']['content']}")
        else:
            print(f"❌ API call failed: {response.text}")
            
        await client.aclose()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_deepseek_api())
