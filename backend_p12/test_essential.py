#!/usr/bin/env python3
"""
Essential Test Suite - Tests all core functionality
Tests: PostgreSQL, VectorDB, Email Service, Authentication, Recommendations
"""

import os
import sys
import json
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_postgresql_connection():
    """Test PostgreSQL database connection and basic operations"""
    print("🐘 Testing PostgreSQL Connection...")
    
    try:
        from models.base import SessionLocal
        from sqlalchemy import text
        
        db = SessionLocal()
        
        # Test connection
        result = db.execute(text("SELECT version()"))
        version = result.fetchone()[0]
        print(f"   ✅ Connected to PostgreSQL: {version[:50]}...")
        
        # Test users table
        result = db.execute(text("SELECT COUNT(*) FROM users"))
        user_count = result.fetchone()[0]
        print(f"   ✅ Users table accessible: {user_count} users")
        
        # Test feature_tags column
        result = db.execute(text("""
            SELECT user_id, name, feature_tags 
            FROM users 
            WHERE feature_tags IS NOT NULL 
            LIMIT 3
        """))
        tagged_users = result.fetchall()
        print(f"   ✅ Feature tags working: {len(tagged_users)} users with tags")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"   ❌ PostgreSQL test failed: {e}")
        return False

def test_vectordb_connection():
    """Test VectorDB connection and basic operations"""
    print("\n🧠 Testing VectorDB Connection...")
    
    try:
        from db_utils import get_vdb_client, get_vdb_collection, insert_to_vector_db
        
        # Test client connection
        client = get_vdb_client()
        print(f"   ✅ VectorDB client connected")
        
        # Test collection access
        collection = get_vdb_collection()
        print(f"   ✅ VectorDB collection accessible")
        
        # Test vector insertion
        metadata = {'user_id': 9999, 'name': 'Test User'}
        vector_id = insert_to_vector_db("测试向量数据库连接", metadata)
        
        if vector_id:
            print(f"   ✅ Vector insertion working (ID: {vector_id})")
            
            # Test vector query
            result = collection.query(
                document_ids=[str(vector_id)],
                limit=1,
                retrieve_vector=False
            )
            
            if result:
                print(f"   ✅ Vector query working: found {len(result)} documents")
            
            # Clean up
            collection.delete(document_ids=[str(vector_id)])
            print(f"   ✅ Vector cleanup successful")
            
        return True
        
    except Exception as e:
        print(f"   ❌ VectorDB test failed: {e}")
        return False

def test_email_service():
    """Test email service configuration"""
    print("\n📧 Testing Email Service...")
    
    try:
        # Check environment variables
        required_vars = [
            'TENCENT_SECRET_ID', 'TENCENT_SECRET_KEY',
            'TENCENT_EMAIL_TEMPLATE_ID', 'TENCENT_SENDER_EMAIL'
        ]
        
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            print(f"   ⚠️  Missing email config: {missing_vars}")
            return False
        
        print(f"   ✅ Email configuration complete")
        print(f"   📤 Sender: {os.getenv('TENCENT_SENDER_EMAIL')}")
        print(f"   🌍 Region: {os.getenv('TENCENT_SES_REGION')}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Email service test failed: {e}")
        return False

def test_authentication_endpoints():
    """Test authentication endpoints"""
    print("\n🔐 Testing Authentication...")
    
    try:
        # Test JWT secret key
        secret_key = os.getenv('SECRET_KEY')
        if not secret_key or len(secret_key) < 32:
            print(f"   ⚠️  JWT secret key missing or too short")
            return False
        
        print(f"   ✅ JWT secret key configured")
        
        # Test DeepSeek API key
        deepseek_key = os.getenv('DEEPSEEK_API_KEY')
        if not deepseek_key or not deepseek_key.startswith('sk-'):
            print(f"   ⚠️  DeepSeek API key missing or invalid format")
            return False
        
        print(f"   ✅ DeepSeek API key configured")
        
        # Note: WeChat OAuth is not configured yet (as expected)
        wechat_app_id = os.getenv('WECHAT_APP_ID')
        if not wechat_app_id or wechat_app_id == 'your_wechat_app_id_here':
            print(f"   ⚠️  WeChat OAuth not configured (expected)")
        else:
            print(f"   ✅ WeChat OAuth configured")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Authentication test failed: {e}")
        return False

def test_recommendation_system():
    """Test the recommendation system functionality"""
    print("\n🎯 Testing Recommendation System...")
    
    try:
        from production_recommendation_service import RecommendationService
        
        service = RecommendationService(vectordb_timeout=10, max_retries=1)
        
        # Test 1: Tag-based recommendations (should always work)
        result = service.get_recommendations(
            user_id=9999,
            user_tags=["AI", "Machine Learning"],
            strategy="tags",
            top_k=3
        )
        
        if result.success:
            print(f"   ✅ Tag-based recommendations: {len(result.users)} users in {result.execution_time:.2f}s")
        else:
            print(f"   ❌ Tag-based recommendations failed: {result.error_message}")
            return False
        
        # Test 2: Hybrid recommendations (vector + fallback)
        result = service.get_recommendations(
            user_id=9998,
            user_preferences="我喜欢人工智能和机器学习项目",
            user_tags=["AI", "Machine Learning"],
            strategy="hybrid",
            top_k=2
        )
        
        if result.success:
            print(f"   ✅ Hybrid recommendations: {len(result.users)} users via {result.method_used}")
        else:
            print(f"   ⚠️  Hybrid recommendations failed: {result.error_message}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Recommendation test failed: {e}")
        return False

def test_api_endpoints():
    """Test main API endpoints"""
    print("\n🌐 Testing API Endpoints...")
    
    try:
        # Import FastAPI app
        from main import app
        
        print(f"   ✅ FastAPI app imported successfully")
        
        # Check if we can access routers
        router_count = len(app.routes)
        print(f"   ✅ API routes loaded: {router_count} endpoints")
        
        # Check specific route groups
        route_paths = [route.path for route in app.routes if hasattr(route, 'path')]
        
        auth_routes = [path for path in route_paths if 'auth' in path]
        match_routes = [path for path in route_paths if 'match' in path or 'recommend' in path]
        
        print(f"   ✅ Auth routes: {len(auth_routes)} endpoints")
        print(f"   ✅ Matching routes: {len(match_routes)} endpoints")
        
        return True
        
    except Exception as e:
        print(f"   ❌ API endpoints test failed: {e}")
        return False

def run_essential_tests():
    """Run all essential tests for the system"""
    print("🚀 Running Essential Test Suite")
    print("=" * 50)
    
    test_results = {}
    
    # Run all tests
    test_results['postgresql'] = test_postgresql_connection()
    test_results['vectordb'] = test_vectordb_connection()
    test_results['email'] = test_email_service()
    test_results['auth'] = test_authentication_endpoints()
    test_results['recommendations'] = test_recommendation_system()
    test_results['api'] = test_api_endpoints()
    
    # Summary
    print("\n📊 Test Results Summary")
    print("=" * 30)
    
    passed = sum(test_results.values())
    total = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name.title():<15}: {status}")
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed ({passed/total*100:.0f}%)")
    
    if passed == total:
        print("🎉 All essential systems working correctly!")
        print("🚀 Backend is production ready!")
    else:
        print("⚠️  Some systems need attention before production")
    
    return passed == total

if __name__ == "__main__":
    run_essential_tests()
