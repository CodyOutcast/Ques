#!/usr/bin/env python3
"""
Test subscription pricing logic
"""

import sys
from enum import Enum
from datetime import datetime, timedelta
from decimal import Decimal

class SubscriptionPeriod(Enum):
    """Subscription period enumeration"""
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    ANNUAL = "annual"

class MembershipType(Enum):
    """Membership type enumeration"""
    FREE = "FREE"
    PAID = "PAID"
    PREMIUM = "PREMIUM"

class SubscriptionPricing:
    """Handle subscription pricing calculations"""
    
    # Base prices in USD (could be made configurable)
    PRICING = {
        MembershipType.PREMIUM: {
            SubscriptionPeriod.WEEKLY: Decimal("7.50"),
            SubscriptionPeriod.MONTHLY: Decimal("29.99"),
            SubscriptionPeriod.ANNUAL: Decimal("305.90")  # ~15% discount
        },
        MembershipType.PAID: {
            SubscriptionPeriod.WEEKLY: Decimal("7.50"),
            SubscriptionPeriod.MONTHLY: Decimal("29.99"),
            SubscriptionPeriod.ANNUAL: Decimal("305.90")
        }
    }
    
    PERIOD_DAYS = {
        SubscriptionPeriod.WEEKLY: 7,
        SubscriptionPeriod.MONTHLY: 30,
        SubscriptionPeriod.ANNUAL: 365
    }
    
    @classmethod
    def get_subscription_amount(
        cls, 
        membership_type: MembershipType, 
        period: SubscriptionPeriod
    ) -> Decimal:
        """Get subscription amount for given membership type and period"""
        return cls.PRICING.get(membership_type, {}).get(period, Decimal("0"))
    
    @classmethod
    def get_subscription_duration(cls, period: SubscriptionPeriod) -> int:
        """Get subscription duration in days"""
        return cls.PERIOD_DAYS.get(period, 0)
    
    @classmethod
    def calculate_end_date(
        cls, 
        start_date: datetime, 
        period: SubscriptionPeriod
    ) -> datetime:
        """Calculate subscription end date"""
        days = cls.get_subscription_duration(period)
        return start_date + timedelta(days=days)

def test_pricing():
    print("🧪 Subscription Pricing Test")
    print("=" * 40)
    
    membership_types = [MembershipType.PREMIUM, MembershipType.PAID]
    periods = [SubscriptionPeriod.WEEKLY, SubscriptionPeriod.MONTHLY, SubscriptionPeriod.ANNUAL]
    
    for membership_type in membership_types:
        print(f"\n{membership_type.value} MEMBERSHIP:")
        
        for period in periods:
            amount = SubscriptionPricing.get_subscription_amount(membership_type, period)
            days = SubscriptionPricing.get_subscription_duration(period)
            weekly_rate = (amount / days) * 7
            
            print(f"  {period.value.title()}: ${amount} for {days} days (${weekly_rate:.2f}/week)")
    
    print(f"\n🧪 Testing Date Calculations")
    start_date = datetime.utcnow()
    
    for period in periods:
        end_date = SubscriptionPricing.calculate_end_date(start_date, period)
        duration = (end_date - start_date).days
        print(f"  {period.value.title()}: {duration} days ({start_date.strftime('%Y-%m-%d')} → {end_date.strftime('%Y-%m-%d')})")
    
    print(f"\n✅ Pricing System Test Complete!")

if __name__ == "__main__":
    test_pricing()
