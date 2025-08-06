"""
Fix alembic_version table
"""
from dependencies.db import engine
from sqlalchemy import text

# Remove invalid migration version
with engine.connect() as conn:
    conn.execute(text("DELETE FROM alembic_version WHERE version_num = 'add_media_fields'"))
    conn.commit()
    print("Removed invalid migration version")
    
    # Check current versions
    result = conn.execute(text("SELECT * FROM alembic_version"))
    versions = result.fetchall()
    print("Current versions:", versions)
