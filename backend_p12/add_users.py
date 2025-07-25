# Utility script for adding a user profile with feature tags
# This is useful for testing the recommendation system (Page 1)

import sys
import json
from models.base import SessionLocal
from models.users import User
from db_utils import insert_to_vector_db, store_user_tags

def add_user_profile(name, bio, tags_list):
    """Add a new user with feature tags and vector representation"""
    db = SessionLocal()
    try:
        # Check if user already exists
        existing = db.query(User).filter(User.name == name).first()
        if existing:
            print(f"User {name} already exists!")
            return existing.id
        
        # Create user
        user = User(name=name, bio=bio)
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # Store tags and create vector
        tags_text = " ".join(tags_list)
        vector_id = insert_to_vector_db(tags_text, metadata={"user_id": user.id})
        
        # Update user with tags and vector_id
        store_user_tags(user.id, tags_list, vector_id)
        
        print(f"Successfully created user {name} (ID: {user.id}) with vector ID {vector_id}")
        return user.id
        
    except Exception as e:
        print(f"Error creating user {name}: {e}")
        db.rollback()
        return None
    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python add_users.py <name> <bio> <tag1,tag2,tag3,...>")
        print("Example: python add_users.py 'John Doe' 'Experienced developer' 'good at coding,startup founder,AI enthusiast'")
        sys.exit(1)
    
    name = sys.argv[1]
    bio = sys.argv[2]
    tags = [tag.strip() for tag in sys.argv[3].split(',')]
    
    user_id = add_user_profile(name, bio, tags)
    if user_id:
        print(f"User profile created successfully with ID: {user_id}")
    else:
        print("Failed to create user profile")