#!/usr/bin/env python3
"""
Database Tables Checker
Shows all current tables in the database with their columns and relationships
"""

import os
import sys
from pathlib import Path
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_database_url():
    """Get database URL from environment"""
    db_url = os.getenv("DATABASE_URL")
    if db_url:
        return db_url
    
    # Build from individual components
    pg_user = os.getenv("PG_USER", "postgres")
    pg_password = os.getenv("PG_PASSWORD", "password")
    pg_host = os.getenv("PG_HOST", "localhost")
    pg_port = os.getenv("PG_PORT", "5432")
    pg_database = os.getenv("PG_DATABASE", "ques_merged_db")
    
    return f"postgresql://{pg_user}:{pg_password}@{pg_host}:{pg_port}/{pg_database}"

def check_database_connection():
    """Test database connection"""
    try:
        database_url = get_database_url()
        engine = create_engine(database_url)
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"✅ Database connection successful!")
            print(f"   PostgreSQL version: {version.split()[1]}")
            return engine
            
    except SQLAlchemyError as e:
        print(f"❌ Database connection failed: {e}")
        return None
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return None

def get_all_tables(engine):
    """Get all tables in the database"""
    try:
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        return sorted(tables)
    except Exception as e:
        print(f"❌ Error getting tables: {e}")
        return []

def get_table_info(engine, table_name):
    """Get detailed information about a table"""
    try:
        inspector = inspect(engine)
        
        # Get columns
        columns = inspector.get_columns(table_name)
        
        # Get primary keys
        pk_constraint = inspector.get_pk_constraint(table_name)
        primary_keys = pk_constraint.get('constrained_columns', [])
        
        # Get foreign keys
        foreign_keys = inspector.get_foreign_keys(table_name)
        
        # Get indexes
        indexes = inspector.get_indexes(table_name)
        
        return {
            'columns': columns,
            'primary_keys': primary_keys,
            'foreign_keys': foreign_keys,
            'indexes': indexes
        }
    except Exception as e:
        print(f"❌ Error getting info for table {table_name}: {e}")
        return None

def get_table_row_count(engine, table_name):
    """Get row count for a table"""
    try:
        with engine.connect() as conn:
            result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
            return result.fetchone()[0]
    except Exception as e:
        return f"Error: {e}"

def format_column_info(column):
    """Format column information for display"""
    col_type = str(column['type'])
    nullable = "NULL" if column['nullable'] else "NOT NULL"
    default = f" DEFAULT {column['default']}" if column['default'] else ""
    return f"{column['name']} {col_type} {nullable}{default}"

def main():
    print("🔍 Database Tables Checker")
    print("=" * 60)
    
    # Check database connection
    engine = check_database_connection()
    if not engine:
        print("\n❌ Cannot connect to database. Please check your configuration.")
        print("\nRequired environment variables:")
        print("- PG_HOST, PG_PORT, PG_USER, PG_PASSWORD, PG_DATABASE")
        print("- Or DATABASE_URL")
        return
    
    # Get all tables
    print(f"\n📊 Checking database: {os.getenv('PG_DATABASE', 'ques_merged_db')}")
    tables = get_all_tables(engine)
    
    if not tables:
        print("❌ No tables found in database")
        return
    
    print(f"✅ Found {len(tables)} tables")
    print("-" * 60)
    
    # Display each table
    for table_name in tables:
        print(f"\n📋 Table: {table_name}")
        
        # Get row count
        row_count = get_table_row_count(engine, table_name)
        print(f"   Rows: {row_count}")
        
        # Get table info
        table_info = get_table_info(engine, table_name)
        if not table_info:
            continue
        
        # Display columns
        print("   Columns:")
        for column in table_info['columns']:
            col_info = format_column_info(column)
            pk_marker = " 🔑" if column['name'] in table_info['primary_keys'] else ""
            print(f"     - {col_info}{pk_marker}")
        
        # Display foreign keys
        if table_info['foreign_keys']:
            print("   Foreign Keys:")
            for fk in table_info['foreign_keys']:
                local_cols = ', '.join(fk['constrained_columns'])
                ref_table = fk['referred_table']
                ref_cols = ', '.join(fk['referred_columns'])
                print(f"     - {local_cols} → {ref_table}({ref_cols})")
        
        # Display indexes (only non-primary key indexes)
        non_pk_indexes = [idx for idx in table_info['indexes'] 
                         if not any(col in table_info['primary_keys'] 
                                   for col in idx.get('column_names', []) if col)]
        if non_pk_indexes:
            print("   Indexes:")
            for idx in non_pk_indexes:
                cols = ', '.join([col for col in idx.get('column_names', []) if col])
                unique = " (UNIQUE)" if idx.get('unique') else ""
                print(f"     - {idx.get('name', 'unnamed')}: {cols}{unique}")
    
    # Summary
    print("\n" + "=" * 60)
    print("📈 SUMMARY:")
    print(f"   Total tables: {len(tables)}")
    
    # Get total row count across all tables
    total_rows = 0
    for table_name in tables:
        count = get_table_row_count(engine, table_name)
        if isinstance(count, int):
            total_rows += count
    
    print(f"   Total rows: {total_rows}")
    print(f"   Database: {os.getenv('PG_DATABASE', 'ques_merged_db')}")
    print("\n💡 Use Alembic to manage database migrations:")
    print("   alembic current    # Show current migration")
    print("   alembic history    # Show migration history")
    print("   alembic upgrade head  # Apply latest migrations")

if __name__ == "__main__":
    main()
