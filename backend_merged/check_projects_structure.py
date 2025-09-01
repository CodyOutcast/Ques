import psycopg2
from config.database import db_config

def check_projects_table():
    try:
        conn = psycopg2.connect(
            host=db_config.PG_HOST,
            port=db_config.PG_PORT,
            database=db_config.PG_DATABASE,
            user=db_config.PG_USER,
            password=db_config.PG_PASSWORD
        )
        cur = conn.cursor()
        
        # Get column information for projects table
        cur.execute("""
            SELECT column_name, data_type, is_nullable 
            FROM information_schema.columns 
            WHERE table_name = 'projects' 
            ORDER BY ordinal_position;
        """)
        
        columns = cur.fetchall()
        print("📋 Projects table columns:")
        for col in columns:
            nullable = "NULL" if col[2] == "YES" else "NOT NULL"
            print(f"  - {col[0]} ({col[1]}) {nullable}")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_projects_table()
