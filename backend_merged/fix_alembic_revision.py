import os
import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def fix_alembic_revision():
    try:
        # Database connection parameters
        conn = psycopg2.connect(
            host=os.getenv('PG_HOST', 'localhost'),
            database=os.getenv('PG_DATABASE'),
            user=os.getenv('PG_USER'),
            password=os.getenv('PG_PASSWORD'),
            port=os.getenv('PG_PORT', '5432')
        )
        cursor = conn.cursor()
        
        print("🔍 Current alembic version state...")
        
        # Check current version
        cursor.execute("SELECT version_num FROM alembic_version;")
        result = cursor.fetchone()
        if result:
            print(f"📊 Current version in DB: {result[0]}")
        
        # Update to the latest valid revision
        # Based on our database tables, it looks like we should be at 008_message_search_indexes
        print("🔧 Fixing revision to 008_message_search_indexes...")
        cursor.execute("UPDATE alembic_version SET version_num = '008_message_search_indexes';")
        
        # Verify the change
        cursor.execute("SELECT version_num FROM alembic_version;")
        result = cursor.fetchone()
        print(f"✅ Updated version to: {result[0]}")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("🎉 Revision chain fixed! You can now run migrations.")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    fix_alembic_revision()
