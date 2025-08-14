import os
import logging
import json
from dotenv import load_dotenv
from sqlalchemy import text  # For raw SQL execution

# Load environment first
load_dotenv()
logging.basicConfig(level=logging.INFO)

# Import dependencies with error handling
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
    SentenceTransformer = None  # Define as None to prevent NameError

# Import database session
try:
    from dependencies.db import SessionLocal
except ImportError as e:
    logging.warning(f"dependencies.db import failed: {e}")
    SessionLocal = None

# Store tags and vector_id in PG
def store_user_tags(user_id, tags, vector_id):
    if not SessionLocal:
        logging.warning("Database not available, skipping store_user_tags")
        return
    
    db = SessionLocal()
    try:
        db.execute(
            text("UPDATE users SET feature_tags = :tags, vector_id = :vector_id WHERE user_id = :user_id"),
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
        timeout=20  # Can externalize to .env if needed
    )

# Get or create database and collection (with server-side embedding)
def get_vdb_collection():
    if not TCVECTORDB_AVAILABLE:
        raise RuntimeError("tcvectordb not available")
        
    client = get_vdb_client()
    database_name = 'startup_db'  # Can externalize to .env if needed
    collection_name = os.getenv('VECTORDB_COLLECTION')
    
    if not collection_name:
        raise ValueError("Missing required environment variable: VECTORDB_COLLECTION")

    # Get or create database
    try:
        db = client.database(database_name)
    except Exception as e:
        # Handle case where database already exists
        if "already exist" in str(e):
            db = client.database(database_name)
        else:
            db = client.create_database(database_name)

    # Get or create collection
    try:
        coll = db.collection(collection_name)
    except Exception as e:
        # Configure server-side embedding (auto-embeds text to vector)
        embedding = Embedding(
            vector_field="vector",
            field="text",
            model=EmbeddingModel.BGE_BASE_ZH  # Matches 768 dim; adjust if using another model
        )

        # Get dimension with default
        dimension = int(os.getenv('VECTORDB_DIMENSION', '768'))

        # Index setup: Primary key on id, HNSW vector index with COSINE for similarity
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
            shard=1,  # Basic setup; increase for production
            replicas=0,
            description="User feature vectors for Ques recommendations",
            index=index,
            embedding=embedding
        )
        logging.info(f"Created collection {collection_name}")

    return coll

# Insert text to VectorDB (auto-embeds on server)
def insert_to_vector_db(text, metadata=None):
    if not TCVECTORDB_AVAILABLE:
        logging.warning("Vector database not available, skipping insert")
        return None
        
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
    if not TCVECTORDB_AVAILABLE:
        logging.warning("Vector database not available, returning empty results")
        return []
        
    try:
        coll = get_vdb_collection()
        res = coll.search(
            vectors=[query_vector],  # List of [float vector]
            limit=top_k,
            retrieve_vector=False  # Don't return vectors, just ids/scores
        )
        matches = []
        for hits in res:  # res is list of hit lists (for batch, but we have 1)
            for hit in hits:
                # Handle both object-style and dict-style responses
                if hasattr(hit, 'id'):
                    matches.append({"id": hit.id, "score": hit.score})
                else:
                    matches.append({"id": hit.get('id'), "score": hit.get('score', 0)})
        matches = sorted(matches, key=lambda x: x['score'], reverse=True)  # Higher cosine is better
        logging.info(f"Found {len(matches)} matches")
        return [m['id'] for m in matches]  # Return list of str user_ids
    except Exception as e:
        logging.error(f"VectorDB search error: {e}")
        return []  # Return empty list instead of raising

# Fetch user infos from PG by ids (assume schema: id, name, bio, feature_tags)
def get_user_infos(user_ids):
    if not user_ids or not SessionLocal:
        return []
    
    db = SessionLocal()
    try:
        # Create placeholders for the IN clause
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
        return []  # Return empty list instead of raising
    finally:
        db.close()

# Helper: Embed text locally to match server model
def embed_text(text):
    if not SENTENCE_TRANSFORMER_AVAILABLE:
        logging.warning("SentenceTransformer not available, returning dummy vector")
        # Return a dummy vector of the expected dimension
        expected_dim = int(os.getenv('VECTORDB_DIMENSION', '768'))
        return [0.0] * expected_dim
    
    try:
        model = SentenceTransformer('BAAI/bge-base-zh')
        vector = model.encode(text, normalize_embeddings=True)
        
        # Convert to list - handle different return types
        import numpy as np
        if isinstance(vector, np.ndarray):
            vector = vector.tolist()
        else:
            # Handle tensor or other types
            vector = list(vector)
        
        # Validate dimension
        expected_dim = int(os.getenv('VECTORDB_DIMENSION', '768'))
        if len(vector) != expected_dim:
            raise ValueError(f"Embedding dimension mismatch: got {len(vector)}, expected {expected_dim}")
        
        return vector
    except Exception as e:
        logging.error(f"Error in embed_text: {e}")
        # Return dummy vector as fallback
        expected_dim = int(os.getenv('VECTORDB_DIMENSION', '768'))
        return [0.0] * expected_dim

