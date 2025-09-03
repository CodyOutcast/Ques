"""
Test Subscription System
Run this to verify subscription creation and management works
"""

import asyncio
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models.users import User
from models.user_membership import UserMembership, MembershipType
from models.payments import MembershipTransaction, PaymentMethod, PaymentStatus
from services.subscription_service_working import SubscriptionService, SubscriptionPeriod
from services.cron_subscription_service import SubscriptionCronService

# Database setup
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./test.db')
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

async def test_subscription_system():
    """Test the complete subscription system"""
    
    print("🚀 Testing Subscription System")
    print("=" * 50)
    
    db = SessionLocal()
    
    try:
        # 1. Test subscription creation
        print("\n1. Testing Subscription Creation")
        subscription_service = SubscriptionService()
        
        # Create a test user if needed
        test_user = db.query(User).filter(User.phone_number == "test123").first()
        if not test_user:
            print("❌ No test user found. Please create a user first.")
            return
        
        user_id = test_user.user_id
        print(f"✅ Using test user ID: {user_id}")
        
        # Test weekly subscription
        try:
            result = subscription_service.create_subscription(
                db=db,
                user_id=user_id,
                membership_type=MembershipType.PREMIUM,
                period=SubscriptionPeriod.WEEKLY,
                payment_method="wechat_pay"
            )
            print(f"✅ Weekly subscription created: {result}")
        except Exception as e:
            print(f"❌ Failed to create weekly subscription: {e}")
        
        # 2. Test subscription status
        print("\n2. Testing Subscription Status")
        try:
            status = subscription_service.get_subscription_status(db, user_id)
            print(f"✅ Subscription status: {status}")
        except Exception as e:
            print(f"❌ Failed to get subscription status: {e}")
        
        # 3. Test pricing calculation
        print("\n3. Testing Pricing Calculation")
        try:
            # Test different periods
            periods = [SubscriptionPeriod.WEEKLY, SubscriptionPeriod.MONTHLY, SubscriptionPeriod.ANNUALLY]
            levels = [MembershipType.PREMIUM, MembershipType.PAID]
            
            for level in levels:
                print(f"\n{level.value.upper()} Pricing:")
                for period in periods:
                    amount, days = subscription_service._calculate_subscription_details(level, period)
                    print(f"  {period.value}: ${amount:.2f} for {days} days")
        except Exception as e:
            print(f"❌ Failed to calculate pricing: {e}")
        
        # 4. Test cron service
        print("\n4. Testing Cron Renewal Service")
        try:
            cron_service = SubscriptionCronService()
            results = await cron_service.run_daily_subscription_check()
            print(f"✅ Cron service results: {results}")
        except Exception as e:
            print(f"❌ Failed to run cron service: {e}")
        
        # 5. Test subscription management
        print("\n5. Testing Subscription Management")
        
        # Test pause
        try:
            pause_result = subscription_service.pause_subscription(
                db=db,
                user_id=user_id,
                pause_until=None
            )
            print(f"✅ Subscription paused: {pause_result}")
        except Exception as e:
            print(f"❌ Failed to pause subscription: {e}")
        
        # Test cancel
        try:
            cancel_result = subscription_service.cancel_subscription(
                db=db,
                user_id=user_id,
                immediate=False
            )
            print(f"✅ Subscription cancelled: {cancel_result}")
        except Exception as e:
            print(f"❌ Failed to cancel subscription: {e}")
        
        print("\n" + "=" * 50)
        print("🎉 Subscription System Test Complete!")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
    
    finally:
        db.close()

async def test_payment_amounts():
    """Test payment amount calculations"""
    
    print("\n💰 Testing Payment Amount Calculations")
    print("=" * 50)
    
    service = SubscriptionService()
    
    # Test all combinations
    levels = [MembershipType.PREMIUM, MembershipType.PAID]
    periods = [SubscriptionPeriod.WEEKLY, SubscriptionPeriod.MONTHLY, SubscriptionPeriod.ANNUALLY]
    
    for level in levels:
        print(f"\n{level.value.upper()} MEMBERSHIP:")
        for period in periods:
            try:
                amount, days = service._calculate_subscription_details(level, period)
                weekly_equivalent = (amount / days) * 7
                monthly_equivalent = (amount / days) * 30
                annual_equivalent = (amount / days) * 365
                
                print(f"  {period.value.capitalize()}:")
                print(f"    Price: ${amount:.2f}")
                print(f"    Duration: {days} days")
                print(f"    Weekly equivalent: ${weekly_equivalent:.2f}")
                print(f"    Monthly equivalent: ${monthly_equivalent:.2f}")
                print(f"    Annual equivalent: ${annual_equivalent:.2f}")
                
                if period == SubscriptionPeriod.ANNUALLY:
                    monthly_total = service._calculate_subscription_details(level, SubscriptionPeriod.MONTHLY)[0] * 12
                    savings = monthly_total - amount
                    savings_percent = (savings / monthly_total) * 100
                    print(f"    Annual savings: ${savings:.2f} ({savings_percent:.1f}%)")
                
            except Exception as e:
                print(f"    ❌ Error calculating {period.value}: {e}")

if __name__ == "__main__":
    print("🧪 Subscription System Test Suite")
    
    # Run payment calculation test first
    asyncio.run(test_payment_amounts())
    
    # Run full system test
    asyncio.run(test_subscription_system())
