"""
Add missing columns to users table for VectorDB functionality
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def add_vector_columns():
    """Add feature_tags and vector_id columns to users table"""
    print("🔧 Adding Vector Columns to Users Table")
    print("=" * 45)
    
    try:
        from models.base import SessionLocal
        from sqlalchemy import text
        
        db = SessionLocal()
        
        # Check if columns already exist
        print("\n1. Checking existing columns...")
        result = db.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'users'
        """))
        existing_columns = [row[0] for row in result.fetchall()]
        print(f"   Existing columns: {existing_columns}")
        
        # Add feature_tags column if not exists
        if 'feature_tags' not in existing_columns:
            print("\n2. Adding feature_tags column...")
            db.execute(text("""
                ALTER TABLE users 
                ADD COLUMN feature_tags JSON
            """))
            print("   ✅ feature_tags column added")
        else:
            print("\n2. feature_tags column already exists")
        
        # Add vector_id column if not exists
        if 'vector_id' not in existing_columns:
            print("\n3. Adding vector_id column...")
            db.execute(text("""
                ALTER TABLE users 
                ADD COLUMN vector_id VARCHAR
            """))
            print("   ✅ vector_id column added")
        else:
            print("\n3. vector_id column already exists")
        
        # Commit changes
        db.commit()
        print("\n✅ All vector columns are ready!")
        
        # Verify the changes
        print("\n4. Verifying changes...")
        result = db.execute(text("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'users'
            ORDER BY ordinal_position
        """))
        columns = result.fetchall()
        
        print("   📋 Updated users table structure:")
        for col_name, col_type in columns:
            print(f"      - {col_name}: {col_type}")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Error adding vector columns: {e}")
        return False

if __name__ == "__main__":
    success = add_vector_columns()
    if success:
        print("\n🎉 Vector columns successfully added!")
        print("   You can now run the PostgreSQL test again.")
    else:
        print("\n❌ Failed to add vector columns")
