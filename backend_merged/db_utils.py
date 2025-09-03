"""Database utility functions"""

import os
import json
import logging
from dotenv import load_dotenv
from sqlalchemy import text
from sqlalchemy.orm import Session
from dependencies.db import SessionLocal
from models.likes import UserSwipe, SwipeDirection

# Load environment variables
load_dotenv()

# Import vector database with error handling
try:
    import tcvectordb
    from tcvectordb.model.document import Document
    from tcvectordb.model.enum import EmbeddingModel, IndexType, MetricType, FieldType
    from tcvectordb.model.collection import Embedding
    from tcvectordb.model.index import Index, FilterIndex, VectorIndex, HNSWParams
    TCVECTORDB_AVAILABLE = True
    logging.info("tcvectordb imported successfully")
except ImportError as e:
    logging.warning(f"tcvectordb import failed: {e}")
    logging.warning("Vector database features may not work properly")
    TCVECTORDB_AVAILABLE = False

# Import sentence transformer with error handling
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMER_AVAILABLE = True
    logging.info("SentenceTransformer imported successfully")
except (ImportError, ValueError) as e:
    logging.warning(f"SentenceTransformer import failed: {e}")
    logging.warning("Some vector embedding features may not work properly")
    SENTENCE_TRANSFORMER_AVAILABLE = False
    SentenceTransformer = None


def store_swipe_action(liker_id: int, liked_item_id: int, liked_item_type: str, is_like: bool):
    """Store user's swipe action in the user_swipes table"""
    if not SessionLocal:
        logging.warning("Database not available, skipping store_swipe_action")
        return
        
    db = SessionLocal()
    try:
        # Convert boolean to enum
        direction = SwipeDirection.like if is_like else SwipeDirection.dislike
        
        user_swipe = UserSwipe(
            swiper_id=liker_id,
            target_id=liked_item_id,
            direction=direction
        )
        db.add(user_swipe)
        db.commit()
        logging.info(f"Stored swipe action: user {liker_id} {direction.value} user {liked_item_id}")
        
    except Exception as e:
        db.rollback()
        logging.error(f"Error storing swipe action: {e}")
        raise
    finally:
        db.close()


def get_vdb_client():
    """Get Tencent VectorDB client"""
    if not TCVECTORDB_AVAILABLE:
        raise RuntimeError("tcvectordb not available")
    
    endpoint = os.getenv('VECTORDB_ENDPOINT')
    username = os.getenv('VECTORDB_USERNAME')
    key = os.getenv('VECTORDB_KEY')
    
    if not all([endpoint, username, key]):
        raise ValueError("Missing required VectorDB environment variables: VECTORDB_ENDPOINT, VECTORDB_USERNAME, VECTORDB_KEY")
    
    return tcvectordb.VectorDBClient(
        url=endpoint,
        username=username,
        key=key,
        timeout=20
    )


def get_vdb_collection():
    """Get or create vector database collection"""
    if not TCVECTORDB_AVAILABLE:
        raise RuntimeError("tcvectordb not available")
        
    client = get_vdb_client()
    database_name = 'startup_db'
    collection_name = os.getenv('VECTORDB_COLLECTION')
    
    if not collection_name:
        raise ValueError("Missing required environment variable: VECTORDB_COLLECTION")

    # Get or create database
    try:
        db = client.database(database_name)
    except Exception as e:
        if "already exist" in str(e):
            db = client.database(database_name)
        else:
            db = client.create_database(database_name)

    # Get or create collection
    try:
        coll = db.collection(collection_name)
    except Exception as e:
        embedding = Embedding(
            vector_field="vector",
            field="text",
            model=EmbeddingModel.BGE_BASE_ZH
        )

        dimension = int(os.getenv('VECTORDB_DIMENSION', '768'))

        index = Index(
            FilterIndex("id", FieldType.String, IndexType.PRIMARY_KEY),
            VectorIndex(
                "vector",
                dimension,
                IndexType.HNSW,
                MetricType.COSINE,
                HNSWParams(m=16, efconstruction=200)
            )
        )

        coll = db.create_collection(
            name=collection_name,
            shard=1,
            replicas=0,
            description="User feature vectors for Ques recommendations",
            index=index,
            embedding=embedding
        )
        logging.info(f"Created collection {collection_name}")

    return coll


def query_vector_db(query_vector, top_k=20):
    """Query VectorDB for top_k similar users"""
    if not TCVECTORDB_AVAILABLE:
        logging.warning("Vector database not available, returning empty results")
        return []
        
    try:
        coll = get_vdb_collection()
        res = coll.search(
            vectors=[query_vector],
            limit=top_k,
            retrieve_vector=False
        )
        matches = []
        for hits in res:
            for hit in hits:
                if hasattr(hit, 'id'):
                    matches.append({"id": hit.id, "score": hit.score})
                else:
                    matches.append({"id": hit.get('id'), "score": hit.get('score', 0)})
        matches = sorted(matches, key=lambda x: x['score'], reverse=True)
        logging.info(f"Found {len(matches)} matches")
        return [m['id'] for m in matches]
    except Exception as e:
        logging.error(f"VectorDB search error: {e}")
        return []


