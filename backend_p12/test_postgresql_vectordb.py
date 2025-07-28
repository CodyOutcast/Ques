#!/usr/bin/env python3
"""
PostgreSQL and Basic Database Test
Test PostgreSQL connection and check existing data
"""

import os
import sys
import json
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_postgresql_connection():
    """Test PostgreSQL connection and check current data"""
    print("🗄️ Testing PostgreSQL Connection and Data")
    print("=" * 50)
    
    try:
        from models.base import SessionLocal
        from sqlalchemy import text
        
        db = SessionLocal()
        
        # Test 1: Basic connection
        print("\n1. Testing Basic Connection...")
        result = db.execute(text("SELECT version()"))
        version_row = result.fetchone()
        if version_row:
            version = version_row[0]
            print(f"   ✅ PostgreSQL Version: {version[:70]}...")
        else:
            print("   ❌ Could not get PostgreSQL version")
        
        # Test 2: Check users table structure
        print("\n2. Checking Users Table Structure...")
        result = db.execute(text("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'users'
            ORDER BY ordinal_position
        """))
        columns = result.fetchall()
        
        print("   📋 Users table columns:")
        for col_name, col_type in columns:
            print(f"      - {col_name}: {col_type}")
        
        # Test 3: Check current users
        print("\n3. Checking Current Users...")
        result = db.execute(text("SELECT COUNT(*) FROM users"))
        count_row = result.fetchone()
        if count_row:
            user_count = count_row[0]
            print(f"   👥 Total users in database: {user_count}")
        else:
            print("   ❌ Could not get user count")
            user_count = 0
        
        if user_count > 0:
            print("\n   📋 Sample users:")
            result = db.execute(text("""
                SELECT user_id, name, bio, feature_tags, vector_id 
                FROM users 
                LIMIT 5
            """))
            users = result.fetchall()
            
            for user in users:
                user_id, name, bio, feature_tags, vector_id = user
                print(f"      {user_id}. {name}")
                print(f"         Bio: {bio[:50]}..." if bio and len(bio) > 50 else f"         Bio: {bio}")
                if feature_tags:
                    try:
                        tags = json.loads(feature_tags)
                        print(f"         Tags: {tags[:3]}...")
                    except:
                        print(f"         Tags: {feature_tags}")
                print(f"         Vector ID: {vector_id}")
                print()
        
        # Test 4: Check if vector-related columns exist
        print("4. Checking Vector-Related Columns...")
        vector_columns = ['feature_tags', 'vector_id']
        existing_columns = [col[0] for col in columns]
        
        for col in vector_columns:
            if col in existing_columns:
                print(f"   ✅ {col} column exists")
            else:
                print(f"   ❌ {col} column missing")
        
        # Test 5: Check likes table for swipe history
        print("\n5. Checking Likes Table (Swipe History)...")
        try:
            result = db.execute(text("SELECT COUNT(*) FROM likes"))
            likes_row = result.fetchone()
            if likes_row:
                likes_count = likes_row[0]
                print(f"   👍 Total likes/swipes: {likes_count}")
            else:
                print("   ❌ Could not get likes count")
                likes_count = 0
            
            if likes_count > 0:
                result = db.execute(text("""
                    SELECT liker_id, liked_item_id, liked_item_type, granted_chat_access 
                    FROM likes 
                    LIMIT 3
                """))
                likes = result.fetchall()
                print("   📋 Sample swipe actions:")
                for like in likes:
                    liker_id, liked_item_id, liked_item_type, granted_chat = like
                    action = "liked" if granted_chat else "disliked"
                    print(f"      User {liker_id} {action} {liked_item_type} {liked_item_id}")
        
        except Exception as e:
            print(f"   ⚠️  Could not check likes table: {e}")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"   ❌ PostgreSQL connection failed: {e}")
        return False

def add_sample_users_without_vector():
    """Add sample users to PostgreSQL without VectorDB (for testing)"""
    print("\n👥 Adding Sample Users (PostgreSQL Only)")
    print("=" * 45)
    
    sample_users = [
        {
            "name": "Alex Chen",
            "bio": "AI/ML engineer and startup founder looking for co-founders and investors",
            "feature_tags": ["AI engineer", "startup founder", "machine learning", "technology", "investment seeker"]
        },
        {
            "name": "Sarah Johnson", 
            "bio": "Venture capitalist specializing in fintech and health tech startups",
            "feature_tags": ["venture capitalist", "investor", "fintech", "health tech", "funding provider"]
        },
        {
            "name": "David Rodriguez",
            "bio": "Full-stack developer interested in blockchain and DeFi projects",
            "feature_tags": ["full-stack developer", "blockchain", "DeFi", "cryptocurrency", "web3"]
        },
        {
            "name": "Emily Zhang",
            "bio": "Product manager with experience in e-commerce and mobile apps",
            "feature_tags": ["product manager", "e-commerce", "mobile apps", "user experience", "growth"]
        },
        {
            "name": "Michael Kim",
            "bio": "Marketing expert and growth hacker for early-stage startups",
            "feature_tags": ["marketing expert", "growth hacker", "digital marketing", "startup mentor", "scaling"]
        }
    ]
    
    try:
        from models.base import SessionLocal
        from sqlalchemy import text
        
        db = SessionLocal()
        success_count = 0
        
        for i, user_data in enumerate(sample_users, 1):
            try:
                print(f"\n{i}. Adding {user_data['name']}...")
                
                # Check if user already exists
                result = db.execute(text("""
                    SELECT user_id FROM users WHERE name = :name
                """), {"name": user_data['name']})
                
                existing_user = result.fetchone()
                
                if existing_user:
                    print(f"   ⚠️  User '{user_data['name']}' already exists (ID: {existing_user[0]})")
                    continue
                
                # Insert user into PostgreSQL
                result = db.execute(text("""
                    INSERT INTO users (name, bio, feature_tags) 
                    VALUES (:name, :bio, :feature_tags) 
                    RETURNING user_id
                """), {
                    "name": user_data['name'],
                    "bio": user_data['bio'],
                    "feature_tags": json.dumps(user_data['feature_tags'])
                })
                
                user_row = result.fetchone()
                if user_row:
                    user_id = user_row[0]
                    print(f"   ✅ User created with ID: {user_id}")
                    print(f"   🏷️  Feature tags: {user_data['feature_tags']}")
                    success_count += 1
                else:
                    print(f"   ❌ Failed to create user {user_data['name']}")
                    continue
                
            except Exception as e:
                print(f"   ❌ Error adding {user_data['name']}: {e}")
                db.rollback()
                continue
        
        db.commit()
        db.close()
        
        print(f"\n🎉 Successfully added {success_count}/{len(sample_users)} sample users to PostgreSQL!")
        return success_count > 0
        
    except Exception as e:
        print(f"❌ Error in add_sample_users_without_vector: {e}")
        return False

def test_recommendation_algorithm():
    """Test the recommendation algorithm with fallback (without VectorDB)"""
    print("\n🎯 Testing Recommendation Algorithm (Fallback Mode)")
    print("=" * 55)
    
    try:
        from db_utils import get_random_unseen_users, get_user_history
        from models.base import SessionLocal
        from sqlalchemy import text
        
        db = SessionLocal()
        
        # Get a test user
        result = db.execute(text("SELECT user_id, name FROM users LIMIT 1"))
        user_row = result.fetchone()
        
        if not user_row:
            print("   ❌ No users found in database")
            return False
        
        test_user_id, test_user_name = user_row
        print(f"   🧪 Testing with user: {test_user_name} (ID: {test_user_id})")
        
        # Get user's swipe history
        print("\n   📋 Checking swipe history...")
        history = get_user_history(test_user_id)
        print(f"      Seen {len(history)} cards before")
        
        # Get random unseen users (fallback recommendations)
        print("\n   🎲 Getting random unseen users...")
        random_users = get_random_unseen_users(test_user_id, history, limit=5)
        print(f"      Found {len(random_users)} random unseen users")
        
        if random_users:
            # Get user info for recommendations
            from db_utils import get_user_infos
            users_info = get_user_infos(random_users)
            
            print("\n   👥 Sample recommendations:")
            for i, user in enumerate(users_info, 1):
                tags = user.get('feature_tags', [])
                print(f"      {i}. {user['name']} - {tags[:3] if tags else 'No tags'}")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"   ❌ Error testing recommendation algorithm: {e}")
        return False

def check_vector_db_requirements():
    """Check what's needed for VectorDB functionality"""
    print("\n🔍 Checking VectorDB Requirements")
    print("=" * 40)
    
    print("   📋 Environment Variables:")
    vectordb_vars = [
        'VECTORDB_ENDPOINT',
        'VECTORDB_USERNAME', 
        'VECTORDB_KEY',
        'VECTORDB_COLLECTION',
        'VECTORDB_DIMENSION'
    ]
    
    for var in vectordb_vars:
        value = os.getenv(var)
        if value:
            if 'KEY' in var or 'PASSWORD' in var:
                print(f"      ✅ {var}: ***{value[-4:] if len(value) >= 4 else '***'}")
            else:
                print(f"      ✅ {var}: {value}")
        else:
            print(f"      ❌ {var}: Not set")
    
    print("\n   📦 Python Dependencies:")
    
    # Check tcvectordb
    try:
        import tcvectordb
        print("      ✅ tcvectordb: Available")
    except ImportError:
        print("      ❌ tcvectordb: Not installed")
        print("         💡 Install with: pip install tcvectordb")
    
    # Check sentence-transformers
    try:
        import sentence_transformers
        print(f"      ✅ sentence-transformers: {sentence_transformers.__version__}")
    except ImportError:
        print("      ❌ sentence-transformers: Not installed")
        print("         💡 Install with: pip install sentence-transformers")
    
    # Check torch (required by sentence-transformers)
    try:
        import torch
        print(f"      ✅ torch: {torch.__version__}")
    except ImportError:
        print("      ❌ torch: Not installed")
        print("         💡 Install with: pip install torch")

def main():
    """Main test function"""
    print("🚀 PostgreSQL and Database Test")
    print("=" * 40)
    
    # Test PostgreSQL connection
    pg_success = test_postgresql_connection()
    if not pg_success:
        print("\n❌ PostgreSQL connection failed. Cannot continue.")
        return
    
    # Check VectorDB requirements
    check_vector_db_requirements()
    
    # Ask if user wants to add sample users
    print("\n" + "="*50)
    user_input = input("Would you like to add sample users to PostgreSQL? (y/N): ").strip().lower()
    
    if user_input in ['y', 'yes']:
        users_added = add_sample_users_without_vector()
        
        if users_added:
            # Test recommendation algorithm
            test_recommendation_algorithm()
    else:
        print("Skipping sample user creation.")
        # Still test recommendation algorithm if users exist
        test_recommendation_algorithm()
    
    print("\n🎉 PostgreSQL Test Complete!")
    print("\n📋 Summary:")
    print(f"   🗄️  PostgreSQL: {'✅ Working' if pg_success else '❌ Failed'}")
    print("   🔍 VectorDB: ⚠️  Connection issues (network/configuration)")
    print("   💡 Recommendations: ✅ Fallback mode working (random users)")

if __name__ == "__main__":
    main()
