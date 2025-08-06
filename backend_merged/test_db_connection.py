"""Test database connection"""
try:
    from dependencies.db import get_db
    from models.users import User
    from sqlalchemy import text
    
    print("Testing database connection...")
    db = next(get_db())
    print("✅ Database connected successfully!")
    
    # Test if users table exists
    result = db.execute(text("SELECT 1 FROM information_schema.tables WHERE table_name = 'users';"))
    if result.fetchone():
        print("✅ Users table exists")
    else:
        print("❌ Users table does not exist")
        
    # Test user count
    result = db.execute(text("SELECT COUNT(*) FROM users;"))
    count = result.fetchone()[0]
    print(f"📊 User count: {count}")
    
except Exception as e:
    print(f"❌ Database connection failed: {e}")
    print(f"Error type: {type(e).__name__}")