def get_user_infos(user_ids):
    """Fetch user infos from database by IDs"""
    if not user_ids or not SessionLocal:
        return []
    
    db = SessionLocal()
    try:
        placeholders = ','.join([':user_id_' + str(i) for i in range(len(user_ids))])
        user_id_params = {f'user_id_{i}': int(uid) for i, uid in enumerate(user_ids)}
        
        result = db.execute(
            text(f"SELECT user_id, name, bio, feature_tags FROM users WHERE user_id IN ({placeholders})"),
            user_id_params
        )
        rows = result.fetchall()
        users = [
            {
                "id": row[0], 
                "name": row[1], 
                "bio": row[2], 
                "feature_tags": row[3] if isinstance(row[3], list) else (json.loads(row[3]) if row[3] else [])
            }
            for row in rows
        ]
        logging.info(f"Fetched {len(users)} user infos")
        return users
    except Exception as e:
        logging.error(f"PG fetch error: {e}")
        return []
    finally:
        db.close()


def embed_text(text):
    """Embed text using SentenceTransformer"""
    if not SENTENCE_TRANSFORMER_AVAILABLE:
        logging.warning("SentenceTransformer not available, returning dummy vector")
        expected_dim = int(os.getenv('VECTORDB_DIMENSION', '768'))
        return [0.0] * expected_dim
    
    try:
        model = SentenceTransformer('BAAI/bge-base-zh')
        vector = model.encode(text, normalize_embeddings=True)
        
        import numpy as np
        if isinstance(vector, np.ndarray):
            vector = vector.tolist()
        else:
            vector = list(vector)
        
        expected_dim = int(os.getenv('VECTORDB_DIMENSION', '768'))
        if len(vector) != expected_dim:
            raise ValueError(f"Embedding dimension mismatch: got {len(vector)}, expected {expected_dim}")
        
        return vector
    except Exception as e:
        logging.error(f"Error in embed_text: {e}")
        expected_dim = int(os.getenv('VECTORDB_DIMENSION', '768'))
        return [0.0] * expected_dim


def get_user_vector(user_id):
    """Get user's vector by embedding their feature tags"""
    if not SessionLocal:
        logging.warning("Database not available")
        return None
        
    db = SessionLocal()
    try:
        result = db.execute(
            text("SELECT feature_tags FROM users WHERE user_id = :user_id"),
            {"user_id": user_id}
        )
        row = result.fetchone()
        if not row or not row[0]:
            return None
        
        tags = json.loads(row[0])
        tags_text = " ".join(tags)
        return embed_text(tags_text)
        
    except Exception as e:
        logging.error(f"Error getting user vector: {e}")
        return None
    finally:
        db.close()


def get_user_history(user_id):
    """Get list of card IDs this user has already seen/swiped"""
    if not SessionLocal:
        return []
        
    db = SessionLocal()
    try:
        # Query both old likes table and new user_swipes table
        likes_result = db.execute(
            text("SELECT liked_item_id FROM likes WHERE liker_id = :user_id AND liked_item_type = 'profile'"),
            {"user_id": user_id}
        )
        likes_rows = likes_result.fetchall()
        
        swipes_result = db.execute(
            text("SELECT target_id FROM user_swipes WHERE swiper_id = :user_id"),
            {"user_id": user_id}
        )
        swipes_rows = swipes_result.fetchall()
        
        # Combine both results
        seen_ids = set()
        for row in likes_rows:
            seen_ids.add(str(row[0]))
        for row in swipes_rows:
            seen_ids.add(str(row[0]))
            
        return list(seen_ids)
        
    except Exception as e:
        logging.error(f"Error getting user history: {e}")
        return []
    finally:
        db.close()


def get_random_unseen_users(user_id, seen_card_ids, limit):
    """Get random users that haven't been seen yet by the user"""
    if not SessionLocal:
        return []
        
    db = SessionLocal()
    try:
        seen_ids_int = []
        for card_id in seen_card_ids:
            try:
                seen_ids_int.append(int(card_id))
            except (ValueError, TypeError):
                continue
        
        exclude_ids = [user_id] + seen_ids_int
        
        if exclude_ids:
            exclude_ids_str = ','.join(map(str, exclude_ids))
            result = db.execute(
                text(f"""
                    SELECT user_id FROM users 
                    WHERE user_id NOT IN ({exclude_ids_str}) 
                    ORDER BY RANDOM() 
                    LIMIT :limit
                """),
                {"limit": limit}
            )
        else:
            result = db.execute(
                text("""
                    SELECT user_id FROM users 
                    WHERE user_id != :user_id 
                    ORDER BY RANDOM() 
                    LIMIT :limit
                """),
                {"user_id": user_id, "limit": limit}
            )
        
        rows = result.fetchall()
        random_user_ids = [str(row[0]) for row in rows]
        
        logging.info(f"Found {len(random_user_ids)} random unseen users for user {user_id}")
        return random_user_ids
        
    except Exception as e:
        logging.error(f"Error getting random unseen users: {e}")
        return []
    finally:
        db.close()
