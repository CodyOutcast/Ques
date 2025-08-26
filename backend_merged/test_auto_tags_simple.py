"""
Simple test for auto tag generation using actual environment variables
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import asyncio
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_deepseek_api():
    """Test the DeepSeek API directly with real API key"""
    print("🧪 Testing DeepSeek API for Auto Tag Generation")
    print("=" * 50)
    
    # Configuration from environment
    api_url = "https://api.deepseek.com/v1/chat/completions"
    api_key = os.getenv("DEEPSEEK_API_KEY")
    
    if not api_key:
        print("❌ DEEPSEEK_API_KEY not found in environment variables")
        return False
        
    print(f"🔑 Using API key: {api_key[:8]}...{api_key[-4:] if len(api_key) > 12 else api_key}")
    
    # Test bio
    test_bio = "I'm a software engineer with 5 years of experience in Python and React. I love building innovative web applications and am passionate about AI/ML. Currently working on a startup that uses machine learning to optimize supply chains. In my free time, I enjoy hiking, photography, and playing guitar."
    
    # Available tags (from our analysis)
    available_tags = [
        "Web Development", "Mobile Development", "Data Science", "AI/ML", 
        "Blockchain", "Gaming", "Design", "Marketing", "Business", 
        "Entrepreneurship", "Music", "Art", "Photography", "Sports", "Travel"
    ]
    
    # Create the prompt
    prompt = f"""
Based on the following user bio, extract relevant tags from this list: {', '.join(available_tags)}

User Bio: "{test_bio}"

Instructions:
1. Only return tags from the provided list
2. Return 3-6 most relevant tags
3. Return as a JSON array of strings
4. Focus on skills, interests, and professional areas mentioned in the bio

Response format: ["tag1", "tag2", "tag3"]
"""

    # Make the API request
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    data = {
        "model": "deepseek-chat",
        "messages": [
            {
                "role": "user", 
                "content": prompt
            }
        ],
        "temperature": 0.3,
        "max_tokens": 200
    }
    
    try:
        print(f"📝 Testing with bio: {test_bio[:100]}...")
        print(f"🎯 Available tags: {available_tags}")
        print("\n🔄 Making API request...")
        
        response = requests.post(api_url, headers=headers, json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            content = result['choices'][0]['message']['content'].strip()
            print(f"✅ API Response: {content}")
            
            # Try to parse the JSON
            try:
                tags = json.loads(content)
                print(f"🏷️  Extracted tags: {tags}")
                print(f"📊 Number of tags: {len(tags)}")
                
                # Validate tags
                valid_tags = [tag for tag in tags if tag in available_tags]
                invalid_tags = [tag for tag in tags if tag not in available_tags]
                
                print(f"✅ Valid tags: {valid_tags}")
                if invalid_tags:
                    print(f"❌ Invalid tags: {invalid_tags}")
                
                return valid_tags
                
            except json.JSONDecodeError as e:
                print(f"❌ Failed to parse JSON: {e}")
                print(f"Raw content: {content}")
                return []
        else:
            print(f"❌ API request failed: {response.status_code}")
            print(f"Error: {response.text}")
            return []
            
    except Exception as e:
        print(f"❌ Test error: {e}")
        return []

def test_multiple_bios():
    """Test with multiple different bios"""
    print("\n\n🔬 Testing Multiple User Bios")
    print("=" * 50)
    
    test_bios = [
        "Software engineer with 5 years of experience in Python and React. Passionate about AI/ML and building innovative web applications.",
        "Digital marketing specialist focusing on social media campaigns and brand strategy. Love photography and travel in my spare time.",
        "Blockchain developer working on DeFi protocols. Also interested in gaming and competitive esports.",
        "UX/UI designer with a background in psychology. Enjoy creating user-centered designs and playing music.",
        "Data scientist specializing in machine learning for healthcare. Passionate about sports analytics and hiking."
    ]
    
    results = []
    for i, bio in enumerate(test_bios, 1):
        print(f"\n--- Test Bio {i} ---")
        tags = test_deepseek_api()
        results.append({
            'bio': bio,
            'tags': tags
        })
        
        # Add delay to avoid rate limiting
        import time
        time.sleep(1)
    
    print("\n\n📋 Summary of Results:")
    print("=" * 50)
    for i, result in enumerate(results, 1):
        print(f"{i}. Bio: {result['bio'][:50]}...")
        print(f"   Tags: {result['tags']}")
        print()

if __name__ == "__main__":
    # Test single bio first
    tags = test_deepseek_api()
    
    if tags:
        print(f"\n🎉 Successfully extracted {len(tags)} tags!")
        
        # If successful, test multiple bios
        user_input = input("\nTest with multiple bios? (y/n): ")
        if user_input.lower() == 'y':
            test_multiple_bios()
    else:
        print("\n❌ Failed to extract tags. Check API configuration.")
