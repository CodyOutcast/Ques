#!/usr/bin/env python3
"""
Test Auto Tag Generation Service
"""

import sys
sys.path.append('.')

from services.auto_tag_service import AutoTagService
from dependencies.db import SessionLocal
from models.users import User

def test_auto_tag_generation():
    """Test automatic tag generation from user bios"""
    print("🧪 Testing Auto Tag Generation Service")
    print("=" * 50)
    
    db = SessionLocal()
    try:
        # Find a user with a bio but no tags
        user_with_bio = db.query(User).filter(
            User.bio.isnot(None),
            User.bio != ""
        ).first()
        
        if not user_with_bio:
            print("❌ No users found with bios")
            return
        
        print(f"👤 Testing with user: {user_with_bio.name}")
        print(f"📝 Bio: {user_with_bio.bio[:200]}..." if len(user_with_bio.bio) > 200 else f"📝 Bio: {user_with_bio.bio}")
        print(f"🏷️ Current tags: {user_with_bio.feature_tags}")
        
        # Test tag extraction from bio
        print("\n🔍 Extracting tags from bio...")
        extracted_tags = AutoTagService.extract_tags_from_bio(user_with_bio.bio)
        
        if extracted_tags:
            print(f"✅ Successfully extracted {len(extracted_tags)} tags:")
            for i, tag in enumerate(extracted_tags, 1):
                print(f"   {i}. {tag}")
            
            # Ask if we should save the tags
            print(f"\n💾 Would you like to save these tags for user {user_with_bio.name}? (y/n)")
            response = input().lower().strip()
            
            if response == 'y':
                success = AutoTagService.auto_generate_user_tags(
                    db, 
                    user_with_bio.user_id, 
                    force_update=True
                )
                if success:
                    print("✅ Tags saved successfully!")
                else:
                    print("❌ Failed to save tags")
            else:
                print("ℹ️ Tags not saved")
        else:
            print("❌ Failed to extract tags from bio")
        
        # Test batch processing
        print(f"\n🔄 Testing batch tag generation...")
        count = AutoTagService.auto_generate_tags_for_users_without_tags(db, limit=3)
        print(f"✅ Generated tags for {count} users in batch")
        
    except Exception as e:
        print(f"❌ Test error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_auto_tag_generation()
