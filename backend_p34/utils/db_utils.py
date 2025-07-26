import os
import logging
import json
from dotenv import load_dotenv
import tcvectordb
from tcvectordb.model.document import Document
from tcvectordb.model.enum import EmbeddingModel, IndexType, MetricType, FieldType
from tcvectordb.model.collection import Embedding
from tcvectordb.model.index import Index, FilterIndex, VectorIndex, HNSWParams
from sentence_transformers import SentenceTransformer  # For local query embedding
from sqlalchemy import text  # For raw SQL execution

load_dotenv()
logging.basicConfig(level=logging.INFO)

# Assuming models/base.py exists with the following:
# from sqlalchemy import create_engine
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import sessionmaker
# DATABASE_URL = os.getenv('DATABASE_URL') or f"postgresql://{os.getenv('PG_USER')}:{os.getenv('PG_PASSWORD')}@{os.getenv('PG_HOST')}:{os.getenv('PG_PORT')}/{os.getenv('PG_DATABASE')}"
# engine = create_engine(DATABASE_URL)
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# Base = declarative_base()
from models.base import SessionLocal

# Store tags and vector_id in PG
def store_user_tags(user_id, tags, vector_id):
    db = SessionLocal()
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

# Tencent VectorDB Client
def get_vdb_client():
    return tcvectordb.VectorDBClient(
        url=os.getenv('VECTORDB_ENDPOINT'),
        username=os.getenv('VECTORDB_USERNAME'),
        key=os.getenv('VECTORDB_KEY'),
        timeout=20  # Can externalize to .env if needed
    )

# Get or create database and collection (with server-side embedding)
def get_vdb_collection():
    client = get_vdb_client()
    database_name = 'startup_db'  # Can externalize to .env if needed
    collection_name = os.getenv('VECTORDB_COLLECTION')

    # Get or create database
    try:
        db = client.database(database_name)
    except tcvectordb.exceptions.VectorDBException:
        db = client.create_database(database_name)

    # Get or create collection
    try:
        coll = db.collection(collection_name)
    except tcvectordb.exceptions.VectorDBException:
        # Configure server-side embedding (auto-embeds text to vector)
        embedding = Embedding(
            vector_field="vector",
            field="text",
            model=EmbeddingModel.BGE_BASE_ZH  # Matches 768 dim; adjust if using another model
        )

        # Index setup: Primary key on id, HNSW vector index with COSINE for similarity
        index = Index(
            FilterIndex("id", FieldType.String, IndexType.PRIMARY_KEY),
            VectorIndex(
                "vector",
                int(os.getenv('VECTORDB_DIMENSION')),
                IndexType.HNSW,
                MetricType.COSINE,
                HNSWParams(m=16, efconstruction=200)
            )
        )

        coll = db.create_collection(
            name=collection_name,
            shard=1,  # Basic setup; increase for production
            replicas=0,
            description="User feature vectors for project matchmaking",
            index=index,
            embedding=embedding
        )
        logging.info(f"Created collection {collection_name}")

    return coll

# Insert text to VectorDB (auto-embeds on server)
def insert_to_vector_db(text, metadata=None):
    coll = get_vdb_collection()
    user_id = metadata.get('user_id') if metadata else None
    if not user_id:
        raise ValueError("user_id required in metadata")

    vector_id = str(user_id)  # Use stringified user_id as primary key/ID in VectorDB
    doc = Document(
        id=vector_id,
        text=text  # This gets auto-embedded server-side into 'vector' field
    )

    try:
        res = coll.upsert([doc])
        logging.info(f"Inserted vector for ID: {vector_id}, result: {res}")
        return vector_id
    except Exception as e:
        logging.error(f"VectorDB upsert error: {e}")
        raise

# Query VectorDB for top_k similar (requires pre-embedded vector)
def query_vector_db(query_vector, top_k=20):
    coll = get_vdb_collection()
    try:
        res = coll.search(
            vectors=[query_vector],  # List of [float vector]
            limit=top_k,
            retrieve_vector=False  # Don't return vectors, just ids/scores
        )
        matches = []
        for hits in res:  # res is list of hit lists (for batch, but we have 1)
            for hit in hits:
                matches.append({"id": hit.id, "score": hit.score})
        matches = sorted(matches, key=lambda x: x['score'], reverse=True)  # Higher cosine is better
        logging.info(f"Found {len(matches)} matches")
        return [m['id'] for m in matches]  # Return list of str user_ids
    except Exception as e:
        logging.error(f"VectorDB search error: {e}")
        raise

# Fetch user infos from PG by ids (assume schema: id, name, bio, feature_tags)
def get_user_infos(user_ids):
    if not user_ids:
        return []
    db = SessionLocal()
    try:
        result = db.execute(
            text("SELECT id, name, bio, feature_tags FROM users WHERE id::text IN :user_ids"),
            {"user_ids": tuple(user_ids)}  # ids are str, cast id to text
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

# Helper: Embed text locally to match server model
def embed_text(text):
    model = SentenceTransformer('BAAI/bge-base-zh')
    vector = model.encode(text, normalize_embeddings=True).tolist()  # Cosine-ready
    if len(vector) != int(os.getenv('VECTORDB_DIMENSION')):
        raise ValueError("Embedding dimension mismatch")
    return vector