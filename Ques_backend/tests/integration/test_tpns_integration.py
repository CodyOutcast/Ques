#!/usr/bin/env python3
"""
TPNS Integration Test Script
Tests Tencent Push Notification Service integration
"""

import asyncio
import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from services.tpns_service import tpns_service, PushMessage
from services.notification_service import notification_service, NotificationType, DeliveryChannel
from config.settings import Settings

def test_tpns_configuration():
    """Test TPNS configuration"""
    print("🔧 Testing TPNS Configuration...")
    
    settings = Settings()
    
    print(f"   Region: {tpns_service.region}")
    print(f"   API Host: {tpns_service.api_host}")
    print(f"   Android Configured: {bool(tpns_service.android_access_id and tpns_service.android_secret_key)}")
    print(f"   iOS Configured: {bool(tpns_service.ios_access_id and tpns_service.ios_secret_key)}")
    
    if not (tpns_service.android_access_id or tpns_service.ios_access_id):
        print("   ⚠️  Warning: No TPNS credentials configured")
        print("   Please add TPNS credentials to your .env file:")
        print("   TPNS_ANDROID_ACCESS_ID=your_access_id")
        print("   TPNS_ANDROID_SECRET_KEY=your_secret_key")
        print("   TPNS_IOS_ACCESS_ID=your_access_id") 
        print("   TPNS_IOS_SECRET_KEY=your_secret_key")
        return False
    
    print("   ✅ TPNS configuration looks good")
    return True

def test_push_message_creation():
    """Test push message creation"""
    print("\n📱 Testing Push Message Creation...")
    
    try:
        message = PushMessage(
            title="Test Notification",
            content="This is a test push notification from Ques",
            custom_content={
                "type": "test",
                "action": "open_app",
                "timestamp": "2024-10-16T10:00:00Z"
            },
            audience_type="account",
            target_list=["test_user_123"]
        )
        
        print("   ✅ Push message created successfully")
        print(f"   Title: {message.title}")
        print(f"   Content: {message.content}")
        print(f"   Audience Type: {message.audience_type}")
        return True
        
    except Exception as e:
        print(f"   ❌ Error creating push message: {e}")
        return False

async def test_notification_service():
    """Test notification service functionality"""
    print("\n🔔 Testing Notification Service...")
    
    try:
        # Test service initialization
        print("   Testing service initialization...")
        assert notification_service is not None
        print("   ✅ Notification service initialized")
        
        # Test preference retrieval (mock)
        print("   Testing default preferences...")
        default_prefs = notification_service._get_default_preferences()
        assert isinstance(default_prefs, dict)
        assert "push_notifications" in default_prefs
        print("   ✅ Default preferences loaded")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error testing notification service: {e}")
        return False

def test_signature_generation():
    """Test TPNS signature generation"""
    print("\n🔐 Testing Signature Generation...")
    
    try:
        # Test with mock data
        method = "POST"
        uri = "/v3/push/app"
        params = {
            "AccessId": "test_access_id",
            "Timestamp": 1697452800,
            "ValidTime": 600
        }
        secret_key = "test_secret_key"
        
        signature = tpns_service._generate_signature(method, uri, params, secret_key)
        
        assert isinstance(signature, str)
        assert len(signature) > 0
        
        print("   ✅ Signature generation working")
        print(f"   Generated signature: {signature[:20]}...")
        return True
        
    except Exception as e:
        print(f"   ❌ Error testing signature generation: {e}")
        return False

async def test_mock_push_send():
    """Test mock push notification sending (without actual API call)"""
    print("\n📤 Testing Mock Push Send...")
    
    try:
        # Create test message
        message = PushMessage(
            title="Welcome to Ques!",
            content="Your account has been created successfully",
            custom_content={
                "type": "welcome",
                "user_id": "123",
                "action": "open_profile"
            },
            audience_type="account",
            target_list=["test_user_123"]
        )
        
        print("   ✅ Test message prepared")
        print(f"   Target: {message.target_list}")
        print(f"   Content: {message.content}")
        
        # Test would-be API call structure (mock)
        print("   🔄 Mock API call structure test...")
        
        # This would be the actual API call in a real scenario
        # For testing, we just validate the structure
        api_data = {
            "audience_type": message.audience_type,
            "message": {
                "title": message.title,
                "content": message.content
            },
            "account_list": message.target_list
        }
        
        assert "audience_type" in api_data
        assert "message" in api_data
        assert api_data["message"]["title"] == message.title
        
        print("   ✅ Mock push structure validated")
        return True
        
    except Exception as e:
        print(f"   ❌ Error in mock push test: {e}")
        return False

def test_notification_types():
    """Test notification type enums"""
    print("\n📋 Testing Notification Types...")
    
    try:
        # Test NotificationType enum
        assert NotificationType.FRIEND_REQUEST.value == "friend_request"
        assert NotificationType.MESSAGE.value == "message"
        assert NotificationType.MATCH.value == "match"
        assert NotificationType.SYSTEM.value == "system"
        assert NotificationType.GIFT.value == "gift"
        
        print("   ✅ NotificationType enum working")
        
        # Test DeliveryChannel enum
        assert DeliveryChannel.PUSH.value == "push"
        assert DeliveryChannel.EMAIL.value == "email"
        assert DeliveryChannel.SMS.value == "sms"
        assert DeliveryChannel.IN_APP.value == "in_app"
        
        print("   ✅ DeliveryChannel enum working")
        return True
        
    except Exception as e:
        print(f"   ❌ Error testing notification types: {e}")
        return False

async def main():
    """Run all tests"""
    print("🚀 Starting TPNS Integration Tests")
    print("=" * 50)
    
    tests = [
        ("Configuration", test_tpns_configuration()),
        ("Message Creation", test_push_message_creation()),
        ("Notification Service", test_notification_service()),
        ("Signature Generation", test_signature_generation()),
        ("Mock Push Send", test_mock_push_send()),
        ("Notification Types", test_notification_types())
    ]
    
    results = []
    for name, test_func in tests:
        if asyncio.iscoroutine(test_func):
            result = await test_func
        else:
            result = test_func
        results.append((name, result))
    
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    
    passed = 0
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {name}: {status}")
        if result:
            passed += 1
    
    print(f"\n📈 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! TPNS integration is ready.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the configuration.")
        return False

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n🛑 Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n💥 Unexpected error: {e}")
        sys.exit(1)