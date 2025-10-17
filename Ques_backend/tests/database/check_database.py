#!/usr/bin/env python3
"""
Check current database tables and schema
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text, inspect
from dependencies.db import engine

def check_database_tables():
    """Check what tables exist in the database"""
    
    print("🔍 Checking current database tables...")
    
    try:
        # Get inspector
        inspector = inspect(engine)
        
        # Get all table names
        tables = inspector.get_table_names()
        
        print(f"\n📋 Found {len(tables)} tables:")
        for table in sorted(tables):
            print(f"  - {table}")
            
        print("\n🔍 Detailed table information:")
        
        for table_name in sorted(tables):
            print(f"\n📋 Table: {table_name}")
            
            # Get columns
            columns = inspector.get_columns(table_name)
            print("  Columns:")
            for col in columns:
                nullable = "NULL" if col['nullable'] else "NOT NULL"
                pk = " (PK)" if col.get('primary_key', False) else ""
                print(f"    - {col['name']}: {col['type']} {nullable}{pk}")
            
            # Get foreign keys
            foreign_keys = inspector.get_foreign_keys(table_name)
            if foreign_keys:
                print("  Foreign Keys:")
                for fk in foreign_keys:
                    print(f"    - {fk['constrained_columns']} -> {fk['referred_table']}.{fk['referred_columns']}")
            
            # Get indexes
            indexes = inspector.get_indexes(table_name)
            if indexes:
                print("  Indexes:")
                for idx in indexes:
                    unique = " (UNIQUE)" if idx['unique'] else ""
                    print(f"    - {idx['name']}: {idx['column_names']}{unique}")
                    
        return True
        
    except Exception as e:
        print(f"❌ Error checking database: {e}")
        return False

def check_membership_table():
    """Specifically check if membership table exists and its structure"""
    
    try:
        with engine.connect() as conn:
            # Check if memberships table exists
            result = conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'memberships'
                );
            """))
            exists = result.fetchone()[0]
            
            if exists:
                print("\n✅ Memberships table exists")
                
                # Get column info
                result = conn.execute(text("""
                    SELECT column_name, data_type, is_nullable, column_default
                    FROM information_schema.columns 
                    WHERE table_name = 'memberships'
                    ORDER BY ordinal_position;
                """))
                
                columns = result.fetchall()
                print("  Columns:")
                for col in columns:
                    print(f"    - {col[0]}: {col[1]} ({'NULL' if col[2] == 'YES' else 'NOT NULL'})")
                    
            else:
                print("\n❌ Memberships table does NOT exist")
                
    except Exception as e:
        print(f"❌ Error checking memberships table: {e}")

if __name__ == "__main__":
    print("🔍 Testing current database models...")
    check_database_tables()
    check_membership_table()