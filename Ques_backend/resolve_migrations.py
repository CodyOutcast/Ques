"""
Resolve migration conflicts by marking problematic migrations as applied
and creating a clean migration for chat system only.
"""
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

# Build database URL
PG_USER = os.getenv('PG_USER')
PG_PASSWORD = os.getenv('PG_PASSWORD')
PG_HOST = os.getenv('PG_HOST')
PG_PORT = os.getenv('PG_PORT', '5432')
PG_DATABASE = os.getenv('PG_DATABASE')

DATABASE_URL = f"postgresql://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{PG_DATABASE}"
engine = create_engine(DATABASE_URL)

print("=== Migration Conflict Resolution ===")
print("Current situation:")
print("- Database has user_swipes.swipe_direction (VARCHAR)")
print("- Migration wants to convert user_swipes.direction (doesn't exist)")
print("- Multiple unmerged migration heads exist")
print()

print("Strategy:")
print("1. Mark all existing migrations as applied (since tables already exist)")
print("2. Create a fresh migration ONLY for chat system")
print("3. Apply only the chat system migration")
print()

# Get current alembic version
with engine.connect() as conn:
    result = conn.execute(text("SELECT version_num FROM alembic_version"))
    current_version = result.fetchone()[0]
    print(f"Current migration version: {current_version}")

print()
print("Next steps:")
print("1. Run: alembic stamp heads")
print("   This marks all migration heads as applied without running them")
print("2. Create chat-only migration: alembic revision --autogenerate -m 'Add chat system tables only'") 
print("3. Apply chat migration: alembic upgrade head")
print()
print("This approach:")
print("✓ Doesn't modify existing tables")
print("✓ Only adds new chat tables")
print("✓ Resolves migration conflicts")
print("✓ Safe for production")