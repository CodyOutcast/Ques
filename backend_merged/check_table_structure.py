from sqlalchemy import create_engine, text
from config.database import db_config

engine = create_engine(db_config.database_url)
with engine.connect() as conn:
    result = conn.execute(text("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'user_swipes' ORDER BY ordinal_position"))
    columns = [(row[0], row[1]) for row in result]
    print('user_swipes table columns:')
    for col_name, col_type in columns:
        print(f"  {col_name}: {col_type}")
