"""
Test script for message search functionality
Run this after setting up the database and having some test messages
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"

def test_message_search():
    """Test the message search endpoints"""
    
    print("🔍 Testing Message Search Functionality")
    print("=" * 50)
    
    # You'll need to replace these with actual values from your database
    # Get these by logging in and getting a real token
    test_token = "your_jwt_token_here"
    test_match_id = 1  # Replace with actual match ID
    test_message_id = 1  # Replace with actual message ID
    
    headers = {
        "Authorization": f"Bearer {test_token}",
        "Content-Type": "application/json"
    }
    
    # Test 1: Search messages in a specific conversation
    print("\n1. Testing conversation-specific search...")
    try:
        response = requests.get(
            f"{API_BASE}/messages/{test_match_id}/search",
            params={"query": "hello", "limit": 10},
            headers=headers
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Found {data['total_count']} messages containing 'hello'")
            print(f"Showing {len(data['results'])} results")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 2: Global search across all conversations
    print("\n2. Testing global message search...")
    try:
        response = requests.get(
            f"{API_BASE}/messages/search/global",
            params={"query": "test", "limit": 10},
            headers=headers
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Found {data['total_count']} messages containing 'test' across all conversations")
            print(f"Showing {len(data['results'])} results")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 3: Get message context (for jump-to-message functionality)
    print("\n3. Testing message context retrieval...")
    try:
        response = requests.get(
            f"{API_BASE}/messages/{test_match_id}/message/{test_message_id}/context",
            params={"before": 3, "after": 3},
            headers=headers
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Retrieved {data['total_context']} messages for context")
            print(f"Target message ID: {data['target_message_id']}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Message search tests completed!")
    print("\nNOTE: Update the test_token, test_match_id, and test_message_id")
    print("with real values from your database to run actual tests.")

def print_api_endpoints():
    """Print all the new message search endpoints"""
    
    print("\n📡 New Message Search API Endpoints:")
    print("=" * 50)
    
    endpoints = [
        {
            "method": "GET",
            "path": "/api/v1/messages/{match_id}/search",
            "description": "Search messages within a specific conversation",
            "params": "query, limit, offset"
        },
        {
            "method": "GET", 
            "path": "/api/v1/messages/search/global",
            "description": "Search messages across all user's conversations",
            "params": "query, limit, offset"
        },
        {
            "method": "GET",
            "path": "/api/v1/messages/{match_id}/message/{message_id}/context",
            "description": "Get context around a specific message (for jump-to)",
            "params": "before, after"
        }
    ]
    
    for endpoint in endpoints:
        print(f"\n{endpoint['method']} {endpoint['path']}")
        print(f"   📝 {endpoint['description']}")
        print(f"   📋 Parameters: {endpoint['params']}")
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    print_api_endpoints()
    
    # Uncomment to run tests (after updating tokens/IDs)
    # test_message_search()
