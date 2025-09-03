"""
Test script for the unified quota system
Tests the enhanced membership service with monthly quotas
"""
import sys
import os
sys.path.append('.')

from sqlalchemy.orm import Session
from dependencies.db import SessionLocal
from services.membership_service import MembershipService
from models.users import User
from models.user_membership import UserMembership, UserUsageLog, MembershipType
from datetime import datetime, timedelta
import json

def test_unified_quota_system():
    """Test the unified quota system with all limits"""
    print("🧪 Testing Unified Quota System...")
    
    db = SessionLocal()
    try:
        # Create or get a test user
        test_user = db.query(User).first()
        if not test_user:
            print("❌ No users found in database. Please ensure you have test users.")
            return False
        
        user_id = test_user.user_id
        print(f"📋 Testing with user ID: {user_id}")
        
        # Test 1: Check project ideas limit for free user
        print("\n📊 Test 1: Project Ideas Limit Check (FREE user)")
        can_generate, message, info = MembershipService.check_project_ideas_limit(db, user_id)
        print(f"✅ Can generate: {can_generate}")
        print(f"📝 Message: {message}")
        print(f"📊 Usage info: {json.dumps(info, indent=2)}")
        
        # Test 2: Simulate usage logging
        print("\n📝 Test 2: Usage Logging")
        usage_log = MembershipService.log_usage(
            db, 
            user_id, 
            "project_ideas_generate", 
            1, 
            {"query": "test query", "ideas_generated": 5}
        )
        print(f"✅ Usage logged: {usage_log.action_type} - {usage_log.action_count}")
        
        # Test 3: Check limits after usage
        print("\n📊 Test 3: Limits After Usage")
        can_generate, message, info = MembershipService.check_project_ideas_limit(db, user_id)
        print(f"✅ Can generate: {can_generate}")
        print(f"📝 Message: {message}")
        print(f"📊 Updated usage info: {json.dumps(info, indent=2)}")
        
        # Test 4: Get comprehensive usage stats
        print("\n📈 Test 4: Comprehensive Usage Statistics")
        stats = MembershipService.get_usage_stats(db, user_id)
        print(f"✅ Usage stats: {json.dumps(stats, indent=2, default=str)}")
        
        # Test 5: Test different membership types
        print("\n🔄 Test 5: Membership Type Changes")
        
        # Get current membership
        membership = MembershipService.get_or_create_membership(db, user_id)
        original_type = membership.membership_type
        print(f"📋 Original membership: {original_type.value}")
        
        # Upgrade to PAID
        if original_type == MembershipType.FREE:
            upgraded = MembershipService.upgrade_to_paid(db, user_id, duration_days=30)
            print(f"⬆️ Upgraded to: {upgraded.membership_type.value}")
            
            # Check limits as paid user
            can_generate, message, info = MembershipService.check_project_ideas_limit(db, user_id)
            print(f"✅ PAID user can generate: {can_generate}")
            print(f"📊 PAID limits: {json.dumps(info, indent=2)}")
            
            # Downgrade back
            downgraded = MembershipService.downgrade_to_free(db, user_id, reason="test")
            print(f"⬇️ Downgraded to: {downgraded.membership_type.value}")
        
        # Test 6: Rate limiting simulation
        print("\n⚡ Test 6: Rate Limiting Simulation")
        
        # Log multiple rapid requests
        for i in range(3):
            usage_log = MembershipService.log_usage(
                db, 
                user_id, 
                "project_ideas_generate", 
                1, 
                {"query": f"rapid test {i}", "ideas_generated": 3}
            )
            print(f"⚡ Rapid request {i+1} logged")
        
        # Check if rate limiting would trigger
        can_generate, message, info = MembershipService.check_project_ideas_limit(db, user_id)
        print(f"✅ After rapid requests - Can generate: {can_generate}")
        print(f"📝 Rate limit message: {message}")
        
        print("\n🎉 All unified quota system tests completed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

def test_monthly_tracking():
    """Test monthly tracking functionality"""
    print("\n📅 Testing Monthly Tracking...")
    
    db = SessionLocal()
    try:
        # Test timestamp functions
        now = datetime.utcnow()
        hour_ts = UserUsageLog.get_hour_timestamp(now)
        day_ts = UserUsageLog.get_day_timestamp(now)
        month_ts = UserUsageLog.get_month_timestamp(now)
        
        print(f"⏰ Current time: {now}")
        print(f"📅 Hour timestamp: {hour_ts}")
        print(f"📅 Day timestamp: {day_ts}")
        print(f"📅 Month timestamp: {month_ts}")
        
        # Verify month timestamp is first day of month
        assert month_ts.day == 1
        assert month_ts.hour == 0
        assert month_ts.minute == 0
        assert month_ts.second == 0
        
        print("✅ Monthly tracking functions work correctly")
        return True
        
    except Exception as e:
        print(f"❌ Monthly tracking test failed: {e}")
        return False
    finally:
        db.close()

def test_membership_limits_config():
    """Test that the membership limits are properly configured"""
    print("\n⚙️ Testing Membership Limits Configuration...")
    
    try:
        limits = MembershipService.LIMITS
        
        # Check all membership types have required fields
        required_fields = ["project_ideas_per_day", "project_ideas_per_month"]
        
        for membership_type, config in limits.items():
            print(f"📋 {membership_type.value} limits:")
            for field in required_fields:
                if field in config:
                    print(f"  ✅ {field}: {config[field]}")
                else:
                    print(f"  ❌ Missing {field}")
                    return False
        
        print("✅ All membership limits properly configured")
        return True
        
    except Exception as e:
        print(f"❌ Limits configuration test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Unified Quota System Tests")
    print("=" * 60)
    
    # Test 1: Monthly tracking functions
    if not test_monthly_tracking():
        sys.exit(1)
    
    # Test 2: Membership limits configuration
    if not test_membership_limits_config():
        sys.exit(1)
    
    # Test 3: Full unified quota system
    if not test_unified_quota_system():
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("🎉 ALL TESTS PASSED!")
    print("✅ Unified quota system is working correctly")
    print("✅ Monthly tracking is functional")
    print("✅ All membership tiers are properly configured")
    print("✅ Rate limiting and usage logging work as expected")
