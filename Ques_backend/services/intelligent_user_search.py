"""
Intelligent User Search Service
Integrates the end-to-end search pipeline into the chat system
"""
import os
import json
import uuid
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from services.intelligent_search.intelligent_search_agent import SearchAgent
from services.intelligent_search.tencent_vectordb_adapter import TencentVectorDBAdapter
from services.glm4_client import GLM4Client
from tcvectordb import VectorDBClient


class IntelligentUserSearchService:
    """
    Service that provides AI-powered user search functionality
    Integrates intent detection, vector search, and LLM analysis
    """
    
    def __init__(self):
        """Initialize the search service with required components"""
        self.glm_api_key = os.getenv("ZHIPUAI_API_KEY")
        self.vectordb_url = os.getenv("VECTORDB_ENDPOINT")
        self.vectordb_username = os.getenv("VECTORDB_USERNAME")
        self.vectordb_key = os.getenv("VECTORDB_KEY")
        
        # Initialize components
        self.glm_client = None
        self.vectordb_adapter = None
        self.search_agent = None
        self.doc_map = {}
        self._initialized = False
    
    async def initialize(self):
        """Initialize all components asynchronously"""
        if self._initialized:
            return
        
        try:
            # 1. GLM-4 Client for Intent Detection and Analysis
            self.glm_client = GLM4Client(api_key=self.glm_api_key, model="glm-4-flash")
            
            # 2. VectorDB Adapter
            self.vectordb_adapter = TencentVectorDBAdapter(
                url=self.vectordb_url,
                username=self.vectordb_username,
                key=self.vectordb_key,
                database_name='intelligent_search',
                collection_name='user_vectors_hybrid'
            )
            
            # Check health
            health = await self.vectordb_adapter.health_check()
            if not health:
                raise Exception("VectorDB health check failed")
            
            # 3. Search Agent with BGE-M3
            self.search_agent = SearchAgent(
                glm_api_key=self.glm_api_key,
                vectordb_adapter=self.vectordb_adapter,
                collection_name='user_vectors_hybrid'
            )
            
            # 4. Load document mapping for full user data
            await self._load_document_map()
            
            self._initialized = True
            print("✅ IntelligentUserSearchService initialized successfully")
            
        except Exception as e:
            print(f"❌ Failed to initialize IntelligentUserSearchService: {e}")
            raise
    
    async def _load_document_map(self):
        """Load all documents from VectorDB for quick lookup"""
        try:
            client = VectorDBClient(
                url=self.vectordb_url, 
                username=self.vectordb_username, 
                key=self.vectordb_key, 
                timeout=30
            )
            database = client.database('intelligent_search')
            collection = database.collection('user_vectors_hybrid')
            all_docs = collection.query(limit=200, retrieve_vector=False)
            self.doc_map = {doc.get('user_id'): doc for doc in all_docs}
            print(f"✅ Loaded {len(self.doc_map)} user documents")
        except Exception as e:
            print(f"⚠️ Failed to load document map: {e}")
            self.doc_map = {}
    
    async def detect_intent(self, query: str) -> Dict[str, Any]:
        """
        Detect user intent from query
        Returns: {intent: str, confidence: float, reasoning: str}
        """
        intent_prompt = f"""Analyze the user's intent from this query:
Query: "{query}"

Classify the intent as one of:
- search: User wants to find/discover people
- chat: User wants to have a conversation
- question: User is asking a question

Return JSON:
{{
    "intent": "search|chat|question",
    "confidence": 0.0-1.0,
    "reasoning": "explanation"
}}"""
        
        try:
            response = self.glm_client.chat_completion(
                messages=[{"role": "user", "content": intent_prompt}],
                temperature=0.1,
                max_tokens=200
            )
            
            # Parse JSON response - handle different response formats
            if isinstance(response, dict) and 'choices' in response:
                response_text = response['choices'][0]['message']['content'].strip()
            else:
                response_text = str(response).strip()
            
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            intent_data = json.loads(response_text)
            return {
                "intent": intent_data.get('intent', 'search'),
                "confidence": intent_data.get('confidence', 0.8),
                "reasoning": intent_data.get('reasoning', '')
            }
        except Exception as e:
            print(f"⚠️ Intent detection failed: {e}")
            return {"intent": "search", "confidence": 0.8, "reasoning": "Default to search"}
    
    async def optimize_query(self, query: str) -> str:
        """Optimize query for semantic similarity search"""
        optimization_prompt = f"""Optimize this search query for semantic similarity:
Original: "{query}"

Make it more descriptive and search-friendly. Keep it concise (under 100 chars).
Return ONLY the optimized query, no explanation."""
        
        try:
            response = self.glm_client.chat_completion(
                messages=[{"role": "user", "content": optimization_prompt}],
                temperature=0.3,
                max_tokens=100
            )
            optimized = response['choices'][0]['message']['content'].strip().strip('"').strip("'")
            return optimized
        except Exception as e:
            print(f"⚠️ Query optimization failed: {e}")
            return query
    
    async def extract_keywords(self, query: str) -> str:
        """Extract keywords for sparse vector search"""
        keyword_prompt = f"""Extract key search keywords from this query:
Query: "{query}"

Return 3-5 most important keywords for matching, separated by spaces.
Focus on: skills, interests, roles, technologies.
Return ONLY the keywords, no explanation."""
        
        try:
            response = self.glm_client.chat_completion(
                messages=[{"role": "user", "content": keyword_prompt}],
                temperature=0.1,
                max_tokens=50
            )
            keywords = response['choices'][0]['message']['content'].strip()
            return keywords
        except Exception as e:
            print(f"⚠️ Keyword extraction failed: {e}")
            return query
    
    async def perform_hybrid_search(
        self, 
        optimized_query: str, 
        keywords: str, 
        exclude_user_id: int,
        top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """Perform hybrid vector search (dense + sparse)"""
        try:
            # Generate dense vector
            dense_model = self.search_agent._dense_model
            dense_vector = dense_model.encode(optimized_query, normalize_embeddings=True).tolist()
            
            # Generate sparse vector
            sparse_terms = keywords.lower().split()
            sparse_dict = {term: 1.0 for term in sparse_terms}
            
            # Perform hybrid search
            search_results = await self.vectordb_adapter.hybrid_search(
                query_vector=dense_vector,
                sparse_vector=sparse_dict,
                top_k=top_k,
                exclude_ids=[str(exclude_user_id)]
            )
            
            return search_results
        except Exception as e:
            print(f"⚠️ Hybrid search failed: {e}")
            return []
    
    async def analyze_candidates_with_llm(
        self, 
        query: str, 
        search_results: List[Dict[str, Any]], 
        current_user_context: Dict[str, Any],
        top_n: int = 5
    ) -> List[Dict[str, Any]]:
        """Analyze candidates using LLM and select top matches"""
        if not search_results:
            return []
        
        try:
            # Prepare candidate descriptions
            candidate_descriptions = []
            for idx, result in enumerate(search_results[:10], 1):
                desc = f"Candidate {idx} (ID: {result['user_id']}, Score: {result['score']:.3f}):\n"
                desc += f"  Name: {result.get('name', 'N/A')}\n"
                desc += f"  Skills: {result.get('skills', [])}\n"
                desc += f"  Bio: {result.get('bio', 'N/A')[:100]}\n"
                candidate_descriptions.append(desc)
            
            analysis_prompt = f"""Analyze these candidates for the query: "{query}"

Current User: {current_user_context.get('name', 'User')} (Skills: {current_user_context.get('skills', [])})

Candidates:
{chr(10).join(candidate_descriptions)}

Select the TOP {top_n} best matches and rate them 1-10. Return JSON:
{{
    "top_matches": [
        {{"user_id": 7, "score": 8.5, "reason": "Perfect match because..."}},
        ...
    ]
}}"""
            
            response = self.glm_client.chat_completion(
                messages=[{"role": "user", "content": analysis_prompt}],
                temperature=0.3,
                max_tokens=500
            )
            analysis_response = response['choices'][0]['message']['content']
            
            # Parse analysis
            response_text = analysis_response.strip()
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            analysis_data = json.loads(response_text)
            return analysis_data.get('top_matches', [])
            
        except Exception as e:
            print(f"⚠️ LLM candidate analysis failed: {e}")
            # Fallback to top vector search results
            return [
                {
                    "user_id": r['user_id'], 
                    "score": r['score'] * 10, 
                    "reason": "High vector similarity"
                }
                for r in search_results[:top_n]
            ]
    
    async def generate_suggested_queries(self, query: str, results: List[Dict]) -> List[str]:
        """Generate AI-suggested follow-up queries"""
        if not results:
            return [
                "Tell me more about users who share my interests",
                "Find people in my area", 
                "Show me users with similar goals"
            ]
        
        try:
            suggestion_prompt = f"""Based on this search query and results, suggest 3 follow-up queries:
Original query: "{query}"
Found {len(results)} matches

Generate 3 natural follow-up questions a user might ask. Return as JSON array:
["query1", "query2", "query3"]"""
            
            response = self.glm_client.chat_completion(
                messages=[{"role": "user", "content": suggestion_prompt}],
                temperature=0.5,
                max_tokens=150
            )
            
            response_text = response['choices'][0]['message']['content'].strip()
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            suggestions = json.loads(response_text)
            return suggestions if isinstance(suggestions, list) else []
            
        except Exception as e:
            print(f"⚠️ Suggested queries generation failed: {e}")
            return [
                f"Find more users like the ones you showed me",
                f"Show me {query.split()[-1] if query.split() else 'users'} in my area",
                f"Tell me more about these recommendations"
            ]
    
    async def search_users(
        self, 
        query: str, 
        current_user_id: int, 
        current_user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Main search method - performs complete intelligent user search
        
        Args:
            query: User's search query
            current_user_id: ID of the user making the search
            current_user_context: Optional context about current user
            
        Returns:
            {
                "user_ids": List[int],
                "recommendations": List[Dict],
                "suggested_queries": List[str],
                "search_metadata": Dict
            }
        """
        await self.initialize()
        
        if current_user_context is None:
            current_user_context = {"name": "User", "skills": []}
        
        try:
            # Step 1: Intent Detection
            intent_result = await self.detect_intent(query)
            if intent_result["intent"] != "search":
                return {
                    "user_ids": [],
                    "recommendations": [],
                    "suggested_queries": ["How can I help you find the right people?"],
                    "search_metadata": {
                        "intent": intent_result["intent"],
                        "message": f"Intent detected as '{intent_result['intent']}', not performing search"
                    }
                }
            
            # Step 2: Query Optimization
            optimized_query = await self.optimize_query(query)
            
            # Step 3: Keyword Extraction
            keywords = await self.extract_keywords(query)
            
            # Step 4: Hybrid Vector Search
            search_results = await self.perform_hybrid_search(
                optimized_query, keywords, current_user_id, top_k=10
            )
            
            if not search_results:
                return {
                    "user_ids": [],
                    "recommendations": [],
                    "suggested_queries": [
                        "Try a different search term",
                        "Find users in my field",
                        "Show me recent users"
                    ],
                    "search_metadata": {
                        "intent": "search",
                        "message": "No matching users found"
                    }
                }
            
            # Step 5: LLM Candidate Analysis
            top_matches = await self.analyze_candidates_with_llm(
                query, search_results, current_user_context, top_n=5
            )
            
            # Step 6: Build full recommendations with user data
            recommendations = []
            user_ids = []
            
            for match in top_matches:
                user_id = match['user_id']
                user_ids.append(user_id)
                
                # Get full user data from document map
                full_data = self.doc_map.get(user_id, {})
                
                # Handle skills data - convert string to list if needed
                skills = full_data.get('skills', [])
                if isinstance(skills, str):
                    try:
                        skills = json.loads(skills)
                    except:
                        skills = skills.split(',') if skills else []
                
                recommendation = {
                    "user_id": user_id,
                    "name": full_data.get('name', 'Unknown User'),
                    "skills": skills,
                    "bio": full_data.get('bio', ''),
                    "location": full_data.get('location', ''),
                    "match_score": match.get('score', 0) / 10.0,  # Scale to 0-1
                    "why_match": match.get('reason', 'AI-selected match'),
                    "vector_score": next((r['score'] for r in search_results if r['user_id'] == user_id), 0.0)
                }
                recommendations.append(recommendation)
            
            # Step 7: Generate Suggested Queries
            suggested_queries = await self.generate_suggested_queries(query, recommendations)
            
            return {
                "user_ids": user_ids,
                "recommendations": recommendations,
                "suggested_queries": suggested_queries,
                "search_metadata": {
                    "intent": "search",
                    "optimized_query": optimized_query,
                    "keywords": keywords,
                    "total_found": len(search_results),
                    "llm_selected": len(top_matches),
                    "search_successful": True
                }
            }
            
        except Exception as e:
            print(f"❌ Search failed: {e}")
            return {
                "user_ids": [],
                "recommendations": [],
                "suggested_queries": ["Try searching again", "Find users by skill", "Browse recent users"],
                "search_metadata": {
                    "intent": "search",
                    "error": str(e),
                    "search_successful": False
                }
            }


# Global service instance
_search_service = None

async def get_search_service() -> IntelligentUserSearchService:
    """Get or create the global search service instance"""
    global _search_service
    if _search_service is None:
        _search_service = IntelligentUserSearchService()
        await _search_service.initialize()
    return _search_service