#!/usr/bin/env python3
"""
Test enhanced recommendations using direct SQL to avoid model conflicts
"""

from sqlalchemy import create_engine, text
from config.database import db_config

def test_enhanced_recommendations_sql():
    """Test the enhanced recommendation service using direct SQL"""
    print("🧪 Testing Enhanced Recommendation Service (SQL-Only)")
    print("=" * 60)
    
    engine = create_engine(db_config.database_url)
    
    with engine.connect() as conn:
        user_id = 14
        limit = 5
        
        print(f"👤 Getting recommendations for user {user_id}")
        
        # Step 1: Get mutual likes (working from previous test)
        print("\n🔍 Step 1: Checking mutual likes")
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
        
        print(f"📊 Found {len(mutual_pairs)} mutual like pairs:")
        for i, (u1, u2) in enumerate(list(mutual_pairs)[:5]):
            print(f"   {i+1}. User {u1} ↔ User {u2}")
        
        # Get users to exclude for current user
        exclude_users = set()
        for user1, user2 in mutual_pairs:
            if user1 == user_id:
                exclude_users.add(user2)
            elif user2 == user_id:
                exclude_users.add(user1)
        
        print(f"🚫 Excluding {len(exclude_users)} mutual like users for user {user_id}")
        
        # Step 2: Find users who liked this user's projects
        print("\n🔍 Step 2: Finding users who liked user's projects")
        
        # Get user's projects
        user_projects_query = text("""
            SELECT project_id, short_description 
            FROM projects 
            WHERE creator_id = :user_id AND is_active = true
        """)
        user_projects_result = conn.execute(user_projects_query, {"user_id": user_id})
        user_projects = list(user_projects_result.fetchall())
        
        print(f"📁 User has {len(user_projects)} active projects")
        
        if user_projects:
            project_ids = [p.project_id for p in user_projects]
            
            # Find who liked these projects
            liked_my_projects_query = text("""
                SELECT DISTINCT 
                    l.liker_id,
                    u.name as liker_name,
                    COUNT(*) as like_count
                FROM likes l 
                JOIN users u ON l.liker_id = u.user_id
                WHERE l.liked_item_type = 'PROJECT'
                    AND l.liked_item_id = ANY(:project_ids)
                    AND l.liker_id != :user_id
                    AND l.liker_id NOT IN (
                        SELECT UNNEST(:exclude_users)
                    )
                GROUP BY l.liker_id, u.name
                ORDER BY like_count DESC
                LIMIT 10
            """)
            
            liked_result = conn.execute(liked_my_projects_query, {
                "project_ids": project_ids,
                "user_id": user_id,
                "exclude_users": list(exclude_users) if exclude_users else [0]
            })
            
            liker_users = []
            for row in liked_result.fetchall():
                liker_users.append({
                    "user_id": row.liker_id,
                    "name": row.liker_name,
                    "like_count": row.like_count
                })
            
            print(f"💝 Found {len(liker_users)} users who liked this user's projects:")
            for user_data in liker_users:
                print(f"   - {user_data['name']} (liked {user_data['like_count']} projects)")
        else:
            liker_users = []
            print("💝 No active projects found")
        
        # Step 3: Generate enhanced recommendations
        print("\n🔍 Step 3: Generating enhanced recommendations")
        
        # Vector similarity simulation (get recent projects excluding mutual likes)
        vector_sim_query = text("""
            SELECT 
                p.project_id,
                p.short_description as title,
                p.creator_id,
                u.name as creator_name,
                p.created_at
            FROM projects p
            JOIN users u ON p.creator_id = u.user_id
            WHERE p.creator_id != :user_id
                AND p.is_active = true
                AND p.creator_id NOT IN (
                    SELECT UNNEST(:exclude_users)
                )
            ORDER BY p.created_at DESC
            LIMIT :limit
        """)
        
        vector_result = conn.execute(vector_sim_query, {
            "user_id": user_id,
            "exclude_users": list(exclude_users) if exclude_users else [0],
            "limit": limit
        })
        
        recommendations = []
        for row in vector_result.fetchall():
            recommendations.append({
                "project_id": row.project_id,
                "title": row.title[:80] + "..." if len(row.title) > 80 else row.title,
                "creator_id": row.creator_id,
                "creator_name": row.creator_name,
                "recommendation_type": "vector_similarity",
                "created_at": row.created_at
            })
        
        print(f"🎯 Generated {len(recommendations)} vector-based recommendations")
        
        # Fill remaining slots with like-based recommendations
        if len(recommendations) < limit and liker_users:
            remaining_slots = limit - len(recommendations)
            used_creator_ids = {r["creator_id"] for r in recommendations}
            
            like_based_query = text("""
                SELECT 
                    p.project_id,
                    p.short_description as title,
                    p.creator_id,
                    u.name as creator_name,
                    p.created_at
                FROM projects p
                JOIN users u ON p.creator_id = u.user_id
                WHERE p.creator_id = ANY(:liker_user_ids)
                    AND p.creator_id != :user_id
                    AND p.is_active = true
                    AND p.creator_id NOT IN (
                        SELECT UNNEST(:used_creator_ids)
                    )
                ORDER BY p.created_at DESC
                LIMIT :remaining_slots
            """)
            
            liker_user_ids = [u["user_id"] for u in liker_users]
            like_result = conn.execute(like_based_query, {
                "liker_user_ids": liker_user_ids,
                "user_id": user_id,
                "used_creator_ids": list(used_creator_ids) if used_creator_ids else [0],
                "remaining_slots": remaining_slots
            })
            
            for row in like_result.fetchall():
                recommendations.append({
                    "project_id": row.project_id,
                    "title": row.title[:80] + "..." if len(row.title) > 80 else row.title,
                    "creator_id": row.creator_id,
                    "creator_name": row.creator_name,
                    "recommendation_type": "like_based",
                    "created_at": row.created_at
                })
        
        # Display final recommendations
        print(f"\n🎯 Final Enhanced Recommendations ({len(recommendations)}):")
        for i, rec in enumerate(recommendations, 1):
            print(f"   {i}. [{rec['recommendation_type'].upper()}] '{rec['title']}' by {rec['creator_name']}")
        
        print(f"\n✅ Enhanced Algorithm Test Complete!")
        print(f"📊 Summary:")
        print(f"   - Mutual like pairs detected: {len(mutual_pairs)}")
        print(f"   - Users excluded (mutual likes): {len(exclude_users)}")
        print(f"   - Users who liked current user's projects: {len(liker_users)}")
        print(f"   - Total recommendations generated: {len(recommendations)}")
        print(f"   - Vector-based: {len([r for r in recommendations if r['recommendation_type'] == 'vector_similarity'])}")
        print(f"   - Like-based: {len([r for r in recommendations if r['recommendation_type'] == 'like_based'])}")
        
        return recommendations

if __name__ == "__main__":
    test_enhanced_recommendations_sql()
