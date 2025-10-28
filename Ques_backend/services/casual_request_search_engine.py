"""
Casual Request Search Engine
As specified in casual_request_integration_guide_en.md
"""

import json
import time
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer
from services.glm4_client import GLM4Client


class CasualRequestSearchEngine:
    """Casual request search engine"""
    
    def __init__(
        self,
        glm_api_key: str = None,
        qdrant_client=None,
        collection_name: str = "casual_requests",
        glm_model: str = "glm-4-flash",
        api_base_url: str = "http://localhost:8000",
        embedding_model: SentenceTransformer = None
    ):
        """Initialize search engine"""
        self.glm_client = GLM4Client(
            api_key=glm_api_key,
            model=glm_model
        )
        self.qdrant_client = qdrant_client
        self.collection_name = collection_name
        self.api_base_url = api_base_url.rstrip('/')
        
        # Use shared embedding model
        self.embedding_model = embedding_model or SentenceTransformer('BAAI/bge-m3')
    
    async def search_casual_requests(self, query_text: str, limit: int = 10) -> List[Dict]:
        """Search for similar casual requests"""
        try:
            # Generate query vector (consider moving this step to the vector database side to reduce server load)
            query_vector = self.embedding_model.encode(query_text, normalize_embeddings=True).tolist()
            
            # Execute vector search - note this only uses dense vector search, no sparse vectors and no search strategy expansion
            search_results = self.qdrant_client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                limit=limit  # Direct search for specified number, no complex search strategy
            )
            
            # Process results
            results = []
            for hit in search_results:
                # Extract payload from results
                payload = hit.payload
                
                # Add search score
                result = {
                    "user_id": payload.get("user_id", "unknown"),
                    "query": payload.get("query", ""),
                    "optimized_query": payload.get("optimized_query", ""),
                    "score": hit.score,  # Similarity score
                    "last_activity_at": payload.get("last_activity_at", 0)
                }
                
                results.append(result)
            
            return results
        
        except Exception as e:
            print(f"Error searching request: {e}")
            return []
    
    async def find_best_match(
        self,
        casual_results: List[Dict],
        query_text: str,
        current_user: Dict = None,
        language_code: str = "zh"
    ) -> Dict:
        """Find the best match from search results"""
        if not casual_results:
            # No results
            return {
                "match_found": False,
                "reason": "No matching casual requests found"
            }
        
        # Build LLM prompt
        system_prompt = f"""
        You are a specialist in analyzing the match degree of casual social requests. Your task is to analyze the match between the original query and search results.
        
        Original query: "{query_text}"
        
        Search results:
        {json.dumps(casual_results[:3], ensure_ascii=False, indent=2)}
        
        Please analyze these results and return your answer in the following JSON format:
        {{
            "best_match": {{
                "user_id": "",                // User ID of the best match
                "score": 0.0-1.0,             // Match score
                "reason": "",                 // Match reason
                "receiver_notification": ""   // Notification for the receiver, format: "[Sender name] is looking for social partners, they want to [activity description], which matches your interests very well"
            }},
            "should_contact": true/false,     // Whether contact is recommended
            "suggestion": ""                  // Suggestion for the query user
        }}
        
        Please use {"Chinese" if language_code == "zh" else "English"}.
        Return only JSON format results, do not add extra explanations.
        """
        
        try:
            # Get current user name
            sender_name = current_user.get("name", "User") if current_user else "User"
            
            # Call LLM for match analysis
            response = self.glm_client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": "Please analyze the match degree of these search results"}
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            # Parse results
            result_text = response.choices[0].message.content
            result = json.loads(result_text)
            
            # Ensure return results include necessary fields
            best_match = result.get("best_match", {})
            if best_match:
                best_match["match_found"] = True
            
            return {
                "match_found": True,
                "user_id": best_match.get("user_id", casual_results[0].get("user_id", "")),
                "score": best_match.get("score", casual_results[0].get("score", 0.0)),
                "reason": best_match.get("reason", "Matched based on similar activity interests"),
                "receiver_notification": best_match.get("receiver_notification", 
                    f"{sender_name} is looking for social partners, wants to {casual_results[0].get('optimized_query', 'participate in activities')} together"),
                "should_contact": result.get("should_contact", True),
                "suggestion": result.get("suggestion", "")
            }
        except Exception as e:
            print(f"Error analyzing match: {e}")
            # Return default result
            return {
                "match_found": True,
                "user_id": casual_results[0].get("user_id", ""),
                "score": casual_results[0].get("score", 0.0),
                "reason": "Matched based on similar activity interests",
                "receiver_notification": f"{sender_name if current_user else 'User'} is looking for social partners, wants to participate in activities together",
                "should_contact": True,
                "suggestion": ""
            }