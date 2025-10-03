#!/usr/bin/env python3
"""
Intelligent Search Agent Algorithm Implementation
Intelligent talent search system based on GLM-4 and hybrid vector search

Reference documentation: docs/search_agent_design_new.md
"""

import asyncio
import json
import re
import time
import httpx
from typing import Dict, List, Optional, Union, Any, Tuple
from datetime import datetime
from qdrant_client import QdrantClient, models
from qdrant_client.http.models import Distance, VectorParams

# Import GLM-4 client
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'llm'))
try:
    from glm4_client import GLM4Client, GLM4Model, ResponseFormat
except ImportError:
    # If direct import fails, try relative import
    try:
        from ..llm.glm4_client import GLM4Client, GLM4Model, ResponseFormat
    except ImportError:
        print("Warning: Unable to import GLM4Client, please check path configuration")
        GLM4Client = None


class SearchAgent:
    """Intelligent Search Agent Core Class"""
    
    def __init__(
        self,
        glm_api_key: str = None,
        qdrant_client: QdrantClient = None,
        collection_name: str = "users_rawjson",
        glm_model: str = "glm-4-flash",
        api_base_url: str = "http://localhost:8000"
    ):
        """
        Initialize search agent
        
        Args:
            glm_api_key: GLM-4 API key
            qdrant_client: Qdrant client instance
            collection_name: Qdrant collection name
            glm_model: GLM-4 model name
            api_base_url: Database API base URL
        """
        # Initialize GLM-4 client
        self.glm_client = GLM4Client(
            api_key=glm_api_key,
            model=glm_model
        )
        
        # Initialize Qdrant client
        self.qdrant_client = qdrant_client or QdrantClient("localhost", port=6333)
        self.collection_name = collection_name
        
        # Database API configuration
        self.api_base_url = api_base_url.rstrip('/')
        
        # Preload embedding models
        print("🔄 Loading embedding models...")
        self._initialize_embedding_models()
        print("✅ Embedding models loaded successfully")
        
        # Statistics
        self.stats = {
            "search_count": 0,
            "total_search_time": 0.0,
            "llm_calls": 0,
            "cache_hits": 0,
            "vector_searches": 0
        }
    
    def _initialize_embedding_models(self):
        """Initialize embedding models"""
        try:
            # Initialize BGE-M3 dense vector model
            from sentence_transformers import SentenceTransformer
            print("  📥 Loading BGE-M3 dense vector model...")
            self._dense_model = SentenceTransformer('BAAI/bge-m3')
            
            # Initialize SPLADE sparse vector model
            from transformers import AutoModelForMaskedLM, AutoTokenizer
            import torch
            print("  📥 Loading SPLADE sparse vector model...")
            self._splade_tokenizer = AutoTokenizer.from_pretrained("naver/splade-v3")
            self._splade_model = AutoModelForMaskedLM.from_pretrained("naver/splade-v3")
            
            # Set device
            self._device = 'mps' if torch.backends.mps.is_available() else ('cuda' if torch.cuda.is_available() else 'cpu')
            self._splade_model = self._splade_model.to(self._device)
            print(f"  🔧 Using device: {self._device}")
            
        except Exception as e:
            print(f"❌ Embedding model loading failed: {e}")
            # Set to None, reload when needed
            self._dense_model = None
            self._splade_model = None
            self._splade_tokenizer = None
    
    # ===== 3.0 Intent Recognition System =====
    
    def analyze_user_intent(
        self, 
        user_input: str, 
        referenced_user: Dict = None, 
        current_user: Dict = None
    ) -> Dict:
        """
        Analyze user intent, identifying search, inquiry, and chat types
        
        Args:
            user_input: User input text
            referenced_user: Referenced user information (if any)
            current_user: Current user information (if any)
            
        Returns:
            Intent analysis result: {
                "intent": "search|inquiry|chat",
                "confidence": float,
                "reasoning": str,
                "clarification_needed": bool,
                "uncertainty_reason": str (if clarification needed)
            }
        """
        self.stats["llm_calls"] += 1
        
        # Build referenced user information
        referenced_info = ""
        if referenced_user:
            referenced_info = f"""
Referenced user information:
{json.dumps(referenced_user, ensure_ascii=False, indent=2)}
"""
        
        # Build current user information
        current_user_info = ""
        if current_user:
            current_user_info = f"""
Current user information:
{json.dumps(current_user, ensure_ascii=False, indent=2)}
"""
        
        system_prompt = """
You are a professional user intent analysis expert. Your task is to accurately identify user intent types and provide detailed analysis.

Intent Type Definitions:

1. **Search**: User wants to find talents or users that meet specific criteria
   - Key features: Contains verbs like find, search, look for people
   - Describes conditions: Skills, experience, location, industry filtering criteria
   - Typical expressions: "Help me find a Python engineer", "Looking for product managers in Beijing"

2. **Inquiry**: User asks questions about specific referenced users or needs detailed information
   - Key features: Questions targeting specific users
   - Requires referenced user: Must have a clear target user
   - Typical expressions: "How are this person's skills?", "Is he suitable for our project?", "Can you introduce in detail?"

3. **Chat**: General conversation, consultation, or unclear communication
   - Key features: No clear search or inquiry target
   - Includes greetings, general consultation, feature understanding, etc.
   - Typical expressions: "Hello", "How to use this system?", "Any suggestions?"

Analysis Requirements:
- Carefully analyze the semantics and context of user input
- Consider whether there is referenced user information to assist judgment
- If intent is unclear, mark as needing clarification
- Provide clear reasoning process

Return JSON format:
{
    "intent": "search|inquiry|chat",
    "confidence": 0.0-1.0,
    "reasoning": "Detailed analysis reasoning process",
    "clarification_needed": boolean,
    "uncertainty_reason": "If clarification needed, explain reason"
}
"""
        
        user_prompt = f"""
User input: "{user_input}"

{referenced_info}

{current_user_info}

Please analyze the user's intent type. Pay special attention to:
- If there is a referenced user and the user is asking related questions, it's likely inquiry type
- If the user is describing search criteria, it's likely search type  
- If intent is unclear or general conversation, it's likely chat type

Please provide detailed intent analysis.
"""
        
        try:
            result = self.glm_client.json_chat(
                content=user_prompt,
                system_prompt=system_prompt,
                temperature=0.1,
                max_tokens=500
            )
            
            # Validate and standardize result
            intent = result.get("intent", "chat").lower()
            if intent not in ["search", "inquiry", "chat"]:
                intent = "chat"
            
            confidence = float(result.get("confidence", 0.5))
            confidence = max(0.0, min(1.0, confidence))  # Ensure in 0-1 range
            
            return {
                "intent": intent,
                "confidence": confidence,
                "reasoning": result.get("reasoning", "Unable to get analysis reasoning"),
                "clarification_needed": result.get("clarification_needed", False),
                "uncertainty_reason": result.get("uncertainty_reason", "")
            }
            
        except Exception as e:
            print(f"Intent analysis failed: {e}")
            # Return default conservative analysis
            return {
                "intent": "chat",
                "confidence": 0.3,
                "reasoning": "LLM analysis failed, returning default chat intent",
                "clarification_needed": True,
                "uncertainty_reason": "System analysis failed, suggest user clarify requirements"
            }
    
    # ===== 3.1 Language Detector =====
    
    def detect_language(self, text: str) -> Tuple[str, float]:
        """
        Detect text language
        
        Args:
            text: Input text
            
        Returns:
            (language_code, confidence)
        """
        # Simple Chinese character detection
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
        total_chars = len(text.strip())
        
        if total_chars == 0:
            return "zh", 0.5
        
        chinese_ratio = chinese_chars / total_chars
        
        # Adjust detection logic: if Chinese character ratio exceeds 20%, consider it Chinese
        if chinese_ratio > 0.2:
            return "zh", min(0.9, 0.5 + chinese_ratio)
        else:
            return "en", min(0.9, 0.5 + (1 - chinese_ratio))
    
    # ===== 3.2 Inquiry Processor =====
    
    def process_inquiry(
        self, 
        user_input: str, 
        referenced_user: Dict, 
        current_user: Dict = None,
        language_code: str = "zh"
    ) -> Dict:
        """
        Process user inquiry about specific user
        
        Args:
            user_input: User's inquiry content
            referenced_user: User information being inquired about
            current_user: Current user information
            language_code: Language code for response ("zh" or "en")
        
        Returns:
            Formatted response result
        """
        self.stats["llm_calls"] += 1
        
        # Determine response language instruction
        language_instruction = "请使用中文回复" if language_code == "zh" else "Please respond in English"
        
        system_prompt = f"""
You are a professional user analysis expert. Please provide detailed and accurate analysis and recommendations based on user information and inquiry content.

Please provide detailed analysis and response, including:

1. **Direct Answer**: Direct answer to user questions
2. **User Analysis**: In-depth analysis of the inquired user's professional capabilities, experience, and characteristics
3. **Compatibility Assessment**: If current user information is available, assess compatibility with current user needs
4. **Collaboration Suggestions**: Provide specific collaboration suggestions based on analysis results
5. **Considerations**: Risks or suggestions that need attention

Response requirements:
- Professional, objective, and constructive
- Analyze based on facts, avoid subjective assumptions
- Provide specific suggestions and action guidance
- Natural and easy-to-understand language
- {language_instruction}

Please respond in natural conversation format, do not use numbering or list format.
"""
        
        # Build user prompt
        current_user_section = ""
        if current_user and not current_user.get('error'):
            current_user_section = f"""
Current user information:
{json.dumps(current_user, ensure_ascii=False, indent=2)}
"""
        
        user_prompt = f"""
Inquired user information:
{json.dumps(referenced_user, ensure_ascii=False, indent=2)}

{current_user_section}

User inquiry: "{user_input}"

Please provide detailed analysis and response.
"""
        
        try:
            response = self.glm_client.simple_chat(
                content=user_prompt,
                system_prompt=system_prompt,
                temperature=0.4,
                max_tokens=1000
            )
            
            return {
                "type": "inquiry_response",
                "content": response.strip(),
                "referenced_user": referenced_user,
                "query": user_input,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Inquiry processing failed: {e}")
            return {
                "type": "inquiry_response",
                "content": f"Sorry, I cannot process your inquiry. Please try again later. Error: {str(e)}",
                "referenced_user": referenced_user,
                "query": user_input,
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }
    
    # ===== 3.3 Chat Processor =====
    
    def process_chat(
        self, 
        user_input: str, 
        current_user: Dict = None, 
        clarification_needed: bool = False, 
        uncertainty_reason: str = None,
        language_code: str = "zh"
    ) -> Dict:
        """
        Process chat conversation
        
        Args:
            user_input: User input
            current_user: Current user information
            clarification_needed: Whether clarification is needed
            uncertainty_reason: Reason for unclear intent
            language_code: Language code for response ("zh" or "en")
        
        Returns:
            Chat response result
        """
        self.stats["llm_calls"] += 1
        
        # Determine response language instruction
        language_instruction = "请使用中文回复" if language_code == "zh" else "Please respond in English"
        
        if clarification_needed:
            system_prompt = f"""
            You are the AI networking matching agent for a software called Ques.

            The user's intent is not clear enough, please kindly guide the user to clarify their needs.

            Response requirements:
            - Friendly, warm tone
            - Provide specific guidance options
            - Avoid confusing the user
            - Clear and concise
            - {language_instruction}
            """
                        
            user_prompt = f"""
            User input: "{user_input}"

            Unclear reason: {uncertainty_reason if uncertainty_reason else 'Intent not clear enough'}

            User background: {json.dumps(current_user, ensure_ascii=False, indent=2) if current_user else 'No user information'}

            Please provide a friendly guiding response.
            """
        else:
            system_prompt = f"""
                You are the AI networking matching agent for a software called Ques. Please provide helpful responses to users.

                You can provide natural, helpful responses by:
                1. Answering user questions
                2. Providing relevant suggestions
                3. Engaging in friendly conversation

                Response requirements:
                - Natural, friendly conversational tone
                - Provide valuable information or suggestions
                - Consider user background information (if available)
                - Maintain professionalism while being approachable
                - {language_instruction}
                """
            
            user_prompt = f"""
            User input: "{user_input}"

            User background: {json.dumps(current_user, ensure_ascii=False, indent=2) if current_user else 'No user information'}

            Please provide a natural, helpful response.
            """
        
        try:
            response = self.glm_client.simple_chat(
                content=user_prompt,
                system_prompt=system_prompt,
                temperature=0.5,
                max_tokens=800
            )
            
            return {
                "type": "chat_response",
                "content": response.strip(),
                "clarification": clarification_needed,
                "query": user_input,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Chat processing failed: {e}")
            return {
                "type": "chat_response", 
                "content": "Sorry, I cannot respond normally right now. Please try again later.",
                "clarification": clarification_needed,
                "query": user_input,
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }
    
    # ===== 3.4 Dense Vector Query Optimizer =====
    
    def optimize_query_for_dense_vector(
        self, 
        text: str, 
        referenced_users: List[Dict] = None
    ) -> str:
        """
        Optimize query text for dense vector search
        Generate clear person descriptions based on real user payload structure
        
        Args:
            text: Original query text
            referenced_users: Referenced user list
            
        Returns:
            Optimized query text
        """
        self.stats["llm_calls"] += 1
        
        # Build referenced user information
        referenced_info = ""
        if referenced_users:
            referenced_info = "\n\nReferenced users (already shown to user):\n"
            for i, ref_user in enumerate(referenced_users, 1):
                referenced_info += f"Ref{i}. Complete profile: {json.dumps(ref_user, ensure_ascii=False, indent=2)}\n"

        system_prompt = """
        You are a search query optimizer. Your task is to understand what the user is looking for and create a better search description.

        Instructions:
        1. Read the user's search query and any referenced users carefully
        2. Understand what type of person they want to find
        3. Create a clear description for semantic matching

        If referenced users are provided, consider:
        - What patterns or similarities the user might be looking for
        - Whether they want similar or different types of people

        Use the same language as the user's query. Keep your response short and focused.
        """
        
        user_prompt = f"""
        User's search query: {text}
        User's referenced users:
        {referenced_info}
        
        Create a simple, optimized description:
        """
        
        try:
            optimized_query = self.glm_client.simple_chat(
                content=user_prompt,
                system_prompt=system_prompt,
                temperature=0.3,
                max_tokens=150
            )
            return optimized_query.strip()
        except Exception as e:
            print(f"Query optimization failed: {e}")
            return text  # Return original query as fallback
    
    # ===== 3.5 Hybrid Vector Search Engine =====
    
    async def hybrid_search(
        self,
        dense_query: str,
        sparse_query: str,
        search_strategy: str = "standard",
        limit: int = 10,
        viewed_user_ids: List[str] = None,
        fetch_db_details: bool = True
    ) -> List[Dict]:
        """
        Execute hybrid vector search and fetch database details
        
        Args:
            dense_query: Dense vector query text
            sparse_query: Sparse vector query text
            search_strategy: Search strategy ("standard", "expanded", "custom")
            limit: Number of results to return
            viewed_user_ids: List of viewed user IDs
            fetch_db_details: Whether to fetch detailed information from database
            
        Returns:
            Search result list (including database detailed information)
        """
        try:
            # Build basic filter (only for excluding viewed users)
            filter_obj = None
            if viewed_user_ids:
                filter_obj = models.Filter(
                    must_not=[
                        models.FieldCondition(
                            key="user_id", 
                            match=models.MatchAny(any=viewed_user_ids)
                        )
                    ]
                )
            
            # Execute vector search
            if search_strategy == "standard":
                vector_results = self._standard_search(dense_query, sparse_query, filter_obj, limit)
            elif search_strategy == "expanded":
                vector_results = self._expanded_search(dense_query, sparse_query, filter_obj, limit)
            elif search_strategy == "custom":
                vector_results = self._custom_search(dense_query, sparse_query, filter_obj, limit)
            else:
                raise ValueError(f"Unsupported search strategy: {search_strategy}")
            
            # If no database details needed or no search results, return vector search results directly
            if not fetch_db_details or not vector_results:
                return vector_results
            
            # Extract user ID list
            user_ids = [str(result.get("user_id")) for result in vector_results if result.get("user_id")]
            
            if not user_ids:
                return vector_results
            
            print(f"🔍 Vector search found {len(vector_results)} candidates, fetching database details...")
            
            # Fetch user detailed information from database
            db_details = await self._fetch_user_details_from_db(user_ids)
            
            # Merge vector search results and database details
            merged_results = self._merge_vector_and_db_results(vector_results, db_details)
            
            print(f"✅ Successfully fetched database details for {len([r for r in db_details.values() if not r.get('error')])} users")
            
            return merged_results
                
        except Exception as e:
            print(f"Hybrid search failed: {e}")
            return []
    
    def _standard_search(
        self, 
        dense_query: str, 
        sparse_query: str, 
        filter_obj: models.Filter, 
        limit: int
    ) -> List[Dict]:
        """Standard search strategy - prefetch limit=50, use native DBSF fusion"""
        try:
            # Use preloaded dense vector model
            if self._dense_model is None:
                from sentence_transformers import SentenceTransformer
                self._dense_model = SentenceTransformer('BAAI/bge-m3')
            
            dense_vec = self._dense_model.encode(dense_query, normalize_embeddings=True).tolist()
            
            # Generate sparse vector
            sparse_vec = self._build_splade_sparse_vector(sparse_query)
            
            # Use native DBSF fusion method
            result = self.qdrant_client.query_points(
                collection_name=self.collection_name,
                prefetch=[
                    {"query": sparse_vec, "using": "sparse", "limit": 50},
                    {"query": dense_vec, "using": "dense", "limit": 50}
                ],
                query=models.FusionQuery(fusion=models.Fusion.DBSF),
                query_filter=filter_obj,
                limit=limit,
                with_payload=True
            )
            
            return [
                {
                    "user_id": hit.id,
                    "score": hit.score,
                    **hit.payload
                } for hit in result.points
            ]
        except Exception as e:
            print(f"Standard search failed: {e}")
            return []
    
    def _expanded_search(
        self, 
        dense_query: str, 
        sparse_query: str, 
        filter_obj: models.Filter, 
        limit: int
    ) -> List[Dict]:
        """Expanded search strategy - prefetch limit=150, use RRF fusion"""
        try:
            # Use preloaded dense vector model
            if self._dense_model is None:
                from sentence_transformers import SentenceTransformer
                self._dense_model = SentenceTransformer('BAAI/bge-m3')
            
            dense_vec = self._dense_model.encode(dense_query, normalize_embeddings=True).tolist()
            
            # Generate sparse vector
            sparse_vec = self._build_splade_sparse_vector(sparse_query)
            
            # Use RRF fusion method
            result = self.qdrant_client.query_points(
                collection_name=self.collection_name,
                prefetch=[
                    {"query": sparse_vec, "using": "sparse", "limit": 150},
                    {"query": dense_vec, "using": "dense", "limit": 150}
                ],
                query=models.FusionQuery(fusion=models.Fusion.RRF),
                query_filter=filter_obj,
                limit=limit,
                with_payload=True
            )
            
            return [
                {
                    "user_id": hit.id,
                    "score": hit.score,
                    **hit.payload
                } for hit in result.points
            ]
        except Exception as e:
            print(f"Expanded search failed: {e}")
            return []
    
    def _custom_search(
        self, 
        dense_query: str, 
        sparse_query: str, 
        filter_obj: models.Filter, 
        limit: int
    ) -> List[Dict]:
        """Custom search strategy - separate requests then custom DBSF fusion"""
        try:
            # Use preloaded dense vector model
            if self._dense_model is None:
                from sentence_transformers import SentenceTransformer
                self._dense_model = SentenceTransformer('BAAI/bge-m3')
            
            dense_vec = self._dense_model.encode(dense_query, normalize_embeddings=True).tolist()
            
            # Generate sparse vector
            sparse_vec = self._build_splade_sparse_vector(sparse_query)
            
            # Execute dense and sparse searches separately
            dense_results = self.qdrant_client.query_points(
                collection_name=self.collection_name,
                query=dense_vec,
                using="dense",
                query_filter=filter_obj,
                limit=60,
                with_payload=True
            ).points
            
            sparse_results = self.qdrant_client.query_points(
                collection_name=self.collection_name,
                query=sparse_vec,
                using="sparse",
                query_filter=filter_obj,
                limit=60,
                with_payload=True
            ).points
            
            # Custom DBSF fusion
            fused_results = self._custom_dbsf_fusion(dense_results, sparse_results, alpha=0.2, limit=limit)
            
            return fused_results
        except Exception as e:
            print(f"Custom search failed: {e}")
            return []
    
    def _build_splade_sparse_vector(self, text: str) -> models.SparseVector:
        """Generate SPLADE sparse vector"""
        try:
            import torch
            
            # Use preloaded model, if not available then load temporarily
            if self._splade_model is None or self._splade_tokenizer is None:
                from transformers import AutoModelForMaskedLM, AutoTokenizer
                print("⚠️  SPLADE model not preloaded, loading temporarily...")
                tokenizer = AutoTokenizer.from_pretrained("naver/splade-v3")
                model = AutoModelForMaskedLM.from_pretrained("naver/splade-v3")
                device = 'mps' if torch.backends.mps.is_available() else ('cuda' if torch.cuda.is_available() else 'cpu')
                model = model.to(device)
                model.eval()
                self._splade_tokenizer = tokenizer
                self._splade_model = model
                self._device = device
            
            inputs = self._splade_tokenizer(text, return_tensors="pt", truncation=True, max_length=256)
            inputs = {k: v.to(self._device) for k, v in inputs.items()}
            
            with torch.no_grad():
                outputs = self._splade_model(**inputs)
                logits = outputs.logits
                relu_logits = torch.relu(logits)
                splade_scores = torch.log1p(relu_logits)
                sparse_vec, _ = splade_scores.max(dim=1)
                sparse_vec = sparse_vec[0]
                nonzero_indices = (sparse_vec > 0).nonzero(as_tuple=True)[0]
                indices = nonzero_indices.detach().cpu().tolist()
                values = sparse_vec[nonzero_indices].detach().cpu().tolist()
            
            return models.SparseVector(indices=indices, values=values)
        except Exception as e:
            print(f"Sparse vector generation failed: {e}")
            return models.SparseVector(indices=[], values=[])
    
    def _custom_dbsf_fusion(self, dense_results: List, sparse_results: List, alpha: float, limit: int) -> List[Dict]:
        """Custom DBSF fusion algorithm"""
        import numpy as np
        
        # Build candidate set
        id_to_result = {}
        for result in dense_results:
            id_to_result[result.id] = result
        for result in sparse_results:
            id_to_result[result.id] = result
        all_ids = list(id_to_result.keys())
        
        if not all_ids:
            return []
        
        # Calculate score distribution and normalize
        dense_scores = np.array([r.score for r in dense_results]) if dense_results else np.array([])
        sparse_scores = np.array([r.score for r in sparse_results]) if sparse_results else np.array([])
        
        dense_mean, dense_std = (dense_scores.mean(), dense_scores.std()) if len(dense_scores) else (0, 1)
        sparse_mean, sparse_std = (sparse_scores.mean(), sparse_scores.std()) if len(sparse_scores) else (0, 1)
        
        # Avoid division by zero
        dense_std = dense_std if dense_std > 1e-6 else 1.0
        sparse_std = sparse_std if sparse_std > 1e-6 else 1.0
        
        dense_id_score = {r.id: (r.score - dense_mean) / dense_std for r in dense_results}
        sparse_id_score = {r.id: (r.score - sparse_mean) / sparse_std for r in sparse_results}
        
        # Calculate fusion scores
        score_map = {}
        for pid in all_ids:
            score = 0.0
            if pid in dense_id_score:
                score += alpha * dense_id_score[pid]
            if pid in sparse_id_score:
                score += (1 - alpha) * sparse_id_score[pid]
            score_map[pid] = score
        
        # Sort and return results
        sorted_ids = sorted(score_map.items(), key=lambda x: x[1], reverse=True)[:limit]
        
        fused_list = []
        for pid, score in sorted_ids:
            result = id_to_result[pid]
            payload_dict = dict(result.payload) if hasattr(result, 'payload') and result.payload else {}
            fused_list.append({
                "user_id": pid,
                "score": score,
                **payload_dict
            })
        
        return fused_list
    
    async def _fetch_user_details_from_db(self, user_ids: List[str]) -> Dict[str, Dict]:
        """
        Fetch user detailed information from database API
        
        Args:
            user_ids: List of user IDs
            
        Returns:
            Mapping dictionary from user ID to user details
        """
        user_details = {}
        
        if not user_ids:
            return user_details
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Concurrent requests for multiple users' detailed information
                tasks = []
                for user_id in user_ids:
                    task = self._fetch_single_user_detail(client, user_id)
                    tasks.append(task)
                
                # Wait for all requests to complete
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Process results
                for user_id, result in zip(user_ids, results):
                    if isinstance(result, Exception):
                        print(f"Failed to fetch user {user_id} details: {result}")
                        # Use empty user information as fallback
                        user_details[str(user_id)] = {
                            "id": user_id,
                            "name": "Unknown user",
                            "error": str(result)
                        }
                    elif result:
                        user_details[str(user_id)] = result
                    else:
                        print(f"User {user_id} details are empty")
                        user_details[str(user_id)] = {
                            "id": user_id,
                            "name": "Unknown user",
                            "error": "User does not exist"
                        }
                        
        except Exception as e:
            print(f"Batch fetch user details failed: {e}")
            # Return empty user information as fallback
            for user_id in user_ids:
                user_details[str(user_id)] = {
                    "id": user_id,
                    "name": "Unknown user",
                    "error": str(e)
                }
        
        return user_details
    
    async def _fetch_single_user_detail(self, client: httpx.AsyncClient, user_id: str) -> Optional[Dict]:
        """
        Fetch detailed information for a single user
        
        Args:
            client: HTTP client
            user_id: User ID
            
        Returns:
            User detailed information or None
        """
        try:
            url = f"{self.api_base_url}/users/{user_id}"
            response = await client.get(url)
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                print(f"User {user_id} does not exist")
                return None
            else:
                print(f"Failed to fetch user {user_id} details, status code: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Exception occurred while requesting user {user_id} details: {e}")
            return None
    
    def _merge_vector_and_db_results(
        self, 
        vector_results: List[Dict], 
        db_details: Dict[str, Dict]
    ) -> List[Dict]:
        """
        Merge vector search results and database detailed information
        
        Args:
            vector_results: Vector search results
            db_details: Database user details
            
        Returns:
            Merged candidate list
        """
        merged_results = []
        
        for vector_result in vector_results:
            user_id = str(vector_result.get("user_id"))
            
            # Get detailed information from database
            db_detail = db_details.get(user_id, {})
            
            # Merge data: database information takes priority, vector search information as supplement
            merged_candidate = {
                # Basic information from vector search
                "user_id": user_id,
                "score": vector_result.get("score", 0.0),
                
                # Database detailed information (higher priority)
                **db_detail,
                
                # Vector search payload as supplement (if corresponding field not in database)
                **{k: v for k, v in vector_result.items() 
                   if k not in db_detail and k not in ["user_id", "score"]}
            }
            
            merged_results.append(merged_candidate)
        
        return merged_results
    
    
    # ===== 3.8 Intelligent Search Scheduler =====
    
    def analyze_candidates_quality(
        self,
        user_query: str,
        candidates: List[Dict],
        search_attempt: int = 1,
        current_user_info: Dict = None,
        language_code: str = "zh",
        referenced_users: List[Dict] = None,
        total_found: int = 0
    ) -> Dict:
        """
        Use LLM to analyze candidate quality and matching degree (support bidirectional matching), 
        and generate match reasons and guiding responses
        Based on real users_rawjson payload structure
        
        Args:
            user_query: User query
            candidates: Candidate list
            search_attempt: Search attempt count
            current_user_info: Current user's complete information (including demands and goals)
            language_code: Language code
            referenced_users: Referenced user list
            total_found: Total found candidates count
            
        Returns:
            Analysis result, including quality assessment, candidate details (with match reasons) and guiding response
        """
        self.stats["llm_calls"] += 1
        
        if not candidates:
            # Determine reasons for poor search quality
            poor_quality_intro = ""
            if language_code == "zh":
                if len(user_query.strip()) < 10:
                    poor_quality_intro = "Your search query is too vague or short. Please provide more detailed criteria like skills, experience level, location, etc."
                elif not current_user_info or current_user_info.get('error'):
                    poor_quality_intro = "Your profile information is incomplete. Please complete your skills, demands, and goals for more accurate recommendations."
                else:
                    poor_quality_intro = "No suitable candidates found. Please try expanding your search criteria or adjusting search conditions."
            else:
                if len(user_query.strip()) < 10:
                    poor_quality_intro = "Your search query is too vague or short. Please provide more detailed criteria like skills, experience level, location, etc."
                elif not current_user_info or current_user_info.get('error'):
                    poor_quality_intro = "Your profile information is incomplete. Please complete your skills, demands, and goals for more accurate recommendations."
                else:
                    poor_quality_intro = "No suitable candidates found. Consider expanding search criteria or adjusting requirements."
                    
            return {
                "overall_quality": "poor",
                "candidate_count": 0,
                "should_continue": True,
                "analysis": "No suitable candidates found, suggest expanding search criteria",
                "intro": poor_quality_intro
            }

        system_prompt = f"""
        You are a professional candidate matching analyst with expertise in mutual compatibility assessment, match reasoning, and user guidance. Your task is to analyze candidate profiles using BIDIRECTIONAL MATCHING criteria, generate natural match reasons, and create engaging introductions.

        BIDIRECTIONAL MATCHING APPROACH:
        1. Read the user's search query carefully to understand what they are looking for
        2. If current user information is provided, analyze their demands and goals
        3. Examine each candidate's profile (skills, experience, background, goals, demands)
        4. Evaluate MUTUAL COMPATIBILITY using these criteria:

        CRITERIA 1 - CANDIDATES MEET USER NEEDS (One-way matching):
        - How well candidates match the user's search query requirements
        - How well candidates satisfy the current user's stated demands (semantic matching, not literal)
        - How well candidates align with the current user's goals (semantic matching, not literal)
        
        CRITERIA 2 - USER MEETS CANDIDATE NEEDS (Reverse matching):  
        - How well the current user satisfies each candidate's demands (semantic matching, not literal)
        - How well the current user aligns with each candidate's goals (semantic matching, not literal)
        - Consider the user's background, skills, and experience in relation to candidate needs

        SEMANTIC MATCHING PRINCIPLE:
        - Focus on meaning and intent rather than exact literal matches
        - Consider related skills, complementary experiences, and aligned interests
        - Value conceptual alignment over precise terminology matches

        QUALITY ASSESSMENT RULES:
        CRITICAL: If fewer than 3 candidates satisfy the PRIMARY REQUIREMENT, overall quality MUST be "poor"
        
        - poor: Fewer than 3 candidates meet PRIMARY REQUIREMENT - DO NOT include selected_candidates for poor quality
        - fair: Exactly 3 candidates meet PRIMARY REQUIREMENT with basic BIDIRECTIONAL compatibility (40-60% mutual match)
        - good: 3+ candidates meet PRIMARY REQUIREMENT with decent BIDIRECTIONAL compatibility (60-80% mutual match)  
        - excellent: 3+ candidates meet PRIMARY REQUIREMENT with strong BIDIRECTIONAL compatibility (>80% mutual match)
        
        SELECTION CRITERIA FOR TOP 3:
            STEP 1 - PRIMARY REQUIREMENT FILTERING (Must be satisfied for inclusion):
            - Strong match for user's query + user's demands + user's goals (at least one requirement)
            - Strong potential for user to satisfy candidate's demands + candidate's goals (at least one requirement)
            
            STEP 2 - COUNT CHECK:
            - If fewer than 3 candidates meet PRIMARY REQUIREMENT → quality = "poor", skip selection
            - If 3+ candidates meet PRIMARY REQUIREMENT → proceed to ranking
            
            STEP 3 - RANKING PRIORITY (Among candidates who meet primary requirements):
            1. **Query Match Priority**: Candidates who better satisfy the user's search query should be ranked higher
            2. **Comprehensive Match**: The more mutual needs satisfied, the better the ranking
            3. **Balance**: Consider both directions but prioritize query relevance in final ranking

        MATCH REASON GENERATION REQUIREMENTS:
        - Use natural, conversational language (avoid robotic "satisfies" descriptions)
        - Focus on candidate strengths and collaborative potential with specific details
        - Highlight query relevance first, then broader compatibility with concrete examples
        - {"使用中文" if language_code == "zh" else "Use English"}
        - Provide specific details about skills, experience, and background when available
        - Examples:
          * Chinese: "Python expert with 5 years of machine learning project experience, worked at ByteDance responsible for recommendation algorithm optimization, highly aligned with your AI technology direction"
          * English: "Senior frontend developer with 3+ years Vue.js experience at Google, led 5 major product launches, perfect technical and leadership match"

        INTRO MESSAGE REQUIREMENTS:
        - Professional and friendly tone
        - {"使用中文" if language_code == "zh" else "Use English"}
        - Briefly summarize key characteristics of found candidates
        - Encourage user to learn more about candidates
        - Keep under 200 characters
        - Examples:
          * Chinese: "Carefully selected 3 high-quality candidates for you: senior Python engineer, AI algorithm expert, product-tech hybrid talent, all from top internet companies with rich project experience. We recommend you learn more about their detailed backgrounds."
          * English: "Found 3 excellent candidates: Senior Python engineer, AI algorithm expert, and product-tech hybrid talent from top tech companies with rich project experience."

        JSON RESPONSE FORMAT:
        For quality "excellent", "good", or "fair":
        {{
            "overall_quality": "quality_level",
            "candidate_count": candidate_count,
            "should_continue": boolean,
            "selected_candidates": [
                {{
                    "user_id": "candidate_id",
                    "match_score": score_1_to_10,
                    "key_strengths": ["list_of_relevant_strengths"],
                    "match_reason": "natural_detailed_match_reason"
                }}
            ],
            "analysis": "overall_bidirectional_analysis_and_recommendations",
            "intro": "friendly_professional_introduction_message"
        }}

        For quality "poor":
        {{
            "overall_quality": "poor",
            "candidate_count": candidate_count,
            "should_continue": boolean,
            "analysis": "analysis_of_poor_results",
            "intro": "explanation_of_poor_quality_with_suggestions"
        }}
        """
        
        # Build referenced user information
        referenced_info = ""
        if referenced_users:
            referenced_info = "\n\nReferenced users (already shown to user):\n"
            for i, ref_user in enumerate(referenced_users, 1):
                referenced_info += f"Ref{i}. Complete profile: {json.dumps(ref_user, ensure_ascii=False, indent=2)}\n"
        
        # Build candidate information based on real payload
        candidates_info = []
        for i, candidate in enumerate(candidates[:10], 1):  # Only analyze first 10
            candidates_info.append(f"Candidate{i}: {json.dumps(candidate, ensure_ascii=False, indent=2)}")
        
        # Build current user information
        current_user_section = ""
        if current_user_info and not current_user_info.get('error'):
            current_user_section = f"""
        Current User Profile (for bidirectional matching):
        {json.dumps(current_user_info, ensure_ascii=False, indent=2)}
        
        Please pay special attention to:
        - Current user's demands: {current_user_info.get('demands', [])}
        - Current user's goals: {current_user_info.get('goals', [])}
        - Current user's skills and background for reverse matching
        """
        else:
            current_user_section = """
        Current User Profile: Not available
        Note: Without current user information, focus primarily on how well candidates match the search query requirements.
        """
        
        user_content = f"""
        User search query: {user_query}
        Search attempt: {search_attempt}
        Total candidates found in this search: {total_found}
        Language: {language_code}
        
        {current_user_section}
        
        {referenced_info}
        
        Candidate profiles (JSON format):
        {chr(10).join(candidates_info)}
        
        Please analyze bidirectional compatibility and select the top 3 candidates with the best mutual fit.
        For each selected candidate, generate a natural, detailed match reason highlighting their strengths and compatibility.
        Also generate a friendly introduction message summarizing the overall search results.
        Consider semantic matching rather than literal word matching for demands and goals.
        
        IMPORTANT: If quality is "poor", do NOT include selected_candidates field and provide suggestions in the intro field.
        """
        
        try:
            result = self.glm_client.json_chat(
                content=user_content,
                system_prompt=system_prompt,
                temperature=0.2,
                max_tokens=2000  # Increase token limit to accommodate more content
            )
            
            # Process quality assessment results
            overall_quality = result.get("overall_quality", "fair")
            
            if overall_quality == "poor":
                # For poor quality results, do not include selected_candidates
                return {
                    "overall_quality": "poor",
                    "candidate_count": result.get("candidate_count", len(candidates)),
                    "should_continue": result.get("should_continue", True),
                    "analysis": result.get("analysis", "Candidate quality does not meet requirements"),
                    "intro": result.get("intro", "No suitable candidates found, suggest adjusting search criteria")
                }
            else:
                # For qualified results, process selected_candidates
                selected_candidates = result.get("selected_candidates", [])[:3]  # Limit to maximum 3
                
                # Add complete original information for each selected candidate
                enhanced_candidates = []
                for selected in selected_candidates:
                    # Find original candidate data by user_id
                    original_candidate = None
                    for candidate in candidates:
                        if candidate.get("user_id") == selected.get("user_id"):
                            original_candidate = candidate
                            break
                    
                    if original_candidate:
                        # Merge LLM analysis results and original candidate data
                        enhanced_candidate = original_candidate.copy()
                        enhanced_candidate.update({
                            "match_score": selected.get("match_score", 6),
                            "key_strengths": selected.get("key_strengths", []),
                            "match_reason": selected.get("match_reason", "Comprehensive background match")
                        })
                        enhanced_candidates.append(enhanced_candidate)
                    else:
                        # If original data not found, keep LLM analysis results
                        enhanced_candidates.append(selected)
                
                return {
                    "overall_quality": overall_quality,
                    "candidate_count": result.get("candidate_count", len(candidates)),
                    "should_continue": result.get("should_continue", len(candidates) < 5),
                    "selected_candidates": enhanced_candidates,
                    "analysis": result.get("analysis", ""),
                    "intro": result.get("intro", "Found quality candidates for you, suggest further understanding.")
                }
            
        except Exception as e:
            print(f"Candidate analysis failed: {e}")
            # Return default analysis results, including complete candidate information
            selected_candidates = []
            for candidate in candidates[:3]:
                enhanced_candidate = candidate.copy()
                enhanced_candidate.update({
                    "match_score": 6,
                    "key_strengths": ["Has relevant skills"],
                    "match_reason": self._generate_default_match_reason(candidate, language_code)
                })
                selected_candidates.append(enhanced_candidate)
            
            default_intro = "Found candidates for you, recommend further review." if language_code == "zh" else "Found candidates for your review."
            
            return {
                "overall_quality": "fair",
                "candidate_count": len(candidates),
                "should_continue": len(candidates) < 5,
                "selected_candidates": selected_candidates,
                "analysis": "LLM analysis failed, returning default result",
                "intro": default_intro
            }
    
    def _generate_default_match_reason(self, candidate: Dict, language_code: str = "zh") -> str:
        """Generate default match reason"""
        default_parts = []
        
        skills = candidate.get('skills', [])
        if skills:
            default_parts.append(f"Skilled in {', '.join(skills[:2])}" if language_code == "zh" else f"Skilled in {', '.join(skills[:2])}")
        
        if candidate.get('current_university'):
            default_parts.append(f"{candidate['current_university']} background" if language_code == "zh" else f"{candidate['current_university']} background")
        
        project_count = candidate.get('project_count', 0)
        if project_count > 0:
            default_parts.append(f"{project_count} projects experience" if language_code == "zh" else f"{project_count} projects experience")
        
        # Generate more natural, detailed expressions
        if default_parts:
            if language_code == "zh":
                company = candidate.get('current_company', '')
                experience_level = f"{project_count} years experience" if project_count > 2 else "Rich experience"
                company_suffix = f", worked at {company}" if company else ""
                return f"{default_parts[0]}, {experience_level}, {', '.join(default_parts[1:])}, high technical compatibility{company_suffix}" if len(default_parts) > 1 else f"{default_parts[0]}, {experience_level}, meets technical requirements{company_suffix}"
            else:
                company = candidate.get('current_company', '')
                company_suffix = f" at {company}" if company else ""
                return f"Strong background in {', '.join(default_parts)}, {project_count}+ projects experience{company_suffix}, excellent technical fit"
        else:
            if language_code == "zh":
                return "Has relevant technical background, rich experience, suitable for collaboration"
            else:
                return "Relevant technical background with solid experience, good collaboration potential"
    
    def extract_tags_for_sparse_search(
        self,
        user_query: str,
        referenced_users: List[Dict] = None
    ) -> str:
        """
        Extract keywords for sparse vector search
        Extract precisely matched keywords based on real user payload structure
        
        Args:
            user_query: User query
            referenced_users: Referenced user list
            
        Returns:
            Keyword text for sparse search
        """
        self.stats["llm_calls"] += 1
        
        # Build referenced user information
        referenced_info = ""
        if referenced_users:
            referenced_info = "\n\nReferenced users (already shown to user):\n"
            for i, ref_user in enumerate(referenced_users, 1):
                referenced_info += f"Ref{i}. Complete profile: {json.dumps(ref_user, ensure_ascii=False, indent=2)}\n"

        system_prompt = """
        You are a keyword extraction specialist for search systems. Extract precise keywords and terms for sparse vector matching.

        Instructions:
        1. Extract specific technical skills, tools, frameworks, and technologies
        2. Include job titles, roles, and positions mentioned
        3. Extract company names, institutions, and organizations
        4. Include industry terms and domain-specific vocabulary
        5. Extract location names if relevant
        6. Include experience levels and qualifications

        Focus on exact terms that would appear in user profiles for precise matching.
        Use the same language as the user's query. Return keywords separated by spaces.
        """
        
        user_prompt = f"""
        User's search query: {user_query}
        User's referenced users:
        {referenced_info}
        
        Extract precise keywords for exact matching:
        """
        
        try:
            keywords = self.glm_client.simple_chat(
                content=user_prompt,
                system_prompt=system_prompt,
                temperature=0.1,
                max_tokens=150
            )
            return keywords.strip()
        except Exception as e:
            print(f"Keyword extraction failed: {e}")
            return user_query  # Return original query as fallback
    
    async def intelligent_search(
        self,
        user_query: str,
        current_user: dict = None,
        referenced_users: List[Dict] = None,
        viewed_user_ids: List[str] = None
    ) -> Dict:
        """
        Complete intelligent search method - includes language detection, search scheduling and result generation
        
        Args:
            user_query: User query
            current_user: Current user's complete information (including demands and goals)
            referenced_users: Referenced user list
            viewed_user_ids: Viewed user ID list
            
        Returns:
            Complete formatted search results
        """
        total_start_time = time.time()
        self.stats["search_count"] += 1
        
        # Initialize performance statistics
        performance_stats = {
            "language_detection": 0.0,
            "preprocessing": 0.0,
            "vector_searches": {},
            "candidate_analysis": {},
            "result_generation": 0.0,
            "total_time": 0.0
        }
        
        try:
            # Step 1: Language detection
            step_start = time.time()
            language_code, confidence = self.detect_language(user_query)
            performance_stats["language_detection"] = time.time() - step_start
            print(f"🌐 Detected language: {language_code} (confidence: {confidence:.2f}) - Time: {performance_stats['language_detection']:.3f}s")
            
            # Step 2: Use passed current_user information
            current_user_info = current_user
            if current_user_info:
                print(f"✅ Using passed user information")
            
            # Step 3: Preprocessing phase - concurrent execution of independent components
            step_start = time.time()
            print("🔄 Starting preprocessing phase...")
            
            # Execute preprocessing tasks concurrently
            tasks = [
                asyncio.create_task(self._async_optimize_dense_query(user_query, referenced_users)),
                asyncio.create_task(self._async_extract_sparse_tags(user_query, referenced_users))
            ]
            
            dense_query, sparse_query = await asyncio.gather(*tasks)
            performance_stats["preprocessing"] = time.time() - step_start
            
            print(f"✅ Preprocessing completed - Dense: {len(dense_query)}, Sparse: {len(sparse_query)} - Time: {performance_stats['preprocessing']:.3f}s")
            
            # Step 4: Three-phase search loop
            search_strategies = ["standard", "expanded", "custom"]
            all_candidates = []
            best_analysis = None
            
            for attempt, strategy in enumerate(search_strategies, 1):
                print(f"🔍 Search attempt {attempt}/3: {strategy} strategy")
                
                # Execute search
                search_start = time.time()
                candidates = await self.hybrid_search(
                    dense_query=dense_query,
                    sparse_query=sparse_query,
                    search_strategy=strategy,
                    limit=10,
                    viewed_user_ids=viewed_user_ids or [],
                    fetch_db_details=True
                )
                search_time = time.time() - search_start
                performance_stats["vector_searches"][f"attempt_{attempt}_{strategy}"] = search_time
                
                if candidates:
                    all_candidates.extend(candidates)
                    
                    # LLM analyze candidate quality
                    analysis_start = time.time()
                    analysis = self.analyze_candidates_quality(
                        user_query=user_query,
                        candidates=candidates,
                        search_attempt=attempt,
                        current_user_info=current_user_info,
                        language_code=language_code,
                        referenced_users=referenced_users,
                        total_found=len(all_candidates)
                    )
                    analysis_time = time.time() - analysis_start
                    performance_stats["candidate_analysis"][f"attempt_{attempt}"] = analysis_time
                    
                    print(f"📊 Analysis result: {analysis.get('overall_quality', 'unknown')} - {analysis.get('candidate_count', 0)} candidates")
                    print(f"    Search time: {search_time:.3f}s, Analysis time: {analysis_time:.3f}s")
                    
                    # If quality is good or this is the last attempt, stop searching
                    if (analysis.get("overall_quality") in ["excellent", "good"] or 
                        not analysis.get("should_continue", True) or 
                        attempt == len(search_strategies)):
                        best_analysis = analysis
                        break
                else:
                    print(f"    Search time: {search_time:.3f}s, no candidates")
                
                print(f"⏭️ Continue to next search phase...")
            
            # Step 5: Final result organization
            if not best_analysis:
                # If no candidates found, generate default poor quality analysis
                poor_quality_intro = ""
                if language_code == "zh":
                    if len(user_query.strip()) < 10:
                        poor_quality_intro = "Your search query is too vague or short. Please provide more detailed criteria like skills, experience level, location, etc."
                    elif not current_user_info or current_user_info.get('error'):
                        poor_quality_intro = "Your profile information is incomplete. Please complete your skills, demands, and goals for more accurate recommendations."
                    else:
                        poor_quality_intro = "No suitable candidates found. Please try expanding your search criteria or adjusting search conditions."
                else:
                    if len(user_query.strip()) < 10:
                        poor_quality_intro = "Your search query is too vague or short. Please provide more detailed criteria like skills, experience level, location, etc."
                    elif not current_user_info or current_user_info.get('error'):
                        poor_quality_intro = "Your profile information is incomplete. Please complete your skills, demands, and goals for more accurate recommendations."
                    else:
                        poor_quality_intro = "No suitable candidates found. Consider expanding search criteria or adjusting requirements."
                
                best_analysis = {
                    "overall_quality": "poor",
                    "candidate_count": 0,
                    "should_continue": True,
                    "analysis": "All search strategies failed to find suitable candidates",
                    "intro": poor_quality_intro
                }

            # Step 6: Process analysis results
            step_start = time.time()
            selected_candidates = best_analysis.get("selected_candidates", [])
            intro_response = best_analysis.get("intro", "")
            
            # Since analyze_candidates_quality already includes match reasons, use results directly
            candidates_with_reasons = selected_candidates
            
            performance_stats["result_generation"] = time.time() - step_start
            print(f"🎯 Result processing completed - Time: {performance_stats['result_generation']:.3f}s")
            
            # Calculate search statistics
            end_time = time.time()
            search_time = end_time - total_start_time
            performance_stats["total_time"] = search_time
            self.stats["total_search_time"] += search_time
            
            # Print performance statistics summary
            print(f"\n📈 Performance Statistics Summary:")
            print(f"  Language detection: {performance_stats['language_detection']:.3f}s")
            print(f"  Preprocessing phase: {performance_stats['preprocessing']:.3f}s")
            for search_key, search_time in performance_stats['vector_searches'].items():
                print(f"  Vector search {search_key}: {search_time:.3f}s")
            for analysis_key, analysis_time in performance_stats['candidate_analysis'].items():
                print(f"  Candidate analysis {analysis_key}: {analysis_time:.3f}s")
            print(f"  Result generation: {performance_stats['result_generation']:.3f}s")
            print(f"  Total time: {performance_stats['total_time']:.3f}s")
            
            # Build final result
            result = {
                "status": "success",
                "search_time": search_time,
                "query": user_query,
                "candidates": candidates_with_reasons,
                "intro_message": intro_response,
                "language": language_code,
                "candidate_count": len(candidates_with_reasons),
                "total_candidates_found": len(all_candidates),
                "search_quality": best_analysis.get("overall_quality", "unknown"),
                "analysis": best_analysis.get("analysis", ""),
                "search_attempts": attempt,
                "performance_stats": performance_stats,  # Add performance statistics
                "stats": self.get_search_stats()
            }
            
            print(f"✅ Search completed: Found {len(result['candidates'])} recommended candidates")
            return result
            
        except Exception as e:
            performance_stats["total_time"] = time.time() - total_start_time
            print(f"❌ Search failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "query": user_query,
                "candidates": [],
                "search_time": time.time() - total_start_time,
                "performance_stats": performance_stats
            }
    
    async def _async_optimize_dense_query(self, query: str, referenced_users: List[Dict]) -> str:
        """Asynchronously optimize dense query"""
        return self.optimize_query_for_dense_vector(query, referenced_users)
    
    async def _async_extract_sparse_tags(self, query: str, referenced_users: List[Dict]) -> str:
        """Asynchronously extract sparse tags"""
        return self.extract_tags_for_sparse_search(query, referenced_users)
    
    # ===== Utility Methods =====
    
    def get_search_stats(self) -> Dict:
        """Get search statistics"""
        avg_search_time = (
            self.stats["total_search_time"] / self.stats["search_count"] 
            if self.stats["search_count"] > 0 else 0
        )
        
        return {
            "total_searches": self.stats["search_count"],
            "total_llm_calls": self.stats["llm_calls"],
            "total_search_time": round(self.stats["total_search_time"], 2),
            "average_search_time": round(avg_search_time, 2),
            "cache_hits": self.stats["cache_hits"]
        }
    
    # ===== Intelligent Routing Scheduler =====
    
    async def route_to_processor(
        self,
        intent_result: Dict,
        user_input: str,
        referenced_users: List[Dict] = None,
        current_user: Dict = None,
        viewed_user_ids: List[str] = None,
        language_code: str = "zh"
    ) -> Dict:
        """
        Route to corresponding processor based on intent analysis result
        
        Args:
            intent_result: Intent analysis result
            user_input: User input
            referenced_users: Referenced user list
            current_user: Current user information
            viewed_user_ids: Viewed user ID list
            language_code: Language code for response ("zh" or "en")
            
        Returns:
            Processing result
        """
        intent = intent_result.get("intent", "chat")
        confidence = intent_result.get("confidence", 0.0)
        
        print(f"🎯 Route to processor: {intent} (confidence: {confidence:.2f})")
        
        try:
            if intent == "search":
                # Search mode: Start complete intelligent search process
                return await self.intelligent_search(
                    user_query=user_input,
                    current_user=current_user,
                    referenced_users=referenced_users,
                    viewed_user_ids=viewed_user_ids
                )
                
            elif intent == "inquiry":
                # Inquiry mode: Provide detailed analysis for specific user
                if not referenced_users or not referenced_users[0]:
                    # If no referenced user, convert to chat mode and provide suggestions
                    return self.process_chat(
                        user_input=user_input,
                        current_user=current_user,
                        clarification_needed=True,
                        uncertainty_reason="Inquiry mode requires referencing specific user, but no referenced user information found",
                        language_code=language_code
                    )
                
                return self.process_inquiry(
                    user_input=user_input,
                    referenced_user=referenced_users[0],
                    current_user=current_user,
                    language_code=language_code
                )
                
            elif intent == "chat":
                # Chat mode: Provide natural conversation experience
                clarification_needed = intent_result.get("clarification_needed", False)
                uncertainty_reason = intent_result.get("uncertainty_reason", "")
                
                return self.process_chat(
                    user_input=user_input,
                    current_user=current_user,
                    clarification_needed=clarification_needed,
                    uncertainty_reason=uncertainty_reason,
                    language_code=language_code
                )
                
            else:
                # Unknown intent, default to chat mode
                return self.process_chat(
                    user_input=user_input,
                    current_user=current_user,
                    clarification_needed=True,
                    uncertainty_reason=f"Unrecognized intent type: {intent}",
                    language_code=language_code
                )
                
        except Exception as e:
            print(f"Routing processing failed: {e}")
            return {
                "type": "error_response",
                "content": f"Sorry, an error occurred while processing your request: {str(e)}",
                "intent": intent,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    # ===== Main Entry Interface =====
    
    async def intelligent_conversation(
        self,
        user_input: str,
        user_id: str = None,
        referenced_ids: List[str] = None,
        viewed_user_ids: List[str] = None
    ) -> Dict:
        """
        Intelligent interaction unified entry point (integrates intent recognition and multi-mode processing)
        
        Args:
            user_input: User input text content
            user_id: User ID, used to get user's demands and goals information (optional)
            referenced_ids: Array of user IDs referenced by user, system will fetch complete user information from database (optional)
            viewed_user_ids: List of user IDs already viewed by user, used to exclude duplicate recommendations (optional)
        
        Returns:
            Interaction result: Intent-based personalized response, including result type tags
        """
        start_time = time.time()
        
        try:
            # Step 1: Language detection
            language_code, confidence = self.detect_language(user_input)
            print(f"🌐 Detected language: {language_code} (confidence: {confidence:.2f})")
            
            # Step 2: Get current user information (if user_id provided)
            current_user = None
            if user_id:
                print(f"🔍 Getting current user information: {user_id}")
                user_details = await self._fetch_user_details_from_db([user_id])
                current_user = user_details.get(str(user_id))
                if current_user and not current_user.get('error'):
                    print(f"✅ Successfully retrieved user information")
                else:
                    print(f"⚠️ Unable to retrieve user information or user does not exist")
            
            # Step 3: Get referenced user information (if referenced_ids provided)
            referenced_users = None
            if referenced_ids:
                print(f"🔍 Getting referenced user information: {referenced_ids}")
                referenced_details = await self._fetch_user_details_from_db(referenced_ids)
                referenced_users = []
                for ref_id in referenced_ids:
                    user_data = referenced_details.get(str(ref_id))
                    if user_data and not user_data.get('error'):
                        referenced_users.append(user_data)
                print(f"✅ Successfully retrieved {len(referenced_users)} referenced user information")
            
            # Step 4: Intent recognition
            intent_result = self.analyze_user_intent(
                user_input=user_input,
                referenced_user=referenced_users[0] if referenced_users else None,
                current_user=current_user
            )
            
            print(f"🎯 Intent recognition result: {intent_result['intent']} (confidence: {intent_result['confidence']:.2f})")
            if intent_result.get('reasoning'):
                print(f"   Reasoning process: {intent_result['reasoning']}")
            
            # Step 5: Use route_to_processor to handle routing logic
            raw_result = await self.route_to_processor(
                intent_result=intent_result,
                user_input=user_input,
                referenced_users=referenced_users,
                current_user=current_user,
                viewed_user_ids=viewed_user_ids,
                language_code=language_code
            )
            
            # Step 6: Add metadata and format results
            total_time = time.time() - start_time
            
            # Build final result
            result = {
                **raw_result,  # Include all results returned by processor
                "intent_analysis": intent_result,
                "language": language_code,
                "processing_time": round(total_time, 3),
                "user_id": user_id,
                "referenced_ids": referenced_ids,
                "viewed_user_ids": viewed_user_ids,
                "stats": self.get_search_stats()
            }
            
            print(f"✅ Intelligent interaction completed, processing time: {total_time:.3f}s")
            return result
            
        except Exception as e:
            total_time = time.time() - start_time
            print(f"❌ Intelligent interaction failed: {e}")
            return {
                "type": "error_response",
                "content": f"Sorry, an error occurred while processing your request: {str(e)}",
                "error": str(e),
                "processing_time": round(total_time, 3),
                "user_input": user_input,
                "timestamp": datetime.now().isoformat()
            }


# ===== Simplified Main Interface =====

def create_search_agent(
    glm_api_key: str = None,
    qdrant_client: QdrantClient = None,
    collection_name: str = "users_rawjson",
    glm_model: str = "glm-4-flash",
    api_base_url: str = "http://localhost:8000"
) -> SearchAgent:
    """
    Create search agent instance
    
    Args:
        glm_api_key: GLM-4 API key
        qdrant_client: Qdrant client instance
        collection_name: Qdrant collection name
        glm_model: GLM-4 model name
        api_base_url: Database API base URL
        
    Returns:
        SearchAgent instance
    """
    return SearchAgent(
        glm_api_key=glm_api_key,
        qdrant_client=qdrant_client,
        collection_name=collection_name,
        glm_model=glm_model,
        api_base_url=api_base_url
    )


async def quick_search(
    user_query: str,
    glm_api_key: str = None,
    **kwargs
) -> Dict:
    """
    Quick search interface - create temporary agent and execute search
    
    Args:
        user_query: User query text
        glm_api_key: GLM-4 API key
        **kwargs: Other search parameters
        
    Returns:
        Search results
    """
    agent = create_search_agent(glm_api_key=glm_api_key)
    return await agent.intelligent_search(user_query=user_query, **kwargs)


if __name__ == "__main__":
    # Simple component functionality test
    print("=" * 60)
    print("Intelligent Search Agent - Component Functionality Test")
    print("=" * 60)
    
    # Initialize agent (no real API key needed for basic testing)
    agent = SearchAgent(glm_api_key="test_key")
    
    # Test language detection
    print("\n🌐 Language Detection Test")
    print("-" * 30)
    test_texts = [
        "寻找Python工程师",
        "Looking for a Python developer", 
        "Find 有经验的 developer",
        "帮我找个AI算法工程师，会深度学习"
    ]
    
    for text in test_texts:
        lang, conf = agent.detect_language(text)
        print(f"'{text}' -> {lang} (confidence: {conf:.2f})")
    # Test hybrid search (using mock data)
    print("\n⚡ Hybrid Search Test")
    print("-" * 30)
    
    search_strategies = ["standard", "expanded", "custom"]
    for strategy in search_strategies:
        try:
            # Note: Since we're not in an async environment, search may fail
            # In actual usage, should be called within async functions
            print(f"{strategy.title()} search: Needs testing in async environment")
        except Exception as e:
            print(f"{strategy.title()} search test skipped: {e}")
    
    # Test statistics
    print("\n📊 Search Statistics")
    print("-" * 30)
    stats = agent.get_search_stats()
    for key, value in stats.items():
        print(f"{key}: {value}")
    
    print("\n✅ Component functionality test completed!")
    print("\n💡 To run complete intelligent search test, execute:")
    print("python test_intelligent_search.py")