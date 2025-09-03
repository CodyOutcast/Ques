#!/usr/bin/env python3
"""Simple database connection test"""

import os
from dependencies.db import engine, SessionLocal
from sqlalchemy import text

def test_database():
    print("🔍 Testing Database Connection")
    print("=" * 50)
    
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ Database connection successful")
            print(f"   Database URL: {engine.url}")
            
            # Check if tables exist
            tables_to_check = ["user_memberships", "membership_transactions", "users"]
            for table in tables_to_check:
                try:
                    result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                    count = result.scalar()
                    print(f"✅ {table} table exists with {count} records")
                except Exception as e:
                    print(f"❌ {table} table issue: {e}")
    
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False
    
    print("\n🎯 Database Test Complete")
    return True

if __name__ == "__main__":
    test_database()
