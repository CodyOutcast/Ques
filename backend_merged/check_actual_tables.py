#!/usr/bin/env python3

from sqlalchemy import create_engine, text
from config.database import db_config

def get_actual_database_tables():
    """Get list of actual tables in the database"""
    engine = create_engine(db_config.database_url)
    
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name
        """))
        
        tables = [row[0] for row in result.fetchall()]
        
        print("📊 Actual Database Tables:")
        print("=" * 40)
        for i, table in enumerate(tables, 1):
            print(f"{i:2d}. {table}")
        
        return tables

if __name__ == "__main__":
    get_actual_database_tables()
