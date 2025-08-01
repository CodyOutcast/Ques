from sqlalchemy import create_engine, text
from config.settings import settings

# Create engine
engine = create_engine(settings.DATABASE_URL)

# Check columns
with engine.connect() as conn:
    result = conn.execute(text("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'users' 
        ORDER BY column_name
    """))
    
    print("Users table columns:")
    for row in result:
        print(f"  {row[0]}: {row[1]}")

    # Check specifically for location columns
    location_columns = ['latitude', 'longitude', 'city', 'state', 'country', 'postal_code', 'address']
    print("\nLocation columns status:")
    for col in location_columns:
        result = conn.execute(text(f"""
            SELECT EXISTS(
                SELECT 1 FROM information_schema.columns 
                WHERE table_name = 'users' AND column_name = '{col}'
            )
        """))
        exists = result.scalar()
        status = "✓ EXISTS" if exists else "✗ MISSING"
        print(f"  {col}: {status}")
