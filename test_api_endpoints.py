"""
Test script for the merged backend API
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_endpoints():
    print("🧪 Testing Merged Backend API Endpoints")
    print("=" * 50)
    
    # Test root endpoint
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"✅ Root endpoint: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"❌ Root endpoint failed: {e}")
    
    print()
    
    # Test health check
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"✅ Health check: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
    
    print()
    
    # Test API info
    try:
        response = requests.get(f"{BASE_URL}/api/v1/info")
        print(f"✅ API info: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"❌ API info failed: {e}")
    
    print()
    
    # Test registration endpoint (should fail without data)
    try:
        response = requests.post(f"{BASE_URL}/api/v1/auth/register")
        print(f"📝 Registration (no data): {response.status_code}")
        print(f"   Expected 422 (validation error)")
    except Exception as e:
        print(f"❌ Registration test failed: {e}")
    
    print()
    print("🎉 Basic endpoint tests completed!")
    print("📚 Full documentation available at: http://localhost:8000/docs")

if __name__ == "__main__":
    test_endpoints()
