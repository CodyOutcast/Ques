import os
from sqlalchemy import create_engine, text

# Use the database URL from .env
DATABASE_URL = f"postgresql://{os.getenv('PG_USER', 'PostgreSQL')}:{os.getenv('PG_PASSWORD', 'Startup-Project-42069')}@{os.getenv('PG_HOST', 'gz-postgres-7aqk65fn.sql.tencentcdb.com')}:{os.getenv('PG_PORT', '29158')}/{os.getenv('PG_DATABASE', 'postgres')}"

# Create engine
engine = create_engine(DATABASE_URL)

# Check tables
with engine.connect() as conn:
    # Check which tables exist
    result = conn.execute(text("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        ORDER BY table_name
    """))
    
    print("Existing tables:")
    tables = []
    for row in result:
        tables.append(row[0])
        print(f"  ✓ {row[0]}")
    
    # Check specifically for project-related tables
    project_tables = ['projects', 'user_projects']
    print(f"\nProject tables status:")
    for table in project_tables:
        status = "✓ EXISTS" if table in tables else "✗ MISSING"
        print(f"  {table}: {status}")
    
    # Check location columns in users table
    if 'users' in tables:
        result = conn.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'users' AND column_name IN ('latitude', 'longitude', 'city', 'state', 'country', 'postal_code', 'address')
            ORDER BY column_name
        """))
        
        print(f"\nLocation columns in users table:")
        location_cols = [row[0] for row in result]
        expected_cols = ['latitude', 'longitude', 'city', 'state', 'country', 'postal_code', 'address']
        for col in expected_cols:
            status = "✓ EXISTS" if col in location_cols else "✗ MISSING"
            print(f"  {col}: {status}")
    
    # Check projects table structure if it exists
    if 'projects' in tables:
        result = conn.execute(text("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'projects' 
            ORDER BY column_name
        """))
        
        print(f"\nProjects table columns:")
        for row in result:
            print(f"  {row[0]}: {row[1]}")
