#!/usr/bin/env python3
"""
Test Vector-based Project Card Recommendations
"""

import os
import sys
import json
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)

try:
    from services.vector_recommendations import VectorRecommendationService
    from models.project_cards import ProjectCard, ProjectType, ModerationStatus
    from models.users import User
    from dependencies.db import SessionLocal
    from sqlalchemy import text
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

def create_test_project_card(db, user_id: int, title: str, description: str, 
                           category: str, looking_for: list, skills_needed: list):
    """Create a test project card"""
    project = ProjectCard(
        creator_id=user_id,
        title=title,
        description=description,
        short_description=description[:200],
        category=category,
        project_type=ProjectType.STARTUP,
        looking_for=looking_for,
        skills_needed=skills_needed,
        feature_tags=skills_needed + [category],
        moderation_status=ModerationStatus.APPROVED,
        is_active=True
    )
    
    db.add(project)
    db.commit()
    db.refresh(project)
    return project

def test_vector_recommendations():
    """Test the vector recommendation system"""
    print("🧪 Testing Vector-based Project Card Recommendations")
    print("=" * 60)
    
    db = SessionLocal()
    try:
        # Check if we have users to work with
        users = db.query(User).limit(5).all()
        if len(users) < 2:
            print("❌ Need at least 2 users in database for testing")
            return False
        
        print(f"📊 Found {len(users)} users for testing")
        
        # Create some test project cards if none exist
        existing_projects = db.query(ProjectCard).count()
        print(f"📊 Found {existing_projects} existing projects")
        
        if existing_projects == 0:
            print("🔨 Creating test project cards...")
            
            # Create AI/ML project
            ai_project = create_test_project_card(
                db, users[0].user_id,
                "AI-Powered Data Analytics Platform",
                "Building an advanced AI platform for business intelligence and predictive analytics. Using machine learning to transform raw data into actionable insights.",
                "technology",
                ["investor", "data_scientist", "frontend_developer"],
                ["python", "machine_learning", "tensorflow", "react"]
            )
            
            # Create blockchain project
            blockchain_project = create_test_project_card(
                db, users[1].user_id if len(users) > 1 else users[0].user_id,
                "Decentralized Finance Protocol",
                "Revolutionary DeFi protocol for cross-chain liquidity mining and yield farming. Smart contracts built on Ethereum and Polygon.",
                "fintech",
                ["investor", "blockchain_developer", "security_auditor"],
                ["solidity", "web3", "defi", "smart_contracts"]
            )
            
            # Create mobile app project  
            if len(users) > 2:
                mobile_project = create_test_project_card(
                    db, users[2].user_id,
                    "Social Fitness Mobile App",
                    "Community-driven fitness app with social features, workout tracking, and gamification elements.",
                    "lifestyle",
                    ["mobile_developer", "ui_designer", "marketing_expert"],
                    ["react_native", "nodejs", "firebase", "design"]
                )
            
            print("✅ Created test project cards")
        
        # Test 1: Update user vectors
        print("\n🔍 Test 1: Updating User Vectors")
        test_user = users[0]
        print(f"Testing with user: {test_user.name} (ID: {test_user.user_id})")
        
        vector_id = VectorRecommendationService.update_user_vector(db, test_user.user_id)
        if vector_id:
            print(f"✅ Updated user vector: {vector_id}")
        else:
            print("❌ Failed to update user vector")
        
        # Test 2: Update project vectors
        print("\n🔍 Test 2: Updating Project Vectors")
        projects = db.query(ProjectCard).limit(3).all()
        
        for project in projects:
            vector_id = VectorRecommendationService.update_project_vector(db, project.project_id)
            if vector_id:
                print(f"✅ Updated project vector: {project.title} -> {vector_id}")
            else:
                print(f"❌ Failed to update project vector: {project.title}")
        
        # Test 3: Get recommendations for user
        print("\n🔍 Test 3: Getting Personalized Recommendations")
        recommendations = VectorRecommendationService.get_recommended_projects_for_user(
            user_id=test_user.user_id,
            limit=5
        )
        
        print(f"📋 Found {len(recommendations)} recommendations for {test_user.name}:")
        for i, card in enumerate(recommendations, 1):
            print(f"  {i}. {card['title']}")
            print(f"     Tags: {card.get('tags', [])}")
            print(f"     Looking for: {card.get('lookingFor', {}).get('tags', [])}")
            print()
        
        # Test 4: Get similar users for a project
        if projects:
            print(f"🔍 Test 4: Finding Similar Users for Project")
            test_project = projects[0]
            print(f"Testing with project: {test_project.title}")
            
            similar_users = VectorRecommendationService.get_similar_users_for_project(
                project_id=test_project.project_id,
                limit=5
            )
            
            print(f"📋 Found {len(similar_users)} similar users:")
            for i, user in enumerate(similar_users, 1):
                print(f"  {i}. {user['name']}")
                print(f"     Bio: {user.get('bio', 'No bio')[:100]}...")
                print(f"     Tags: {user.get('feature_tags', [])}")
                print()
        
        print("✅ All vector recommendation tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Test error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

def test_card_conversion():
    """Test project card conversion to dict format"""
    print("\n🔍 Test: Project Card Conversion")
    
    db = SessionLocal()
    try:
        projects = db.query(ProjectCard).limit(3).all()
        
        for project in projects:
            try:
                card_dict = project.to_card_dict()
                print(f"✅ Successfully converted: {project.title}")
                print(f"   Keys: {list(card_dict.keys())}")
                
                # Validate required fields
                required_fields = ['id', 'title', 'description', 'tags', 'type', 'owner']
                missing_fields = [field for field in required_fields if field not in card_dict]
                
                if missing_fields:
                    print(f"   ⚠️ Missing fields: {missing_fields}")
                else:
                    print(f"   ✅ All required fields present")
                
            except Exception as e:
                print(f"❌ Failed to convert {project.title}: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Card conversion test error: {e}")
        return False
    finally:
        db.close()

def main():
    """Run all tests"""
    print("🧪 Vector Recommendation System Test Suite")
    print("=" * 60)
    
    # Test vector recommendations
    vector_success = test_vector_recommendations()
    
    # Test card conversion
    card_success = test_card_conversion()
    
    # Summary
    print("\n" + "=" * 60)
    print("🎯 Test Results Summary:")
    print(f"  Vector Recommendations: {'✅ PASS' if vector_success else '❌ FAIL'}")
    print(f"  Card Conversion: {'✅ PASS' if card_success else '❌ FAIL'}")
    
    overall_success = all([vector_success, card_success])
    print(f"\n🎉 Overall Status: {'✅ ALL TESTS PASSED' if overall_success else '❌ SOME TESTS FAILED'}")
    
    return overall_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
