#!/usr/bin/env python3
"""
Simple test for enhanced recommendation algorithm using direct SQL
"""

from dependencies.db import SessionLocal
from sqlalchemy import text

def test_enhanced_algorithm_sql():
    """Test the enhanced recommendation algorithm using direct SQL"""
    
    print("🧪 Testing Enhanced Recommendation Algorithm (SQL)")
    print("=" * 60)
    
    db = SessionLocal()
    try:
        # Test 1: Check for mutual likes
        print("🔍 Test 1: Checking for Mutual Likes")
        
        mutual_query = text("""
            SELECT DISTINCT s1.swiper_id, s1.target_id
            FROM user_swipes s1
            JOIN user_swipes s2 ON s1.swiper_id = s2.target_id 
                                AND s1.target_id = s2.swiper_id
            WHERE s1.direction = 'like' AND s2.direction = 'like'
            LIMIT 5
        """)
        
        result = db.execute(mutual_query)
        mutual_pairs = result.fetchall()
        
        print(f"📊 Found {len(mutual_pairs)} mutual like pairs:")
        for pair in mutual_pairs:
            print(f"   - User {pair[0]} ↔ User {pair[1]}")
        
        # Test 2: Check project likes
        print(f"\n🔍 Test 2: Project Likes")
        
        project_likes_query = text("""
            SELECT
                l.liker_id,
                l.liked_item_id as project_id,
                u.name as liker_name,
                p.short_description as project_title,
                p.creator_id as project_owner
            FROM likes l
            JOIN users u ON l.liker_id = u.user_id
            JOIN projects p ON l.liked_item_id = p.project_id
            WHERE l.liked_item_type = 'PROJECT'
            LIMIT 5
        """)
        result = db.execute(project_likes_query)
        project_likes = result.fetchall()
        
        print(f"📊 Found {len(project_likes)} project likes:")
        for like in project_likes:
            print(f"   - {like.liker_name} liked '{like.project_title}' by user {like.project_owner}")
        
        # Test 3: Simulate enhanced algorithm logic
        print(f"\n🔍 Test 3: Enhanced Algorithm Simulation")
        
        # Get a test user
        user_query = text("SELECT user_id, name FROM users WHERE user_id IS NOT NULL LIMIT 1")
        user_result = db.execute(user_query)
        test_user = user_result.fetchone()
        
        if not test_user:
            print("❌ No users found")
            return
        
        user_id = test_user.user_id
        print(f"👤 Testing with user: {test_user.name} (ID: {user_id})")
        
        # Step 1: Find mutual like partners to exclude
        mutual_exclude_query = text("""
            SELECT DISTINCT 
                CASE 
                    WHEN s1.swiper_id = :user_id THEN s1.target_id
                    ELSE s1.swiper_id
                END as mutual_user_id
            FROM user_swipes s1
            JOIN user_swipes s2 ON s1.swiper_id = s2.target_id 
                                AND s1.target_id = s2.swiper_id
            WHERE s1.direction = 'like' AND s2.direction = 'like'
                AND (:user_id = s1.swiper_id OR :user_id = s1.target_id)
        """)
        
        result = db.execute(mutual_exclude_query, {"user_id": user_id})
        mutual_users = [row.mutual_user_id for row in result.fetchall()]
        
        print(f"🚫 Excluding projects from {len(mutual_users)} mutual like users: {mutual_users}")
        
        # Step 2: Find users who liked this user's projects
        users_who_liked_query = text("""
            SELECT DISTINCT 
                l.liker_id,
                u.name as liker_name,
                p.short_description as liked_project,
                p.project_id
            FROM likes l
            JOIN users u ON l.liker_id = u.user_id
            JOIN projects p ON l.liked_item_id = p.project_id
            WHERE l.liked_item_type = 'PROJECT' 
                AND p.creator_id = :user_id
                AND l.liker_id != :user_id
                AND l.liker_id != ALL(:mutual_users)
            LIMIT 5
        """)
        
        result = db.execute(users_who_liked_query, {
            "user_id": user_id,
            "mutual_users": mutual_users if mutual_users else [0]  # Avoid empty array issue
        })
        
        users_who_liked = result.fetchall()
        print(f"💝 Found {len(users_who_liked)} users who liked this user's projects:")
        for like in users_who_liked:
            print(f"   - {like.liker_name} liked '{like.liked_project}'")
        
        # Step 3: Get projects from these users (one per user)
        if users_who_liked:
            like_based_projects_query = text("""
                SELECT DISTINCT ON (p.creator_id)
                    p.project_id,
                    p.title,
                    p.creator_id,
                    u.name as creator_name
                FROM project_cards p
                JOIN users u ON p.creator_id = u.user_id
                WHERE p.creator_id = ANY(:liker_ids)
                    AND p.is_active = true
                    AND p.creator_id != :user_id
                ORDER BY p.creator_id, p.created_at DESC
            """)
            
            liker_ids = [like.liker_id for like in users_who_liked]
            result = db.execute(like_based_projects_query, {
                "liker_ids": liker_ids,
                "user_id": user_id
            })
            
            like_based_projects = result.fetchall()
            print(f"🎯 Like-based project recommendations ({len(like_based_projects)}):")
            for project in like_based_projects:
                print(f"   - '{project.title}' by {project.creator_name}")
        
        # Step 4: Fill remaining with recent projects
        remaining_projects_query = text("""
            SELECT
                p.project_id,
                p.short_description as title,
                p.creator_id,
                u.name as creator_name
            FROM projects p
            JOIN users u ON p.creator_id = u.user_id
            WHERE p.is_active = true
                AND p.creator_id != :user_id
                AND p.creator_id != ALL(:mutual_users)
            ORDER BY p.created_at DESC
            LIMIT 10
        """)
        result = db.execute(remaining_projects_query, {
            "user_id": user_id,
            "mutual_users": mutual_users if mutual_users else [0]
        })
        
        recent_projects = result.fetchall()
        print(f"🔄 Recent project recommendations ({len(recent_projects)}):")
        for project in recent_projects[:5]:  # Show first 5
            print(f"   - '{project.title}' by {project.creator_name}")
        
        print(f"\n✅ Enhanced algorithm simulation completed!")
        print(f"📊 Algorithm Summary:")
        print(f"   🚫 Mutual exclusions: {len(mutual_users)}")
        print(f"   💝 Like-based recommendations: {len(users_who_liked) if users_who_liked else 0}")
        print(f"   🔄 Fallback recommendations: {len(recent_projects)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    test_enhanced_algorithm_sql()
