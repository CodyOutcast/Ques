#adding test data to the database
from models.base import SessionLocal
from models.users import User
from models.likes import Like

db = SessionLocal()
try:
    # Add a user if needed
    user = User(name="Alice", bio="Test bio")
    db.add(user)
    db.commit()
    db.refresh(user)

    # Add a like
    like = Like(liker_id=user.id, liked_item_id=1, liked_item_type="profile")
    db.add(like)
    db.commit()
    print("Test data added")
finally:
    db.close()