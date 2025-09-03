from sqlalchemy import create_engine, text
from config.database import db_config

engine = create_engine(db_config.database_url)
with engine.connect() as conn:
    # Check what enum types exist
    result = conn.execute(text("SELECT typname, enumlabel FROM pg_type JOIN pg_enum ON pg_type.oid = pg_enum.enumtypid WHERE typname = 'swipedirection' ORDER BY enumsortorder"))
    enum_info = [(row[0], row[1]) for row in result]
    print('Enum type info:')
    for type_name, label in enum_info:
        print(f"  {type_name}: {label}")
    
    # Check what the actual values are in the table
    result2 = conn.execute(text("SELECT direction FROM user_swipes LIMIT 5"))
    direction_values = [row[0] for row in result2]
    print(f'Actual direction values in table: {direction_values}')
