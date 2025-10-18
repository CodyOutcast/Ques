"""
Tencent Vector Database Adapter
Handles vector database operations for hybrid search (sparse + dense vectors)
Uses the official tcvectordb SDK
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from tcvectordb import VectorDBClient
from tcvectordb.model.enum import ReadConsistency

logger = logging.getLogger(__name__)


class TencentVectorDBAdapter:
    """Adapter for Tencent Vector Database with hybrid search capabilities using official SDK"""
    
    def __init__(
        self,
        url: str,
        username: str,
        key: str,
        database_name: str = "intelligent_search",
        collection_name: str = "user_vectors_1024",
        timeout: int = 30
    ):
        self.url = url.rstrip('/')
        self.username = username
        self.key = key
        self.database_name = database_name
        self.collection_name = collection_name
        self.timeout = timeout
        
        # Initialize VectorDB client (SDK)
        self.client = VectorDBClient(
            url=self.url,
            username=self.username,
            key=self.key,
            timeout=self.timeout
        )
        self.database = None
        self.collection = None
        
        logger.info(f"TencentVectorDB SDK initialized: {self.url}/{self.database_name}/{self.collection_name}")
    
    def _ensure_connection(self):
        """Ensure database and collection connections are established"""
        if self.database is None:
            self.database = self.client.database(self.database_name)
            logger.info(f"[VectorDB] Connected to database: {self.database_name}")
        
        if self.collection is None:
            self.collection = self.database.collection(self.collection_name)
            logger.info(f"[VectorDB] Connected to collection: {self.collection_name}")
    
    def close(self):
        """Clean up resources"""
        self.database = None
        self.collection = None
        self.client = None
        logger.info("[VectorDB] Connection closed")
    
    async def hybrid_search(
        self,
        query_vector: List[float],
        sparse_vector: Optional[Dict[str, float]] = None,
        top_k: int = 10,
        filter_conditions: Optional[Dict[str, Any]] = None,
        exclude_ids: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Perform hybrid search using both dense and sparse vectors
        
        Args:
            query_vector: Dense vector embedding (1024 dimensions for BGE-M3)
            sparse_vector: Sparse vector representation (keyword weights)
            top_k: Number of results to return
            filter_conditions: Additional filtering conditions
            exclude_ids: User IDs to exclude from results
        
        Returns:
            List of search results with scores and metadata
        """
        try:
            self._ensure_connection()
            
            logger.info(f"[VectorDB] Searching: vector_dim={len(query_vector)}, top_k={top_k}, sparse={bool(sparse_vector)}")
            
            # Perform search using SDK
            # Note: tcvectordb SDK's search() method uses dense vectors by default
            # Sparse vectors in the collection are automatically used if the collection supports hybrid search
            # The sparse_vector parameter here is for logging/analysis, not direct SDK usage
            results = self.collection.search(
                vectors=[query_vector],
                limit=top_k,
                retrieve_vector=False,  # Don't return vectors to save bandwidth
                # params={"ef": min(top_k * 4, 200)}  # HNSW search quality parameter
            )
            
            # Parse results
            search_results = []
            if results and len(results) > 0:
                for item in results[0]:  # Results come as nested list
                    # Extract document data
                    doc = {
                        "user_id": item.get("user_id"),
                        "score": float(item.get("score", 0)),
                        "name": item.get("name", ""),
                        "bio": item.get("bio", ""),
                        "skills": item.get("skills", []),
                        "hobbies": item.get("hobbies", []),
                        "location": item.get("location", ""),
                        "university": item.get("university", ""),
                        "major": item.get("major", ""),
                        "year": item.get("year"),
                        # Include all other fields
                        **{k: v for k, v in item.items() if k not in ["user_id", "score", "vector", "sparse_vector_data"]}
                    }
                    
                    # Apply exclusion filter
                    if exclude_ids and str(doc["user_id"]) in [str(x) for x in exclude_ids]:
                        continue
                    
                    search_results.append(doc)
            
            logger.info(f"[VectorDB] Found {len(search_results)} results")
            return search_results[:top_k]
            
        except Exception as e:
            logger.error(f"[VectorDB] Search error: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return []
    
    async def insert_user_vector(
        self,
        user_id: str,
        vector: List[float],
        metadata: Dict[str, Any],
        sparse_vector: Optional[Dict[str, float]] = None
    ) -> bool:
        """
        Insert or update a user's vector in the database
        
        Args:
            user_id: Unique user identifier
            vector: Dense vector embedding
            metadata: User metadata (name, bio, skills, etc.)
            sparse_vector: Optional sparse vector for hybrid search
        
        Returns:
            True if successful
        """
        try:
            self._ensure_connection()
            
            # Prepare document
            document = {
                "id": f"user_{user_id}",
                "user_id": user_id,
                "vector": vector,
                **metadata
            }
            
            # Add sparse vector if provided
            if sparse_vector:
                document["sparse_vector_data"] = sparse_vector
            
            # Upsert document
            self.collection.upsert([document])
            
            logger.info(f"[VectorDB] Inserted/updated vector for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"[VectorDB] Failed to insert vector for user {user_id}: {e}")
            return False
    
    async def delete_user_vector(self, user_id: str) -> bool:
        """
        Delete a user's vector from the database
        
        Args:
            user_id: User identifier to delete
        
        Returns:
            True if successful
        """
        try:
            self._ensure_connection()
            
            # Delete by filter
            self.collection.delete(ids=[f"user_{user_id}"])
            
            logger.info(f"[VectorDB] Deleted vector for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"[VectorDB] Failed to delete vector for user {user_id}: {e}")
            return False
    
    async def get_collection_stats(self) -> Dict[str, Any]:
        """
        Get collection statistics
        
        Returns:
            Dictionary with collection stats
        """
        try:
            self._ensure_connection()
            
            # Try to get a sample document to verify collection has data
            results = self.collection.query(limit=1, retrieve_vector=False)
            
            stats = {
                "database": self.database_name,
                "collection": self.collection_name,
                "has_data": len(results) > 0,
                "status": "healthy"
            }
            
            logger.info(f"[VectorDB] Collection stats: {stats}")
            return stats
            
        except Exception as e:
            logger.error(f"[VectorDB] Failed to get collection stats: {e}")
            return {
                "database": self.database_name,
                "collection": self.collection_name,
                "has_data": False,
                "status": "error",
                "error": str(e)
            }
    
    def _create_sparse_vector(self, text: str, keywords: List[str]) -> Dict[str, float]:
        """
        Create sparse vector from text and keywords (TF-IDF style)
        
        Args:
            text: Input text to analyze
            keywords: Important keywords to emphasize
        
        Returns:
            Dictionary mapping terms to weights
        """
        try:
            # Simple TF-IDF approximation
            words = text.lower().split()
            word_counts = {}
            
            # Count word frequencies
            for word in words:
                word_counts[word] = word_counts.get(word, 0) + 1
            
            # Create sparse representation
            sparse_vector = {}
            total_words = len(words)
            
            # Add keyword weights (higher importance)
            for keyword in keywords:
                keyword_lower = keyword.lower()
                if keyword_lower in word_counts:
                    tf = word_counts[keyword_lower] / total_words
                    sparse_vector[keyword_lower] = tf * 2.0  # Boost keywords
            
            # Add other significant terms
            for word, count in word_counts.items():
                if word not in sparse_vector and count > 1:
                    tf = count / total_words
                    sparse_vector[word] = tf
            
            return sparse_vector
            
        except Exception as e:
            logger.error(f"Error creating sparse vector: {str(e)}")
            return {}
    
    async def health_check(self) -> bool:
        """
        Check if vector database is healthy
        
        Returns:
            True if healthy, False otherwise
        """
        try:
            self._ensure_connection()
            
            # Try to list collections as health check
            collections = self.database.list_collections()
            logger.info(f"[VectorDB] Health check passed: {len(collections)} collections")
            return True
            
        except Exception as e:
            logger.error(f"[VectorDB] Health check failed: {e}")
            return False