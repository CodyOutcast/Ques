#!/usr/bin/env python3
"""
Test the enhanced recommendation algorithm
"""

import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dependencies.db import SessionLocal
from services.enhanced_recommendations import EnhancedRecommendationService
from models.users import User
from models.project_cards import ProjectCard
from models.likes import Like, UserSwipe
from sqlalchemy import text

def test_enhanced_recommendations():
    """Test the enhanced recommendation algorithm"""
    
    print("🧪 Testing Enhanced Recommendation Algorithm")
    print("=" * 60)
    
    db = SessionLocal()
    try:
        # Get a test user
        test_user = db.query(User).first()
        if not test_user:
            print("❌ No test users found")
            return
        
        user_id = test_user.user_id
        print(f"👤 Testing with user: {test_user.name} (ID: {user_id})")
        
        # Test 1: Check mutual like pairs
        print(f"\n🔍 Test 1: Checking Mutual Like Pairs")
        mutual_pairs = EnhancedRecommendationService.get_mutual_like_pairs(db)
        print(f"📊 Found {len(mutual_pairs)} mutual like pairs in the system")
        
        # Show user's mutual likes
        user_mutual_likes = [pair for pair in mutual_pairs if user_id in pair]
        if user_mutual_likes:
            print(f"💕 User {user_id} has mutual likes with:")
            for pair in user_mutual_likes:
                other_user = pair[1] if pair[0] == user_id else pair[0]
                other_user_obj = db.query(User).filter(User.user_id == other_user).first()
                print(f"   - User {other_user} ({other_user_obj.name if other_user_obj else 'Unknown'})")
        else:
            print(f"💔 User {user_id} has no mutual likes yet")
        
        # Test 2: Check users who liked current user's projects
        print(f"\n🔍 Test 2: Users Who Liked My Projects")
        users_who_liked = EnhancedRecommendationService.get_users_who_liked_my_projects(db, user_id)
        print(f"📊 Found {len(users_who_liked)} users who liked user {user_id}'s projects")
        
        for i, user_data in enumerate(users_who_liked[:3]):  # Show first 3
            print(f"   {i+1}. {user_data['name']} liked project: {user_data['liked_project_title']}")
        
        # Test 3: Get enhanced recommendations
        print(f"\n🔍 Test 3: Enhanced Recommendations")
        recommendations = EnhancedRecommendationService.get_enhanced_recommendations(
            user_id=user_id,
            limit=10,
            exclude_own_projects=True
        )
        
        print(f"📊 Generated {len(recommendations)} enhanced recommendations:")
        
        vector_based = 0
        like_based = 0
        fallback = 0
        
        for i, card in enumerate(recommendations, 1):
            recommendation_reason = card.get('recommendation_reason', 'Vector similarity')
            liker_context = card.get('liker_context')
            
            print(f"   {i}. {card.get('title', 'Untitled')} by {card.get('owner', {}).get('name', 'Unknown')}")
            print(f"      Reason: {recommendation_reason}")
            
            if 'Vector similarity' in recommendation_reason:
                vector_based += 1
            elif 'This user liked your project' in recommendation_reason:
                like_based += 1
                if liker_context:
                    print(f"      Context: {liker_context['user_name']} liked '{liker_context['liked_project']}'")
            else:
                fallback += 1
        
        print(f"\n📊 Recommendation Breakdown:")
        print(f"   🎯 Vector-based: {vector_based}")
        print(f"   💝 Like-based: {like_based}")
        print(f"   🔄 Fallback: {fallback}")
        
        # Test 4: Verify mutual exclusion
        print(f"\n🔍 Test 4: Mutual Exclusion Verification")
        mutual_user_ids = set()
        for pair in mutual_pairs:
            if user_id in pair:
                other_user = pair[1] if pair[0] == user_id else pair[0]
                mutual_user_ids.add(other_user)
        
        excluded_projects = 0
        for card in recommendations:
            creator_id = card.get('owner', {}).get('id')
            if creator_id in mutual_user_ids:
                excluded_projects += 1
                print(f"⚠️  Found project from mutual like user {creator_id} - this shouldn't happen!")
        
        if excluded_projects == 0:
            print("✅ No projects from mutual like users found - exclusion working correctly!")
        
        print(f"\n🎉 Enhanced recommendation test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

def create_test_data(db):
    """Create some test data for demonstration"""
    print("🔧 Creating test data...")
    
    # This would create test likes, projects, etc.
    # For now, we'll work with existing data
    pass

if __name__ == "__main__":
    test_enhanced_recommendations()
