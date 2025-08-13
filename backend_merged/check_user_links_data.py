import os
import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_user_links_data():
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
        
        print("🔍 Checking user_links table data...")
        
        # Check current file_type values
        cursor.execute("SELECT DISTINCT file_type FROM user_links;")
        results = cursor.fetchall()
        
        print("📊 Current file_type values:")
        for row in results:
            print(f"  - {row[0]}")
            
        # Count of each type
        cursor.execute("SELECT file_type, COUNT(*) FROM user_links GROUP BY file_type;")
        results = cursor.fetchall()
        
        print("\n📈 Count by file_type:")
        for row in results:
            print(f"  - {row[0]}: {row[1]} records")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_user_links_data()
