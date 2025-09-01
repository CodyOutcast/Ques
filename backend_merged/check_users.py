"""
Simple script to check existing users in the database
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dependencies.db import get_db
from models.users import User

def check_users():
    """Check what users exist in the database"""
    db = next(get_db())
    
    try:
        users = db.query(User).limit(10).all()
        print(f"Found {len(users)} users:")
        for user in users:
            print(f"- User ID: {user.user_id}, Name: {user.name}")
            
        if len(users) == 0:
            print("No users found in database. Creating a test user...")
            
            test_user = User(
                name="Test User",
                bio="Test user for card limits testing",
                verification_status="verified",
                is_active=True,
                feature_tags=["developer", "entrepreneur"]
            )
            
            db.add(test_user)
            db.commit()
            db.refresh(test_user)
            
            print(f"Created test user with ID: {test_user.user_id}")
            return test_user.user_id
        else:
            return users[0].user_id
            
    except Exception as e:
        print(f"Error: {e}")
        return None
    finally:
        db.close()

if __name__ == "__main__":
    check_users()
