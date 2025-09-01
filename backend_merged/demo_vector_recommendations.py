#!/usr/bin/env python3
"""
Quick demo of vector-based project recommendations
"""

import sys
sys.path.append('.')

from services.vector_recommendations import VectorRecommendationService
from dependencies.db import SessionLocal
from models.users import User
from models.project_cards import ProjectCard
import json

def demo_recommendations():
    """Demo the vector recommendation system with real data"""
    db = SessionLocal()
    try:
        print("🎯 Vector-based Project Recommendation Demo")
        print("=" * 60)
        
        # Get users with vector_id
        users_with_vectors = db.query(User).filter(User.vector_id.isnot(None)).limit(3).all()
        print(f"📊 Found {len(users_with_vectors)} users with vectors")
        
        # Get projects
        projects = db.query(ProjectCard).limit(5).all()
        print(f"📊 Found {len(projects)} projects")
        
        if users_with_vectors and projects:
            print("\n🔍 Testing user-to-project recommendations:")
            
            for user in users_with_vectors[:2]:  # Test first 2 users
                print(f"\n👤 User: {user.name}")
                print(f"   Bio: {user.bio[:80]}..." if user.bio else "   No bio available")
                
                # Get recommendations for this user
                recommendations = VectorRecommendationService.get_recommended_projects_for_user(
                    user_id=user.user_id,
                    limit=3
                )
                
                if recommendations:
                    print(f"📋 Top {len(recommendations)} recommendations:")
                    for i, rec in enumerate(recommendations, 1):
                        print(f"   {i}. {rec.get('title', 'No Title')}")
                        print(f"      {rec.get('description', 'No description')[:60]}...")
                        if rec.get('tags'):
                            print(f"      Tags: {rec['tags'][:3]}")  # Show first 3 tags
                else:
                    print("   ❌ No recommendations found")
        
        if projects:
            print(f"\n✅ Testing user-to-project recommendations completed!")
        
        print(f"\n✅ Demo completed!")
        
    except Exception as e:
        print(f"❌ Demo error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    demo_recommendations()
