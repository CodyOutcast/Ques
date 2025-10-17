#!/usr/bin/env python3
"""
API Documentation Validation Script
Tests if the documented API endpoints match the actual backend implementation
"""

import requests
import json
import sys
from typing import Dict, Any

# API Base URL
BASE_URL = "http://localhost:8000"

def test_endpoint(method: str, path: str, data: Dict[Any, Any] = None, headers: Dict[str, str] = None) -> Dict[str, Any]:
    """Test an API endpoint and return the result"""
    url = f"{BASE_URL}{path}"
    
    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=headers, timeout=10)
        elif method.upper() == "POST":
            response = requests.post(url, json=data, headers=headers, timeout=10)
        elif method.upper() == "PUT":
            response = requests.put(url, json=data, headers=headers, timeout=10)
        elif method.upper() == "DELETE":
            response = requests.delete(url, headers=headers, timeout=10)
        else:
            return {"error": f"Unsupported method: {method}"}
        
        return {
            "status_code": response.status_code,
            "success": response.status_code < 400,
            "data": response.json() if response.text else None,
            "headers": dict(response.headers)
        }
    except requests.ConnectionError:
        return {"error": "Connection failed - server not running"}
    except requests.Timeout:
        return {"error": "Request timeout"}
    except Exception as e:
        return {"error": str(e)}

def main():
    """Test key API endpoints from the documentation"""
    
    print("🔍 API Documentation Validation")
    print("=" * 50)
    
    # Test 1: Server Health Check
    print("\n1. Testing Server Health...")
    result = test_endpoint("GET", "/health")
    if "error" in result:
        print(f"❌ Server not running: {result['error']}")
        print("\nTo start the server, run:")
        print("uvicorn main:app --host 127.0.0.1 --port 8000 --reload")
        return False
    else:
        print(f"✅ Server is running: {result['data']}")
    
    # Test 2: Basic API Info
    print("\n2. Testing API Info...")
    result = test_endpoint("GET", "/")
    if result["success"]:
        print(f"✅ Root endpoint: {result['data']}")
    else:
        print(f"❌ Root endpoint failed: {result}")
    
    # Test 3: API V1 Info
    print("\n3. Testing API V1 Info...")
    result = test_endpoint("GET", "/api/v1/info")
    if result["success"]:
        print(f"✅ API V1 info: {result['data']}")
    else:
        print(f"❌ API V1 info failed: {result}")
    
    # Test 4: Authentication endpoints (no token required)
    print("\n4. Testing Authentication Endpoints...")
    
    # Test SMS send code endpoint
    sms_data = {
        "phone_number": "+1234567890",
        "country_code": "+1",
        "purpose": "REGISTRATION"
    }
    result = test_endpoint("POST", "/api/v1/sms/send-code", sms_data)
    print(f"SMS Send Code: {'✅' if result.get('success') else '❌'} Status: {result.get('status_code', 'N/A')}")
    
    # Test 5: User registration endpoint (should work without auth)
    print("\n5. Testing User Registration...")
    user_data = {
        "email": "test@example.com",
        "password": "TestPass123",
        "name": "Test User",
        "bio": "Test user for API validation"
    }
    result = test_endpoint("POST", "/api/v1/basic/users", user_data)
    print(f"User Registration: {'✅' if result.get('success') else '❌'} Status: {result.get('status_code', 'N/A')}")
    if result.get("data"):
        print(f"Response: {json.dumps(result['data'], indent=2)}")
    
    # Test 6: Protected endpoints (should fail without auth)
    print("\n6. Testing Protected Endpoints (should fail without auth)...")
    
    protected_endpoints = [
        ("GET", "/api/v1/users/profile"),
        ("GET", "/api/v1/users/discover"),
        ("POST", "/api/v1/whispers"),
        ("GET", "/api/v1/notifications"),
        ("GET", "/api/v1/contacts")
    ]
    
    for method, path in protected_endpoints:
        result = test_endpoint(method, path)
        expected_fail = result.get("status_code") in [401, 422]  # 401 Unauthorized or 422 for missing auth
        print(f"{method} {path}: {'✅' if expected_fail else '❌'} Status: {result.get('status_code', 'N/A')}")
    
    print("\n🏁 API Documentation Validation Complete!")
    return True

if __name__ == "__main__":
    main()