"""
API Testing Script for Project Idea Generation Agent
Tests the actual FastAPI endpoints
"""

import requests
import json
import time
from typing import Dict, Any

class ProjectIdeaAPITester:
    """Tester for Project Idea API endpoints"""
    
    def __init__(self, base_url: str = "http://localhost:8000", auth_token: str = None):  # type: ignore
        self.base_url = base_url
        self.auth_token = auth_token
        self.headers = {
            "Content-Type": "application/json"
        }
        if auth_token:
            self.headers["Authorization"] = f"Bearer {auth_token}"
    
    def test_health_check(self) -> bool:
        """Test if the server is running"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=10)
            if response.status_code == 200:
                print("✅ Server health check: PASSED")
                return True
            else:
                print(f"❌ Server health check: FAILED (Status: {response.status_code})")
                return False
        except Exception as e:
            print(f"❌ Server health check: FAILED (Error: {str(e)})")
            return False
    
    def test_quota_endpoint(self) -> Dict[str, Any]:
        """Test quota status endpoint"""
        try:
            response = requests.get(
                f"{self.base_url}/api/v1/project-ideas/quota",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                quota_data = response.json()
                print("✅ Quota endpoint: PASSED")
                print(f"   Daily limit: {quota_data.get('daily_limit')}")
                print(f"   Used today: {quota_data.get('used_today')}")
                print(f"   Remaining: {quota_data.get('remaining_today')}")
                return quota_data
            else:
                print(f"❌ Quota endpoint: FAILED (Status: {response.status_code})")
                print(f"   Response: {response.text}")
                return {}
        except Exception as e:
            print(f"❌ Quota endpoint: FAILED (Error: {str(e)})")
            return {}
    
    def test_generate_ideas(self, query: str) -> Dict[str, Any]:
        """Test project idea generation endpoint"""
        print(f"\n🎯 Testing idea generation for: '{query}'")
        
        start_time = time.time()
        
        try:
            response = requests.post(
                f"{self.base_url}/api/v1/project-ideas/generate",
                headers=self.headers,
                json={"query": query},
                timeout=120  # Extended timeout for processing
            )
            
            end_time = time.time()
            processing_time = end_time - start_time
            
            if response.status_code == 201:
                result = response.json()
                print(f"✅ Idea generation: PASSED ({processing_time:.2f}s)")
                
                # Validate response structure
                required_fields = [
                    "search_id", "original_query", "generated_prompts",
                    "total_sources_found", "total_ideas_extracted",
                    "project_ideas", "processing_time_seconds", "created_at"
                ]
                
                missing_fields = [field for field in required_fields if field not in result]
                if missing_fields:
                    print(f"⚠️  Missing fields: {missing_fields}")
                else:
                    print("✅ Response structure: VALID")
                
                # Validate project ideas
                ideas = result.get("project_ideas", [])
                if len(ideas) == 3:
                    print("✅ Project ideas count: CORRECT (3 ideas)")
                else:
                    print(f"⚠️  Project ideas count: {len(ideas)} (expected 3)")
                
                # Display summary
                print(f"   Search ID: {result.get('search_id')}")
                print(f"   Sources found: {result.get('total_sources_found')}")
                print(f"   Ideas extracted: {result.get('total_ideas_extracted')}")
                print(f"   Processing time: {result.get('processing_time_seconds')}s")
                
                # Display first idea details
                if ideas:
                    first_idea = ideas[0]
                    print(f"   First idea: {first_idea.get('project_idea_title')}")
                    print(f"   Difficulty: {first_idea.get('difficulty_level')}")
                    print(f"   Timeline: {first_idea.get('estimated_timeline')}")
                    print(f"   Relevance: {first_idea.get('relevance_score')}")
                
                return result
                
            elif response.status_code == 429:
                print("❌ Idea generation: QUOTA EXCEEDED")
                print(f"   Response: {response.json()}")
                return {}
            else:
                print(f"❌ Idea generation: FAILED (Status: {response.status_code})")
                print(f"   Response: {response.text}")
                return {}
                
        except Exception as e:
            end_time = time.time()
            processing_time = end_time - start_time
            print(f"❌ Idea generation: FAILED after {processing_time:.2f}s")
            print(f"   Error: {str(e)}")
            return {}
    
    def run_comprehensive_test(self):
        """Run all API tests"""
        print("🧪 Project Idea API Comprehensive Test")
        print("=" * 50)
        
        # Test 1: Health check
        if not self.test_health_check():
            print("❌ Server not available. Please start the server first.")
            return
        
        # Test 2: Quota status
        quota_data = self.test_quota_endpoint()
        
        if not quota_data.get('has_quota', False):
            print("❌ No quota available. Cannot test idea generation.")
            return
        
        # Test 3: Idea generation with different query types
        test_queries = [
            "Build a simple Python web scraper",
            "Create a mobile app for fitness tracking",
            "Write a technical blog about machine learning",
            "Design an interactive data visualization",
            "Develop a chrome extension for productivity"
        ]
        
        successful_tests = 0
        for i, query in enumerate(test_queries[:3], 1):  # Limit to 3 to respect quota
            print(f"\n--- Test {i}/3 ---")
            result = self.test_generate_ideas(query)
            if result:
                successful_tests += 1
        
        # Test 4: Final quota check
        print(f"\n--- Final Quota Check ---")
        final_quota = self.test_quota_endpoint()
        
        # Summary
        print(f"\n{'='*50}")
        print(f"📊 Test Summary:")
        print(f"   Successful generations: {successful_tests}/3")
        print(f"   Initial quota: {quota_data.get('remaining_today', 0)}")
        print(f"   Final quota: {final_quota.get('remaining_today', 0)}")
        print(f"   Quota used: {quota_data.get('remaining_today', 0) - final_quota.get('remaining_today', 0)}")


def create_test_jwt_token():
    """Helper to create a test JWT token (you'll need to implement this based on your auth system)"""
    # This is a placeholder - you'll need to:
    # 1. Create a test user in your database
    # 2. Use your auth system to generate a valid JWT token
    # 3. Or use an existing valid token
    
    print("⚠️  AUTH TOKEN NEEDED:")
    print("1. Create a test user account")
    print("2. Login to get a JWT token")
    print("3. Pass the token to this script")
    print("\nExample:")
    print("python api_test.py --token 'your_jwt_token_here'")
    
    return None


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Test Project Idea API endpoints")
    parser.add_argument("--url", default="http://localhost:8000", help="Base URL of the API")
    parser.add_argument("--token", help="JWT authentication token")
    parser.add_argument("--create-token", action="store_true", help="Show how to create auth token")
    
    args = parser.parse_args()
    
    if args.create_token:
        create_test_jwt_token()
        exit()
    
    if not args.token:
        print("❌ Authentication token required!")
        print("Use --create-token to see how to get one, or --token <your_token>")
        exit()
    
    # Run tests
    tester = ProjectIdeaAPITester(args.url, args.token)
    tester.run_comprehensive_test()
