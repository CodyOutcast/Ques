"""
Demo script showing how auto tag generation would work
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import json
import re
from typing import List

def mock_extract_tags_from_bio(bio: str) -> List[str]:
    """
    Mock function to demonstrate tag extraction from bio
    In real implementation, this would call DeepSeek API
    """
    # Available tags (from our database analysis)
    available_tags = [
        "Web Development", "Mobile Development", "Data Science", "AI/ML", 
        "Blockchain", "Gaming", "Design", "Marketing", "Business", 
        "Entrepreneurship", "Music", "Art", "Photography", "Sports", "Travel"
    ]
    
    # Simple keyword matching (would be replaced by AI in real implementation)
    keyword_mapping = {
        "Web Development": ["web", "website", "react", "angular", "vue", "html", "css", "javascript", "frontend", "backend"],
        "Mobile Development": ["mobile", "app", "ios", "android", "flutter", "react native"],
        "Data Science": ["data", "analytics", "statistics", "python", "r", "sql", "analysis"],
        "AI/ML": ["ai", "artificial intelligence", "machine learning", "ml", "deep learning", "neural network"],
        "Blockchain": ["blockchain", "crypto", "bitcoin", "ethereum", "defi", "smart contract"],
        "Gaming": ["game", "gaming", "unity", "unreal", "esports", "video game"],
        "Design": ["design", "ui", "ux", "figma", "photoshop", "creative", "visual"],
        "Marketing": ["marketing", "social media", "advertising", "campaign", "brand"],
        "Business": ["business", "strategy", "consulting", "management", "operations"],
        "Entrepreneurship": ["startup", "entrepreneur", "founder", "business", "venture"],
        "Music": ["music", "guitar", "piano", "singing", "composer", "band"],
        "Art": ["art", "painting", "drawing", "artist", "creative", "illustration"],
        "Photography": ["photo", "photography", "camera", "photographer", "visual"],
        "Sports": ["sport", "fitness", "gym", "running", "basketball", "football", "soccer"],
        "Travel": ["travel", "traveling", "explore", "adventure", "countries", "culture"]
    }
    
    bio_lower = bio.lower()
    extracted_tags = []
    
    # Find matching tags based on keywords
    for tag, keywords in keyword_mapping.items():
        for keyword in keywords:
            if keyword in bio_lower:
                if tag not in extracted_tags:
                    extracted_tags.append(tag)
                break
    
    # Return top 3-6 most relevant tags
    return extracted_tags[:6]

def demo_auto_tag_generation():
    """Demo the auto tag generation functionality"""
    print("🏷️  Auto Tag Generation Demo")
    print("=" * 50)
    
    # Test cases with different user bios
    test_cases = [
        {
            "name": "Software Engineer",
            "bio": "I'm a software engineer with 5 years of experience in Python and React. I love building innovative web applications and am passionate about AI/ML. Currently working on a startup that uses machine learning to optimize supply chains. In my free time, I enjoy hiking, photography, and playing guitar."
        },
        {
            "name": "Marketing Specialist", 
            "bio": "Digital marketing specialist focusing on social media campaigns and brand strategy. Love photography and travel in my spare time. Always looking for creative ways to engage audiences."
        },
        {
            "name": "Blockchain Developer",
            "bio": "Blockchain developer working on DeFi protocols and smart contracts. Also interested in gaming and competitive esports. Building the future of decentralized finance."
        },
        {
            "name": "UX Designer",
            "bio": "UX/UI designer with a background in psychology. Enjoy creating user-centered designs and playing music. Passionate about making technology accessible to everyone."
        },
        {
            "name": "Data Scientist",
            "bio": "Data scientist specializing in machine learning for healthcare. Passionate about sports analytics and hiking. Using data to make better decisions."
        },
        {
            "name": "User without tags",
            "bio": "Just a regular person who likes to learn new things and meet interesting people. Looking for opportunities to collaborate and grow."
        }
    ]
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n--- Test Case {i}: {test_case['name']} ---")
        print(f"📝 Bio: {test_case['bio'][:100]}{'...' if len(test_case['bio']) > 100 else ''}")
        
        # Extract tags using mock function
        extracted_tags = mock_extract_tags_from_bio(test_case['bio'])
        
        print(f"🏷️  Auto-generated tags: {extracted_tags}")
        print(f"📊 Number of tags: {len(extracted_tags)}")
        
        results.append({
            'name': test_case['name'],
            'bio': test_case['bio'],
            'tags': extracted_tags
        })
    
    # Summary
    print("\n\n📋 Summary of Auto Tag Generation")
    print("=" * 50)
    
    for result in results:
        print(f"👤 {result['name']}")
        print(f"   Tags: {', '.join(result['tags']) if result['tags'] else 'No tags extracted'}")
        print()
    
    return results

def demo_integration_workflow():
    """Demo how this would integrate with the profile update workflow"""
    print("\n\n🔄 Integration Workflow Demo")
    print("=" * 50)
    
    # Simulate user updating their bio
    print("1. 👤 User updates their bio:")
    bio = "I'm a full-stack developer passionate about web development and AI. Love creating innovative solutions."
    print(f"   Bio: \"{bio}\"")
    
    print("\n2. 🔍 System checks if user has existing tags:")
    existing_tags = []  # Simulate user has no tags
    print(f"   Existing tags: {existing_tags if existing_tags else 'None'}")
    
    if not existing_tags:
        print("\n3. 🤖 Auto-generating tags from bio using AI...")
        new_tags = mock_extract_tags_from_bio(bio)
        print(f"   Generated tags: {new_tags}")
        
        print("\n4. 💾 Updating user profile with auto-generated tags...")
        print(f"   ✅ User.feature_tags updated: {new_tags}")
        
        print("\n5. 🎯 User can now be matched based on these tags!")
        print(f"   🔍 Other users with similar tags will see this user in recommendations")
    else:
        print("\n3. ⏭️  User already has tags, skipping auto-generation")
    
    print("\n6. 📊 Analytics:")
    print("   - Auto-tag generation helps users who don't manually add tags")
    print("   - Improves matching quality by ensuring most users have some tags")
    print("   - Uses existing DeepSeek AI infrastructure")

def demo_api_integration():
    """Demo how this integrates with existing API"""
    print("\n\n🛠️  API Integration Demo")
    print("=" * 50)
    
    print("📡 New API Endpoints:")
    print("1. POST /api/users/{user_id}/auto-generate-tags")
    print("   - Generates tags from user's existing bio")
    print("   - Returns: {\"tags\": [\"Web Development\", \"AI/ML\"]}")
    print()
    
    print("2. PUT /api/users/{user_id}/profile (Enhanced)")
    print("   - Updates user profile with optional auto-tag generation")
    print("   - Parameter: auto_generate_tags=true")
    print("   - When bio is updated and user has no tags, automatically generates them")
    print()
    
    print("🔧 Backend Services:")
    print("1. AutoTagService - Handles AI-powered tag extraction")
    print("2. EnhancedProfileService - Integrates auto-tagging with profile updates")
    print("3. Uses existing DeepSeek API infrastructure from matches.py")
    print()
    
    print("💡 Usage Example:")
    example_request = {
        "bio": "Software engineer passionate about web development and AI",
        "auto_generate_tags": True
    }
    print(f"Request: PUT /api/users/123/profile")
    print(f"Body: {json.dumps(example_request, indent=2)}")
    print()
    
    example_response = {
        "user_id": 123,
        "bio": "Software engineer passionate about web development and AI",
        "feature_tags": ["Web Development", "AI/ML"],
        "auto_generated_tags": True
    }
    print(f"Response: {json.dumps(example_response, indent=2)}")

if __name__ == "__main__":
    # Run the demo
    results = demo_auto_tag_generation()
    demo_integration_workflow()
    demo_api_integration()
    
    print("\n\n🎉 Auto Tag Generation Demo Complete!")
    print("=" * 50)
    print("Key Features Demonstrated:")
    print("✅ AI-powered tag extraction from user bios")
    print("✅ Integration with existing profile update workflow") 
    print("✅ Uses existing DeepSeek API infrastructure")
    print("✅ Automatic tag generation for users without manual tags")
    print("✅ Improves matching quality by ensuring users have relevant tags")
    print("\nReady for implementation with real DeepSeek API key! 🚀")
