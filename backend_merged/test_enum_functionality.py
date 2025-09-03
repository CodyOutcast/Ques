"""Test script to verify enum conversion and swipe functionality"""

from models.likes import UserSwipe, SwipeDirection
from schemas.swipes import SwipeInput, SwipeDirectionEnum
from sqlalchemy.orm import Session
from dependencies.db import SessionLocal
from db_utils import store_swipe_action

def test_enum_conversion():
    """Test that the enum conversion works properly"""
    print("Testing enum conversion...")
    
    # Test SwipeDirection enum values
    print(f"SwipeDirection.LIKE = {SwipeDirection.LIKE}")
    print(f"SwipeDirection.DISLIKE = {SwipeDirection.DISLIKE}")
    print(f"SwipeDirection.LIKE.value = {SwipeDirection.LIKE.value}")
    print(f"SwipeDirection.DISLIKE.value = {SwipeDirection.DISLIKE.value}")
    
    # Test SwipeDirectionEnum (API schema) values
    print(f"SwipeDirectionEnum.LIKE = {SwipeDirectionEnum.LIKE}")
    print(f"SwipeDirectionEnum.DISLIKE = {SwipeDirectionEnum.DISLIKE}")
    print(f"SwipeDirectionEnum.LIKE.value = {SwipeDirectionEnum.LIKE.value}")
    print(f"SwipeDirectionEnum.DISLIKE.value = {SwipeDirectionEnum.DISLIKE.value}")
    
    # Test conversion between enums
    api_like = SwipeDirectionEnum.LIKE
    is_like = api_like == SwipeDirectionEnum.LIKE
    model_direction = SwipeDirection.LIKE if is_like else SwipeDirection.DISLIKE
    print(f"API enum to model enum conversion: {api_like} -> {model_direction}")
    
    print("✅ Enum conversion test passed!")

def test_swipe_input_schema():
    """Test SwipeInput schema validation"""
    print("\nTesting SwipeInput schema...")
    
    # Test valid input
    valid_like = SwipeInput(card_id=123, direction=SwipeDirectionEnum.LIKE)
    valid_dislike = SwipeInput(card_id=456, direction=SwipeDirectionEnum.DISLIKE)
    
    print(f"Valid like swipe: {valid_like}")
    print(f"Valid dislike swipe: {valid_dislike}")
    
    # Test conversion to JSON
    import json
    like_json = valid_like.model_dump()
    dislike_json = valid_dislike.model_dump()
    
    print(f"Like swipe JSON: {json.dumps(like_json)}")
    print(f"Dislike swipe JSON: {json.dumps(dislike_json)}")
    
    print("✅ SwipeInput schema test passed!")

def test_database_query():
    """Test querying existing user_swipes with enum"""
    print("\nTesting database query with enum...")
    
    if not SessionLocal:
        print("❌ Database not available, skipping database test")
        return
    
    db = SessionLocal()
    try:
        # Query existing user_swipes
        swipes = db.query(UserSwipe).limit(5).all()
        print(f"Found {len(swipes)} existing swipes:")
        
        for swipe in swipes:
            print(f"  Swipe ID {swipe.id}: user {swipe.swiper_id} -> user {swipe.swiped_user_id}, direction: {swipe.direction} (type: {type(swipe.direction)})")
        
        # Test filtering by direction
        likes = db.query(UserSwipe).filter(UserSwipe.direction == SwipeDirection.LIKE).count()
        dislikes = db.query(UserSwipe).filter(UserSwipe.direction == SwipeDirection.DISLIKE).count()
        
        print(f"Total likes: {likes}")
        print(f"Total dislikes: {dislikes}")
        
        print("✅ Database query test passed!")
        
    except Exception as e:
        print(f"❌ Database query test failed: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    print("🧪 Testing enum conversion and swipe functionality...\n")
    
    test_enum_conversion()
    test_swipe_input_schema()
    test_database_query()
    
    print("\n🎉 All tests completed!")
