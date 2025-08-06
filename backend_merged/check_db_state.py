#!/usr/bin/env python3
"""
Check database state for project status migration
"""
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()

# Build connection URL from environment variables
host = os.getenv('PG_HOST')
port = os.getenv('PG_PORT')
user = os.getenv('PG_USER')
password = os.getenv('PG_PASSWORD')
database = os.getenv('PG_DATABASE')

db_url = f'postgresql://{user}:{password}@{host}:{port}/{database}'
print('Connecting to database...')

try:
    engine = create_engine(db_url)
    with engine.connect() as conn:
        # Check if projectstatus enum exists
        result = conn.execute(text("SELECT EXISTS(SELECT 1 FROM pg_type WHERE typname = 'projectstatus')"))
        enum_exists = result.scalar()
        print(f'ProjectStatus enum exists: {enum_exists}')
        
        # Check if projects table has status column
        result = conn.execute(text("SELECT EXISTS(SELECT 1 FROM information_schema.columns WHERE table_name = 'projects' AND column_name = 'status')"))
        column_exists = result.scalar()
        print(f'Projects.status column exists: {column_exists}')
        
        # Check if projects table exists
        result = conn.execute(text("SELECT EXISTS(SELECT 1 FROM information_schema.tables WHERE table_name = 'projects')"))
        table_exists = result.scalar()
        print(f'Projects table exists: {table_exists}')
        
        # If enum exists, show its values
        if enum_exists:
            try:
                result = conn.execute(text("SELECT unnest(enum_range(NULL::projectstatus))"))
                enum_values = [row[0] for row in result]
                print(f'Current enum values: {enum_values}')
            except Exception as e:
                print(f'Could not get enum values: {e}')

except Exception as e:
    print(f'Database connection error: {e}')
