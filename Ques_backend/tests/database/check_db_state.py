"""
Check current database state to understand migration conflicts
"""
import os
from sqlalchemy import create_engine, text, inspect
from dotenv import load_dotenv

load_dotenv()

# Build database URL from environment variables
PG_USER = os.getenv('PG_USER')
PG_PASSWORD = os.getenv('PG_PASSWORD')
PG_HOST = os.getenv('PG_HOST')
PG_PORT = os.getenv('PG_PORT', '5432')
PG_DATABASE = os.getenv('PG_DATABASE')

if not all([PG_USER, PG_PASSWORD, PG_HOST, PG_DATABASE]):
    print("Missing database environment variables")
    print(f"PG_USER: {PG_USER}")
    print(f"PG_PASSWORD: {'***' if PG_PASSWORD else None}")
    print(f"PG_HOST: {PG_HOST}")
    print(f"PG_PORT: {PG_PORT}")
    print(f"PG_DATABASE: {PG_DATABASE}")
    exit(1)

DATABASE_URL = f"postgresql://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{PG_DATABASE}"

engine = create_engine(DATABASE_URL)
inspector = inspect(engine)

print("=== Current Database Tables ===")
tables = inspector.get_table_names()
for table in sorted(tables):
    print(f"✓ {table}")

print(f"\nTotal tables: {len(tables)}")

# Check if user_swipes table exists and its structure
if 'user_swipes' in tables:
    print("\n=== user_swipes table structure ===")
    columns = inspector.get_columns('user_swipes')
    for col in columns:
        print(f"  {col['name']}: {col['type']}")
else:
    print("\n❌ user_swipes table does not exist")

# Check if swipe_records table exists
if 'swipe_records' in tables:
    print("\n=== swipe_records table structure ===")
    columns = inspector.get_columns('swipe_records')
    for col in columns:
        print(f"  {col['name']}: {col['type']}")
else:
    print("\n❌ swipe_records table does not exist")

# Check migration version table
if 'alembic_version' in tables:
    print("\n=== Current migration version ===")
    with engine.connect() as conn:
        result = conn.execute(text("SELECT version_num FROM alembic_version"))
        for row in result:
            print(f"Current version: {row[0]}")
else:
    print("\n❌ alembic_version table does not exist")

print("\n=== Migration Strategy ===")
print("1. Mark problematic migrations as applied (if tables already exist)")
print("2. Create new migration for chat system")
print("3. Apply only the chat system migration")