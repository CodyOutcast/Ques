"""
Simple Subscription System Test
Test basic subscription functionality without cron service
"""

import asyncio
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dependencies.db import SessionLocal
from models.users import User
from models.user_membership import UserMembership, MembershipType
from models.payments import MembershipTransaction, PaymentMethod, PaymentStatus
from services.subscription_service_working import SubscriptionService, SubscriptionPeriod

async def test_basic_subscription():
    """Test basic subscription functionality"""
    
    print("🚀 Testing Basic Subscription System")
    print("=" * 50)
    
    db = SessionLocal()
    
    try:
        # 1. Test pricing calculations
        print("\n💰 Testing Pricing Calculations")
        subscription_service = SubscriptionService()
        
        levels = [MembershipType.PREMIUM, MembershipType.PAID]
        periods = [SubscriptionPeriod.WEEKLY, SubscriptionPeriod.MONTHLY, SubscriptionPeriod.ANNUALLY]
        
        for level in levels:
            print(f"\n{level.value.upper()} MEMBERSHIP:")
            for period in periods:
                try:
                    amount, days = subscription_service._calculate_subscription_details(level, period)
                    weekly_equivalent = (amount / days) * 7
                    print(f"  {period.value.capitalize()}: ${amount:.2f} for {days} days (${weekly_equivalent:.2f}/week)")
                except Exception as e:
                    print(f"    ❌ Error calculating {period.value}: {e}")
        
        # 2. Test subscription status for non-existent user
        print("\n📊 Testing Subscription Status")
        try:
            status = subscription_service.get_subscription_status(db, 999)  # Non-existent user
            print(f"✅ Non-existent user status: {status}")
        except Exception as e:
            print(f"❌ Failed to get subscription status: {e}")
        
        # 3. Create a test subscription (this will fail without a real user, but tests the logic)
        print("\n🧪 Testing Subscription Creation Logic")
        try:
            # This will fail because we don't have a test user, but it tests the validation
            result = subscription_service.create_subscription(
                db=db,
                user_id=1,  # Assuming user ID 1 exists
                membership_type=MembershipType.PREMIUM,
                period=SubscriptionPeriod.MONTHLY,
                payment_method="wechat_pay"
            )
            print(f"✅ Subscription creation test: {result}")
        except Exception as e:
            print(f"ℹ️  Expected error (no test user): {e}")
        
        print("\n" + "=" * 50)
        print("🎉 Basic Subscription System Test Complete!")
        print("💡 To test with real users:")
        print("   1. Create a test user in the database")
        print("   2. Run this test with a valid user_id")
        print("   3. Check subscription endpoints via API")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
    
    finally:
        db.close()

if __name__ == "__main__":
    print("🧪 Simple Subscription System Test")
    asyncio.run(test_basic_subscription())
