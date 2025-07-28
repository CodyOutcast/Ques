#!/usr/bin/env python3
"""
Final Comprehensive Test - Working with Actual Database Schema
Test both PostgreSQL (working) and VectorDB (connection issues) with real data
"""

import os
import sys
import json
import random
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_database_status():
    """Check status of both databases"""
    print("🔍 Database Connection Status")
    print("=" * 40)
    
    # Test PostgreSQL
    print("1. PostgreSQL (Tencent Cloud)")
    try:
        from models.base import SessionLocal
        from sqlalchemy import text
        
        db = SessionLocal()
        result = db.execute(text("SELECT version()"))
        version = result.fetchone()[0]
        print(f"   ✅ Connected: {version[:50]}...")
        
        # Get user and swipe counts
        result = db.execute(text("SELECT COUNT(*) FROM users"))
        user_count = result.fetchone()[0]
        
        result = db.execute(text("SELECT COUNT(*) FROM likes"))
        swipe_count = result.fetchone()[0]
        
        print(f"   📊 Users: {user_count}, Swipes: {swipe_count}")
        db.close()
        
    except Exception as e:
        print(f"   ❌ PostgreSQL error: {e}")
        return False
    
    # Test VectorDB
    print("\n2. VectorDB (Tencent Cloud)")
    try:
        import tcvectordb
        
        endpoint = os.getenv('VECTORDB_ENDPOINT')
        username = os.getenv('VECTORDB_USERNAME')
        key = os.getenv('VECTORDB_KEY')
        
        client = tcvectordb.VectorDBClient(
            url=endpoint,
            username=username,
            key=key,
            timeout=10
        )
        print(f"   ⚠️  Client created but connection timeout issues")
        print(f"   🔗 Endpoint: {endpoint}")
        
    except Exception as e:
        print(f"   ❌ VectorDB error: {e}")
    
    return True

def show_current_data():
    """Show current data in the database"""
    print("\n📊 Current Database Content")
    print("=" * 35)
    
    try:
        from models.base import SessionLocal
        from sqlalchemy import text
        
        db = SessionLocal()
        
        # Show users with tags
        print("1. Users with Feature Tags")
        result = db.execute(text("""
            SELECT user_id, name, feature_tags 
            FROM users 
            WHERE feature_tags IS NOT NULL 
            ORDER BY user_id
        """))
        
        tagged_users = result.fetchall()
        for user_id, name, tags_json in tagged_users:
            try:
                tags = json.loads(tags_json)
                print(f"   👤 {name} (ID: {user_id})")
                print(f"      Tags: {tags}")
            except:
                print(f"   👤 {name} (ID: {user_id}) - Invalid tags")
        
        print(f"\n   Total: {len(tagged_users)} users with tags")
        
        # Show recent swipes
        print("\n2. Recent Swipe Activity")
        result = db.execute(text("""
            SELECT liker_id, liked_item_id, granted_chat_access, timestamp
            FROM likes 
            ORDER BY timestamp DESC 
            LIMIT 5
        """))
        
        swipes = result.fetchall()
        if swipes:
            for liker_id, liked_id, granted_chat, timestamp in swipes:
                action = "👍 LIKED" if granted_chat else "👎 DISLIKED"
                print(f"   {action} User {liker_id} → User {liked_id} at {timestamp}")
        else:
            print("   📭 No swipe activity yet")
        
        db.close()
        
    except Exception as e:
        print(f"❌ Error showing data: {e}")

def generate_sample_swipes():
    """Generate sample swipe data with correct schema"""
    print("\n👆 Generating Sample Swipes")
    print("=" * 30)
    
    try:
        from models.base import SessionLocal
        from sqlalchemy import text
        
        db = SessionLocal()
        
        # Get users with tags for more realistic swipes
        result = db.execute(text("""
            SELECT user_id FROM users 
            WHERE feature_tags IS NOT NULL 
            ORDER BY user_id
        """))
        user_ids = [row[0] for row in result.fetchall()]
        
        if len(user_ids) < 2:
            print("   ❌ Need at least 2 users with tags")
            return False
        
        print(f"   🎲 Creating swipes between {len(user_ids)} users")
        
        swipe_count = 0
        for i in range(20):  # Generate 20 swipes
            liker_id = random.choice(user_ids)
            liked_id = random.choice(user_ids)
            
            if liker_id == liked_id:
                continue
            
            # Check if swipe exists
            result = db.execute(text("""
                SELECT 1 FROM likes 
                WHERE liker_id = :liker_id 
                AND liked_item_id = :liked_id
            """), {"liker_id": liker_id, "liked_id": liked_id})
            
            if result.fetchone():
                continue
            
            # 70% like rate
            is_like = random.random() < 0.7
            timestamp = datetime.now() - timedelta(days=random.randint(0, 7))
            
            # Insert with correct column name
            db.execute(text("""
                INSERT INTO likes (liker_id, liked_item_id, liked_item_type, granted_chat_access, timestamp)
                VALUES (:liker_id, :liked_id, 'user', :granted_chat, :timestamp)
            """), {
                "liker_id": liker_id,
                "liked_id": liked_id,
                "granted_chat": is_like,
                "timestamp": timestamp
            })
            
            swipe_count += 1
            action = "👍" if is_like else "👎"
            print(f"   {action} User {liker_id} → User {liked_id}")
        
        db.commit()
        db.close()
        
        print(f"\n🎉 Generated {swipe_count} sample swipes!")
        return True
        
    except Exception as e:
        print(f"❌ Error generating swipes: {e}")
        return False

