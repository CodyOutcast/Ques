#!/usr/bin/env python3
"""
Test script for password reset functionality
Tests the complete password reset flow
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
TEST_EMAIL = "test.user@example.com"
TEST_PASSWORD = "testpassword123"
NEW_PASSWORD = "newpassword456"

def test_password_reset_flow():
    """Test complete password reset flow"""
    print("Password Reset Flow Test")
    print("=" * 50)
    
    # Step 1: Register a test user first (if not exists)
    print("\n1. Registering test user...")
    register_data = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD,
        "name": "Test User"
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/auth/register/email", json=register_data)
    if response.status_code == 201:
        print("✅ Test user registered successfully")
    elif response.status_code == 400 and "already exists" in response.text:
        print("ℹ️  Test user already exists")
    else:
        print(f"❌ Failed to register test user: {response.status_code}")
        print(response.text)
        return False
    
    # Step 2: Request password reset
    print("\n2. Requesting password reset...")
    forgot_data = {
        "email": TEST_EMAIL
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/auth/forgot-password", json=forgot_data)
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Password reset requested: {result['message']}")
    else:
        print(f"❌ Failed to request password reset: {response.status_code}")
        print(response.text)
        return False
    
    # Step 3: Simulate getting reset code from email/logs
    print("\n3. Simulating reset code retrieval...")
    print("📧 In production, user would get reset code from email")
    print("🔍 For testing, check server logs for the 6-digit reset code")
    
    # Get reset code from user input
    reset_code = input("\n🔑 Enter the 6-digit reset code from server logs: ").strip()
    
    if not reset_code or len(reset_code) != 6:
        print("❌ Invalid reset code format")
        return False
    
    # Step 4: Reset password
    print("\n4. Resetting password...")
    reset_data = {
        "email": TEST_EMAIL,
        "reset_code": reset_code,
        "new_password": NEW_PASSWORD
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/auth/reset-password", json=reset_data)
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Password reset successful: {result['message']}")
    else:
        print(f"❌ Failed to reset password: {response.status_code}")
        print(response.text)
        return False
    
    # Step 5: Test login with new password
    print("\n5. Testing login with new password...")
    login_data = {
        "email": TEST_EMAIL,
        "password": NEW_PASSWORD
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/auth/login/email", json=login_data)
    if response.status_code == 200:
        result = response.json()
        print("✅ Login successful with new password")
        print(f"   Access token: {result['access_token'][:20]}...")
    else:
        print(f"❌ Failed to login with new password: {response.status_code}")
        print(response.text)
        return False
    
    # Step 6: Verify old password doesn't work
    print("\n6. Verifying old password is invalid...")
    old_login_data = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/auth/login/email", json=old_login_data)
    if response.status_code == 401:
        print("✅ Old password correctly rejected")
    else:
        print(f"❌ Old password should have been rejected: {response.status_code}")
        return False
    
    print("\n🎉 Password reset flow completed successfully!")
    return True

def test_invalid_scenarios():
    """Test invalid scenarios for password reset"""
    print("\n\n🧪 Testing Invalid Scenarios")
    print("=" * 50)
    
    # Test 1: Invalid email
    print("\n1. Testing non-existent email...")
    forgot_data = {
        "email": "nonexistent@example.com"
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/auth/forgot-password", json=forgot_data)
    if response.status_code == 200:
        print("✅ Non-existent email handled correctly (no enumeration)")
    else:
        print(f"❌ Unexpected response for non-existent email: {response.status_code}")
    
    # Test 2: Invalid reset code
    print("\n2. Testing invalid reset code...")
    reset_data = {
        "email": TEST_EMAIL,
        "reset_code": "123456",  # Invalid code
        "new_password": "newpassword789"
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/auth/reset-password", json=reset_data)
    if response.status_code == 400:
        print("✅ Invalid reset code correctly rejected")
    else:
        print(f"❌ Invalid reset code should have been rejected: {response.status_code}")
    
    # Test 3: Weak password
    print("\n3. Testing weak password...")
    reset_data = {
        "email": TEST_EMAIL,
        "reset_code": "123456",
        "new_password": "123"  # Too short
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/auth/reset-password", json=reset_data)
    if response.status_code == 422:
        print("✅ Weak password correctly rejected")
    else:
        print(f"❌ Weak password should have been rejected: {response.status_code}")

def main():
    """Main test function"""
    print(f"🚀 Starting Password Reset Tests at {datetime.now()}")
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
        if test_password_reset_flow():
            test_invalid_scenarios()
            print("\n🎉 All tests completed!")
        else:
            print("\n❌ Main flow test failed")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure it's running on port 8000")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()
