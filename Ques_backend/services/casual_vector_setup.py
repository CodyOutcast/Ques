"""
Casual Requests Vector Database Setup
As specified in casual_request_integration_guide_en.md
"""

from qdrant_client import QdrantClient
from qdrant_client import models


def initialize_casual_request_collection(client: QdrantClient, collection_name: str = "casual_requests"):
    """Initialize vector collection for casual requests"""
    # Check if collection exists
    collections = client.get_collections().collections
    collection_names = [collection.name for collection in collections]
    
    # Create collection if it doesn't exist
    if collection_name not in collection_names:
        # Create collection, only using dense vectors
        client.create_collection(
            collection_name=collection_name,
            vectors_config=models.VectorParams(
                size=1024,  # Dimension based on the dense vector model used
                distance=models.Distance.COSINE
            )
        )
        
        # Create payload field indices for storage and filtering
        client.create_payload_index(
            collection_name=collection_name,
            field_name="user_id",
            field_schema="keyword"  # Set as keyword type
        )
        
        client.create_payload_index(
            collection_name=collection_name,
            field_name="last_activity_at",
            field_schema="float"  # Store timestamp
        )
        
        print(f"Collection '{collection_name}' created successfully.")
    else:
        print(f"Collection '{collection_name}' already exists.")


def clean_expired_casual_request_vectors(
    qdrant_client: QdrantClient,
    collection_name: str = "casual_requests",
    days_threshold: int = 7
):
    """Clean casual requests in vector database that have been inactive beyond the specified number of days"""
    import time
    try:
        # Calculate cutoff timestamp (seconds)
        cutoff_timestamp = time.time() - (days_threshold * 24 * 60 * 60)
        
        # Create filter condition
        expired_filter = models.Filter(
            must=[
                models.FieldCondition(
                    key="last_activity_at",
                    range=models.Range(
                        lt=cutoff_timestamp  # Less than cutoff time
                    )
                )
            ]
        )
        
        # Search for records to be deleted
        expired_points = qdrant_client.scroll(
            collection_name=collection_name,
            scroll_filter=expired_filter,
            limit=1000,  # Process up to 1000 at a time
            with_payload=False,
            with_vectors=False
        )
        
        # Extract IDs
        point_ids = [point.id for point in expired_points[0]]
        
        if point_ids:
            # Delete expired records
            qdrant_client.delete(
                collection_name=collection_name,
                points_selector=models.PointIdsList(
                    points=point_ids
                )
            )
            
            print(f"Cleaned {len(point_ids)} expired casual requests from vector database")
            return len(point_ids)
        else:
            print("No expired casual requests found in vector database")
            return 0
    except Exception as e:
        print(f"Error cleaning expired casual requests from vector database: {e}")
        return 0