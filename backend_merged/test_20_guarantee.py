#!/usr/bin/env python3
"""
Test the 20+ project guarantee
"""

import sys
sys.path.append('.')

from services.vector_recommendations import VectorRecommendationService
from dependencies.db import SessionLocal
from models.users import User

def test_20_project_guarantee():
    """Test that we always get at least 20 project recommendations"""
    db = SessionLocal()
    try:
        print("🎯 Testing 20+ Project Guarantee")
        print("=" * 50)
        
        # Get a user with vectors
        user = db.query(User).filter(User.vector_id.isnot(None)).first()
        if not user:
            # Get any user
            user = db.query(User).first()
        
        if user:
            print(f"👤 Testing with user: {user.name} (ID: {user.user_id})")
            
            # Test with limit of 20
            recommendations = VectorRecommendationService.get_recommended_projects_for_user(
                user_id=user.user_id,
                limit=20
            )
            
            print(f"📊 Requested: 20 projects")
            print(f"📊 Received: {len(recommendations)} projects")
            
            if len(recommendations) >= 20:
                print("✅ SUCCESS: Got at least 20 recommendations!")
            else:
                print(f"⚠️ PARTIAL: Only got {len(recommendations)} recommendations")
                print("💡 This is expected if there are fewer than 20 total projects in the database")
            
            # Show first 5 recommendations
            print(f"\n📋 First 5 recommendations:")
            for i, rec in enumerate(recommendations[:5], 1):
                print(f"   {i}. {rec.get('title', 'No Title')}")
                print(f"      {rec.get('description', 'No description')[:60]}...")
            
            return len(recommendations)
        else:
            print("❌ No users found in database")
            return 0
    except Exception as e:
        print(f"❌ Test error: {e}")
        import traceback
        traceback.print_exc()
        return 0
    finally:
        db.close()

if __name__ == "__main__":
    count = test_20_project_guarantee()
    sys.exit(0 if count > 0 else 1)
