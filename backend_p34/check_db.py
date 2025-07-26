from models.base import engine
from sqlalchemy import text

# Check what tables exist
with engine.connect() as conn:
    result = conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"))
    tables = [row[0] for row in result]
    print("Existing tables:", tables)
    
    # Check users table structure
    if 'users' in tables:
        result = conn.execute(text("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'users'"))
        columns = [(row[0], row[1]) for row in result]
        print("Users table columns:", columns)
