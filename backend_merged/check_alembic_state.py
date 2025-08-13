import os
import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_alembic_state():
    try:
        # Database connection parameters
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            database=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            port=os.getenv('DB_PORT', '5432')
        )
        cursor = conn.cursor()
        
        print("🔍 Checking alembic version table...")
        
        # Check if alembic_version table exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT 1 FROM information_schema.tables 
                WHERE table_name = 'alembic_version'
            );
        """)
        
        if cursor.fetchone()[0]:
            print("✅ alembic_version table exists")
            
            # Get current version
            cursor.execute("SELECT version_num FROM alembic_version;")
            result = cursor.fetchone()
            if result:
                print(f"📊 Current version: {result[0]}")
            else:
                print("⚠️ No version recorded in alembic_version table")
        else:
            print("❌ alembic_version table does not exist")
            
        # List all migration files
        import glob
        print("\n📂 Available migration files:")
        migration_files = glob.glob("migrations/versions/*.py")
        for file in sorted(migration_files):
            filename = os.path.basename(file)
            if not filename.startswith('__'):
                print(f"  - {filename}")
                
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_alembic_state()
