import os
from sqlalchemy import create_engine, text

DATABASE_URL = f"postgresql://{os.getenv('PG_USER', 'PostgreSQL')}:{os.getenv('PG_PASSWORD', 'Startup-Project-42069')}@{os.getenv('PG_HOST', 'gz-postgres-7aqk65fn.sql.tencentcdb.com')}:{os.getenv('PG_PORT', '29158')}/{os.getenv('PG_DATABASE', 'postgres')}"

engine = create_engine(DATABASE_URL)
with engine.connect() as conn:
    result = conn.execute(text("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'user_links' ORDER BY column_name"))
    print('user_links table structure:')
    for row in result:
        print(f'  {row[0]}: {row[1]}')
        
    # Check primary key constraints
    result = conn.execute(text("""
        SELECT kcu.column_name
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu ON tc.constraint_name = kcu.constraint_name
        WHERE tc.table_name = 'user_links' AND tc.constraint_type = 'PRIMARY KEY'
    """))
    print('\nPrimary key columns:')
    for row in result:
        print(f'  {row[0]}')
