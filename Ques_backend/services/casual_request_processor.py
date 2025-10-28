"""
Casual Request Processing Functions
As specified in casual_request_integration_guide_en.md
"""

import time
from typing import Dict, Optional, Any
from datetime import datetime
from sqlalchemy.orm import Session
from qdrant_client import QdrantClient
from qdrant_client import models
from sentence_transformers import SentenceTransformer

from services.casual_request_classifier import CasualRequestClassifier
from services.casual_request_optimizer import CasualRequestOptimizer


async def process_and_store_casual_request(
    user_input: str,
    user_id: str,
    classifier: CasualRequestClassifier,
    optimizer: CasualRequestOptimizer,
    qdrant_client: QdrantClient,
    embedding_model: SentenceTransformer,
    collection_name: str = "casual_requests",
    db_conn: Session = None
) -> Dict:
    """Process and store casual request"""
    # 1. Use classifier to determine if it's a casual request
    classification = classifier.is_casual_request(user_input)
    
    if not classification.get("is_casual", False):
        # If not a casual request, return directly
        return {
            "is_stored": False,
            "reason": "Not a casual request"
        }
    
    # 2. Optimize request text
    optimization_result = optimizer.optimize_query(user_input)
    optimized_query = optimization_result.get("optimized_query", user_input)
    
    # 3. Generate vector embedding
    vector = embedding_model.encode(optimized_query, normalize_embeddings=True).tolist()
    current_timestamp = time.time()
    
    # 4. Update or insert into vector database
    point_id = f"casual_request_{user_id}"  # Use user ID as unique identifier
    
    try:
        # Check if already exists
        search_result = qdrant_client.search(
            collection_name=collection_name,
            query_filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key="user_id",
                        match=models.MatchValue(value=user_id)
                    )
                ]
            ),
            limit=1
        )
        
        if search_result and len(search_result) > 0:
            # Update if exists
            qdrant_client.update_vectors(
                collection_name=collection_name,
                points=[
                    models.PointVectors(
                        id=search_result[0].id,
                        vector=vector
                    )
                ]
            )
            
            # Update payload
            qdrant_client.update_payload(
                collection_name=collection_name,
                points=[search_result[0].id],
                payload={
                    "user_id": user_id,
                    "query": user_input,
                    "optimized_query": optimized_query,
                    "last_activity_at": current_timestamp
                }
            )
        else:
            # Insert if doesn't exist
            qdrant_client.upsert(
                collection_name=collection_name,
                points=[
                    models.PointStruct(
                        id=point_id,
                        vector=vector,
                        payload={
                            "user_id": user_id,
                            "query": user_input,
                            "optimized_query": optimized_query,
                            "last_activity_at": current_timestamp
                        }
                    )
                ]
            )
    except Exception as e:
        print(f"Error storing vector: {e}")
        # Continue to save to database, even if vector storage fails
    
    # 5. Update or insert into relational database
    if db_conn:
        try:
            from models.casual_requests import CasualRequest
            
            # Use the upsert_request method from the model
            casual_request = CasualRequest.upsert_request(
                db=db_conn,
                user_id=user_id,
                query=user_input,
                optimized_query=optimized_query
            )
            
        except Exception as e:
            print(f"Error storing to database: {e}")
            if hasattr(db_conn, 'rollback'):
                db_conn.rollback()
    
    return {
        "is_stored": True,
        "query": user_input,
        "optimized_query": optimized_query
    }