# Seed script for adding test data to the database
import json
from models.base import SessionLocal
from models.users import User
from models.likes import Like
from db_utils import insert_to_vector_db

def seed_database():
    db = SessionLocal()
    try:
        # Sample users with diverse feature tags for testing
        test_users = [
            {
                "name": "Alice Chen",
                "bio": "Experienced AI researcher looking for innovative projects to invest in.",
                "feature_tags": ["AI enthusiast", "investor", "machine learning", "tech startup", "research"]
            },
            {
                "name": "Bob Martinez", 
                "bio": "Full-stack developer seeking co-founders for a fintech startup.",
                "feature_tags": ["full-stack developer", "fintech", "startup founder", "good at coding", "entrepreneur"]
            },
            {
                "name": "Carol Thompson",
                "bio": "Marketing expert with experience in scaling consumer products.",
                "feature_tags": ["marketing expert", "consumer products", "growth hacking", "social media", "branding"]
            },
            {
                "name": "David Kim",
                "bio": "UX designer passionate about creating user-centric mobile experiences.",
                "feature_tags": ["UX designer", "mobile design", "user research", "prototyping", "creative"]
            },
            {
                "name": "Elena Rodriguez",
                "bio": "Venture capitalist focused on early-stage tech companies.",
                "feature_tags": ["venture capitalist", "investor", "early-stage", "tech companies", "funding"]
            },
            {
                "name": "Frank Zhang",
                "bio": "Data scientist with expertise in recommendation systems and ML.",
                "feature_tags": ["data scientist", "machine learning", "recommendation systems", "analytics", "AI"]
            }
        ]
        
        created_users = []
        for user_data in test_users:
            # Check if user already exists
            existing = db.query(User).filter(User.name == user_data["name"]).first()
            if existing:
                print(f"User {user_data['name']} already exists, skipping...")
                created_users.append(existing)
                continue
                
            # Create user
            user = User(
                name=user_data["name"],
                bio=user_data["bio"],
                feature_tags=user_data["feature_tags"]
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            
            # Create vector entry for this user
            tags_text = " ".join(user_data["feature_tags"])
            try:
                vector_id = insert_to_vector_db(tags_text, metadata={"user_id": user.id})
                user.vector_id = vector_id
                db.commit()
                print(f"Created user {user.name} with vector ID {vector_id}")
            except Exception as e:
                print(f"Failed to create vector for user {user.name}: {e}")
            
            created_users.append(user)
        
        # Add some sample like relationships for testing history
        if len(created_users) >= 2:
            # Alice likes Bob's profile
            alice = created_users[0]
            bob = created_users[1]
            
            existing_like = db.query(Like).filter(
                Like.liker_id == alice.id,
                Like.liked_item_id == bob.id,
                Like.liked_item_type == "profile"
            ).first()
            
            if not existing_like:
                like = Like(
                    liker_id=alice.id,
                    liked_item_id=bob.id,
                    liked_item_type="profile",
                    granted_chat_access=True
                )
                db.add(like)
                db.commit()
                print(f"Created like: {alice.name} -> {bob.name}")
        
        print(f"Seeding completed! Created/verified {len(created_users)} users.")
        
    except Exception as e:
        print(f"Error during seeding: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()