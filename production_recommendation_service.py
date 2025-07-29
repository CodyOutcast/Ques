#!/usr/bin/env python3
"""
Production-Ready Recommendation Service with Robust Error Handling
"""

import logging
import time
import json
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass

@dataclass
class RecommendationResult:
    """Result object for recommendation operations"""
    users: List[Dict[str, Any]]
    method_used: str
    success: bool
    error_message: Optional[str] = None
    execution_time: float = 0.0

class RecommendationService:
    """
    Production-ready recommendation service with multiple fallback strategies
    """
    
    def __init__(self, vectordb_timeout=15, max_retries=2):
        self.vectordb_timeout = vectordb_timeout
        self.max_retries = max_retries
        self.logger = logging.getLogger(__name__)
        
    def _retry_operation(self, operation_func, operation_name: str, max_retries: int = None):
        """Retry operation with exponential backoff"""
        max_retries = max_retries or self.max_retries
        
        for attempt in range(max_retries):
            try:
                return operation_func()
            except Exception as e:
                error_msg = str(e).lower()
                is_timeout = any(keyword in error_msg for keyword in 
                               ['timeout', 'connection', 'network', 'unreachable', '502', '503'])
                
                if is_timeout and attempt < max_retries - 1:
                    delay = 1.5 ** (attempt + 1)  # 1.5, 2.25, 3.375 seconds
                    self.logger.warning(f"{operation_name} timeout on attempt {attempt + 1}, retrying in {delay:.1f}s")
                    time.sleep(delay)
                else:
                    self.logger.error(f"{operation_name} failed after {attempt + 1} attempts: {e}")
                    raise
        
        return None
    
    def get_vector_recommendations(self, user_preferences: str, user_id: int, top_k: int = 5) -> List[str]:
        """
        Get recommendations using vector similarity with robust error handling
        """
        try:
            # Import inside method to handle import errors gracefully
            from db_utils import insert_to_vector_db, get_vdb_collection, query_vector_db
            
            # Insert user preferences to get vector
            def insert_operation():
                metadata = {'user_id': user_id, 'temp_query': True}
                return insert_to_vector_db(user_preferences, metadata)
            
            vector_id = self._retry_operation(insert_operation, "Vector insertion")
            
            if not vector_id:
                self.logger.warning("Vector insertion failed, cannot proceed with vector search")
                return []
            
            # Get the embedded vector
            def get_vector_operation():
                collection = get_vdb_collection()
                result = collection.query(
                    document_ids=[str(user_id)],
                    limit=1,
                    retrieve_vector=True
                )
                if result and result[0].get('vector'):
                    return result[0]['vector']
                return None
            
            query_vector = self._retry_operation(get_vector_operation, "Vector retrieval")
            
            if not query_vector:
                self.logger.warning("Could not retrieve query vector")
                return []
            
            # Search for similar users
            def search_operation():
                return query_vector_db(query_vector, top_k * 2)  # Get more to filter
            
            similar_ids = self._retry_operation(search_operation, "Vector search")
            
            # Clean up temporary vector
            try:
                def cleanup_operation():
                    collection = get_vdb_collection()
                    collection.delete(document_ids=[str(user_id)])
                    return True
                
                self._retry_operation(cleanup_operation, "Vector cleanup", max_retries=1)
            except:
                pass  # Ignore cleanup errors
            
            # Filter out the requesting user
            if similar_ids:
                return [uid for uid in similar_ids if str(uid) != str(user_id)][:top_k]
            
            return []
            
        except Exception as e:
            self.logger.error(f"Vector recommendation failed: {e}")
            return []
    
    def get_tag_recommendations(self, user_tags: List[str], user_id: int, top_k: int = 5) -> List[Dict]:
        """
        Get recommendations using tag-based similarity (reliable fallback)
        """
        try:
            from db_utils import get_user_infos
            
            # Get sample of users (in production, this could be optimized)
            user_ids = [str(i) for i in range(1, 101) if i != user_id]  # Sample range
            all_users = get_user_infos(user_ids)
            
            if not all_users:
                return []
            
            # Calculate tag similarity scores
            target_set = set(user_tags)
            scored_users = []
            
            for user in all_users:
                user_tag_list = user.get('feature_tags', [])
                if not user_tag_list:
                    continue
                
                user_set = set(user_tag_list)
                
                # Jaccard similarity
                intersection = len(target_set & user_set)
                union = len(target_set | user_set)
                
                if union > 0 and intersection > 0:  # Only users with some overlap
                    similarity = intersection / union
                    scored_users.append((user, similarity))
            
            # Sort by similarity and return top results
            scored_users.sort(key=lambda x: x[1], reverse=True)
            return [user for user, score in scored_users[:top_k]]
            
        except Exception as e:
            self.logger.error(f"Tag-based recommendation failed: {e}")
            return []
    
    def get_recommendations(
        self, 
        user_id: int,
        user_preferences: str = None,
        user_tags: List[str] = None,
        top_k: int = 5,
        strategy: str = "hybrid"  # "hybrid", "vector", "tags"
    ) -> RecommendationResult:
        """
        Main recommendation method with multiple strategies
        
        Args:
            user_id: ID of user requesting recommendations
            user_preferences: Text description of preferences (for vector search)
            user_tags: List of feature tags (for tag-based search)
            top_k: Number of recommendations to return
            strategy: "hybrid" (try vector, fallback to tags), "vector", or "tags"
        
        Returns:
            RecommendationResult with users and metadata
        """
        start_time = time.time()
        
        recommendations = []
        method_used = "none"
        error_message = None
        
        try:
            if strategy in ["hybrid", "vector"] and user_preferences:
                self.logger.info(f"Attempting vector-based recommendations for user {user_id}")
                
                similar_user_ids = self.get_vector_recommendations(user_preferences, user_id, top_k)
                
                if similar_user_ids:
                    from db_utils import get_user_infos
                    recommendations = get_user_infos(similar_user_ids)
                    method_used = "vector_search"
                    self.logger.info(f"Vector search successful: {len(recommendations)} recommendations")
                else:
                    self.logger.warning("Vector search returned no results")
            
            # Fallback to tag-based search
            if not recommendations and strategy in ["hybrid", "tags"] and user_tags:
                self.logger.info(f"Using tag-based recommendations for user {user_id}")
                
                recommendations = self.get_tag_recommendations(user_tags, user_id, top_k)
                if recommendations:
                    method_used = "tag_based"
                    self.logger.info(f"Tag search successful: {len(recommendations)} recommendations")
            
            # Final fallback - random popular users (in production, use actual popularity metrics)
            if not recommendations:
                self.logger.warning(f"All recommendation methods failed for user {user_id}, using fallback")
                try:
                    from db_utils import get_user_infos
                    fallback_ids = [str(i) for i in [7, 8, 9, 22, 23] if i != user_id]
                    recommendations = get_user_infos(fallback_ids[:top_k])
                    method_used = "fallback"
                except:
                    recommendations = []
                    method_used = "none"
                    error_message = "All recommendation strategies failed"
            
        except Exception as e:
            error_message = str(e)
            self.logger.error(f"Recommendation service error: {e}")
        
        execution_time = time.time() - start_time
        
        return RecommendationResult(
            users=recommendations,
            method_used=method_used,
            success=len(recommendations) > 0,
            error_message=error_message,
            execution_time=execution_time
        )

