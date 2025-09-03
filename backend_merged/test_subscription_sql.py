#!/usr/bin/env python3
"""
Simple subscription test using direct SQL queries
"""

from dependencies.db import SessionLocal
from sqlalchemy import text

def test_subscription_sql():
    print("🧪 Direct SQL Subscription Test")
    print("=" * 40)
    
    with SessionLocal() as db:
        # Get a test user
        result = db.execute(text("SELECT user_id, name FROM users LIMIT 1"))
        user = result.fetchone()
        
        if not user:
            print("❌ No users found")
            return
        
        user_id, name = user
        print(f"✅ Found user: {name} (ID: {user_id})")
        
        # Check current membership
        result = db.execute(text("""
            SELECT membership_type, is_active, start_date, end_date, 
                   CASE 
                       WHEN membership_type = 'FREE' THEN false
                       WHEN end_date IS NULL THEN true
                       WHEN is_active = true AND end_date > NOW() THEN true
                       ELSE false
                   END as is_paid
            FROM user_memberships 
            WHERE user_id = :user_id
        """), {"user_id": user_id})
        
        membership = result.fetchone()
        
        if membership:
            print(f"✅ Current membership:")
            print(f"   Type: {membership[0]}")
            print(f"   Active: {membership[1]}")
            print(f"   Start: {membership[2]}")
            print(f"   End: {membership[3]}")
            print(f"   Is Paid: {membership[4]}")
        else:
            print("ℹ️  No membership record found")
            
            # Create a premium membership
            print("🔧 Creating premium membership...")
            
            db.execute(text("""
                INSERT INTO user_memberships 
                (user_id, membership_type, is_active, start_date, end_date, auto_renew, payment_method)
                VALUES (:user_id, 'PREMIUM', true, NOW(), NOW() + INTERVAL '30 days', true, 'wechat_pay')
            """), {"user_id": user_id})
            
            db.commit()
            print("✅ Premium membership created!")
            
            # Check the result
            result = db.execute(text("""
                SELECT membership_type, 
                       CASE 
                           WHEN membership_type = 'FREE' THEN false
                           WHEN end_date IS NULL THEN true
                           WHEN is_active = true AND end_date > NOW() THEN true
                           ELSE false
                       END as is_paid,
                       EXTRACT(DAYS FROM (end_date - NOW())) as days_remaining
                FROM user_memberships 
                WHERE user_id = :user_id
            """), {"user_id": user_id})
            
            new_membership = result.fetchone()
            if new_membership:
                print(f"   Type: {new_membership[0]}")
                print(f"   Is Paid: {new_membership[1]}")
                print(f"   Days Remaining: {int(new_membership[2])}")

if __name__ == "__main__":
    test_subscription_sql()
