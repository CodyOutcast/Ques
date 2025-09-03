#!/usr/bin/env python3
"""
Test the actual Enhanced Recommendation Service
"""

import sys
import os
from sqlalchemy.orm import Session

# Add the parent directory to the path so we can import modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dependencies.db import get_db
from services.enhanced_recommendations import EnhancedRecommendationService

def test_enhanced_recommendations():
    """Test the enhanced recommendation service with real data"""
    print("🧪 Testing Enhanced Recommendation Service")
    print("=" * 60)
    
    # Get database session
    db_gen = get_db()
    db: Session = next(db_gen)
    
    try:
        # Test with user ID 14 (from our previous test)
        user_id = 14
        limit = 5
        
        print(f"👤 Getting recommendations for user {user_id}")
        
        # Test mutual like detection
        print("\n🔍 Step 1: Checking mutual likes")
        mutual_pairs = EnhancedRecommendationService.get_mutual_like_pairs(db)
        print(f"📊 Found {len(mutual_pairs)} mutual like pairs")
        for pair in list(mutual_pairs)[:5]:  # Show first 5
            print(f"   - User {pair[0]} ↔ User {pair[1]}")
        
        # Test users who liked this user's projects
        print("\n🔍 Step 2: Finding users who liked user's projects")
        liked_users = EnhancedRecommendationService.get_users_who_liked_my_projects(db, user_id)
        print(f"💝 Found {len(liked_users)} users who liked user {user_id}'s projects")
        for user_data in liked_users[:3]:  # Show first 3
            print(f"   - {user_data['name']} liked: {user_data['liked_project_title']}")
        
        # Test the full enhanced algorithm
        print("\n🔍 Step 3: Running enhanced recommendation algorithm")
        recommendations = EnhancedRecommendationService.get_enhanced_recommendations(db, user_id, limit)
        
        print(f"🎯 Generated {len(recommendations)} recommendations:")
        for i, rec in enumerate(recommendations, 1):
            print(f"   {i}. '{rec['title']}' by {rec.get('creator_name', 'Unknown')}")
            if 'recommendation_reason' in rec:
                print(f"      💡 Reason: {rec['recommendation_reason']}")
        
        # Test edge cases
        print("\n🔍 Step 4: Testing edge cases")
        
        # Test with non-existent user
        empty_recs = EnhancedRecommendationService.get_enhanced_recommendations(db, 99999, 5)
        print(f"📭 Non-existent user recommendations: {len(empty_recs)}")
        
        # Test with limit 0
        zero_recs = EnhancedRecommendationService.get_enhanced_recommendations(db, user_id, 0)
        print(f"📭 Zero limit recommendations: {len(zero_recs)}")
        
        print("\n✅ Enhanced recommendation service test completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()

if __name__ == "__main__":
    test_enhanced_recommendations()
