from sqlalchemy import create_engine, text
from config.database import db_config

engine = create_engine(db_config.database_url)
with engine.connect() as conn:
    result = conn.execute(text('SELECT direction, COUNT(*) FROM user_swipes GROUP BY direction'))
    print('Direction values:')
    for row in result:
        print(f"  {row[0]}: {row[1]}")
