import os
import logging
import json
from dotenv import load_dotenv
from sqlalchemy import text
from models.base import SessionLocal

load_dotenv()
logging.basicConfig(level=logging.INFO)

# Get a PostgreSQL connection/session
def get_pg_connection():
    return SessionLocal()

# Store tags and vector_id in PG
def store_user_tags(user_id, tags, vector_id):
    db = get_pg_connection()
    try:
        db.execute(
            text("UPDATE users SET feature_tags = :tags, vector_id = :vector_id WHERE id = :user_id"),
            {"tags": json.dumps(tags), "vector_id": vector_id, "user_id": user_id}
        )
        db.commit()
        logging.info(f"Stored tags for user {user_id}")
    except Exception as e:
        db.rollback()
        logging.error(f"PG error: {e}")
        raise
    finally:
        db.close()

# Fetch user infos from PG by ids (assume schema: id, name, bio, feature_tags)
def get_user_infos(user_ids):
    if not user_ids:
        return []
    db = get_pg_connection()
    try:
        result = db.execute(
            text("SELECT id, name, bio, feature_tags FROM users WHERE id::text IN :user_ids"),
            {"user_ids": tuple(user_ids)}
        )
        rows = result.fetchall()
        users = [
            {"id": row[0], "name": row[1], "bio": row[2], "feature_tags": json.loads(row[3])}
            for row in rows
        ]
        logging.info(f"Fetched {len(users)} user infos")
        return users
    except Exception as e:
        logging.error(f"PG fetch error: {e}")
        raise
    finally:
        db.close()