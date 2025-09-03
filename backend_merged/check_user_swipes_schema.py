#!/usr/bin/env python3

from sqlalchemy import create_engine, text
from config.database import db_config

def check_user_swipes_schema():
    engine = create_engine(db_config.database_url)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'user_swipes' ORDER BY ordinal_position"))
        print('user_swipes table columns:')
        for row in result:
            print(f'  {row[0]}: {row[1]}')

if __name__ == "__main__":
    check_user_swipes_schema()
