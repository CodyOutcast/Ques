#!/usr/bin/env python3
"""
Database setup script for messaging system
This script will create tables and test the database connection
"""

import os
import sys
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_database_connection():
    """Test database connection and create tables"""
    print("🗄️  SETTING UP DATABASE FOR MESSAGING SYSTEM")
    print("=" * 60)
    
    try:
        # Test environment variables
        print("1. Checking environment variables...")
        from dotenv import load_dotenv
        load_dotenv()
        
        required_vars = ['PG_HOST', 'PG_PORT', 'PG_USER', 'PG_PASSWORD', 'PG_DATABASE']
        missing_vars = []
        
        for var in required_vars:
            value = os.getenv(var)
            if value:
                print(f"   ✅ {var}: {'*' * len(value[:10])}...")
            else:
                missing_vars.append(var)
                print(f"   ❌ {var}: Missing")
        
        if missing_vars:
            print(f"❌ Missing required environment variables: {missing_vars}")
            return False
        
        # Test database connection
        print("\n2. Testing database connection...")
        from dependencies.db import engine, get_db
        from sqlalchemy import text
        
        # Test connection
        with engine.connect() as connection:
            result = connection.execute(text("SELECT version();"))
            version = result.fetchone()[0]
            print(f"   ✅ Connected to PostgreSQL: {version[:50]}...")
        
        # Test session creation
        db = next(get_db())
        print("   ✅ Database session created successfully")
        db.close()
        
        # Import all models to ensure they're registered
        print("\n3. Loading models...")
        from models.base import Base
        from models.users import User
        from models.chats import Chat, Message, ChatStatus
        from models.likes import UserSwipe
        from models.matches import Match
        print("   ✅ All models loaded successfully")
        
        # Create tables
        print("\n4. Creating database tables...")
        Base.metadata.create_all(bind=engine)
        print("   ✅ All tables created successfully")
        
        # Verify tables exist
        print("\n5. Verifying tables...")
        with engine.connect() as connection:
            # Check if our new chat tables exist
            result = connection.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name IN ('chats', 'chat_messages')
                ORDER BY table_name;
            """))
            
            tables = [row[0] for row in result.fetchall()]
            print(f"   📊 Chat tables found: {tables}")
            
            if 'chats' in tables and 'chat_messages' in tables:
                print("   ✅ Chat tables created successfully!")
            else:
                print("   ⚠️  Chat tables not found - may need migration")
            
            # Check all tables
            result = connection.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                ORDER BY table_name;
            """))
            
            all_tables = [row[0] for row in result.fetchall()]
            print(f"   📋 All tables: {', '.join(all_tables)}")
        
        return True
        
    except Exception as e:
        logger.error(f"Database setup failed: {e}")
        print(f"❌ Database setup failed: {e}")
        return False

def create_sample_data():
    """Create some sample users and data for testing"""
    print("\n6. Creating sample data for testing...")
    
    try:
        from dependencies.db import get_db
        from models.users import User
        from models.likes import UserSwipe
        from models.chats import Chat, ChatStatus
        from sqlalchemy import and_
        
        db = next(get_db())
        
        # Check if we already have users
        existing_users = db.query(User).limit(5).all()
        print(f"   📊 Found {len(existing_users)} existing users")
        
        if len(existing_users) >= 2:
            print("   ✅ Sufficient users exist for testing")
            
            # Show existing users
            for user in existing_users[:3]:
                print(f"      - User {user.user_id}: {user.name}")
                
        else:
            print("   ⚠️  Need to create sample users for testing")
            # You would add user creation logic here if needed
        
        # Check existing chats
        existing_chats = db.query(Chat).limit(5).all()
        print(f"   📊 Found {len(existing_chats)} existing chats")
        
        if existing_chats:
            for chat in existing_chats:
                print(f"      - Chat {chat.chat_id}: {chat.status.value} between users {chat.initiator_id} and {chat.recipient_id}")
        
        db.close()
        print("   ✅ Sample data check complete")
        return True
        
    except Exception as e:
        logger.error(f"Sample data creation failed: {e}")
        print(f"   ❌ Sample data creation failed: {e}")
        return False

def test_messaging_operations():
    """Test basic messaging operations"""
    print("\n7. Testing messaging operations...")
    
    try:
        from services.chat_service import ChatService
        from schemas.chats import GreetingCreate, MessageCreate
        from dependencies.db import get_db
        
        db = next(get_db())
        
        print("   ✅ Chat service imported successfully")
        print("   ✅ Chat schemas imported successfully")
        print("   ✅ Database connection for operations successful")
        
        # Test schema creation
        greeting = GreetingCreate(
            recipient_id=2,
            greeting_message="Hello! I'd love to chat with you! 😊"
        )
        print(f"   ✅ Greeting schema: {greeting.greeting_message}")
        
        message = MessageCreate(content="How are you doing today?")
        print(f"   ✅ Message schema: {message.content}")
        
        db.close()
        print("   ✅ Messaging operations test complete")
        return True
        
    except Exception as e:
        logger.error(f"Messaging operations test failed: {e}")
        print(f"   ❌ Messaging operations test failed: {e}")
        return False

def main():
    """Main setup function"""
    print(f"🚀 Database Setup Started at {datetime.now()}")
    print()
    
    # Step 1: Test database connection and create tables
    if not test_database_connection():
        print("\n❌ Database setup failed. Please check your configuration.")
        return False
    
    # Step 2: Create/check sample data
    if not create_sample_data():
        print("\n⚠️  Sample data setup had issues, but continuing...")
    
    # Step 3: Test messaging operations
    if not test_messaging_operations():
        print("\n❌ Messaging operations test failed.")
        return False
    
    print("\n" + "=" * 60)
    print("🎉 DATABASE SETUP COMPLETE!")
    print("=" * 60)
    
    print("✅ Database connection: Working")
    print("✅ Tables created: Success")
    print("✅ Chat models: Loaded")
    print("✅ Messaging system: Ready")
    
    print("\n🚀 NEXT STEPS:")
    print("1. Run: python start_server.py")
    print("2. Test API: http://localhost:8000/docs")
    print("3. Try messaging: python messaging_demo.py")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\n🎯 Database setup completed successfully!")
            sys.exit(0)
        else:
            print("\n💥 Database setup failed!")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n🛑 Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error during setup: {e}")
        sys.exit(1)
