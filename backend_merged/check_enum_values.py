from sqlalchemy import create_engine, text
from config.database import db_config

engine = create_engine(db_config.database_url)
with engine.connect() as conn:
    result = conn.execute(text("SELECT unnest(enum_range(NULL::swipedirection))"))
    enum_values = [row[0] for row in result]
    print('Enum values in DB:', enum_values)
