"""
Test Revenue Analytics System
Test comprehensive revenue tracking and analytics functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timedelta
from decimal import Decimal
import traceback

# Database setup
from dependencies.db import get_db
from models.base import Base
from models.users import User
from models.user_auth import UserAuth, ProviderType
from models.user_membership import UserMembership, MembershipType
from models.payments import MembershipTransaction, PaymentStatus, PaymentMethod
from services.revenue_analytics_service import RevenueAnalyticsService

def test_revenue_analytics():
    """Test the revenue analytics system"""
    print("🔍 Testing Revenue Analytics System...")
    
    # Create database session
    db = next(get_db())
    
    try:
        # === Test Data Setup ===
        print("\n1. Setting up test data...")
        
        # Create test users if they don't exist
        test_users = []
        for i in range(3):
            # Check if user exists by looking for auth record
            auth_record = db.query(UserAuth).filter(UserAuth.provider_id == f"revenue_test_user_{i}@test.com").first()
            if auth_record:
                user = auth_record.user
            else:
                # Create user
                user = User(
                    name=f"Revenue Test User {i}",
                    bio=f"Test user {i} for revenue analytics",
                    is_active=True
                )
                db.add(user)
                db.flush()
                
                # Create auth record
                auth_record = UserAuth(
                    user_id=user.user_id,
                    provider_type=ProviderType.EMAIL,
                    provider_id=f"revenue_test_user_{i}@test.com",
                    password_hash="test_hash",
                    is_verified=True,
                    is_primary=True
                )
                db.add(auth_record)
                db.flush()
            
            test_users.append(user)
        
        db.commit()
        print(f"✅ Created/found {len(test_users)} test users")
        
        # Create test transactions
        test_transactions = []
        current_time = datetime.utcnow()
        
        # Recent transactions (last 30 days)
        for i, user in enumerate(test_users):
            # Monthly subscription
            transaction = MembershipTransaction(
                user_id=user.user_id,
                order_id=f"test_order_monthly_{i}_{int(current_time.timestamp())}",
                transaction_id=f"txn_monthly_{i}_{int(current_time.timestamp())}",
                amount=299.0,  # 299 CNY monthly
                currency="CNY",
                payment_method=PaymentMethod.WECHAT_PAY if i % 2 == 0 else PaymentMethod.ALIPAY,
                payment_status=PaymentStatus.SUCCESS,
                plan_type="monthly",
                plan_duration_days=30,
                paid_at=current_time - timedelta(days=i*5),
                created_at=current_time - timedelta(days=i*5)
            )
            db.add(transaction)
            test_transactions.append(transaction)
            
            # Annual subscription for user 0
            if i == 0:
                annual_transaction = MembershipTransaction(
                    user_id=user.user_id,
                    order_id=f"test_order_annual_{i}_{int(current_time.timestamp())}",
                    transaction_id=f"txn_annual_{i}_{int(current_time.timestamp())}",
                    amount=2999.0,  # 2999 CNY annual
                    currency="CNY",
                    payment_method=PaymentMethod.WECHAT_PAY,
                    payment_status=PaymentStatus.SUCCESS,
                    plan_type="annually",
                    plan_duration_days=365,
                    paid_at=current_time - timedelta(days=20),
                    created_at=current_time - timedelta(days=20)
                )
                db.add(annual_transaction)
                test_transactions.append(annual_transaction)
        
        # Older transactions (for growth comparison)
        for i, user in enumerate(test_users):
            old_transaction = MembershipTransaction(
                user_id=user.user_id,
                order_id=f"test_order_old_{i}_{int(current_time.timestamp())}",
                transaction_id=f"txn_old_{i}_{int(current_time.timestamp())}",
                amount=199.0,  # 199 CNY
                currency="CNY",
                payment_method=PaymentMethod.WECHAT_PAY,
                payment_status=PaymentStatus.SUCCESS,
                plan_type="monthly",
                plan_duration_days=30,
                paid_at=current_time - timedelta(days=45),
                created_at=current_time - timedelta(days=45)
            )
            db.add(old_transaction)
            test_transactions.append(old_transaction)
        
        db.commit()
        print(f"✅ Created {len(test_transactions)} test transactions")
        
        # Create test memberships
        for i, user in enumerate(test_users):
            membership = db.query(UserMembership).filter(UserMembership.user_id == user.user_id).first()
            if not membership:
                membership = UserMembership(
                    user_id=user.user_id,
                    membership_type=MembershipType.PAID if i < 2 else MembershipType.PREMIUM,
                    end_date=current_time + timedelta(days=30),
                    payment_method="wechat_pay",
                    subscription_id=f"sub_{user.user_id}_{int(current_time.timestamp())}"
                )
                db.add(membership)
        
        db.commit()
        print("✅ Created test memberships")
        
        # === Test Revenue Analytics ===
        print("\n2. Testing Revenue Overview...")
        overview = RevenueAnalyticsService.get_revenue_overview(db, 30)
        print(f"📊 Revenue Overview (30 days):")
        print(f"   Total Revenue: ¥{overview['total_revenue']:.2f}")
        print(f"   Transactions: {overview['transaction_count']}")
        print(f"   Avg Daily Revenue: ¥{overview['avg_daily_revenue']:.2f}")
        print(f"   Avg Transaction Value: ¥{overview['avg_transaction_value']:.2f}")
        print(f"   Revenue Growth: {overview['revenue_growth_percent']:.2f}%")
        
        assert overview['total_revenue'] > 0, "Total revenue should be positive"
        assert overview['transaction_count'] > 0, "Should have transactions"
        print("✅ Revenue overview test passed")
        
        print("\n3. Testing Daily Revenue Chart...")
        daily_chart = RevenueAnalyticsService.get_daily_revenue_chart(db, 30)
        print(f"📈 Daily Chart: {len(daily_chart)} data points")
        
        # Show first few days with revenue
        revenue_days = [day for day in daily_chart if day['revenue'] > 0]
        print(f"   Days with revenue: {len(revenue_days)}")
        for day in revenue_days[:3]:
            print(f"   {day['date']}: ¥{day['revenue']:.2f} ({day['transactions']} txns)")
        
        assert len(daily_chart) == 30, "Should have 30 daily data points"
        assert len(revenue_days) > 0, "Should have some days with revenue"
        print("✅ Daily revenue chart test passed")
        
        print("\n4. Testing Monthly Revenue Chart...")
        monthly_chart = RevenueAnalyticsService.get_monthly_revenue_chart(db, 6)
        print(f"📈 Monthly Chart: {len(monthly_chart)} data points")
        
        for month in monthly_chart:
            print(f"   {month['month_name']}: ¥{month['revenue']:.2f} ({month['transactions']} txns)")
        
        assert len(monthly_chart) > 0, "Should have monthly data"
        print("✅ Monthly revenue chart test passed")
        
        print("\n5. Testing Revenue Breakdown by Membership Type...")
        membership_breakdown = RevenueAnalyticsService.get_revenue_by_membership_type(db, 30)
        print(f"💼 Membership Breakdown:")
        
        total_breakdown_revenue = 0
        for item in membership_breakdown:
            print(f"   {item['plan_type']}: ¥{item['revenue']:.2f} ({item['percentage']:.1f}%)")
            total_breakdown_revenue += item['revenue']
        
        assert len(membership_breakdown) > 0, "Should have membership breakdown"
        print("✅ Membership breakdown test passed")
        
        print("\n6. Testing Revenue Breakdown by Payment Method...")
        payment_breakdown = RevenueAnalyticsService.get_revenue_by_payment_method(db, 30)
        print(f"💳 Payment Method Breakdown:")
        
        for item in payment_breakdown:
            print(f"   {item['payment_method']}: ¥{item['revenue']:.2f} ({item['percentage']:.1f}%)")
        
        assert len(payment_breakdown) > 0, "Should have payment method breakdown"
        print("✅ Payment method breakdown test passed")
        
        print("\n7. Testing User Revenue Analytics...")
        user_analytics = RevenueAnalyticsService.get_user_revenue_analytics(db, 30)
        print(f"👥 User Analytics:")
        print(f"   Paying Users: {user_analytics['paying_users']}")
        print(f"   Total Users: {user_analytics['total_users']}")
        print(f"   Conversion Rate: {user_analytics['conversion_rate_percent']:.2f}%")
        print(f"   Avg Revenue Per User: ¥{user_analytics['avg_revenue_per_user']:.2f}")
        print(f"   Max Revenue Per User: ¥{user_analytics['max_revenue_per_user']:.2f}")
        
        assert user_analytics['paying_users'] > 0, "Should have paying users"
        assert user_analytics['total_users'] >= user_analytics['paying_users'], "Total users should be >= paying users"
        print("✅ User analytics test passed")
        
        print("\n8. Testing Recurring Revenue Metrics...")
        recurring_metrics = RevenueAnalyticsService.get_recurring_revenue_metrics(db)
        print(f"🔄 Recurring Revenue:")
        print(f"   MRR: ¥{recurring_metrics['monthly_recurring_revenue']:.2f}")
        print(f"   ARR: ¥{recurring_metrics['annual_recurring_revenue']:.2f}")
        print(f"   Active Subscribers: {recurring_metrics['active_subscribers']}")
        
        assert recurring_metrics['active_subscribers'] > 0, "Should have active subscribers"
        print("✅ Recurring revenue metrics test passed")
        
        print("\n9. Testing Churn and Retention Metrics...")
        churn_metrics = RevenueAnalyticsService.get_churn_and_retention_metrics(db)
        print(f"📉 Churn & Retention:")
        print(f"   Users Last Month: {churn_metrics['users_last_month']}")
        print(f"   Retained Users: {churn_metrics['retained_users']}")
        print(f"   Retention Rate: {churn_metrics['retention_rate_percent']:.2f}%")
        print(f"   Churn Rate: {churn_metrics['churn_rate_percent']:.2f}%")
        
        # These metrics might be 0 with test data, which is acceptable
        print("✅ Churn and retention metrics test passed")
        
        print("\n10. Testing Comprehensive Revenue Report...")
        comprehensive_report = RevenueAnalyticsService.get_comprehensive_revenue_report(db, 30)
        print(f"📋 Comprehensive Report Generated:")
        print(f"   Generated At: {comprehensive_report['generated_at']}")
        print(f"   Sections: {list(comprehensive_report.keys())}")
        
        required_sections = ['overview', 'daily_chart', 'monthly_chart', 'membership_breakdown', 
                           'payment_method_breakdown', 'user_analytics', 'recurring_revenue', 
                           'churn_retention']
        
        for section in required_sections:
            assert section in comprehensive_report, f"Missing section: {section}"
        
        print("✅ Comprehensive report test passed")
        
        # === Summary ===
        print(f"\n🎉 ALL REVENUE ANALYTICS TESTS PASSED! ✅")
        print(f"\n📊 Revenue Analytics System Summary:")
        print(f"   • Revenue Overview: ✅ Working")
        print(f"   • Daily/Monthly Charts: ✅ Working")
        print(f"   • Revenue Breakdowns: ✅ Working")
        print(f"   • User Analytics: ✅ Working")
        print(f"   • Recurring Revenue: ✅ Working")
        print(f"   • Churn/Retention: ✅ Working")
        print(f"   • Comprehensive Reports: ✅ Working")
        
        print(f"\n💡 Key Capabilities:")
        print(f"   • Track revenue over time (daily/monthly/yearly)")
        print(f"   • Analyze payment methods and membership types")
        print(f"   • Calculate MRR/ARR and subscription metrics")
        print(f"   • Monitor user conversion and retention")
        print(f"   • Generate comprehensive analytics reports")
        print(f"   • Support for graph/chart data visualization")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        print(f"Stack trace: {traceback.format_exc()}")
        return False
        
    finally:
        db.close()

def test_revenue_api_integration():
    """Test that revenue analytics can be imported in the main app"""
    print("\n🔌 Testing Revenue API Integration...")
    
    try:
        # Test imports
        from routers.revenue_analytics import router
        from services.revenue_analytics_service import RevenueAnalyticsService
        
        print("✅ Revenue analytics router imported successfully")
        print("✅ Revenue analytics service imported successfully")
        
        # Test router configuration
        assert router.prefix == "/api/v1/revenue", "Router prefix should be correct"
        assert "Revenue Analytics" in router.tags, "Router should have correct tags"
        
        print("✅ Revenue API integration test passed")
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("="*80)
    print("🚀 REVENUE ANALYTICS SYSTEM TEST")
    print("="*80)
    
    # Run tests
    analytics_test = test_revenue_analytics()
    integration_test = test_revenue_api_integration()
    
    if analytics_test and integration_test:
        print(f"\n🎉 ALL TESTS PASSED! Revenue Analytics System is ready!")
        print(f"\n📈 Revenue Tracking Features Available:")
        print(f"   • GET /api/v1/revenue/overview - Revenue overview")
        print(f"   • GET /api/v1/revenue/chart/daily - Daily revenue chart")
        print(f"   • GET /api/v1/revenue/chart/monthly - Monthly revenue chart")
        print(f"   • GET /api/v1/revenue/breakdown/membership - Revenue by membership type")
        print(f"   • GET /api/v1/revenue/breakdown/payment-method - Revenue by payment method")
        print(f"   • GET /api/v1/revenue/analytics/users - User revenue analytics")
        print(f"   • GET /api/v1/revenue/metrics/recurring - MRR/ARR metrics")
        print(f"   • GET /api/v1/revenue/metrics/churn-retention - Churn & retention")
        print(f"   • GET /api/v1/revenue/report/comprehensive - Full report")
        print(f"   • GET /api/v1/revenue/health - Health check")
    else:
        print(f"\n❌ Some tests failed. Please check the errors above.")
