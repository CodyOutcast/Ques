"""
Test script for Basic Operations API endpoints
Tests: User creation, Whispers, Swiping, Top Profiles
"""

import requests
import json
from typing import Dict, Optional

# Configuration
BASE_URL = "http://localhost:8000/api/v1/basic"
AUTH_URL = "http://localhost:8000/api/v1/auth"

# Test user data
TEST_USER = {
    "email": f"test_user_{int(time.time())}@example.com",
    "password": "TestPass123",
    "name": "Test User",
    "role": "student",
    "location": "Shenzhen",
    "bio": "Test account for API testing",
    "skills": ["Python", "JavaScript", "React"],
    "interests": ["AI", "web development", "testing"]
}

def print_section(title: str):
    """Print a formatted section header"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80)


def print_response(response: requests.Response, show_full: bool = False):
    """Print formatted response"""
    print(f"Status: {response.status_code}")
    
    try:
        data = response.json()
        if show_full:
            print(json.dumps(data, indent=2, ensure_ascii=False))
        else:
            # Print summary
            if isinstance(data, dict):
                for key, value in data.items():
                    if isinstance(value, (str, int, float, bool)) or value is None:
                        print(f"  {key}: {value}")
                    elif isinstance(value, list):
                        print(f"  {key}: [{len(value)} items]")
                    else:
                        print(f"  {key}: {type(value).__name__}")
    except:
        print(f"Response: {response.text[:200]}")


def test_health_check():
    """Test health endpoint"""
    print_section("🔍 Testing Health Check")
    
    response = requests.get(f"{BASE_URL}/health")
    print_response(response, show_full=True)
    return response.json()


def test_create_user(user_data: Dict) -> Optional[Dict]:
    """Test user creation"""
    print_section("👤 Testing User Creation")
    print(f"Creating user: {user_data['email']}")
    
    response = requests.post(
        f"{BASE_URL}/users",
        json=user_data
    )
    
    print_response(response)
    
    if response.status_code == 201:
        data = response.json()
        print(f"✅ User created with ID: {data['user_id']}")
        return data
    else:
        print(f"❌ Failed to create user")
        return None


def test_get_top_profiles(token: str, limit: int = 10):
    """Test getting top profiles"""
    print_section(f"🔝 Testing Top Profiles (limit={limit})")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        f"{BASE_URL}/top-profiles?limit={limit}&exclude_seen=true",
        headers=headers
    )
    
    print_response(response)
    
    if response.status_code == 200:
        data = response.json()
        profiles = data.get('profiles', [])
        print(f"\n✅ Retrieved {len(profiles)} profiles:")
        
        for i, profile in enumerate(profiles[:3], 1):
            print(f"\n  Profile {i}:")
            print(f"    User ID: {profile['user_id']}")
            print(f"    Name: {profile['name']}")
            print(f"    Role: {profile.get('role', 'N/A')}")
            print(f"    Location: {profile.get('location', 'N/A')}")
            print(f"    Skills: {', '.join(profile.get('skills', [])[:3])}")
        
        if len(profiles) > 3:
            print(f"\n  ... and {len(profiles) - 3} more profiles")
        
        return profiles
    else:
        print(f"❌ Failed to get profiles")
        return []


def test_swipe(token: str, target_user_id: int, direction: str = "like"):
    """Test swiping on a user"""
    print_section(f"👍 Testing Swipe ({direction}) on User {target_user_id}")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    response = requests.post(
        f"{BASE_URL}/swipe",
        headers=headers,
        json={
            "target_user_id": target_user_id,
            "direction": direction
        }
    )
    
    print_response(response)
    
    if response.status_code == 200:
        data = response.json()
        if data.get('is_match'):
            print(f"🎉 IT'S A MATCH!")
        else:
            print(f"✅ Swipe recorded")
        return data
    else:
        print(f"❌ Failed to swipe")
        return None


def test_send_whisper(token: str, recipient_id: int, message: str):
    """Test sending a whisper"""
    print_section(f"💬 Testing Send Whisper to User {recipient_id}")
    print(f"Message: {message}")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    response = requests.post(
        f"{BASE_URL}/whispers",
        headers=headers,
        json={
            "recipient_id": recipient_id,
            "greeting_message": message,
            "from_template": False
        }
    )
    
    print_response(response)
    
    if response.status_code == 201:
        data = response.json()
        print(f"✅ Whisper sent with ID: {data['id']}")
        return data
    else:
        print(f"❌ Failed to send whisper")
        return None


def test_get_whispers(token: str, type: str = "all"):
    """Test getting whispers"""
    print_section(f"📬 Testing Get Whispers (type={type})")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        f"{BASE_URL}/my-whispers?type={type}&limit=10",
        headers=headers
    )
    
    print_response(response)
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n✅ Whispers Summary:")
        print(f"  Total Sent: {data['total_sent']}")
        print(f"  Total Received: {data['total_received']}")
        print(f"  Unread: {data['unread_count']}")
        
        if data['sent']:
            print(f"\n  Recent Sent:")
            for whisper in data['sent'][:3]:
                print(f"    → To {whisper.get('recipient_name', 'Unknown')}: {whisper['greeting_message'][:50]}...")
        
        if data['received']:
            print(f"\n  Recent Received:")
            for whisper in data['received'][:3]:
                print(f"    ← From {whisper.get('sender_name', 'Unknown')}: {whisper['greeting_message'][:50]}...")
        
        return data
    else:
        print(f"❌ Failed to get whispers")
        return None


def test_mark_whisper_read(token: str, whisper_id: int):
    """Test marking a whisper as read"""
    print_section(f"✅ Testing Mark Whisper {whisper_id} as Read")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.patch(
        f"{BASE_URL}/whispers/{whisper_id}/read",
        headers=headers
    )
    
    print_response(response)
    
    if response.status_code == 200:
        print(f"✅ Whisper marked as read")
        return True
    else:
        print(f"❌ Failed to mark whisper as read")
        return False


def main():
    """Run all tests"""
    import time
    
    print("\n" + "🚀 " + "="*75)
    print("  Basic Operations API Test Suite")
    print("="*80 + "\n")
    
    # 1. Health check
    health = test_health_check()
    if not health or health.get('status') != 'healthy':
        print("\n❌ Service is not healthy. Please check the server.")
        return
    
    print("\n✅ Service is healthy!")
    
    # 2. Create a new user
    user_data = TEST_USER.copy()
    user_data['email'] = f"test_user_{int(time.time())}@example.com"
    
    created_user = test_create_user(user_data)
    
    if not created_user:
        print("\n❌ Failed to create user. Cannot continue tests.")
        return
    
    access_token = created_user['access_token']
    user_id = created_user['user_id']
    
    # Wait a moment for user to be fully created
    time.sleep(1)
    
    # 3. Get top profiles
    profiles = test_get_top_profiles(access_token, limit=10)
    
    if not profiles:
        print("\n⚠️  No profiles available for testing swipes and whispers")
        print("    This is expected if database is empty")
    else:
        # 4. Swipe on first 3 profiles
        for i, profile in enumerate(profiles[:3], 1):
            direction = ["like", "like", "dislike"][i-1] if i <= 3 else "like"
            test_swipe(access_token, profile['user_id'], direction)
            time.sleep(0.5)
        
        # 5. Send whisper to first liked profile
        if len(profiles) > 0:
            first_profile = profiles[0]
            whisper_message = f"Hi {first_profile['name']}! I saw your profile and would love to connect. Your skills in {', '.join(first_profile.get('skills', [])[:2])} are impressive!"
            
            sent_whisper = test_send_whisper(
                access_token,
                first_profile['user_id'],
                whisper_message
            )
    
    # 6. Get my whispers
    whispers = test_get_whispers(access_token, type="all")
    
    # 7. Mark a received whisper as read (if any)
    if whispers and whispers['received']:
        first_received = whispers['received'][0]
        test_mark_whisper_read(access_token, first_received['id'])
    
    # 8. Get whispers again to see updated read status
    if whispers and whispers['received']:
        test_get_whispers(access_token, type="received")
    
    print("\n" + "="*80)
    print("✅ All tests completed!")
    print("="*80)
    print(f"\nTest User Created:")
    print(f"  Email: {user_data['email']}")
    print(f"  Password: {user_data['password']}")
    print(f"  User ID: {user_id}")
    print(f"  Access Token: {access_token[:50]}...")
    print("\n")


if __name__ == "__main__":
    import time
    main()
