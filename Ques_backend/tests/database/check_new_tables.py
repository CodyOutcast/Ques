#!/usr/bin/env python3

import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
from config.database import db_config

load_dotenv()

def check_tables():
    engine = create_engine(db_config.database_url)
    
    with engine.connect() as conn:
        # Check if both tables exist
        result = conn.execute(text("""
            SELECT tablename 
            FROM pg_tables 
            WHERE schemaname = 'public' 
            AND tablename IN ('swipe_records', 'user_settings')
            ORDER BY tablename
        """))
        
        tables = [row[0] for row in result]
        
        print("=== New Tables Status ===")
        if 'swipe_records' in tables:
            print("✅ swipe_records table created")
        else:
            print("❌ swipe_records table NOT found")
            
        if 'user_settings' in tables:
            print("✅ user_settings table created")
        else:
            print("❌ user_settings table NOT found")
        
        # Check structure of swipe_records
        if 'swipe_records' in tables:
            print("\n=== swipe_records structure ===")
            result = conn.execute(text("""
                SELECT column_name, data_type, is_nullable 
                FROM information_schema.columns 
                WHERE table_name = 'swipe_records' 
                AND table_schema = 'public'
                ORDER BY ordinal_position
            """))
            
            for row in result:
                nullable = "NULL" if row[2] == "YES" else "NOT NULL"
                print(f"  {row[0]}: {row[1]} {nullable}")
        
        # Check structure of user_settings
        if 'user_settings' in tables:
            print("\n=== user_settings structure ===")
            result = conn.execute(text("""
                SELECT column_name, data_type, is_nullable 
                FROM information_schema.columns 
                WHERE table_name = 'user_settings' 
                AND table_schema = 'public'
                ORDER BY ordinal_position
            """))
            
            for row in result:
                nullable = "NULL" if row[2] == "YES" else "NOT NULL"
                print(f"  {row[0]}: {row[1]} {nullable}")

if __name__ == "__main__":
    check_tables()