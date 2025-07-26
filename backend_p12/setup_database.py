#!/usr/bin/env python3
"""
Database setup script - creates all tables and initial data
"""
from sqlalchemy import text
from models.base import engine, Base
from models.users import User
from models.auth import UserAuth, VerificationCode, RefreshToken, AuthProviderType
from models.likes import Like
import os
from dotenv import load_dotenv

load_dotenv()

def create_tables():
    """Create all database tables"""
    print("🗄️  Setting up database tables...")
    
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("✅ All tables created successfully")
        
        # Check what tables were created
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
                ORDER BY table_name
            """))
            tables = [row[0] for row in result.fetchall()]
            print(f"📋 Created tables: {', '.join(tables)}")
            
            # Check if alembic version table exists
            if 'alembic_version' not in tables:
                print("📝 Setting up Alembic version tracking...")
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS alembic_version (
                        version_num VARCHAR(32) NOT NULL,
                        CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
                    )
                """))
                conn.execute(text("INSERT INTO alembic_version (version_num) VALUES ('26efd846c7f5')"))
                conn.commit()
                print("✅ Alembic version tracking set up")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        return False

def create_sample_data():
    """Create some sample users for testing"""
    print("\n👥 Creating sample user data...")
    
    try:
        from sqlalchemy.orm import sessionmaker
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # Check if we already have users
        existing_users = session.query(User).count()
        if existing_users > 0:
            print(f"ℹ️  Found {existing_users} existing users, skipping sample data creation")
            session.close()
            return True
        
        # Create sample users
        sample_users = [
            {
                "name": "Alice Chen",
                "bio": "Full-stack developer passionate about AI and blockchain. Looking for co-founders for next big startup!"
            },
            {
                "name": "Bob Martinez", 
                "bio": "Marketing expert with 10 years experience. Seeking technical partners for SaaS ventures."
            },
            {
                "name": "Carol Zhang",
                "bio": "Data scientist and ML engineer. Building the future of healthcare technology."
            },
            {
                "name": "David Kim",
                "bio": "Serial entrepreneur and angel investor. Mentoring startups and seeking new opportunities."
            },
            {
                "name": "Emma Wilson",
                "bio": "UX/UI designer with focus on mobile apps. Love creating beautiful, user-friendly interfaces."
            }
        ]
        
        for user_data in sample_users:
            user = User(
                name=user_data["name"],
                bio=user_data["bio"],
                verification_status="active",
                is_active="true"
            )
            session.add(user)
        
        session.commit()
        print(f"✅ Created {len(sample_users)} sample users")
        session.close()
        return True
        
    except Exception as e:
        print(f"❌ Error creating sample data: {e}")
        return False

def test_database_connection():
    """Test database connection"""
    print("🔗 Testing database connection...")
    
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version_row = result.fetchone()
            if version_row:
                version = version_row[0]
                print(f"✅ Connected to PostgreSQL: {version[:50]}...")
            else:
                print("✅ Connected to PostgreSQL")
            
            # Test user count
            result = conn.execute(text("SELECT COUNT(*) FROM users"))
            count_row = result.fetchone()
            user_count = count_row[0] if count_row else 0
            print(f"📊 Database contains {user_count} users")
            
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 Project Tinder Database Setup")
    print("=" * 40)
    
    # Test connection
    if not test_database_connection():
        print("❌ Database connection failed. Please check your .env configuration.")
        return
    
    # Create tables
    if not create_tables():
        print("❌ Table creation failed.")
        return
    
    # Create sample data
    create_sample_data()
    
    print("\n" + "=" * 40)
    print("🎉 Database setup complete!")
    print("\n📋 What was set up:")
    print("   ✅ All database tables created")
    print("   ✅ Alembic version tracking")
    print("   ✅ Sample user data")
    print("\n🔧 Next steps:")
    print("   1. Test authentication endpoints")
    print("   2. Add vector embeddings for users")
    print("   3. Configure external services (WeChat, Tencent SES)")

if __name__ == "__main__":
    main()