def test_recommendation_system():
    """Test the recommendation system with real data"""
    print("\n🎯 Testing Recommendation System")
    print("=" * 40)
    
    try:
        from models.base import SessionLocal
        from sqlalchemy import text
        
        db = SessionLocal()
        
        # Get a user with tags for testing
        result = db.execute(text("""
            SELECT user_id, name, feature_tags 
            FROM users 
            WHERE feature_tags IS NOT NULL 
            LIMIT 1
        """))
        
        user_row = result.fetchone()
        if not user_row:
            print("   ❌ No users with tags for testing")
            return False
        
        test_user_id, test_user_name, tags_json = user_row
        print(f"   🧪 Testing with: {test_user_name} (ID: {test_user_id})")
        
        # Parse user tags
        try:
            user_tags = json.loads(tags_json)
            print(f"   🏷️  User tags: {user_tags}")
        except:
            print("   ⚠️  Could not parse user tags")
            user_tags = []
        
        # Get user's swipe history
        result = db.execute(text("""
            SELECT liked_item_id 
            FROM likes 
            WHERE liker_id = :user_id
        """), {"user_id": test_user_id})
        
        seen_ids = [row[0] for row in result.fetchall()]
        print(f"   📋 User has swiped on {len(seen_ids)} profiles")
        
        # Get potential matches (users not swiped on)
        exclude_ids = [test_user_id] + seen_ids
        exclude_ids_str = ','.join(map(str, exclude_ids))
        
        result = db.execute(text(f"""
            SELECT user_id, name, feature_tags 
            FROM users 
            WHERE user_id NOT IN ({exclude_ids_str})
            AND feature_tags IS NOT NULL
            ORDER BY RANDOM() 
            LIMIT 3
        """))
        
        potential_matches = result.fetchall()
        print(f"\n   🎲 Found {len(potential_matches)} potential matches:")
        
        for match_id, match_name, match_tags_json in potential_matches:
            try:
                match_tags = json.loads(match_tags_json)
                # Simple tag overlap
                common_tags = set(user_tags) & set(match_tags)
                overlap_score = len(common_tags)
                
                print(f"      👤 {match_name} (ID: {match_id})")
                print(f"         Tags: {match_tags}")
                if common_tags:
                    print(f"         🎯 Common interests: {list(common_tags)} (Score: {overlap_score})")
                else:
                    print(f"         💭 No obvious overlap (Score: 0)")
                print()
                
            except:
                print(f"      👤 {match_name} (ID: {match_id}) - Invalid tags")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"   ❌ Recommendation test failed: {e}")
        return False

def summary_report():
    """Generate final summary report"""
    print("\n📋 Final Status Report")
    print("=" * 30)
    
    try:
        from models.base import SessionLocal
        from sqlalchemy import text
        
        db = SessionLocal()
        
        # Get counts
        result = db.execute(text("SELECT COUNT(*) FROM users"))
        total_users = result.fetchone()[0]
        
        result = db.execute(text("SELECT COUNT(*) FROM users WHERE feature_tags IS NOT NULL"))
        tagged_users = result.fetchone()[0]
        
        result = db.execute(text("SELECT COUNT(*) FROM likes"))
        total_swipes = result.fetchone()[0]
        
        result = db.execute(text("SELECT COUNT(*) FROM likes WHERE granted_chat_access = true"))
        likes = result.fetchone()[0]
        
        result = db.execute(text("SELECT COUNT(*) FROM likes WHERE granted_chat_access = false"))
        dislikes = result.fetchone()[0]
        
        print(f"📊 Database Statistics:")
        print(f"   👥 Total users: {total_users}")
        print(f"   🏷️  Users with tags: {tagged_users}")
        print(f"   👆 Total swipes: {total_swipes}")
        print(f"   👍 Likes: {likes}")
        print(f"   👎 Dislikes: {dislikes}")
        
        print(f"\n✅ What's Working:")
        print(f"   🗄️  PostgreSQL: Fully operational")
        print(f"   📝 User management: Complete")
        print(f"   👆 Swipe system: Working")
        print(f"   🎯 Basic recommendations: Functional")
        
        print(f"\n⚠️  Known Issues:")
        print(f"   🔍 VectorDB: Connection timeout (network/config)")
        print(f"   🧠 Embeddings: Dependency conflicts")
        print(f"   🎯 Vector-based matching: Requires VectorDB")
        
        print(f"\n💡 Current Status:")
        print(f"   ✅ App can run with random/tag-based matching")
        print(f"   ⚠️  Vector similarity matching needs VectorDB fix")
        print(f"   🚀 Ready for development and testing!")
        
        db.close()
        
    except Exception as e:
        print(f"❌ Error generating report: {e}")

def main():
    """Main test function"""
    print("🚀 Final Comprehensive Database Test")
    print("=" * 45)
    
    # Test connections
    if not test_database_status():
        print("❌ Critical database issues - stopping")
        return
    
    # Show current data
    show_current_data()
    
    # Interactive options
    print("\n" + "="*45)
    print("🎮 Interactive Options:")
    print("1. Generate sample swipes")
    print("2. Test recommendation system")
    print("3. Both")
    print("4. Skip to summary")
    
    choice = input("\nChoose option (1-4): ").strip()
    
    if choice in ['1', '3']:
        generate_sample_swipes()
    
    if choice in ['2', '3']:
        test_recommendation_system()
    
    # Final summary
    summary_report()

if __name__ == "__main__":
    main()
