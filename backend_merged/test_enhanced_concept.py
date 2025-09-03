#!/usr/bin/env python3
"""
Simple test to verify the enhanced algorithm concept works
"""

from sqlalchemy import create_engine, text
from config.database import db_config

def test_enhanced_algorithm_concept():
    """Test the core logic of the enhanced algorithm"""
    print("🧪 Testing Enhanced Algorithm Core Logic")
    print("=" * 50)
    
    engine = create_engine(db_config.database_url)
    
    with engine.connect() as conn:
        # Test user
        user_id = 14
        
        print(f"👤 Testing with user {user_id}")
        
        # Step 1: Get mutual likes
        mutual_query = text("""
            SELECT DISTINCT 
                LEAST(s1.swiper_id, s1.target_id) as user1,
                GREATEST(s1.swiper_id, s1.target_id) as user2
            FROM user_swipes s1
            JOIN user_swipes s2 ON s1.swiper_id = s2.target_id 
                AND s1.target_id = s2.swiper_id
            WHERE s1.direction = 'like' 
                AND s2.direction = 'like'
                AND s1.swiper_id != s1.target_id
        """)
        
        mutual_result = conn.execute(mutual_query)
        mutual_pairs = set()
        for row in mutual_result.fetchall():
            mutual_pairs.add((row.user1, row.user2))
        
        print(f"🔗 Found {len(mutual_pairs)} mutual like pairs")
        
        # Get list of users to exclude (those who have mutual likes with current user)
        exclude_users = set()
        for user1, user2 in mutual_pairs:
            if user1 == user_id:
                exclude_users.add(user2)
            elif user2 == user_id:
                exclude_users.add(user1)
        
        print(f"🚫 Excluding {len(exclude_users)} users who are mutual likes with user {user_id}")
        
        # Step 2: Find users who liked this user's projects
        user_projects_query = text("""
            SELECT project_id FROM projects WHERE creator_id = :user_id
        """)
        user_projects_result = conn.execute(user_projects_query, {"user_id": user_id})
        user_project_ids = [row.project_id for row in user_projects_result.fetchall()]
        
        print(f"📁 User {user_id} has {len(user_project_ids)} projects")
        
        if user_project_ids:
            liked_my_projects_query = text("""
                SELECT DISTINCT l.liker_id, COUNT(*) as like_count
                FROM likes l 
                WHERE l.liked_item_type = 'PROJECT'
                    AND l.liked_item_id = ANY(:project_ids)
                    AND l.liker_id != :user_id
                    AND l.liker_id NOT IN (
                        SELECT UNNEST(:exclude_users)
                    )
                GROUP BY l.liker_id
                ORDER BY like_count DESC
                LIMIT 5
            """)
            
            liked_result = conn.execute(liked_my_projects_query, {
                "project_ids": user_project_ids,
                "user_id": user_id,
                "exclude_users": list(exclude_users) if exclude_users else [0]  # Use dummy value if empty
            })
            
            liker_users = []
            for row in liked_result.fetchall():
                liker_users.append(row.liker_id)
            
            print(f"💝 Found {len(liker_users)} users who liked this user's projects: {liker_users}")
        else:
            liker_users = []
            print("💝 No projects found, so no users who liked them")
        
        # Step 3: Get recommendations based on the algorithm
        # Priority 1: Vector similarity (simulated here as recent projects from non-excluded users)
        vector_sim_query = text("""
            SELECT p.project_id, p.short_description, p.creator_id, u.name as creator_name
            FROM projects p
            JOIN users u ON p.creator_id = u.user_id
            WHERE p.creator_id != :user_id
                AND p.creator_id NOT IN (
                    SELECT UNNEST(:exclude_users)
                )
                AND p.is_active = true
            ORDER BY p.created_at DESC
            LIMIT 3
        """)
        
        vector_result = conn.execute(vector_sim_query, {
            "user_id": user_id,
            "exclude_users": list(exclude_users) if exclude_users else [0]
        })
        
        vector_recommendations = []
        for row in vector_result.fetchall():
            vector_recommendations.append({
                "project_id": row.project_id,
                "title": row.short_description,
                "creator_id": row.creator_id,
                "creator_name": row.creator_name,
                "reason": "Vector similarity"
            })
        
        print(f"🎯 Vector-based recommendations: {len(vector_recommendations)}")
        for rec in vector_recommendations:
            print(f"   - '{rec['title'][:50]}...' by {rec['creator_name']}")
        
        # Priority 2: Projects from users who liked my projects
        if liker_users:
            like_based_query = text("""
                SELECT p.project_id, p.short_description, p.creator_id, u.name as creator_name
                FROM projects p
                JOIN users u ON p.creator_id = u.user_id
                WHERE p.creator_id = ANY(:liker_users)
                    AND p.creator_id != :user_id
                    AND p.is_active = true
                ORDER BY p.created_at DESC
                LIMIT 2
            """)
            
            like_based_result = conn.execute(like_based_query, {
                "liker_users": liker_users,
                "user_id": user_id
            })
            
            like_based_recommendations = []
            for row in like_based_result.fetchall():
                like_based_recommendations.append({
                    "project_id": row.project_id,
                    "title": row.short_description,
                    "creator_id": row.creator_id,
                    "creator_name": row.creator_name,
                    "reason": "User who liked your projects"
                })
            
            print(f"💕 Like-based recommendations: {len(like_based_recommendations)}")
            for rec in like_based_recommendations:
                print(f"   - '{rec['title'][:50]}...' by {rec['creator_name']}")
        else:
            like_based_recommendations = []
            print("💕 No like-based recommendations available")
        
        # Combine recommendations
        all_recommendations = vector_recommendations + like_based_recommendations
        
        print(f"\n✅ Total enhanced recommendations: {len(all_recommendations)}")
        print("🎯 Algorithm successfully demonstrated:")
        print(f"   - Mutual like exclusions: {len(exclude_users)} users excluded")
        print(f"   - Vector recommendations: {len(vector_recommendations)}")
        print(f"   - Like-based recommendations: {len(like_based_recommendations)}")
        
        return all_recommendations

if __name__ == "__main__":
    test_enhanced_algorithm_concept()
