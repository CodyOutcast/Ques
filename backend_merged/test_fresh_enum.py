"""Fresh test to check enum functionality"""

# Start completely fresh
import sys
import importlib

# Clear any cached modules
modules_to_clear = [mod for mod in sys.modules.keys() if 'models' in mod or 'likes' in mod]
for mod in modules_to_clear:
    if mod in sys.modules:
        del sys.modules[mod]

# Import fresh
from models.likes import UserSwipe, SwipeDirection
from dependencies.db import SessionLocal

def test_fresh_query():
    """Test with fresh imports"""
    print("Testing with fresh imports...")
    
    if not SessionLocal:
        print("❌ Database not available")
        return
    
    db = SessionLocal()
    try:
        # Test creating a new swipe
        print("Testing enum creation...")
        test_direction = SwipeDirection.like
        print(f"Created SwipeDirection.like: {test_direction} (value: {test_direction.value})")
        
        # Query existing data
        print("Querying existing swipes...")
        swipes = db.query(UserSwipe).limit(1).all()
        if swipes:
            swipe = swipes[0]
            print(f"Found swipe: direction = {swipe.direction} (type: {type(swipe.direction)})")
            print(f"Direction value: {swipe.direction.value if hasattr(swipe.direction, 'value') else 'No value attr'}")
        else:
            print("No swipes found in database")
            
        print("✅ Fresh query test completed!")
        
    except Exception as e:
        print(f"❌ Fresh query test failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_fresh_query()
