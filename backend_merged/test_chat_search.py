#!/usr/bin/env python3
"""
Test script for chat search functionality
Tests searching through chats and messages
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
TEST_EMAIL = "test.user@example.com"
TEST_PASSWORD = "testpassword123"

def get_auth_token():
    """Get authentication token for testing"""
    login_data = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/auth/login/email", json=login_data)
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print(f"❌ Failed to login: {response.status_code}")
        print(response.text)
        return None

def test_chat_search():
    """Test chat and message search functionality"""
    print("🔍 Testing Chat Search Functionality")
    print("=" * 50)
    
    # Get auth token
    token = get_auth_token()
    if not token:
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test 1: Basic message content search
    print("\n1. Testing message content search...")
    search_data = {
        "query": "hello",
        "search_messages": True,
        "search_users": False,
        "limit": 10
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/chats/search", json=search_data, headers=headers)
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Message search successful")
        print(f"   Query: '{result['query']}'")
        print(f"   Found messages: {result['total_messages']}")
        print(f"   Found chats: {result['total_chats']}")
        
        if result['messages']:
            msg = result['messages'][0]
            print(f"   First message: {msg['content'][:50]}...")
            if msg.get('highlighted_content'):
                print(f"   Highlighted: {msg['highlighted_content'][:50]}...")
    else:
        print(f"❌ Message search failed: {response.status_code}")
        print(response.text)
        return False
    
    # Test 2: User name search
    print("\n2. Testing user name search...")
    search_data = {
        "query": "john",
        "search_messages": False,
        "search_users": True,
        "limit": 10
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/chats/search", json=search_data, headers=headers)
    if response.status_code == 200:
        result = response.json()
        print(f"✅ User search successful")
        print(f"   Query: '{result['query']}'")
        print(f"   Found chats: {result['total_chats']}")
        
        if result['chats']:
            chat = result['chats'][0]
            print(f"   Found user: {chat['other_user_name']}")
            print(f"   Match reason: {chat['match_reason']}")
            print(f"   Recent messages: {len(chat['recent_messages'])}")
    else:
        print(f"❌ User search failed: {response.status_code}")
        print(response.text)
    
    # Test 3: Combined search
    print("\n3. Testing combined search...")
    search_data = {
        "query": "test",
        "search_messages": True,
        "search_users": True,
        "limit": 20
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/chats/search", json=search_data, headers=headers)
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Combined search successful")
        print(f"   Total results: {result['total_messages'] + result['total_chats']}")
        print(f"   Messages: {result['total_messages']}")
        print(f"   Chats: {result['total_chats']}")
    else:
        print(f"❌ Combined search failed: {response.status_code}")
    
    # Test 4: Search with special characters
    print("\n4. Testing search with special characters...")
    search_data = {
        "query": "😊",
        "search_messages": True,
        "search_users": False,
        "limit": 5
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/chats/search", json=search_data, headers=headers)
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Special character search successful")
        print(f"   Emoji search results: {result['total_messages']}")
    else:
        print(f"❌ Special character search failed: {response.status_code}")
    
    # Test 5: Empty search query (should fail validation)
    print("\n5. Testing empty search query...")
    search_data = {
        "query": "",
        "search_messages": True,
        "search_users": True,
        "limit": 10
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/chats/search", json=search_data, headers=headers)
    if response.status_code == 422:
        print("✅ Empty query correctly rejected")
    else:
        print(f"❌ Empty query should have been rejected: {response.status_code}")
    
    return True

def test_search_performance():
    """Test search performance with different query types"""
    print("\n\n⚡ Testing Search Performance")
    print("=" * 50)
    
    token = get_auth_token()
    if not token:
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    test_queries = [
        ("Short query", "hi"),
        ("Medium query", "how are you"),
        ("Long query", "I was wondering if you would like to meet up"),
        ("Common word", "the"),
        ("Uncommon word", "serendipity")
    ]
    
    for name, query in test_queries:
        start_time = datetime.now()
        
        search_data = {
            "query": query,
            "search_messages": True,
            "search_users": True,
            "limit": 50
        }
        
        response = requests.post(f"{BASE_URL}/api/v1/chats/search", json=search_data, headers=headers)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds() * 1000  # Convert to milliseconds
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ {name}: {duration:.1f}ms ({result['total_messages'] + result['total_chats']} results)")
        else:
            print(f"❌ {name}: Failed ({response.status_code})")

def test_search_edge_cases():
    """Test edge cases for search functionality"""
    print("\n\n🧪 Testing Search Edge Cases")
    print("=" * 50)
    
    token = get_auth_token()
    if not token:
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    edge_cases = [
        ("Very long query", "a" * 100),  # Should be truncated or rejected
        ("SQL injection attempt", "'; DROP TABLE messages; --"),
        ("Unicode characters", "héllo wörld 🌍"),
        ("Numbers only", "12345"),
        ("Special chars", "!@#$%^&*()"),
        ("Mixed case", "HeLLo WoRLd")
    ]
    
    for name, query in edge_cases:
        search_data = {
            "query": query,
            "search_messages": True,
            "search_users": True,
            "limit": 10
        }
        
        response = requests.post(f"{BASE_URL}/api/v1/chats/search", json=search_data, headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ {name}: Handled correctly ({result['total_messages'] + result['total_chats']} results)")
        elif response.status_code == 422:
            print(f"✅ {name}: Validation rejected correctly")
        else:
            print(f"❌ {name}: Unexpected error ({response.status_code})")

def main():
    """Main test function"""
    print(f"🚀 Starting Chat Search Tests at {datetime.now()}")
    print(f"🌐 Server URL: {BASE_URL}")
    print(f"📧 Test Email: {TEST_EMAIL}")
    
    try:
        # Check if server is running
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code != 200:
            print("❌ Server is not running or not responding")
            return
        
        print("✅ Server is running")
        
        # Run tests
        if test_chat_search():
            test_search_performance()
            test_search_edge_cases()
            print("\n🎉 All chat search tests completed!")
        else:
            print("\n❌ Main search test failed")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure it's running on port 8000")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()
