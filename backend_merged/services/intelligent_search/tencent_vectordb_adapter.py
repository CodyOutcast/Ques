"""
Tencent VectorDB Adapter for Intelligent Search
Replaces Qdrant client with Tencent VectorDB client
"""

import os
import json
import logging
from typing import List, Dict, Optional, Any, Tuple, Union
import tcvectordb
from tcvectordb.model.collection import Collection
from tcvectordb.model.document import Document, Filter, SearchParams
from tcvectordb.model.enum import FieldType, IndexType, MetricType, ReadConsistency
from tcvectordb.model.index import Index, VectorIndex, FilterIndex, HNSWParams

logger = logging.getLogger(__name__)


class TencentVectorDBAdapter:
    """
    Adapter class to make Tencent VectorDB work like Qdrant for the intelligent search agent
    """
    
    def __init__(
        self,
        url: str = None,
        username: str = "root",
        key: str = None,
        collection_name: str = "user_vectors_hybrid",
        database_name: str = "intelligent_search",
        timeout: int = 30
    ):
        """
        Initialize Tencent VectorDB client
        
        Args:
            url: Vector database endpoint
            username: Username (default: root)
            key: API key
            collection_name: Collection name
            database_name: Database name
            timeout: Request timeout in seconds
        """
        # Get config from environment if not provided
        self.url = url or os.getenv("VECTORDB_ENDPOINT")
        self.username = username or os.getenv("VECTORDB_USERNAME", "root")
        self.key = key or os.getenv("VECTORDB_KEY")
        self.collection_name = collection_name or os.getenv("VECTORDB_COLLECTION", "user_vectors_hybrid")
        self.database_name = database_name
        self.timeout = timeout
        
        if not self.url or not self.key:
            raise ValueError("Vector database URL and KEY must be provided")
        
        # Initialize client
        self.client = tcvectordb.VectorDBClient(
            url=self.url,
            username=self.username,
            key=self.key,
            timeout=self.timeout
        )
        
        # Get or create database
        self.db = self._get_or_create_database()
        
        # Get or create collection - initialize immediately
        self.collection = None
        try:
            self.collection = self.db.collection(self.collection_name)
            logger.info(f"Connected to existing collection: {self.collection_name}")
        except Exception as e:
            logger.info(f"Collection {self.collection_name} not found: {e}")
            logger.info(f"Use ensure_collection() to create it")
        
        logger.info(f"Tencent VectorDB Adapter initialized: {self.url}")
    
    def _parse_sparse_vector(self, sparse_data: str) -> Dict[int, float]:
        """Parse sparse vector from JSON string"""
        try:
            if isinstance(sparse_data, str):
                return json.loads(sparse_data)
            elif isinstance(sparse_data, dict):
                return sparse_data
            else:
                return {}
        except (json.JSONDecodeError, TypeError):
            return {}
    
    def _get_or_create_database(self):
        """Get existing database or create new one"""
        try:
            # Try to get existing database
            return self.client.database(self.database_name)
        except Exception as e:
            logger.info(f"Database {self.database_name} not found, creating...")
            return self.client.create_database(self.database_name)
    
    def create_collection(
        self,
        dense_dimension: int = 1024,
        sparse_dimension: int = 30000,
        metric_type: str = "cosine",
        description: str = "Intelligent search user vectors with dense and sparse support"
    ):
        """
        Create vector collection with both dense and sparse vector support
        
        Args:
            dense_dimension: Dense vector dimension (BGE-M3: 1024)
            sparse_dimension: Sparse vector dimension (SPLADE: 30000)
            metric_type: Distance metric (cosine, l2, ip)
            description: Collection description
        """
        try:
            # Check if collection exists
            self.collection = self.db.collection(self.collection_name)
            logger.info(f"Collection {self.collection_name} already exists")
            return self.collection
        except Exception:
            logger.info(f"Creating collection {self.collection_name} with dense ({dense_dimension}D) and sparse ({sparse_dimension}D) vectors...")
            
            # Map metric type
            metric_map = {
                "cosine": MetricType.COSINE,
                "l2": MetricType.L2,
                "ip": MetricType.IP
            }
            metric = metric_map.get(metric_type.lower(), MetricType.COSINE)
            
            # Create collection with both dense and sparse vector indexes
            # TencentVectorDB supports native hybrid search with separate dense and sparse fields
            self.collection = self.db.create_collection(
                name=self.collection_name,
                shard=1,
                replicas=1,
                description=description,
                index=Index(
                    FilterIndex(name='id', field_type=FieldType.String, index_type=IndexType.PRIMARY_KEY),
                    FilterIndex(name='user_id', field_type=FieldType.Uint64, index_type=IndexType.FILTER),
                    FilterIndex(name='name', field_type=FieldType.String, index_type=IndexType.FILTER),
                    FilterIndex(name='location', field_type=FieldType.String, index_type=IndexType.FILTER),
                    # Dense vector index (BGE-M3)
                    VectorIndex(
                        name='dense_vector',
                        dimension=dense_dimension,
                        index_type=IndexType.HNSW,
                        metric_type=metric,
                        params=HNSWParams(m=16, efconstruction=200)
                    ),
                    # Sparse vector index (SPLADE/TF-IDF)
                    VectorIndex(
                        name='sparse_vector',
                        dimension=sparse_dimension,
                        index_type=IndexType.SPARSE_INVERTED,
                        metric_type=MetricType.IP,  # Inner product for sparse vectors
                        params=None  # No specific parameters for sparse inverted index
                    )
                )
            )
            
            logger.info(f"Collection {self.collection_name} created successfully")
            return self.collection
    
    def ensure_collection(
        self,
        dimension: int = None,  # Backward compatibility
        dense_dimension: int = None,
        sparse_dimension: int = 30000,
        metric_type: str = "cosine",
        description: str = "Intelligent search user vectors with dense and sparse support"
    ):
        """
        Ensure collection exists (alias for create_collection)
        
        Args:
            dimension: Vector dimension (backward compatibility)
            dense_dimension: Dense vector dimension (BGE-M3: 1024)
            sparse_dimension: Sparse vector dimension (SPLADE: 30000)
            metric_type: Distance metric (cosine, l2, ip)
            description: Collection description
        """
        # Handle backward compatibility
        if dimension is not None:
            dense_dimension = dimension
        elif dense_dimension is None:
            dense_dimension = 1024
            
        return self.create_collection(dense_dimension, sparse_dimension, metric_type, description)
    
    def upsert(
        self,
        points: Union[List[Dict], int] = None,
        dense_vector: List[float] = None,
        sparse_vector: Optional[Dict[int, float]] = None,
        payload: Dict[str, Any] = None,
        user_id: int = None
    ) -> bool:
        """
        Insert or update vector (supports both single and batch operations)
        
        Args:
            points: List of point dicts (batch mode) with format:
                   [{"id": str, "vector": List[float], "payload": Dict}]
            dense_vector: Dense vector for single mode
            sparse_vector: Sparse vector (SPLADE) as {index: value}
            payload: Metadata for single mode
            user_id: User ID for single mode (backward compatibility)
        
        Returns:
            Success status
        """
        try:
            # Batch mode: points is a list
            if isinstance(points, list):
                if not points:
                    return True
                
                # Use first vector to get dimension
                first_vector = points[0].get('vector', [])
                if not self.collection:
                    self.create_collection(dimension=len(first_vector))
                
                # Process each point
                for point in points:
                    point_id = point.get('id', 'user_0')
                    vector = point.get('vector', [])
                    point_payload = point.get('payload', {})
                    
                    # Extract dense and sparse vectors from point
                    dense_vec = point.get('dense_vector', vector)  # Backward compatibility
                    sparse_vec = point.get('sparse_vector', [])
                    
                    # Convert sparse vector dict to list if needed
                    if isinstance(sparse_vec, dict):
                        sparse_vec_list = [0.0] * 30000
                        for idx, val in sparse_vec.items():
                            if idx < 30000:
                                sparse_vec_list[idx] = val
                        sparse_vec = sparse_vec_list
                    elif not sparse_vec:
                        sparse_vec = [0.0] * 30000
                    
                    # Convert sparse vector to proper format
                    if isinstance(sparse_vec, dict):
                        # Convert dict {index: value} to sparse vector format for TencentVectorDB
                        sparse_indices = list(sparse_vec.keys())
                        sparse_values = list(sparse_vec.values())
                        sparse_vector_field = {'indices': sparse_indices, 'values': sparse_values}
                    elif isinstance(sparse_vec, list):
                        # If it's already a list, convert to sparse format (only non-zero values)
                        sparse_indices = [i for i, val in enumerate(sparse_vec) if val != 0]
                        sparse_values = [sparse_vec[i] for i in sparse_indices]
                        sparse_vector_field = {'indices': sparse_indices, 'values': sparse_values}
                    else:
                        sparse_vector_field = {'indices': [], 'values': []}
                    
                    doc_data = {
                        'id': str(point_id),  # Primary key
                        'user_id': int(point_id.replace('user_', '').replace('test_user_', '')) if isinstance(point_id, str) else int(point_id),
                        'dense_vector': dense_vec,  # Dense vector field (BGE-M3)
                        'sparse_vector': sparse_vector_field,  # Sparse vector field (SPLADE/TF-IDF)
                        'name': point_payload.get('name', ''),
                        'location': point_payload.get('location', ''),
                        'skills': json.dumps(point_payload.get('tags', [])),
                        'hobbies': json.dumps(point_payload.get('hobbies', [])),
                        'bio': point_payload.get('bio', '')
                    }
                    
                    doc = Document(**doc_data)
                    self.collection.upsert([doc])
                
                return True
            
            # Single mode (backward compatibility)
            if user_id is not None and dense_vector is not None:
                if not self.collection:
                    self.create_collection(dense_dimension=len(dense_vector))
            
            # Convert sparse vector to list format
            sparse_vec_list = [0.0] * 30000
            if sparse_vector:
                for idx, val in sparse_vector.items():
                    if idx < 30000:
                        sparse_vec_list[idx] = val
            
            # Convert sparse vector to proper format
            if isinstance(sparse_vector, dict):
                sparse_indices = list(sparse_vector.keys())
                sparse_values = list(sparse_vector.values())
                sparse_vector_field = {'indices': sparse_indices, 'values': sparse_values}
            else:
                sparse_vector_field = {'indices': [], 'values': []}
            
            # Prepare document with both vectors
            doc_data = {
                'id': f'user_{user_id}',  # Primary key
                'user_id': user_id,
                'dense_vector': dense_vector,  # Dense vector field (BGE-M3)
                'sparse_vector': sparse_vector_field,  # Sparse vector field (SPLADE/TF-IDF)
            }
            
            # Add payload fields
            if payload:
                doc_data['name'] = payload.get('name', '')
                doc_data['location'] = payload.get('location', '')
                doc_data['skills'] = json.dumps(payload.get('skills', []))
                doc_data['hobbies'] = json.dumps(payload.get('hobbies', []))
                doc_data['bio'] = payload.get('bio', '')
            
            # Upsert document
            self.collection.upsert(documents=[Document(**doc_data)])
            
            logger.debug(f"Upserted vector for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error upserting vector for user {user_id}: {e}")
            return False
    
    def search(
        self,
        dense_vector: Optional[List[float]] = None,
        sparse_vector: Optional[Dict[int, float]] = None,
        limit: int = 10,
        filter_conditions: Optional[Dict] = None,
        use_hybrid: bool = True,
        alpha: float = 0.5
    ) -> List[Dict]:
        """
        Search vectors with hybrid or single vector mode
        
        Args:
            dense_vector: Dense query vector
            sparse_vector: Sparse query vector
            limit: Number of results
            filter_conditions: Filter conditions (e.g., {"location": "Beijing"})
            use_hybrid: Whether to use hybrid search
            alpha: Weight for dense vector (0-1), 1-alpha for sparse
        
        Returns:
            List of search results with scores and payloads
        """
        try:
            if not self.collection:
                raise ValueError("Collection not initialized")
            
            results = []
            
            if use_hybrid and dense_vector and sparse_vector:
                # Hybrid search
                results = self._hybrid_search(
                    dense_vector, sparse_vector, limit, filter_conditions, alpha
                )
            elif dense_vector:
                # Dense vector only
                results = self._dense_search(dense_vector, limit, filter_conditions)
            elif sparse_vector:
                # Sparse vector only
                results = self._sparse_search(sparse_vector, limit, filter_conditions)
            else:
                raise ValueError("At least one vector type must be provided")
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching vectors: {e}")
            return []
    
    def _dense_search(
        self,
        vector: List[float],
        limit: int,
        filter_conditions: Optional[Dict] = None
    ) -> List[Dict]:
        """Search using dense vector only"""
        search_params = SearchParams(ef=200)
        
        if filter_conditions:
            search_params.filter = self._build_filter(filter_conditions)
        
        # Search using dense_vector field
        res = self.collection.search(
            vectors=[vector],
            params=search_params,
            retrieve_vector=False,
            limit=limit,
            # Note: TencentVectorDB uses the first VectorIndex by default (dense_vector)
        )
        
        return self._format_results(res)
    
    def _sparse_search(
        self,
        sparse_vector: Dict[int, float],
        limit: int,
        filter_conditions: Optional[Dict] = None
    ) -> List[Dict]:
        """Search using sparse vector only"""
        # Convert to list format
        sparse_vec_list = [0.0] * 30000
        for idx, val in sparse_vector.items():
            if idx < 30000:
                sparse_vec_list[idx] = val
        
        search_params = SearchParams(ef=200)
        
        if filter_conditions:
            search_params.filter = self._build_filter(filter_conditions)
        
        # Note: For TencentVectorDB, we may need to implement sparse search differently
        # This is a placeholder - actual implementation may vary based on TencentVectorDB API
        res = self.collection.search(
            vectors=[sparse_vec_list],
            params=search_params,
            retrieve_vector=False,
            limit=limit,
            # TODO: Specify sparse_vector field if TencentVectorDB supports field selection
        )
        
        return self._format_results(res)
    
    def export_candidates_for_qdrant_fusion(
        self,
        dense_vector: List[float],
        sparse_vector: Dict[int, float],
        limit: int,
        filter_conditions: Optional[Dict] = None
    ) -> Tuple[List[Dict], List[Dict]]:
        """
        Method 1: Export candidates from TencentVectorDB for Qdrant fusion
        
        Returns:
            Tuple of (dense_results, sparse_results) for Qdrant fusion
        """
        try:
            # Get dense candidates from TencentVectorDB
            dense_results = self._dense_search(
                vector=dense_vector,
                limit=limit * 3,  # More candidates for better fusion
                filter_conditions=filter_conditions
            )
            
            # Simulate sparse search by re-ranking dense results using stored sparse vectors
            sparse_results = []
            for result in dense_results:
                sparse_data = result.get('sparse_vector_data', '{}')
                stored_sparse = self._parse_sparse_vector(sparse_data)
                
                # Calculate sparse similarity
                sparse_score = self._calculate_sparse_similarity(sparse_vector, stored_sparse)
                
                sparse_results.append({
                    **result,
                    'score': sparse_score,  # Override with sparse score
                    'search_type': 'sparse'
                })
            
            # Sort sparse results by sparse score
            sparse_results.sort(key=lambda x: x['score'], reverse=True)
            
            # Mark dense results
            for result in dense_results:
                result['search_type'] = 'dense'
            
            return dense_results[:limit], sparse_results[:limit]
            
        except Exception as e:
            logger.error(f"Export for Qdrant fusion failed: {e}")
            return [], []
    
    def native_hybrid_search(
        self,
        dense_vector: List[float],
        sparse_vector: Dict[int, float],
        limit: int,
        filter_conditions: Optional[Dict] = None,
        rerank_method: str = "weighted"  # "weighted" or "rrf"
    ) -> List[Dict]:
        """
        Method 2: Use TencentVectorDB native hybrid search with separate vector fields
        
        Args:
            dense_vector: Dense query vector (1024D)
            sparse_vector: Sparse query vector (dict format)
            limit: Number of results
            filter_conditions: Filter conditions
            rerank_method: "weighted" or "rrf"
        """
        try:
            from tcvectordb.model.document import AnnSearch, KeywordSearch, RRFRerank, WeightedRerank
            
            if not self.collection:
                raise ValueError("Collection not initialized")
            
            # Convert sparse vector to TencentVectorDB format
            sparse_indices = list(sparse_vector.keys()) if sparse_vector else []
            sparse_values = list(sparse_vector.values()) if sparse_vector else []
            
            # Create ANN search for dense vectors
            ann_search = AnnSearch(
                field_name="dense_vector",  # Use separate dense vector field
                data=dense_vector,
                limit=limit * 3,  # Get more candidates for better fusion
                params={"ef": 200}
            )
            
            # Create keyword/sparse search 
            # For TencentVectorDB, we might need to handle sparse differently
            keyword_search = None
            if sparse_indices and sparse_values:
                try:
                    # Try using KeywordSearch if supported for sparse vectors
                    keyword_search = KeywordSearch(
                        field_name="sparse_vector",
                        data={'indices': sparse_indices, 'values': sparse_values},
                        limit=limit * 3
                    )
                except Exception as e:
                    logger.warning(f"KeywordSearch not supported for sparse vectors: {e}")
                    keyword_search = None
            
            # Build filter if needed
            db_filter = self._build_filter(filter_conditions) if filter_conditions else None
            
            # Choose rerank method
            if rerank_method == "rrf":
                rerank = RRFRerank(k=60)  # RRF with k=60
            else:
                # Weighted rerank: 20% dense, 80% sparse (original alpha=0.2)
                rerank = WeightedRerank(
                    field_list=["dense_vector", "sparse_vector"],
                    weight=[0.2, 0.8]
                )
            
            # Execute native hybrid search
            # Try different API formats for TencentVectorDB hybrid_search
            try:
                results = self.collection.hybrid_search(
                    ann=[ann_search],  # List format
                    match=keyword_search,
                    filter=db_filter,
                    rerank=rerank,
                    limit=limit,
                    retrieve_vector=False,
                    output_fields=["id", "user_id", "name", "location", "skills", "hobbies", "bio"]
                )
            except Exception as e1:
                logger.warning(f"First hybrid_search format failed: {e1}")
                try:
                    # Try alternative format without keyword search
                    results = self.collection.search(
                        vectors=[dense_vector],
                        filter=db_filter,
                        limit=limit,
                        retrieve_vector=False,
                        output_fields=["id", "user_id", "name", "location", "skills", "hobbies", "bio"]
                    )
                    logger.info("Fallback to standard vector search")
                except Exception as e2:
                    logger.error(f"Both search methods failed: {e2}")
                    raise e1
            
            # Format results
            formatted_results = []
            if results and len(results) > 0:
                for hit in results[0]:  # TencentVectorDB returns List[List[Dict]]
                    formatted_results.append({
                        'user_id': hit.get('user_id'),
                        'score': hit.get('score', 0.0),
                        'name': hit.get('name', ''),
                        'location': hit.get('location', ''),
                        'skills': hit.get('skills', ''),
                        'hobbies': hit.get('hobbies', ''),
                        'bio': hit.get('bio', ''),
                        'search_method': 'tencent_native_hybrid'
                    })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"TencentVectorDB native hybrid search failed: {e}")
            logger.error(f"Falling back to manual hybrid search")
            return self._hybrid_search_fallback(dense_vector, sparse_vector, limit, filter_conditions)
    
    def _hybrid_search_fallback(
        self,
        dense_vector: List[float],
        sparse_vector: Dict[int, float],
        limit: int,
        filter_conditions: Optional[Dict],
        alpha: float = 0.3
    ) -> List[Dict]:
        """
        Fallback hybrid search method (original implementation)
        """
        try:
            # Step 1: Get more candidates using dense vector search
            dense_results = self._dense_search(
                vector=dense_vector,
                limit=limit * 3,  # Get more candidates for re-ranking
                filter_conditions=filter_conditions
            )
            
            if not dense_results:
                return []
            
            # Step 2: Calculate sparse similarities for re-ranking
            hybrid_scores = []
            
            for result in dense_results:
                dense_score = result.get('score', 0.0)
                
                # Parse sparse vector from stored data
                sparse_data = result.get('sparse_vector_data', '{}')
                stored_sparse = self._parse_sparse_vector(sparse_data)
                
                # Calculate sparse similarity (cosine similarity)
                sparse_score = self._calculate_sparse_similarity(sparse_vector, stored_sparse)
                
                # Combine scores using alpha weighting
                hybrid_score = alpha * dense_score + (1 - alpha) * sparse_score
                
                hybrid_scores.append({
                    **result,
                    'dense_score': dense_score,
                    'sparse_score': sparse_score,
                    'hybrid_score': hybrid_score,
                    'score': hybrid_score,  # Update main score
                    'search_method': 'manual_fallback'
                })
            
            # Step 3: Sort by hybrid score and return top results
            hybrid_scores.sort(key=lambda x: x['hybrid_score'], reverse=True)
            return hybrid_scores[:limit]
            
        except Exception as e:
            logger.error(f"Fallback hybrid search failed: {e}")
            # Final fallback to dense search only
            return self._dense_search(dense_vector, limit, filter_conditions)
    
    def _hybrid_search(
        self,
        dense_vector: List[float],
        sparse_vector: Dict[int, float],
        limit: int,
        filter_conditions: Optional[Dict],
        alpha: float
    ) -> List[Dict]:
        """
        Legacy hybrid search method - now calls native hybrid search
        """
        return self.native_hybrid_search(
            dense_vector=dense_vector,
            sparse_vector=sparse_vector,
            limit=limit,
            filter_conditions=filter_conditions,
            rerank_method="weighted"
        )
    
    def _calculate_sparse_similarity(self, query_sparse: Dict[int, float], doc_sparse: Dict[int, float]) -> float:
        """Calculate cosine similarity between sparse vectors"""
        if not query_sparse or not doc_sparse:
            return 0.0
        
        # Convert to sets of indices for intersection
        query_indices = set(query_sparse.keys())
        doc_indices = set(doc_sparse.keys())
        common_indices = query_indices.intersection(doc_indices)
        
        if not common_indices:
            return 0.0
        
        # Calculate dot product
        dot_product = sum(query_sparse[i] * doc_sparse[i] for i in common_indices)
        
        # Calculate magnitudes
        query_magnitude = sum(val ** 2 for val in query_sparse.values()) ** 0.5
        doc_magnitude = sum(val ** 2 for val in doc_sparse.values()) ** 0.5
        
        if query_magnitude == 0 or doc_magnitude == 0:
            return 0.0
        
        # Return cosine similarity
        return dot_product / (query_magnitude * doc_magnitude)
    
    def _original_hybrid_search(
        self,
        dense_vector: List[float],
        sparse_vector: Dict[int, float],
        limit: int,
        filter_conditions: Optional[Dict],
        alpha: float
    ) -> List[Dict]:
        """
        Hybrid search combining dense and sparse vectors
        Uses weighted score combination
        """
        # Get results from both searches
        dense_results = self._dense_search(dense_vector, limit * 2, filter_conditions)
        sparse_results = self._sparse_search(sparse_vector, limit * 2, filter_conditions)
        
        # Combine and rerank
        combined_scores = {}
        
        for result in dense_results:
            user_id = result['user_id']
            combined_scores[user_id] = {
                'dense_score': result['score'],
                'sparse_score': 0.0,
                'payload': result['payload']
            }
        
        for result in sparse_results:
            user_id = result['user_id']
            if user_id in combined_scores:
                combined_scores[user_id]['sparse_score'] = result['score']
            else:
                combined_scores[user_id] = {
                    'dense_score': 0.0,
                    'sparse_score': result['score'],
                    'payload': result['payload']
                }
        
        # Calculate weighted scores
        final_results = []
        for user_id, scores in combined_scores.items():
            combined_score = (alpha * scores['dense_score'] + 
                            (1 - alpha) * scores['sparse_score'])
            final_results.append({
                'user_id': user_id,
                'score': combined_score,
                'payload': scores['payload']
            })
        
        # Sort by combined score and return top results
        final_results.sort(key=lambda x: x['score'], reverse=True)
        return final_results[:limit]
    
    def _build_filter(self, conditions: Dict) -> Filter:
        """Build filter from conditions"""
        # Simple filter implementation
        # Can be extended based on needs
        filter_expr = " and ".join([
            f'{key}="{value}"' for key, value in conditions.items()
        ])
        return Filter(filter_expr)
    
    def _format_results(self, raw_results) -> List[Dict]:
        """Format Tencent VectorDB results to standard format"""
        results = []
        
        if not raw_results or not isinstance(raw_results, list):
            return results
        
        # raw_results is a list of lists (one per query vector)
        # We only search with one vector, so use first result set
        documents = raw_results[0] if raw_results else []
        
        for doc in documents:
            # Documents are returned as dicts with all fields
            results.append({
                'user_id': doc.get('user_id'),
                'score': doc.get('score', 0.0),
                'payload': {
                    'name': doc.get('name', ''),
                    'location': doc.get('location', ''),
                    'skills': json.loads(doc.get('skills', '[]')),
                    'hobbies': json.loads(doc.get('hobbies', '[]')),
                    'bio': doc.get('bio', '')
                }
            })
        
        return results
    
    def delete(self, user_ids: List[int]) -> bool:
        """Delete vectors by user IDs"""
        try:
            if not self.collection:
                return False
            
            filter_expr = f"user_id in ({','.join(map(str, user_ids))})"
            self.collection.delete(filter=Filter(filter_expr))
            
            logger.info(f"Deleted {len(user_ids)} vectors")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting vectors: {e}")
            return False
    
    def count(self) -> int:
        """Get total number of vectors in collection"""
        try:
            if not self.collection:
                return 0
            
            stats = self.collection.stats()
            return stats.get('total_count', 0)
            
        except Exception as e:
            logger.error(f"Error getting count: {e}")
            return 0