# Get user's vector for recommendations (Page 1)
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

# Get user's swipe history to avoid showing same cards
def get_user_history(user_id):
    """Get list of card IDs this user has already seen/swiped"""
    if not SessionLocal:
        return []
        
    db = SessionLocal()
    try:
        result = db.execute(
            text("SELECT liked_item_id FROM likes WHERE liker_id = :user_id AND liked_item_type = 'profile'"),
            {"user_id": user_id}
        )
        rows = result.fetchall()
        return [str(row[0]) for row in rows]  # Convert to string to match vector DB IDs
        
    except Exception as e:
        logging.error(f"Error getting user history: {e}")
        return []
    finally:
        db.close()

# Store swipe action (like or dislike)
def store_swipe_action(liker_id, liked_item_id, liked_item_type, is_like):
    """Store user's swipe action in the likes table"""
    if not SessionLocal:
        logging.warning("Database not available, skipping store_swipe_action")
        return
        
    db = SessionLocal()
    try:
        # Import Like model here to avoid circular imports
        from models.likes import Like
        
        like = Like(
            liker_id=liker_id,
            liked_item_id=liked_item_id,
            liked_item_type=liked_item_type,
            granted_chat_access=is_like  # Only grant chat access if it's a like
        )
        db.add(like)
        db.commit()
        logging.info(f"Stored swipe action: user {liker_id} {'liked' if is_like else 'disliked'} {liked_item_type} {liked_item_id}")
        
    except Exception as e:
        db.rollback()
        logging.error(f"Error storing swipe action: {e}")
        raise
    finally:
        db.close()

# Get random unseen users for fallback recommendations
def get_random_unseen_users(user_id, seen_card_ids, limit):
    """
    Get random users that haven't been seen yet by the user.
    Used as fallback when similarity-based recommendations are exhausted.
    """
    if not SessionLocal:
        return []
        
    db = SessionLocal()
    try:
        # Convert seen_card_ids to integers for SQL query
        seen_ids_int = []
        for card_id in seen_card_ids:
            try:
                seen_ids_int.append(int(card_id))
            except (ValueError, TypeError):
                continue
        
        # Build exclusion list (user themselves + seen cards)
        exclude_ids = [user_id] + seen_ids_int
        
        # Query for random users not in exclusion list
        if exclude_ids:
            # Convert to string for SQL
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
            # If no exclusions, just get random users excluding self
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
        random_user_ids = [str(row[0]) for row in rows]  # Convert to string to match vector DB format
        
        logging.info(f"Found {len(random_user_ids)} random unseen users for user {user_id}")
        return random_user_ids
        
    except Exception as e:
        logging.error(f"Error getting random unseen users: {e}")
        return []
    finally:
        db.close()


# Quota system functions for project idea agent
def check_quota(user_id: int) -> bool:
    """
    Check if user has quota remaining for project idea generation
    
    DEPRECATED: Use QuotaService.check_quota() instead for new implementations
    This function is kept for backward compatibility.
    
    Args:
        user_id: User ID to check quota for
        
    Returns:
        True if user has quota remaining, False otherwise
    """
    try:
        from services.quota_service import QuotaService
        has_quota, _ = QuotaService.check_quota(user_id)
        return has_quota
    except ImportError:
        # Fallback to old logic if new service isn't available
        if not SessionLocal:
            logging.warning("Database not available, allowing quota check")
            return True
        
        db = SessionLocal()
        try:
            # Check user's daily quota (assume 10 requests per day per user)
            query = text("""
                SELECT COUNT(*) as used_quota 
                FROM project_idea_requests 
                WHERE user_id = :user_id 
                AND DATE(created_at) = CURRENT_DATE
            """)
            result = db.execute(query, {"user_id": user_id}).fetchone()
            
            used_quota = result.used_quota if result else 0
            daily_limit = 10  # Allow 10 project idea generations per day
            
            return used_quota < daily_limit
            
        except Exception as e:
            logging.error(f"Error checking quota for user {user_id}: {e}")
            return True  # Allow on error
        finally:
            db.close()
        # In case of error, allow the request (fail open)
        return True
    finally:
        db.close()


def deduct_quota(user_id: int, cost: int = 1):
    """
    Deduct quota after successful project idea generation
    
    Args:
        user_id: User ID to deduct quota from
        cost: Cost to deduct (default 1)
    """
    if not SessionLocal:
        logging.warning("Database not available, skipping quota deduction")
        return
    
    db = SessionLocal()
    try:
        # Record the request in project_idea_requests table
        query = text("""
            INSERT INTO project_idea_requests (user_id, cost, created_at)
            VALUES (:user_id, :cost, NOW())
        """)
        db.execute(query, {"user_id": user_id, "cost": cost})
        db.commit()
        
        logging.info(f"Deducted {cost} quota from user {user_id}")
        
    except Exception as e:
        logging.error(f"Error deducting quota for user {user_id}: {e}")
        db.rollback()
    finally:
        db.close()