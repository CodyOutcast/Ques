#!/usr/bin/env python3
"""
Database reset script - drops and recreates all tables
WARNING: This will delete all data!
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from config.settings import settings
from models.base import Base

# Import all models to ensure they're registered
from models import *

def reset_database():
    """Drop and recreate all tables"""
    
    # Create engine
    engine = create_engine(str(settings.DATABASE_URL))
    
    print("🗑️ Dropping all tables...")
    try:
        # Drop all tables
        Base.metadata.drop_all(bind=engine)
        print("✅ All tables dropped successfully")
    except Exception as e:
        print(f"⚠️ Warning during drop: {e}")
    
    print("🏗️ Creating all tables...")
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("✅ All tables created successfully")
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        return False
    
    print("🎉 Database reset complete!")
    return True

if __name__ == "__main__":
    print("⚠️ WARNING: This will delete ALL data in the database!")
    confirmation = input("Type 'YES' to proceed: ")
    
    if confirmation == "YES":
        reset_database()
    else:
        print("Database reset cancelled.")