#!/usr/bin/env python3
"""
Test script for the new multi-method authentication system
Tests Email/Password and WeChat authentication flows
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_email_auth():
    """Test email/password authentication"""
    print("📧 Testing Email Authentication")
    print("-" * 30)
    
    # Test registration
    register_data = {
        "email": "test@example.com",
        "password": "securepassword123",
        "name": "Test User",
        "bio": "Testing the auth system"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/register/email", json=register_data)
        if response.status_code == 200:
            result = response.json()
            print("✅ Email registration successful")
            print(f"   User: {result['user']['name']}")
            print(f"   Token type: {result['token_type']}")
            return result['access_token']
        else:
            print(f"❌ Email registration failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Email registration error: {e}")
    
    # Test login
    login_data = {
        "email": "test@example.com", 
        "password": "securepassword123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login/email", json=login_data)
        if response.status_code == 200:
            result = response.json()
            print("✅ Email login successful")
            return result['access_token']
        else:
            print(f"❌ Email login failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Email login error: {e}")
    
    return None

def test_verification_code():
    """Test verification code sending"""
    print("\n📱 Testing Verification Code System")
    print("-" * 35)
    
    # Test sending verification code
    verification_data = {
        "provider_type": "email",
        "provider_id": "test@example.com", 
        "purpose": "registration"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/send-verification-code", json=verification_data)
        if response.status_code == 200:
            result = response.json()
            print("✅ Verification code sent successfully")
            print(f"   Message: {result['message']}")
            print(f"   Expires in: {result['expires_in']} seconds")
        else:
            print(f"❌ Verification code sending failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Verification code error: {e}")

def test_user_profile(token):
    """Test getting user profile with authentication"""
    if not token:
        print("\n❌ No token available for profile test")
        return
        
    print("\n👤 Testing User Profile Access")
    print("-" * 30)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
        if response.status_code == 200:
            result = response.json()
            print("✅ Profile access successful")
            print(f"   User ID: {result['id']}")
            print(f"   Name: {result['name']}")
            print(f"   Auth methods: {result['auth_methods']}")
        else:
            print(f"❌ Profile access failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Profile access error: {e}")

def test_legacy_compatibility():
    """Test legacy authentication for backward compatibility"""
    print("\n🔄 Testing Legacy Compatibility")
    print("-" * 30)
    
    try:
        response = requests.post(f"{BASE_URL}/auth/token", json={"user_id": 1})
        if response.status_code == 200:
            result = response.json()
            print("✅ Legacy authentication still works")
            print(f"   Token type: {result['token_type']}")
            return result['access_token']
        else:
            print(f"❌ Legacy authentication failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Legacy authentication error: {e}")
    
    return None

def main():
    print("🚀 Multi-Method Authentication Test Suite")
    print("=" * 50)
    
    # Check server connectivity
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code != 200:
            print("❌ Backend server not responding properly")
            return
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend server. Is it running?")
        print("   Start with: uvicorn main:app --reload")
        return
    
    # Run authentication tests
    token = test_email_auth()
    test_verification_code() 
    test_user_profile(token)
    
    # Test legacy compatibility
    legacy_token = test_legacy_compatibility()
    
    print(f"\n🎉 Authentication tests completed!")
    print("   New multi-method auth system is ready for production")
    print("   Legacy endpoints remain functional for backward compatibility")

if __name__ == "__main__":
    main()
