#!/usr/bin/env python3
"""
Check if casual_requests table exists and show its structure
"""
from sqlalchemy import create_engine, text, inspect
from config.database import db_config

def check_casual_requests_table():
    """Check if casual_requests table exists and show its structure"""
    try:
        engine = create_engine(db_config.database_url)
        
        with engine.connect() as conn:
            # Check if table exists
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'casual_requests'
            """))
            
            tables = list(result)
            exists = len(tables) > 0
            
            print(f"🔍 casual_requests table exists: {exists}")
            
            if exists:
                # Get table structure
                result = conn.execute(text("""
                    SELECT 
                        column_name,
                        data_type,
                        is_nullable,
                        column_default
                    FROM information_schema.columns 
                    WHERE table_schema = 'public' 
                    AND table_name = 'casual_requests'
                    ORDER BY ordinal_position
                """))
                
                print("\n📊 Table Structure:")
                print("| Column Name | Data Type | Nullable | Default |")
                print("|-------------|-----------|----------|---------|")
                
                for row in result:
                    nullable = "✅ Yes" if row[2] == "YES" else "❌ No"
                    default = row[3] if row[3] else "None"
                    print(f"| `{row[0]}` | {row[1]} | {nullable} | {default} |")
                
                # Check indexes
                result = conn.execute(text("""
                    SELECT 
                        indexname,
                        indexdef
                    FROM pg_indexes 
                    WHERE tablename = 'casual_requests'
                """))
                
                print("\n🗂️ Indexes:")
                for row in result:
                    print(f"- {row[0]}: {row[1]}")
                
                # Test basic operations
                print("\n🧪 Testing basic operations...")
                
                # Count existing records
                result = conn.execute(text("SELECT COUNT(*) FROM casual_requests"))
                count = result.fetchone()[0]
                print(f"   Current records: {count}")
                
                # Test insert (if no records exist)
                if count == 0:
                    print("   Testing insert...")
                    conn.execute(text("""
                        INSERT INTO casual_requests 
                        (user_id, query, optimized_query, is_active, location, preferences)
                        VALUES 
                        ('test_user_123', 'Test casual request', 'Optimized test request', true, 'Test City', '{"activity_type": "test"}')
                    """))
                    conn.commit()
                    print("   ✅ Insert successful")
                    
                    # Clean up test record
                    conn.execute(text("DELETE FROM casual_requests WHERE user_id = 'test_user_123'"))
                    conn.commit()
                    print("   🧹 Test record cleaned up")
                
            else:
                print("❌ casual_requests table does not exist!")
                print("   Run migration: alembic upgrade casual_requests_001")
                
    except Exception as e:
        print(f"❌ Error checking table: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_casual_requests_table()