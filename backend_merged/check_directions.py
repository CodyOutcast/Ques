#!/usr/bin/env python3

from sqlalchemy import create_engine, text
from config.database import db_config

def check_direction_values():
    """Check what values are currently used in the direction column"""
    engine = create_engine(db_config.database_url)
    
    with engine.connect() as conn:
        # Check current direction values
        result = conn.execute(text("""
            SELECT direction, COUNT(*) as count 
            FROM user_swipes 
            GROUP BY direction 
            ORDER BY count DESC
        """))
        
        print("Current direction values in user_swipes:")
        print("=" * 40)
        
        directions = []
        for row in result.fetchall():
            directions.append(row[0])
            print(f"  '{row[0]}': {row[1]} records")
        
        return directions

if __name__ == "__main__":
    check_direction_values()
