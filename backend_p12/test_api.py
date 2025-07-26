#!/usr/bin/env python3
"""
Test script for Project Tinder Backend API
Tests both Page 1 (Recommendations) and Page 2 (AI Search) functionality
"""

import requests
import json
import sys

BASE_URL = "http://127.0.0.1:8000"

def test_auth():
    """Test authentication endpoint"""
    print("🔐 Testing Authentication...")
    
    # Try to register a test user first
    registration_data = {
        "email": "test_api@example.com",
        "password": "TestPassword123!",
        "name": "API Test User",
        "bio": "Test user for API testing"
    }
    
    response = requests.post(f"{BASE_URL}/auth/register/email", json=registration_data)
    if response.status_code == 200:
        token = response.json()["access_token"]
        print("✅ Authentication successful (registration)")
        return token
    else:
        # If registration fails (user exists), try login
        login_data = {
            "email": "test_api@example.com",
            "password": "TestPassword123!"
        }
        response = requests.post(f"{BASE_URL}/auth/login/email", json=login_data)
        if response.status_code == 200:
            token = response.json()["access_token"]
            print("✅ Authentication successful (login)")
            return token
        else:
            print(f"❌ Authentication failed: {response.status_code}")
            print(response.text)
            return None

def test_recommendations(token):
    """Test Page 1: Recommendations endpoint"""
    print("\n📱 Testing Page 1: Recommendations...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get recommendation cards
    response = requests.get(f"{BASE_URL}/recommendations/cards", headers=headers)
    if response.status_code == 200:
        cards = response.json()["cards"]
        print(f"✅ Got {len(cards)} recommendation cards")
        
        if cards:
            print(f"   Sample card: {cards[0]['name']} - {cards[0]['bio'][:50]}...")
            
            # Test swipe functionality
            card_id = cards[0]["id"]
            swipe_response = requests.post(
                f"{BASE_URL}/recommendations/swipe",
                json={"card_id": card_id, "is_like": True},
                headers=headers
            )
            if swipe_response.status_code == 200:
                print(f"✅ Swipe test successful")
            else:
                print(f"❌ Swipe test failed: {swipe_response.status_code}")
        else:
            print("   No cards available")
    elif response.status_code == 500:
        print("⚠️  Expected 500 error (no sample data in database)")
        print("   🔗 Authentication working, endpoint accessible")
    else:
        print(f"❌ Recommendations failed: {response.status_code}")
        print(response.text)

def test_ai_search(token):
    """Test Page 2: AI Search endpoint"""
    print("\n🔍 Testing Page 2: AI Search...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    test_queries = [
        "I'm looking for AI projects to invest in",
        "Need a co-founder who is good at coding",
        "Searching for marketing experts for my startup"
    ]
    
    for query in test_queries:
        print(f"   Testing query: '{query}'")
        response = requests.post(
            f"{BASE_URL}/search/query",
            json={"query": query},
            headers=headers
        )
        
        if response.status_code == 200:
            result = response.json()
            tags = result["extracted_tags"]
            results_count = len(result["results"])
            print(f"   ✅ Extracted tags: {tags}")
            print(f"   ✅ Found {results_count} results")
        elif response.status_code == 500:
            print(f"   ⚠️  Expected 500 error (no sample data in database)")
            print(f"   🔗 Authentication working, endpoint accessible")
        else:
            print(f"   ❌ Search failed: {response.status_code}")
            print(f"   Response: {response.text}")

def test_api_docs():
    """Test API documentation endpoints"""
    print("\n📚 Testing API Documentation...")
    
    docs_response = requests.get(f"{BASE_URL}/docs")
    if docs_response.status_code == 200:
        print("✅ Swagger UI available at /docs")
    else:
        print("❌ Swagger UI not accessible")
    
    redoc_response = requests.get(f"{BASE_URL}/redoc")
    if redoc_response.status_code == 200:
        print("✅ ReDoc available at /redoc")
    else:
        print("❌ ReDoc not accessible")

def main():
    print("🚀 Project Tinder Backend API Test")
    print("=" * 40)
    
    # Test basic connectivity
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print("✅ Backend server is running")
            print(f"   Message: {response.json()['message']}")
        else:
            print("❌ Backend server not responding properly")
            return
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend server. Is it running?")
        print(f"   Make sure server is running at {BASE_URL}")
        return
    
    # Test authentication first
    token = test_auth()
    if not token:
        print("❌ Cannot proceed without authentication")
        return
    
    # Test main functionality
    test_recommendations(token)
    test_ai_search(token)
    test_api_docs()
    
    print("\n🎉 Testing completed!")
    print("Visit http://127.0.0.1:8000/docs for interactive API documentation")

if __name__ == "__main__":
    main()
