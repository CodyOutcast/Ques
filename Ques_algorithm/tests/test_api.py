#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API test script
Test various endpoints of the FastAPI backend service
"""

import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000"

def test_api():
    """Test API endpoints"""
    print("=" * 60)
    print("QuesAI Backend API Test")
    print("=" * 60)
    
    # 1. Test root path
    print("\n1. Test root path...")
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"Status code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    except Exception as e:
        print(f"Error: {e}")
    
    # 2. Test health check
    print("\n2. Test health check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    except Exception as e:
        print(f"Error: {e}")
    
    # 3. Test statistics
    print("\n3. Test statistics...")
    try:
        response = requests.get(f"{BASE_URL}/stats")
        print(f"Status code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    except Exception as e:
        print(f"Error: {e}")
    
    # 4. Test user list (first 5)
    print("\n4. Test user list...")
    try:
        response = requests.get(f"{BASE_URL}/users?page=1&page_size=5")
        print(f"Status code: {response.status_code}")
        data = response.json()
        print(f"Total users: {data.get('total', 0)}")
        print(f"Current page: {data.get('page', 0)}")
        print(f"Page size: {data.get('page_size', 0)}")
        print(f"Returned users: {len(data.get('users', []))}")
        
        # Show details of the first user
        if data.get('users'):
            user = data['users'][0]
            print(f"\nFirst user details:")
            print(f"  ID: {user.get('id')}")
            print(f"  Name: {user.get('name')}")
            print(f"  Age: {user.get('age')}")
            print(f"  Gender: {user.get('gender')}")
            print(f"  Location: {user.get('province_name', '')}{user.get('city_name', '')}")
            print(f"  Skills: {user.get('skills', [])}")
            print(f"  Introduction: {user.get('one_sentence_intro', '')}")
            print(f"  Projects: {user.get('project_count', 0)}")
            print(f"  Institutions: {user.get('institution_count', 0)}")
            
    except Exception as e:
        print(f"Error: {e}")
    
    # 5. Test user details
    print("\n5. Test user details...")
    try:
        response = requests.get(f"{BASE_URL}/users/1")
        print(f"Status code: {response.status_code}")
        if response.status_code == 200:
            user = response.json()
            print(f"User details:")
            print(f"  ID: {user.get('id')}")
            print(f"  Name: {user.get('name')}")
            print(f"  Age: {user.get('age')}")
            print(f"  Goals: {user.get('goals', '')}")
            print(f"  Demands: {user.get('demands', [])}")
            print(f"  Project count: {len(user.get('projects', []))}")
            print(f"  Institution count: {len(user.get('institutions', []))}")
            
            # Show project information
            if user.get('projects'):
                print(f"  Project experience:")
                for proj in user['projects'][:2]:  # Show only first 2 projects
                    print(f"    - {proj.get('title')}: {proj.get('role')}")
            
            # Show institution information
            if user.get('institutions'):
                print(f"  Institution experience:")
                for inst in user['institutions']:
                    print(f"    - {inst.get('institution_name')}: {inst.get('position')}")
        else:
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")
    
    # 6. Test search functionality
    print("\n6. Test search functionality...")
    try:
        # Search by skill
        response = requests.get(f"{BASE_URL}/users?search=Python&page_size=3")
        print(f"Search 'Python' status code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Found {data.get('total', 0)} Python-related users")
            for user in data.get('users', [])[:3]:
                print(f"  - {user.get('name')}: {user.get('skills', [])}")
        
        # Search by location
        response = requests.get(f"{BASE_URL}/users?province=北京&page_size=3")
        print(f"\nSearch 'Beijing' status code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Found {data.get('total', 0)} Beijing users")
            for user in data.get('users', [])[:3]:
                print(f"  - {user.get('name')}: {user.get('province_name', '')}{user.get('city_name', '')}")
                
    except Exception as e:
        print(f"Error: {e}")
    
    # 7. Test provinces and cities
    print("\n7. Test provinces and cities...")
    try:
        response = requests.get(f"{BASE_URL}/provinces")
        print(f"Province list status code: {response.status_code}")
        if response.status_code == 200:
            provinces = response.json()
            print(f"Total provinces: {len(provinces)}")
            print(f"First 5 provinces: {[p['name_cn'] for p in provinces[:5]]}")
        
        response = requests.get(f"{BASE_URL}/cities?province_id=1")
        print(f"Beijing city list status code: {response.status_code}")
        if response.status_code == 200:
            cities = response.json()
            print(f"Beijing cities count: {len(cities)}")
            print(f"Beijing cities: {[c['name_cn'] for c in cities]}")
            
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n" + "=" * 60)
    print("API test completed!")
    print("=" * 60)

if __name__ == "__main__":
    print("Waiting for server to start...")
    time.sleep(2)
    test_api()