# Test the production service
def test_recommendation_service():
    """Test the production recommendation service"""
    print("🏭 Testing Production Recommendation Service")
    print("=" * 50)
    
    service = RecommendationService(vectordb_timeout=10, max_retries=2)
    
    # Test cases
    test_cases = [
        {
            "user_id": 999,
            "preferences": "我想找专注于人工智能和机器学习的合作伙伴",
            "tags": ["AI", "Machine Learning", "Deep Learning"],
            "strategy": "hybrid"
        },
        {
            "user_id": 998,
            "preferences": None,
            "tags": ["Blockchain", "Web3", "DeFi"],
            "strategy": "tags"
        },
        {
            "user_id": 997,
            "preferences": "区块链和加密货币项目开发",
            "tags": None,
            "strategy": "vector"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. Testing {test_case['strategy']} strategy...")
        
        result = service.get_recommendations(
            user_id=test_case["user_id"],
            user_preferences=test_case["preferences"],
            user_tags=test_case["tags"],
            top_k=3,
            strategy=test_case["strategy"]
        )
        
        print(f"   📊 Result: {result.method_used} method in {result.execution_time:.2f}s")
        if result.success:
            print(f"   ✅ Found {len(result.users)} recommendations:")
            for j, user in enumerate(result.users, 1):
                tags = ", ".join(user.get('feature_tags', []))
                print(f"      {j}. {user['name']}: {tags}")
        else:
            print(f"   ❌ Failed: {result.error_message}")
    
    print(f"\n🎉 Production service testing complete!")

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    test_recommendation_service()
