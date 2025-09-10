#!/usr/bin/env python3
"""Check database tables"""

from dependencies.db import SessionLocal
from sqlalchemy import text

def check_tables():
    db = SessionLocal()
    try:
        result = db.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name"))
        print('Available tables:')
        for row in result.fetchall():
            print(f'  {row[0]}')
    finally:
        db.close()

if __name__ == "__main__":
    check_tables()
