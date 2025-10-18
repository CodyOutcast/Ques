#!/usr/bin/env python3
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

# Connect to database
conn = psycopg2.connect(
    host=os.getenv('DATABASE_HOST', 'localhost'),
    database=os.getenv('DATABASE_NAME', 'ques_db'),
    user=os.getenv('DATABASE_USER', 'postgres'),
    password=os.getenv('DATABASE_PASSWORD', '')
)

# Get user_swipes table structure
cur = conn.cursor()
cur.execute("""
    SELECT column_name, data_type, is_nullable, column_default
    FROM information_schema.columns 
    WHERE table_name = 'user_swipes'
    ORDER BY ordinal_position;
""")

print('user_swipes table structure:')
for row in cur.fetchall():
    print(f'  {row[0]} ({row[1]}) - nullable: {row[2]}, default: {row[3]}')

cur.close()
conn.close()