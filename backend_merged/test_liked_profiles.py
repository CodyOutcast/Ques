#!/usr/bin/env python3
"""
Test script for liked profiles functionality
Tests the /users/liked and /users/liked/mutual endpoints
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

def test_liked_profiles_endpoint():
    """Test the liked profiles endpoint"""
    print("🔍 Testing Liked Profiles Endpoint")
    print("=" * 50)
    
    # Get auth token
    token = get_auth_token()
    if not token:
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test 1: Get liked profiles (default pagination)
    print("\n1. Testing basic liked profiles...")
    response = requests.get(f"{BASE_URL}/api/v1/users/liked", headers=headers)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Liked profiles retrieved successfully")
        print(f"   Total likes: {result['total']}")
        print(f"   Page: {result['page']}/{result['total_pages']}")
        print(f"   Users in this page: {len(result['users'])}")
        
        # Show first few users if any
        if result['users']:
            print(f"   First user: {result['users'][0]['username']} (Mutual: {result['users'][0]['is_mutual_like']})")
        else:
            print("   No liked users found")
            
    else:
        print(f"❌ Failed to get liked profiles: {response.status_code}")
        print(response.text)
        return False
    
    # Test 2: Test pagination
    print("\n2. Testing pagination...")
    response = requests.get(
        f"{BASE_URL}/api/v1/users/liked", 
        headers=headers,
        params={"page": 1, "per_page": 5}
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Pagination works")
        print(f"   Requested 5 per page, got: {len(result['users'])}")
        print(f"   Has next page: {result['has_next']}")
    else:
        print(f"❌ Pagination failed: {response.status_code}")
    
    # Test 3: Get mutual likes
    print("\n3. Testing mutual likes endpoint...")
    response = requests.get(f"{BASE_URL}/api/v1/users/liked/mutual", headers=headers)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Mutual likes retrieved successfully")
        print(f"   Total mutual likes: {result['total']}")
        print(f"   Mutual users in this page: {len(result['users'])}")
        
        if result['users']:
            print(f"   First mutual match: {result['users'][0]['username']}")
        else:
            print("   No mutual likes found")
            
    else:
        print(f"❌ Failed to get mutual likes: {response.status_code}")
        print(response.text)
        return False
    
    return True

def test_error_cases():
    """Test error cases and edge conditions"""
    print("\n\n🧪 Testing Error Cases")
    print("=" * 50)
    
    # Test 1: Invalid token
    print("\n1. Testing invalid token...")
    headers = {"Authorization": "Bearer invalid_token"}
    response = requests.get(f"{BASE_URL}/api/v1/users/liked", headers=headers)
    
    if response.status_code == 401:
        print("✅ Invalid token correctly rejected")
    else:
        print(f"❌ Invalid token should return 401, got: {response.status_code}")
    
    # Test 2: No token
    print("\n2. Testing no token...")
    response = requests.get(f"{BASE_URL}/api/v1/users/liked")
    
    if response.status_code == 403:
        print("✅ Missing token correctly rejected")
    else:
        print(f"❌ Missing token should return 403, got: {response.status_code}")
    
    # Test 3: Invalid pagination
    print("\n3. Testing invalid pagination...")
    token = get_auth_token()
    if token:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(
            f"{BASE_URL}/api/v1/users/liked", 
            headers=headers,
            params={"page": 0, "per_page": -1}  # Invalid values
        )
        
        if response.status_code == 422:
            print("✅ Invalid pagination parameters rejected")
        else:
            print(f"❌ Invalid pagination should return 422, got: {response.status_code}")

def test_schema_validation():
    """Test that response schemas are correct"""
    print("\n\n📋 Testing Response Schemas")
    print("=" * 50)
    
    token = get_auth_token()
    if not token:
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(f"{BASE_URL}/api/v1/users/liked", headers=headers)
    
    if response.status_code == 200:
        result = response.json()
        
        # Check required fields in response
        required_fields = ["page", "per_page", "total", "total_pages", "has_next", "has_prev", "users"]
        missing_fields = [field for field in required_fields if field not in result]
        
        if not missing_fields:
            print("✅ Response schema is valid")
            
            # Check user schema if users exist
            if result["users"]:
                user = result["users"][0]
                user_required = ["id", "username", "liked_at", "is_mutual_like"]
                user_missing = [field for field in user_required if field not in user]
                
                if not user_missing:
                    print("✅ User schema is valid")
                else:
                    print(f"❌ User schema missing fields: {user_missing}")
            else:
                print("ℹ️  No users to validate schema")
        else:
            print(f"❌ Response schema missing fields: {missing_fields}")
    else:
        print(f"❌ Could not test schema: {response.status_code}")

def main():
    """Main test function"""
    print(f"🚀 Starting Liked Profiles Tests at {datetime.now()}")
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
        if test_liked_profiles_endpoint():
            test_error_cases()
            test_schema_validation()
            print("\n🎉 All liked profiles tests completed!")
        else:
            print("\n❌ Main endpoint test failed")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure it's running on port 8000")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()
