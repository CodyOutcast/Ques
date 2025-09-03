#!/usr/bin/env python3
"""Test database connection and table existence"""

import os
import sys
from dependencies.db import engine, SessionLocal
from sqlalchemy import text
from models.user_membership import UserMembership
from models.payments import MembershipTransaction

def test_database_connection():
    """Test database connection and table existence"""
    
    print("🔍 Testing Database Connection")
    print("=" * 50)
    
    # Test basic connection
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ Database connection successful")
            print(f"   Database URL: {engine.url}")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False
    
    # Test if tables exist
    try:
        with SessionLocal() as session:
            # Check if user_memberships table exists
            try:
                result = session.execute(text("SELECT COUNT(*) FROM user_memberships"))
                count = result.scalar()
                print(f"✅ user_memberships table exists with {count} records")
            except Exception as e:
                print(f"❌ user_memberships table issue: {e}")
            
            # Check if membership_transactions table exists
            try:
                result = session.execute(text("SELECT COUNT(*) FROM membership_transactions"))
                count = result.scalar()
                print(f"✅ membership_transactions table exists with {count} records")
            except Exception as e:
                print(f"❌ membership_transactions table issue: {e}")
    
    except Exception as e:
        print(f"❌ Database session failed: {e}")
        return False
    
    print("\n🎯 Database Test Complete")
    return True

if __name__ == "__main__":
    test_database_connection()
