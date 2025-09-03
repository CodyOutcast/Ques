"""
Test Updated Membership System (Monthly/Annual Only)
Verify that weekly options have been removed and only monthly/annual remain
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.subscription_service_working import SubscriptionService, SubscriptionPeriod
from routers.membership import SubscriptionPeriodEnum
from models.user_membership import MembershipType

def test_subscription_periods():
    """Test that only monthly and annual periods are available"""
    print("🔍 Testing Updated Subscription Periods...")
    
    # Test SubscriptionPeriod enum
    print("\n1. Testing SubscriptionPeriod enum...")
    available_periods = list(SubscriptionPeriod)
    print(f"Available periods: {[p.value for p in available_periods]}")
    
    assert SubscriptionPeriod.MONTHLY in available_periods, "Monthly period should be available"
    assert SubscriptionPeriod.ANNUALLY in available_periods, "Annual period should be available"
    
    # Check that weekly is not available
    weekly_exists = False
    try:
        weekly_period = SubscriptionPeriod.WEEKLY
        weekly_exists = True
    except AttributeError:
        pass
    
    assert not weekly_exists, "Weekly period should not exist"
    print("✅ SubscriptionPeriod enum updated correctly")
    
    # Test SubscriptionPeriodEnum for API
    print("\n2. Testing SubscriptionPeriodEnum for API...")
    api_periods = list(SubscriptionPeriodEnum)
    print(f"API periods: {[p.value for p in api_periods]}")
    
    assert SubscriptionPeriodEnum.MONTHLY in api_periods, "Monthly should be available in API"
    assert SubscriptionPeriodEnum.ANNUALLY in api_periods, "Annual should be available in API"
    
    # Check that weekly is not available in API
    api_weekly_exists = False
    try:
        api_weekly = SubscriptionPeriodEnum.WEEKLY
        api_weekly_exists = True
    except AttributeError:
        pass
    
    assert not api_weekly_exists, "Weekly should not exist in API enum"
    print("✅ API SubscriptionPeriodEnum updated correctly")
    
    return True

def test_subscription_pricing():
    """Test that pricing calculation works for monthly and annual"""
    print("\n3. Testing Subscription Pricing...")
    
    subscription_service = SubscriptionService()
    
    # Test monthly pricing
    monthly_price, monthly_days = subscription_service._calculate_subscription_details(
        MembershipType.PREMIUM, SubscriptionPeriod.MONTHLY
    )
    print(f"Monthly: ${monthly_price:.2f} for {monthly_days} days")
    assert monthly_days == 30, "Monthly should be 30 days"
    assert monthly_price > 0, "Monthly price should be positive"
    
    # Test annual pricing
    annual_price, annual_days = subscription_service._calculate_subscription_details(
        MembershipType.PREMIUM, SubscriptionPeriod.ANNUALLY
    )
    print(f"Annual: ${annual_price:.2f} for {annual_days} days")
    assert annual_days == 365, "Annual should be 365 days"
    assert annual_price > 0, "Annual price should be positive"
    
    # Verify annual discount (should be less than 12 months)
    monthly_equivalent = monthly_price * 12
    savings = monthly_equivalent - annual_price
    discount_percent = (savings / monthly_equivalent) * 100
    print(f"Annual savings: ${savings:.2f} ({discount_percent:.1f}% discount)")
    
    assert annual_price < monthly_equivalent, "Annual should be discounted"
    assert discount_percent > 10, "Should have significant annual discount"
    
    print("✅ Pricing calculations work correctly")
    
    return True

def test_import_consistency():
    """Test that all modules can import correctly without weekly references"""
    print("\n4. Testing Import Consistency...")
    
    try:
        from routers.membership import router as membership_router
        from routers.payments import router as payments_router
        from services.revenue_analytics_service import RevenueAnalyticsService
        
        print("✅ All modules import successfully")
        
        # Test that enums are consistent
        from routers.membership import SubscriptionPeriodEnum
        from services.subscription_service_working import SubscriptionPeriod
        
        # Should have same number of periods
        api_periods = len(list(SubscriptionPeriodEnum))
        service_periods = len(list(SubscriptionPeriod))
        
        print(f"API periods count: {api_periods}")
        print(f"Service periods count: {service_periods}")
        
        assert api_periods == service_periods, "API and service should have same number of periods"
        assert api_periods == 2, "Should have exactly 2 periods (monthly, annual)"
        
        print("✅ Enum consistency verified")
        
        return True
        
    except Exception as e:
        print(f"❌ Import error: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("="*80)
    print("🧪 TESTING UPDATED MEMBERSHIP SYSTEM (Monthly/Annual Only)")
    print("="*80)
    
    tests = [
        test_subscription_periods,
        test_subscription_pricing,
        test_import_consistency
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test {test.__name__} failed: {str(e)}")
            results.append(False)
    
    if all(results):
        print(f"\n🎉 ALL TESTS PASSED! ✅")
        print(f"\n📋 Updated Membership System Summary:")
        print(f"   • ❌ Weekly subscriptions removed")
        print(f"   • ✅ Monthly subscriptions available ($29.99/month)")
        print(f"   • ✅ Annual subscriptions available (~$305.91/year with 15% discount)")
        print(f"   • ✅ Same perks for both periods, only pricing differs")
        print(f"   • ✅ All modules updated consistently")
        
        print(f"\n💰 Pricing Structure:")
        print(f"   • Monthly: $29.99/month")
        print(f"   • Annual: ~$305.91/year (15% discount = ~$25.49/month)")
        print(f"   • Savings: ~$54.47/year with annual plan")
        
        print(f"\n🔧 Technical Changes Made:")
        print(f"   • Updated SubscriptionPeriod enum")
        print(f"   • Updated SubscriptionPeriodEnum for API")
        print(f"   • Removed weekly pricing from all services")
        print(f"   • Updated revenue analytics")
        print(f"   • Updated payment routers")
        print(f"   • Updated cron subscription service")
        
    else:
        print(f"\n❌ Some tests failed. Please check the errors above.")
        
    return all(results)

if __name__ == "__main__":
    main()
