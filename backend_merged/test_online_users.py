"""
Test script for concurrent user tracking system
"""
import sys
import os
sys.path.append('.')

from sqlalchemy.orm import Session
from dependencies.db import SessionLocal
from services.online_users_service import OnlineUsersService
from models.users import User
from models.user_auth import UserSession
from datetime import datetime, timedelta
import json

def test_online_users_service():
    """Test the online users service functionality"""
    print("🧪 Testing Online Users Service...")
    
    db = SessionLocal()
    try:
        # Test 1: Get online user count
        print("\n📊 Testing get_online_user_count...")
        count = OnlineUsersService.get_online_user_count(db)
        print(f"✅ Online user count: {count}")
        
        # Test 2: Get online user stats
        print("\n📈 Testing get_online_stats...")
        stats = OnlineUsersService.get_online_stats(db)
        print(f"✅ Online stats: {json.dumps(stats, indent=2, default=str)}")
        
        # Test 3: Get online users list
        print("\n👥 Testing get_online_users...")
        users = OnlineUsersService.get_online_users(db, limit=10)
        print(f"✅ Online users: {len(users)} users found")
        
        # Test 4: Test cleanup function
        print("\n🧹 Testing cleanup_expired_sessions...")
        cleanup_result = OnlineUsersService.cleanup_expired_sessions(db)
        print(f"✅ Cleanup result: {cleanup_result}")
        
        print("\n🎉 All tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

def test_database_connection():
    """Test database connection"""
    print("🔗 Testing database connection...")
    
    try:
        db = SessionLocal()
        
        # Test basic query
        user_count = db.query(User).count()
        print(f"✅ Database connected. Total users: {user_count}")
        
        # Test UserSession model
        session_count = db.query(UserSession).count()
        print(f"✅ UserSession table accessible. Total sessions: {session_count}")
        
        db.close()
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🚀 Starting Concurrent User Tracking Tests")
    print("=" * 50)
    
    # Test database first
    test_database_connection()
    
    print("\n" + "=" * 50)
    
    # Test online users service
    test_online_users_service()
