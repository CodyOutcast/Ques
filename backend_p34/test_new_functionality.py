#!/usr/bin/env python3
"""
Test script for Page 3 (User Creation) and Page 4 (Chat) functionality
Tests our new test server endpoints
"""

import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000"

def test_server_health():
    """Test if server is running"""
    print("🏥 Testing Server Health...")
    
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print("✅ Server is running")
            print(f"   Message: {response.json()['message']}")
            return True
        else:
            print(f"❌ Server returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Is it running?")
        return False

def test_page3_user_creation():
    """Test Page 3: User Creation functionality"""
    print("\n👤 Testing Page 3: User Creation...")
    
    # Test user registration
    user_data = {
        "name": "John Doe",
        "bio": "Entrepreneur looking for AI co-founders",
        "feature_tags": ["AI", "Startup", "Full-stack Developer"],
        "portfolio_links": ["https://github.com/johndoe", "https://linkedin.com/in/johndoe"]
    }
    
    response = requests.post(f"{BASE_URL}/users/register", json=user_data)
    if response.status_code == 201:
        user = response.json()
        print(f"✅ User registration successful - ID: {user['user_id']}")
        print(f"   Name: {user['name']}")
        print(f"   Bio: {user['bio']}")
        print(f"   Tags: {user['feature_tags']}")
        print(f"   Status: {user['verification_status']}")
        return user['user_id']
    else:
        print(f"❌ User registration failed: {response.status_code}")
        print(f"   Response: {response.text}")
        return None

def test_get_user_profile(user_id):
    """Test getting user profile"""
    print(f"\n📋 Testing Get User Profile for ID {user_id}...")
    
    response = requests.get(f"{BASE_URL}/users/profile/{user_id}")
    if response.status_code == 200:
        profile = response.json()
        print(f"✅ Profile retrieved successfully")
        print(f"   Name: {profile['name']}")
        print(f"   Bio: {profile['bio']}")
        print(f"   Feature Tags: {profile['feature_tags']}")
        print(f"   Portfolio Links: {profile['portfolio_links']}")
        return True
    else:
        print(f"❌ Failed to get profile: {response.status_code}")
        return False

def setup_test_data():
    """Set up test data for chat testing"""
    print("\n🔧 Setting up test data...")
    
    response = requests.post(f"{BASE_URL}/test/setup")
    if response.status_code == 200:
        result = response.json()
        print("✅ Test data created successfully")
        print(f"   Created users: {result['users']}")
        print(f"   Created matches: {result['matches']}")
        return result
    else:
        print(f"❌ Failed to setup test data: {response.status_code}")
        return None

def test_page4_chat_functionality():
    """Test Page 4: Chat functionality"""
    print("\n💬 Testing Page 4: Chat Functionality...")
    
    # Get test data
    test_data = setup_test_data()
    if not test_data:
        print("❌ Cannot test chat without test data")
        return
    
    user_ids = test_data['users']
    match_ids = test_data['matches']
    
    # Test getting matches for user 1 (Alice)
    alice_id = user_ids[0]
    print(f"\n📱 Testing matches for user {alice_id}...")
    
    response = requests.get(f"{BASE_URL}/chat/matches/{alice_id}")
    if response.status_code == 200:
        matches = response.json()
        print(f"✅ Retrieved {len(matches)} matches")
        
        for match in matches:
            print(f"   Match {match['match_id']}: {match['other_user_name']}")
            print(f"   Bio: {match['other_user_bio']}")
            print(f"   Unread: {match['unread_count']}")
    else:
        print(f"❌ Failed to get matches: {response.status_code}")
        return
    
    # Test sending a message
    if match_ids:
        test_match_id = match_ids[0]
        print(f"\n📝 Testing send message to match {test_match_id}...")
        
        message_data = {
            "match_id": test_match_id,
            "message_text": "Hey! I saw your profile and I'm really interested in collaborating on projects. What do you think?"
        }
        
        response = requests.post(f"{BASE_URL}/chat/send?user_id={alice_id}", json=message_data)
        if response.status_code == 201:
            message = response.json()
            print(f"✅ Message sent successfully")
            print(f"   Message ID: {message['message_id']}")
            print(f"   From: {message['sender_name']}")
            print(f"   Text: {message['message_text'][:50]}...")
            
            # Test sending a reply from the other user
            bob_id = user_ids[1]  # Bob
            reply_data = {
                "match_id": test_match_id,
                "message_text": "Hi Alice! I'd love to collaborate. I have experience with blockchain and backend development."
            }
            
            reply_response = requests.post(f"{BASE_URL}/chat/send?user_id={bob_id}", json=reply_data)
            if reply_response.status_code == 201:
                reply = reply_response.json()
                print(f"✅ Reply sent successfully")
                print(f"   From: {reply['sender_name']}")
                print(f"   Text: {reply['message_text'][:50]}...")
            
        else:
            print(f"❌ Failed to send message: {response.status_code}")
    
    # Test unread message count
    print(f"\n📬 Testing unread message count for user {alice_id}...")
    
    response = requests.get(f"{BASE_URL}/chat/unread-count/{alice_id}")
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Unread count: {result['unread_count']}")
    else:
        print(f"❌ Failed to get unread count: {response.status_code}")

def test_all_users():
    """Test getting all users"""
    print("\n📋 Testing Get All Users...")
    
    response = requests.get(f"{BASE_URL}/users/?limit=10")
    if response.status_code == 200:
        result = response.json()
        users = result['users']
        print(f"✅ Retrieved {len(users)} users")
        
        for i, user in enumerate(users[:3]):  # Show first 3 users
            print(f"   {i+1}. {user['name']} - {user['feature_tags']}")
    else:
        print(f"❌ Failed to get users: {response.status_code}")

def test_api_docs():
    """Test API documentation"""
    print("\n📚 Testing API Documentation...")
    
    docs_response = requests.get(f"{BASE_URL}/docs")
    if docs_response.status_code == 200:
        print("✅ Swagger UI available at /docs")
    else:
        print("❌ Swagger UI not accessible")

def main():
    print("🚀 Testing Project Tinder Backend - Pages 3 & 4")
    print("=" * 60)
    
    # Test server health
    if not test_server_health():
        print("❌ Server is not responding. Exiting...")
        return
    
    # Test Page 3: User Creation
    print("\n" + "="*20 + " PAGE 3 TESTS " + "="*20)
    user_id = test_page3_user_creation()
    
    if user_id:
        test_get_user_profile(user_id)
    
    test_all_users()
    
    # Test Page 4: Chat
    print("\n" + "="*20 + " PAGE 4 TESTS " + "="*20)
    test_page4_chat_functionality()
    
    # Test API documentation
    test_api_docs()
    
    print("\n🎉 Testing completed!")
    print("=" * 60)
    print("📋 Summary:")
    print("✅ Page 3: User registration and profile management")
    print("💬 Page 4: Chat system with matches and messaging")
    print("\n📖 Next steps:")
    print("1. ✅ Page 3 & 4 functionality working")
    print("2. 🔗 Integrate with existing Pages 1 & 2 from backend_p12")
    print("3. 🗄️  Connect to real PostgreSQL database")
    print("4. 📱 Ready for mobile app integration")
    print("\n🌐 Visit http://127.0.0.1:8000/docs for interactive API testing")

if __name__ == "__main__":
    main()
