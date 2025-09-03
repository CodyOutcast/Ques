#!/usr/bin/env python3
"""
Minimal subscription test
"""

from dependencies.db import SessionLocal
from models.user_membership import UserMembership, MembershipType
from models.users import User
from datetime import datetime, timedelta

def test_minimal_subscription():
    print("🧪 Minimal Subscription Test")
    print("=" * 40)
    
    with SessionLocal() as db:
        # Check if we have a test user
        test_user = db.query(User).first()
        if not test_user:
            print("❌ No users found in database")
            return
        
        print(f"✅ Found test user: {test_user.user_id}")
        
        # Check current membership
        membership = db.query(UserMembership).filter(
            UserMembership.user_id == test_user.user_id
        ).first()
        
        if membership:
            print(f"✅ User has membership: {membership.membership_type.value}")
            print(f"   Is paid: {membership.is_paid}")
            print(f"   End date: {membership.end_date}")
        else:
            print("ℹ️  User has no membership record")
            
            # Create a test subscription
            print("🔧 Creating test premium membership...")
            
            new_membership = UserMembership(
                user_id=test_user.user_id,
                membership_type=MembershipType.PREMIUM,
                start_date=datetime.utcnow(),
                end_date=datetime.utcnow() + timedelta(days=30),
                auto_renew=True,
                payment_method="wechat_pay"
            )
            
            db.add(new_membership)
            db.commit()
            db.refresh(new_membership)
            
            print(f"✅ Created premium membership")
            print(f"   Type: {new_membership.membership_type.value}")
            print(f"   Is paid: {new_membership.is_paid}")
            print(f"   Days remaining: {new_membership.days_remaining}")

if __name__ == "__main__":
    test_minimal_subscription()
