#!/usr/bin/env python3
"""
Check available tags in the database
"""

from dependencies.db import SessionLocal
from sqlalchemy import text

def check_tags():
    """Check what tags are available in the database"""
    db = SessionLocal()
    try:
        # Check the tags table
        result = db.execute(text("""
            SELECT tag_id, tag_name, description, category, usage_count 
            FROM tags 
            ORDER BY category, tag_name
        """))
        tags = result.fetchall()
        
        print("📋 Available Tags in Database:")
        print("=" * 60)
        
        current_category = None
        for tag in tags:
            tag_id, tag_name, description, category, usage_count = tag
            
            if category != current_category:
                print(f"\n🏷️ Category: {category or 'Uncategorized'}")
                print("-" * 40)
                current_category = category
            
            print(f"  • {tag_name} (ID: {tag_id})")
            if description:
                print(f"    Description: {description}")
            print(f"    Usage count: {usage_count}")
            print()
        
        print(f"\n📊 Total tags: {len(tags)}")
        
        # Also check what tags users are actually using
        print("\n🔍 Checking user feature_tags:")
        result = db.execute(text("""
            SELECT user_id, name, feature_tags 
            FROM users 
            WHERE feature_tags IS NOT NULL 
            LIMIT 10
        """))
        
        user_tags = result.fetchall()
        
        print(f"📊 Found {len(user_tags)} users with feature_tags")
        for user_id, name, tags_data in user_tags:
            print(f"  • User {user_id} ({name}): {tags_data}")
    
    finally:
        db.close()

if __name__ == "__main__":
    check_tags()
