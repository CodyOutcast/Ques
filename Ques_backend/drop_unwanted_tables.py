#!/usr/bin/env python3
"""
Drop unwanted tables from database
Based on DATABASE_SCHEMA_COMPLETE.md - only keep the 13 tables that should exist
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from dependencies.db import engine

# Tables that should exist according to DATABASE_SCHEMA_COMPLETE.md
KEEP_TABLES = {
    'cities',
    'institutions', 
    'memberships',
    'provinces',
    'user_institutions',
    'user_profiles',
    'user_projects', 
    'user_quotas',
    'user_reports',
    'user_swipes',
    'users',
    'verification_codes',
    'whispers'
}

# Tables to drop (from our database check)
DROP_TABLES = [
    'user_agent_card_preferences',
    'project_card_slots', 
    'payment_refunds',
    'payment_webhook_logs',
    'membership_transactions',
    'user_memberships',
    'messages',
    'matches',
    'chat_messages',
    'chats',
    'ai_recommendation_swipes',
    'agent_cards',
    'agent_card_swipes',
    'agent_card_likes',
    'agent_card_history',
    'casual_requests',
    'user_usage_logs',
    'user_slot_configurations',
    'user_account_settings',
    'user_security_settings',
    'privacy_consents',
    'data_export_requests',
    'account_actions',
    'security_logs',
    'refresh_tokens',
    'user_auth',
    'university_verifications'
]

def drop_unwanted_tables():
    """Drop all tables that are not in the DATABASE_SCHEMA_COMPLETE.md"""
    
    print("🗑️ Dropping unwanted tables from database...")
    
    try:
        with engine.connect() as conn:
            # Start transaction
            trans = conn.begin()
            
            try:
                # Get all existing tables first
                result = conn.execute(text("""
                    SELECT tablename 
                    FROM pg_tables 
                    WHERE schemaname = 'public'
                    ORDER BY tablename;
                """))
                
                existing_tables = [row[0] for row in result]
                print(f"📋 Found {len(existing_tables)} existing tables")
                
                # Determine which tables to drop
                tables_to_drop = []
                for table in existing_tables:
                    if table not in KEEP_TABLES:
                        tables_to_drop.append(table)
                
                print(f"\n🔍 Tables to keep ({len(KEEP_TABLES)}):")
                for table in sorted(KEEP_TABLES):
                    status = "✅ EXISTS" if table in existing_tables else "❌ MISSING"
                    print(f"  - {table} {status}")
                
                print(f"\n🗑️ Tables to drop ({len(tables_to_drop)}):")
                for table in sorted(tables_to_drop):
                    print(f"  - {table}")
                
                if not tables_to_drop:
                    print("\n✅ No tables need to be dropped!")
                    trans.rollback()
                    return True
                
                # Drop tables with CASCADE to handle foreign key dependencies
                print(f"\n🔨 Dropping {len(tables_to_drop)} tables...")
                
                for table in tables_to_drop:
                    try:
                        print(f"  Dropping {table}...")
                        conn.execute(text(f'DROP TABLE IF EXISTS "{table}" CASCADE;'))
                        print(f"  ✅ Dropped {table}")
                    except Exception as e:
                        print(f"  ⚠️ Warning dropping {table}: {e}")
                
                # Commit transaction
                trans.commit()
                print("\n🎉 All unwanted tables dropped successfully!")
                
                # Verify remaining tables
                result = conn.execute(text("""
                    SELECT tablename 
                    FROM pg_tables 
                    WHERE schemaname = 'public'
                    ORDER BY tablename;
                """))
                
                remaining_tables = [row[0] for row in result]
                print(f"\n📊 Remaining tables ({len(remaining_tables)}):")
                for table in sorted(remaining_tables):
                    status = "✅ EXPECTED" if table in KEEP_TABLES else "⚠️ UNEXPECTED"
                    print(f"  - {table} {status}")
                
                return True
                
            except Exception as e:
                trans.rollback()
                print(f"❌ Error during table dropping: {e}")
                return False
                
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        return False

def verify_schema():
    """Verify that only expected tables remain"""
    
    print("\n🔍 Verifying database schema...")
    
    try:
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT tablename 
                FROM pg_tables 
                WHERE schemaname = 'public'
                ORDER BY tablename;
            """))
            
            existing_tables = set(row[0] for row in result)
            
            print(f"📋 Current tables: {len(existing_tables)}")
            print(f"📋 Expected tables: {len(KEEP_TABLES)}")
            
            missing_tables = KEEP_TABLES - existing_tables
            extra_tables = existing_tables - KEEP_TABLES
            
            if missing_tables:
                print(f"\n❌ Missing expected tables ({len(missing_tables)}):")
                for table in sorted(missing_tables):
                    print(f"  - {table}")
            
            if extra_tables:
                print(f"\n⚠️ Unexpected extra tables ({len(extra_tables)}):")
                for table in sorted(extra_tables):
                    print(f"  - {table}")
            
            if not missing_tables and not extra_tables:
                print("\n✅ Database schema matches DATABASE_SCHEMA_COMPLETE.md perfectly!")
                return True
            else:
                return False
                
    except Exception as e:
        print(f"❌ Schema verification error: {e}")
        return False

if __name__ == "__main__":
    print("⚠️ WARNING: This will drop tables and delete data!")
    print("📋 This script will align the database with DATABASE_SCHEMA_COMPLETE.md")
    print("📋 Only these 13 tables will remain:", sorted(KEEP_TABLES))
    
    confirmation = input("\nType 'DROP TABLES' to proceed: ")
    
    if confirmation == "DROP TABLES":
        success = drop_unwanted_tables()
        if success:
            verify_schema()
    else:
        print("Operation cancelled.")