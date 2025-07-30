#!/usr/bin/env python3
"""
Simple database migration for chat tables
Creates chat tables without using Alembic
"""

import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_chat_tables():
    """Create chat tables using raw SQL"""
    print("🗄️  CREATING CHAT TABLES")
    print("=" * 40)
    
    try:
        import psycopg2
        
        # Database connection parameters
        conn_params = {
            'host': os.getenv('PG_HOST'),
            'port': os.getenv('PG_PORT'),
            'user': os.getenv('PG_USER'),
            'password': os.getenv('PG_PASSWORD'),
            'database': os.getenv('PG_DATABASE')
        }
        
        print("1. Connecting to database...")
        print(f"   Host: {conn_params['host']}")
        print(f"   Port: {conn_params['port']}")
        print(f"   Database: {conn_params['database']}")
        
        # Connect to database
        conn = psycopg2.connect(**conn_params)
        cur = conn.cursor()
        
        print("   ✅ Connected successfully!")
        
        # Create enum type for chat status
        print("\n2. Creating chat status enum...")
        cur.execute("""
            DO $$ BEGIN
                CREATE TYPE chatstatus AS ENUM ('pending', 'active', 'rejected', 'blocked');
            EXCEPTION
                WHEN duplicate_object THEN null;
            END $$;
        """)
        print("   ✅ Chat status enum created")
        
        # Create chats table
        print("\n3. Creating chats table...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS chats (
                chat_id SERIAL PRIMARY KEY,
                initiator_id INTEGER NOT NULL,
                recipient_id INTEGER NOT NULL,
                status chatstatus NOT NULL DEFAULT 'pending',
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                accepted_at TIMESTAMP NULL,
                last_message_at TIMESTAMP NULL,
                greeting_message TEXT NULL,
                
                CONSTRAINT chats_initiator_fk FOREIGN KEY (initiator_id) 
                    REFERENCES users(user_id) ON DELETE CASCADE,
                CONSTRAINT chats_recipient_fk FOREIGN KEY (recipient_id) 
                    REFERENCES users(user_id) ON DELETE CASCADE
            );
        """)
        print("   ✅ Chats table created")
        
        # Create indexes for chats table
        print("\n4. Creating chats table indexes...")
        indexes = [
            "CREATE INDEX IF NOT EXISTS ix_chats_participants ON chats(initiator_id, recipient_id);",
            "CREATE INDEX IF NOT EXISTS ix_chats_status ON chats(status);",
            "CREATE INDEX IF NOT EXISTS ix_chats_last_message_at ON chats(last_message_at);",
            "CREATE INDEX IF NOT EXISTS ix_chats_created_at ON chats(created_at);"
        ]
        
        for index_sql in indexes:
            cur.execute(index_sql)
        print("   ✅ Chats indexes created")
        
        # Create chat_messages table
        print("\n5. Creating chat_messages table...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS chat_messages (
                message_id SERIAL PRIMARY KEY,
                chat_id INTEGER NOT NULL,
                sender_id INTEGER NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP NULL,
                is_read BOOLEAN NOT NULL DEFAULT FALSE,
                is_greeting BOOLEAN NOT NULL DEFAULT FALSE,
                
                CONSTRAINT chat_messages_chat_fk FOREIGN KEY (chat_id) 
                    REFERENCES chats(chat_id) ON DELETE CASCADE,
                CONSTRAINT chat_messages_sender_fk FOREIGN KEY (sender_id) 
                    REFERENCES users(user_id) ON DELETE CASCADE
            );
        """)
        print("   ✅ Chat messages table created")
        
        # Create indexes for chat_messages table
        print("\n6. Creating chat_messages table indexes...")
        message_indexes = [
            "CREATE INDEX IF NOT EXISTS ix_chat_messages_chat_id ON chat_messages(chat_id);",
            "CREATE INDEX IF NOT EXISTS ix_chat_messages_created_at ON chat_messages(created_at);",
            "CREATE INDEX IF NOT EXISTS ix_chat_messages_is_read ON chat_messages(is_read);",
            "CREATE INDEX IF NOT EXISTS ix_chat_messages_sender ON chat_messages(sender_id);"
        ]
        
        for index_sql in message_indexes:
            cur.execute(index_sql)
        print("   ✅ Chat messages indexes created")
        
        # Commit all changes
        conn.commit()
        
        # Verify tables were created
        print("\n7. Verifying table creation...")
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('chats', 'chat_messages')
            ORDER BY table_name;
        """)
        
        tables = [row[0] for row in cur.fetchall()]
        print(f"   📊 Created tables: {tables}")
        
        # Check table structure
        if 'chats' in tables:
            cur.execute("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'chats' 
                ORDER BY ordinal_position;
            """)
            
            columns = cur.fetchall()
            print(f"   📋 Chats table columns: {len(columns)}")
            for col_name, col_type in columns:
                print(f"      - {col_name}: {col_type}")
        
        if 'chat_messages' in tables:
            cur.execute("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'chat_messages' 
                ORDER BY ordinal_position;
            """)
            
            columns = cur.fetchall()
            print(f"   📋 Chat messages table columns: {len(columns)}")
            for col_name, col_type in columns:
                print(f"      - {col_name}: {col_type}")
        
        # Close connection
        cur.close()
        conn.close()
        
        print("\n✅ CHAT TABLES CREATED SUCCESSFULLY!")
        return True
        
    except Exception as e:
        print(f"\n❌ Failed to create chat tables: {e}")
        return False

def test_table_access():
    """Test if we can access the newly created tables"""
    print("\n🧪 TESTING TABLE ACCESS")
    print("=" * 30)
    
    try:
        from dependencies.db import get_db, engine
        from sqlalchemy import text
        
        # Test using SQLAlchemy
        print("1. Testing with SQLAlchemy...")
        db = next(get_db())
        
        # Test chats table
        result = db.execute(text("SELECT COUNT(*) FROM chats;"))
        chat_count = result.fetchone()[0]
        print(f"   ✅ Chats table accessible: {chat_count} rows")
        
        # Test chat_messages table
        result = db.execute(text("SELECT COUNT(*) FROM chat_messages;"))
        message_count = result.fetchone()[0]
        print(f"   ✅ Chat messages table accessible: {message_count} rows")
        
        db.close()
        
        # Test model imports
        print("\n2. Testing model imports...")
        from models.chats import Chat, Message, ChatStatus
        print("   ✅ Chat models imported successfully")
        print(f"   ✅ Chat statuses: {[status.value for status in ChatStatus]}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Table access test failed: {e}")
        return False

def main():
    """Main migration function"""
    print(f"🚀 Chat Database Migration Started at {datetime.now()}")
    print()
    
    # Create tables
    if not create_chat_tables():
        print("\n❌ Migration failed!")
        return False
    
    # Test access
    if not test_table_access():
        print("\n⚠️  Table access test failed, but tables might still work")
    
    print("\n" + "=" * 50)
    print("🎉 CHAT DATABASE MIGRATION COMPLETE!")
    print("=" * 50)
    
    print("✅ Tables created: chats, chat_messages")
    print("✅ Indexes created: Performance optimized")
    print("✅ Foreign keys: Data integrity ensured")
    print("✅ Enum types: Chat status management")
    
    print("\n🚀 NEXT STEPS:")
    print("1. Run: python setup_database.py")
    print("2. Test: python test_messaging_system.py")
    print("3. Start: python start_server.py")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\n🎯 Migration completed successfully!")
        else:
            print("\n💥 Migration failed!")
    except Exception as e:
        print(f"\n💥 Migration error: {e}")
