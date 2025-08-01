import os
from sqlalchemy import create_engine, text

DATABASE_URL = f"postgresql://{os.getenv('PG_USER', 'PostgreSQL')}:{os.getenv('PG_PASSWORD', 'Startup-Project-42069')}@{os.getenv('PG_HOST', 'gz-postgres-7aqk65fn.sql.tencentcdb.com')}:{os.getenv('PG_PORT', '29158')}/{os.getenv('PG_DATABASE', 'postgres')}"

engine = create_engine(DATABASE_URL)
with engine.connect() as conn:
    result = conn.execute(text('SELECT version_num FROM alembic_version'))
    current_version = result.scalar()
    print(f'Database migration version: {current_version}')
