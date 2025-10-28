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
import logging
from typing import Dict, List, Optional, Union, Any, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)


class SearchAgent:
    """Intelligent Search Agent Core Class"""
    
    def __init__(
        self,
        glm_api_key: str = None,
        vectordb_adapter=None,
        collection_name: str = "user_vectors_1024", 
        glm_model: str = "glm-4-flash",
        api_base_url: str = "http://localhost:8000"
    ):
        """
        Initialize search agent
        
        Args:
            glm_api_key: GLM-4 API key
            vectordb_adapter: TencentVectorDBAdapter instance
            collection_name: Vector collection name
            glm_model: GLM-4 model name
            api_base_url: Database API base URL
        """
        # Import GLM4Client from the correct location
        from services.glm4_client import GLM4Client
        
        # Initialize GLM-4 client
        self.glm_client = GLM4Client(
            api_key=glm_api_key,
            model=glm_model
        )
        
        # Initialize TencentVectorDB adapter
        self.vectordb_adapter = vectordb_adapter
        self.collection_name = collection_name
        
        # Database API configuration
        self.api_base_url = api_base_url.rstrip('/')
        
        # Preload embedding models
        print("[info] Loading embedding models...")
        self._initialize_embedding_models()
        print("[info] Embedding models loaded successfully")
        
        # Statistics
        self.stats = {
            "search_count": 0,
            "total_search_time": 0.0,
            "llm_calls": 0,
            "cache_hits": 0,
            "vector_searches": 0,
            "casual_count": 0
        }
        
        # Initialize casual request components (lazy loading for optional functionality)
        self.casual_classifier = None
        self.casual_optimizer = None
        self.casual_search_engine = None
        self.casual_collection_name = "casual_requests"
    
    def _initialize_embedding_models(self):
        """Initialize embedding models"""
        try:
            # Initialize BGE-M3 dense vector model
            from sentence_transformers import SentenceTransformer
            print("  [info] Loading BGE-M3 dense vector model...")
            self._dense_model = SentenceTransformer('BAAI/bge-m3')
            
            # Initialize SPLADE sparse vector model
            from transformers import AutoModelForMaskedLM, AutoTokenizer
            import torch
            print("  [info] Loading SPLADE sparse vector model...")
            
            try:
                # Try publicly available SPLADE models first
                splade_models = [
                    "naver/splade_v2_max",           # SPLADE v2 Max (publicly accessible)
                    "naver/splade_v2_distil",        # SPLADE v2 Distilled (publicly accessible)
                    "naver/splade-cocondenser-ensembledistil",  # Another public SPLADE model
                    "naver/splade-v3"                # Latest but gated (fallback if user has access)
                ]
                
                model_loaded = False
                for model_name in splade_models:
                    try:
                        print(f"  [info] Trying SPLADE model: {model_name}...")
                        self._splade_tokenizer = AutoTokenizer.from_pretrained(model_name)
                        self._splade_model = AutoModelForMaskedLM.from_pretrained(model_name)
                        
                        # Set device
                        self._device = 'mps' if torch.backends.mps.is_available() else ('cuda' if torch.cuda.is_available() else 'cpu')
                        self._splade_model = self._splade_model.to(self._device)
                        print(f"  [info] Using device: {self._device}")
                        print(f"  [info] ✅ SPLADE model loaded successfully: {model_name}")
                        model_loaded = True
                        break
                        
                    except Exception as model_error:
                        if "gated repo" in str(model_error).lower() or "restricted" in str(model_error).lower():
                            print(f"  [warn] {model_name} is gated/restricted, trying next model...")
                        else:
                            print(f"  [warn] Failed to load {model_name}: {str(model_error)[:100]}...")
                        continue
                
                if not model_loaded:
                    raise Exception("All SPLADE models failed to load")
                
            except Exception as splade_error:
                print(f"  [warn] SPLADE model loading failed: {splade_error}")
                if "gated repo" in str(splade_error).lower() or "restricted" in str(splade_error).lower():
                    print("  [info] SPLADE-v3 is a gated repository requiring authentication")
                    print("  [info] To use SPLADE-v3:")
                    print("    1. Create Hugging Face account: https://huggingface.co/join")
                    print("    2. Request access to naver/splade-v3")
                    print("    3. Login: huggingface-cli login")
                print("  [warn] Falling back to TF-IDF for sparse vectors...")
                self._splade_tokenizer = None
                self._splade_model = None
                
                # Set device anyway for dense model
                self._device = 'mps' if torch.backends.mps.is_available() else ('cuda' if torch.cuda.is_available() else 'cpu')
                print(f"  [info] Using device: {self._device}")
            
        except Exception as e:
            print(f"[error] Embedding model loading failed: {e}")
            print("  [warn] Falling back to TF-IDF for sparse vectors...")
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

4. **Casual Request**: Social activity invitations, looking for activity partners, non-work related
   - Key features: Focus on activities rather than skills, emphasis on social aspects and hobbies
   - Typical expressions: "Anyone want to go hiking this weekend?", "Looking for someone to have coffee with", "Who wants to go to the movies together"

Analysis Requirements:
- Carefully analyze the semantics and context of user input
- Consider whether there is referenced user information to assist judgment
- If intent is unclear, mark as needing clarification
- Provide clear reasoning process

Return JSON format:
{
    "intent": "search|inquiry|chat|casual",
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
            if intent not in ["search", "inquiry", "chat", "casual"]:
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
    
    # ===== 3.3.1 Casual Request Processor =====
    
    async def process_casual_request(
        self,
        user_input: str,
        current_user: Dict = None,
        language_code: str = "zh"
    ) -> Dict:
        """Process casual request with full integration"""
        
        # Start timing and update stats
        start_time = time.time()
        self.stats["casual_count"] += 1
        
        # Get user ID
        user_id = current_user.get('id', 'unknown') if current_user else 'unknown'
        
        # Initialize casual request components
        await self._initialize_casual_components()
        
        # 1. Store user's casual request and find matches
        storage_result = None
        matches = []
        
        if user_id != 'unknown' and hasattr(self, 'casual_classifier'):
            try:
                # Import database dependencies
                from dependencies.db import get_db
                
                # Get database session
                db_session = next(get_db())
                
                try:
                    # Process and store the casual request
                    from services.casual_request_processor import process_and_store_casual_request
                    
                    storage_result = await process_and_store_casual_request(
                        user_input=user_input,
                        user_id=str(user_id),
                        classifier=self.casual_classifier,
                        optimizer=self.casual_optimizer,
                        qdrant_client=getattr(self, 'qdrant_client', None),
                        embedding_model=getattr(self, '_dense_model', None),
                        collection_name="casual_requests",
                        db_conn=db_session
                    )
                    
                    print(f"[info] Casual request storage result: {storage_result}")
                    
                    # 2. Search for existing matching casual requests
                    if (hasattr(self, 'casual_search_engine') and 
                        self.casual_search_engine and 
                        storage_result and 
                        storage_result.get('success')):
                        try:
                            matches = await self.casual_search_engine.search_casual_requests(
                                query=user_input,
                                user_id=str(user_id),
                                limit=5
                            )
                            print(f"[info] Found {len(matches)} potential matches")
                        except Exception as e:
                            print(f"[warn] Could not search for matches: {e}")
                            
                finally:
                    db_session.close()
                
            except Exception as e:
                print(f"[warn] Could not process casual request: {e}")
        else:
            # If no valid user ID or components not available, provide basic acknowledgment
            print(f"[info] Processing casual request without storage (user_id: {user_id})")
            if not hasattr(self, 'casual_classifier'):
                print("[warn] Casual components not initialized")
        
        # 3. Build response based on results
        response_content = await self._build_casual_response(
            user_input=user_input,
            language_code=language_code,
            storage_result=storage_result,
            matches=matches
        )
        
        # End timing
        elapsed_time = time.time() - start_time
        
        # Build return result
        result = {
            "type": "casual_request",
            "intent": "casual",
            "content": response_content,
            "query": user_input,
            "user_id": user_id,
            "storage_result": storage_result,
            "matches": matches,
            "processing_time": elapsed_time,
            "timestamp": datetime.now().isoformat(),
            "status": "acknowledged"
        }
        
        return result
    
    # ===== 3.3.1 Casual Request Helper Methods =====
    
    async def _initialize_casual_components(self):
        """Initialize casual request components if not already done"""
        try:
            # Import casual request components
            from services.casual_request_classifier import CasualRequestClassifier
            from services.casual_request_optimizer import CasualRequestOptimizer
            from services.casual_request_search_engine import CasualRequestSearchEngine
            
            # Initialize components if not already done
            if not hasattr(self, 'casual_classifier') or self.casual_classifier is None:
                print(f"[debug] Initializing CasualRequestClassifier with api_key={self.glm_client.api_key[:20] if self.glm_client.api_key else None}...")
                self.casual_classifier = CasualRequestClassifier(
                    glm_api_key=self.glm_client.api_key,
                    glm_model=self.glm_client.default_model
                )
                print(f"[info] ✅ CasualRequestClassifier initialized: {type(self.casual_classifier)}")
            
            if not hasattr(self, 'casual_optimizer') or self.casual_optimizer is None:
                print(f"[debug] Initializing CasualRequestOptimizer with api_key={self.glm_client.api_key[:20] if self.glm_client.api_key else None}...")
                self.casual_optimizer = CasualRequestOptimizer(
                    glm_api_key=self.glm_client.api_key,
                    glm_model=self.glm_client.default_model
                )
                print(f"[info] ✅ CasualRequestOptimizer initialized: {type(self.casual_optimizer)}")
            
            if not hasattr(self, 'casual_search_engine') or self.casual_search_engine is None:
                print(f"[debug] Initializing CasualRequestSearchEngine...")
                self.casual_search_engine = CasualRequestSearchEngine(
                    glm_api_key=self.glm_client.api_key,
                    qdrant_client=getattr(self, 'qdrant_client', None),
                    collection_name="casual_requests",
                    glm_model=self.glm_client.default_model,
                    api_base_url=getattr(self, 'api_base_url', None),
                    embedding_model=getattr(self, '_dense_model', None)
                )
                print(f"[info] ✅ CasualRequestSearchEngine initialized: {type(self.casual_search_engine)}")
                
        except Exception as e:
            print(f"[warn] Could not initialize casual components: {e}")
            import traceback
            traceback.print_exc()
            # Set components to None to indicate failure
            self.casual_classifier = None
            self.casual_optimizer = None
            self.casual_search_engine = None
    
    async def _build_casual_response(
        self,
        user_input: str,
        language_code: str,
        storage_result: dict = None,
        matches: list = None
    ) -> str:
        """Build response content for casual requests"""
        
        if language_code == "zh":
            if storage_result and storage_result.get('success'):
                if matches and len(matches) > 0:
                    # Found matches
                    match_count = len(matches)
                    response = f"我收到了您的社交活动请求：「{user_input}」\n\n"
                    response += f"🎉 找到了 {match_count} 个可能感兴趣的活动伙伴！\n\n"
                    
                    for i, match in enumerate(matches[:3], 1):  # Show top 3 matches
                        activity = match.get('activity_type', '未知活动')
                        location = match.get('preferred_location', '未指定地点')
                        time_pref = match.get('preferred_time', '时间待定')
                        score = match.get('similarity_score', 0.0)
                        
                        response += f"{i}. {activity} | {location} | {time_pref} (匹配度: {score:.2f})\n"
                    
                    if match_count > 3:
                        response += f"\n还有 {match_count - 3} 个其他匹配..."
                        
                else:
                    # Stored but no matches yet
                    response = f"我收到了您的社交活动请求：「{user_input}」\n\n"
                    response += "✅ 已将您的请求记录下来，当有相似兴趣的用户时会为您匹配！"
            else:
                # Storage failed or incomplete
                response = f"我收到了您的社交活动请求：「{user_input}」\n\n"
                response += "📝 暂时记录了您的请求。完整的匹配功能需要配置数据库连接。"
        else:
            if storage_result and storage_result.get('success'):
                if matches and len(matches) > 0:
                    # Found matches
                    match_count = len(matches)
                    response = f"I've received your casual activity request: \"{user_input}\"\n\n"
                    response += f"🎉 Found {match_count} potential activity partners!\n\n"
                    
                    for i, match in enumerate(matches[:3], 1):  # Show top 3 matches
                        activity = match.get('activity_type', 'Unknown activity')
                        location = match.get('preferred_location', 'Location TBD')
                        time_pref = match.get('preferred_time', 'Time TBD')
                        score = match.get('similarity_score', 0.0)
                        
                        response += f"{i}. {activity} | {location} | {time_pref} (Match: {score:.2f})\n"
                    
                    if match_count > 3:
                        response += f"\n{match_count - 3} more matches available..."
                        
                else:
                    # Stored but no matches yet
                    response = f"I've received your casual activity request: \"{user_input}\"\n\n"
                    response += "✅ Your request has been recorded! We'll match you with users who have similar interests."
            else:
                # Storage failed or incomplete
                response = f"I've received your casual activity request: \"{user_input}\"\n\n"
                response += "📝 Temporarily recorded your request. Full matching requires database configuration."
        
        return response
    
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
        swiped_user_ids: List[str] = None,
        fetch_db_details: bool = True
    ) -> List[Dict]:
        """
        Execute hybrid vector search with proper fallback mechanism
        
        Args:
            dense_query: Dense vector query text
            sparse_query: Sparse vector query text
            search_strategy: Search strategy ("standard", "expanded", "custom")
            limit: Number of results to return (default 10)
            viewed_user_ids: List of viewed user IDs (exclude from initial search)
            swiped_user_ids: List of swiped user IDs (filter after getting 50 candidates)
            fetch_db_details: Whether to fetch detailed information from database
            
        Returns:
            Search result list (including database detailed information)
            
        Fallback Mechanism:
            1. Get closest 50 candidates from vector search (exclude viewed users only)
            2. Filter out users who have been swiped (left/right)  
            3. Return top {limit} from remaining candidates
        """
        try:
            # STEP 1: Get 50 candidates (exclude only viewed users, not swiped users)
            fallback_limit = max(50, limit * 5)  # Get at least 50 or 5x the requested limit
            
            filter_conditions = {}
            if viewed_user_ids:
                filter_conditions["user_id"] = {"$nin": viewed_user_ids}

            print(f"[info] Executing {search_strategy} search for {fallback_limit} candidates...")
            
            # Execute vector search using the vectordb adapter
            if search_strategy == "standard":
                vector_results = await self._standard_search(dense_query, sparse_query, filter_conditions, fallback_limit)
            elif search_strategy == "expanded":
                vector_results = await self._expanded_search(dense_query, sparse_query, filter_conditions, fallback_limit)
            elif search_strategy == "custom":
                vector_results = await self._custom_search(dense_query, sparse_query, filter_conditions, fallback_limit)
            else:
                raise ValueError(f"Unsupported search strategy: {search_strategy}")
            
            print(f"[info] Initial vector search found {len(vector_results)} candidates")
            
            # STEP 2: Filter out swiped users (post-search filtering)
            if swiped_user_ids and vector_results:
                swiped_set = set(str(uid) for uid in swiped_user_ids)
                filtered_results = []
                
                for result in vector_results:
                    user_id = str(result.get("user_id", ""))
                    if user_id not in swiped_set:
                        filtered_results.append(result)
                
                print(f"[info] After filtering swiped users: {len(filtered_results)} candidates remain")
                vector_results = filtered_results
            
            # STEP 3: Return top {limit} candidates
            final_results = vector_results[:limit]
            print(f"[info] Returning top {len(final_results)} candidates")
            
            # If no database details needed or no search results, return vector search results directly
            if not fetch_db_details or not final_results:
                return final_results
            
            # Extract user ID list
            user_ids = [str(result.get("user_id")) for result in final_results if result.get("user_id")]
            
            if not user_ids:
                return final_results
            
            print(f"[info] Fetching database details for {len(user_ids)} selected candidates...")
            
            # Fetch user detailed information from database
            db_details = await self._fetch_user_details_from_db(user_ids)
            
            # Merge vector search results and database details
            merged_results = self._merge_vector_and_db_results(final_results, db_details)
            
            print(f"[info] Successfully fetched database details for {len([r for r in db_details.values() if not r.get('error')])} users")
            
            return merged_results
            
            # Fetch user detailed information from database
            db_details = await self._fetch_user_details_from_db(user_ids)
            
            # Merge vector search results and database details
            merged_results = self._merge_vector_and_db_results(vector_results, db_details)
            
            print(f"[info] Successfully fetched database details for {len([r for r in db_details.values() if not r.get('error')])} users")
            
            return merged_results
                
        except Exception as e:
            print(f"Hybrid search failed: {e}")
            return []
    
    async def _standard_search(
        self, 
        dense_query: str, 
        sparse_query: str, 
        filter_conditions: Dict[str, Any], 
        limit: int
    ) -> List[Dict]:
        """Standard search strategy - uses vectordb hybrid search with modest prefetch"""
        try:
            # Ensure dense model is loaded
            if self._dense_model is None:
                from sentence_transformers import SentenceTransformer
                self._dense_model = SentenceTransformer('BAAI/bge-m3')

            dense_vec = self._dense_model.encode(dense_query, normalize_embeddings=True).tolist()

            # Generate sparse dict
            sparse_dict = self._build_splade_sparse_vector(sparse_query)

            # Use the vectordb adapter to perform hybrid search
            prefetch_k = max(limit, 50)
            results = await self.vectordb_adapter.hybrid_search(
                query_vector=dense_vec,
                sparse_vector=sparse_dict if sparse_dict else None,
                top_k=prefetch_k,
                filter_conditions=filter_conditions
            )

            # Map adapter results to expected format and slice to limit
            mapped = [
                {
                    "user_id": r.get("user_id"),
                    "score": r.get("score", 0.0),
                    **(r.get("metadata") or {})
                } for r in results
            ]

            return mapped[:limit]
        except Exception as e:
            print(f"Standard search failed: {e}")
            return []
    
    async def _expanded_search(
        self, 
        dense_query: str, 
        sparse_query: str, 
        filter_conditions: Dict[str, Any], 
        limit: int
    ) -> List[Dict]:
        """Expanded search strategy - larger prefetch and broader recall"""
        try:
            if self._dense_model is None:
                from sentence_transformers import SentenceTransformer
                self._dense_model = SentenceTransformer('BAAI/bge-m3')

            dense_vec = self._dense_model.encode(dense_query, normalize_embeddings=True).tolist()
            sparse_dict = self._build_splade_sparse_vector(sparse_query)

            prefetch_k = max(limit, 150)
            results = await self.vectordb_adapter.hybrid_search(
                query_vector=dense_vec,
                sparse_vector=sparse_dict if sparse_dict else None,
                top_k=prefetch_k,
                filter_conditions=filter_conditions
            )

            mapped = [
                {
                    "user_id": r.get("user_id"),
                    "score": r.get("score", 0.0),
                    **(r.get("metadata") or {})
                } for r in results
            ]

            return mapped[:limit]
        except Exception as e:
            print(f"Expanded search failed: {e}")
            return []
    
    async def _custom_search(
        self, 
        dense_query: str, 
        sparse_query: str, 
        filter_conditions: Dict[str, Any], 
        limit: int
    ) -> List[Dict]:
        """Custom search strategy - use adapter results and perform custom fusion on dense/sparse scores"""
        try:
            if self._dense_model is None:
                from sentence_transformers import SentenceTransformer
                self._dense_model = SentenceTransformer('BAAI/bge-m3')

            dense_vec = self._dense_model.encode(dense_query, normalize_embeddings=True).tolist()
            sparse_dict = self._build_splade_sparse_vector(sparse_query)

            # Request a moderate number of candidates from vectordb
            results = await self.vectordb_adapter.hybrid_search(
                query_vector=dense_vec,
                sparse_vector=sparse_dict if sparse_dict else None,
                top_k=120,
                filter_conditions=filter_conditions
            )

            # Perform custom DBSF-style fusion using returned dense_score and sparse_score
            try:
                import numpy as np
                dense_scores = np.array([r.get('dense_score', 0.0) for r in results])
                sparse_scores = np.array([r.get('sparse_score', 0.0) for r in results])

                dense_mean, dense_std = (dense_scores.mean(), dense_scores.std()) if len(dense_scores) else (0, 1)
                sparse_mean, sparse_std = (sparse_scores.mean(), sparse_scores.std()) if len(sparse_scores) else (0, 1)
                dense_std = dense_std if dense_std > 1e-6 else 1.0
                sparse_std = sparse_std if sparse_std > 1e-6 else 1.0

                dense_norm = {r.get('user_id'): (r.get('dense_score', 0.0) - dense_mean) / dense_std for r in results}
                sparse_norm = {r.get('user_id'): (r.get('sparse_score', 0.0) - sparse_mean) / sparse_std for r in results}

                alpha = 0.2
                score_map = {}
                for r in results:
                    uid = r.get('user_id')
                    score = 0.0
                    score += alpha * dense_norm.get(uid, 0.0)
                    score += (1 - alpha) * sparse_norm.get(uid, 0.0)
                    score_map[uid] = score

                # Sort by fused score
                sorted_ids = sorted(score_map.items(), key=lambda x: x[1], reverse=True)[:limit]
                fused_list = []
                id_to_result = {r.get('user_id'): r for r in results}
                for uid, score in sorted_ids:
                    r = id_to_result.get(uid)
                    fused_list.append({
                        "user_id": uid,
                        "score": float(score),
                        **(r.get('metadata') or {})
                    })

                return fused_list
            except Exception:
                # Fallback: return top-k by adapter score
                mapped = [
                    {"user_id": r.get('user_id'), "score": r.get('score', 0.0), **(r.get('metadata') or {})}
                    for r in results
                ]
                return mapped[:limit]

        except Exception as e:
            print(f"Custom search failed: {e}")
            return []
    
    def _build_splade_sparse_vector(self, text: str) -> Dict[str, float]:
        """Generate sparse vector using SPLADE-v3 model or TF-IDF fallback"""
        try:
            # Try SPLADE-v3 model first
            if self._splade_model is not None and self._splade_tokenizer is not None:
                import torch
                
                # Tokenize input
                inputs = self._splade_tokenizer(text, return_tensors="pt", max_length=512, truncation=True)
                inputs = {k: v.to(self._device) for k, v in inputs.items()}
                
                # Generate SPLADE embeddings
                with torch.no_grad():
                    outputs = self._splade_model(**inputs)
                    logits = outputs.logits
                    
                    # Apply ReLU and log to get sparse representation
                    sparse_embeddings = torch.relu(logits) * torch.log(1 + torch.relu(logits))
                    sparse_embeddings = sparse_embeddings.squeeze(0)  # Remove batch dimension
                    
                    # Convert to dictionary format
                    vocab = self._splade_tokenizer.get_vocab()
                    id_to_token = {v: k for k, v in vocab.items()}
                    
                    sparse_dict = {}
                    for token_id, score in enumerate(sparse_embeddings.max(dim=0)[0]):
                        if score > 0.1:  # Only include tokens with meaningful scores
                            token = id_to_token.get(token_id, f"[UNK_{token_id}]")
                            # Skip special tokens
                            if not token.startswith("[") and len(token) > 1:
                                sparse_dict[token] = float(score.cpu())
                    
                    # Normalize scores
                    if sparse_dict:
                        max_score = max(sparse_dict.values())
                        if max_score > 0:
                            sparse_dict = {k: v / max_score for k, v in sparse_dict.items()}
                    
                    return sparse_dict
            
            # Fallback to TF-IDF if SPLADE is not available
            print(f"  [warn] SPLADE model not available, using TF-IDF fallback")
            return self._build_tfidf_sparse_vector(text)
            
        except Exception as e:
            print(f"SPLADE sparse vector generation failed: {e}")
            print(f"  [warn] Falling back to TF-IDF")
            return self._build_tfidf_sparse_vector(text)
    
    def _build_tfidf_sparse_vector(self, text: str) -> Dict[str, float]:
        """Generate sparse vector using TF-IDF fallback"""
        try:
            # TF-IDF-style sparse vector generation
            import re
            import math
            from collections import Counter
            
            # Tokenize and clean text
            words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
            if not words:
                return {}
            
            # Calculate term frequencies
            word_counts = Counter(words)
            total_words = len(words)
            
            # Create sparse representation with TF-IDF style weights
            sparse_dict = {}
            
            # Common stop words to reduce weight
            stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
            
            for word, count in word_counts.items():
                if len(word) < 2:  # Skip very short words
                    continue
                    
                # Calculate TF (term frequency)
                tf = count / total_words
                
                # Simple IDF approximation (boost less common words)
                # Assume document collection size of 10000 and word appears in 100 docs on average
                idf = math.log(10000 / (100 if word not in stop_words else 1000))
                
                # TF-IDF score
                score = tf * idf
                
                # Boost important keywords
                important_keywords = {
                    'mobile', 'app', 'android', 'ios', 'swift', 'kotlin', 'react', 'flutter',
                    'development', 'developer', 'programming', 'coding', 'student', 'university',
                    'interested', 'passionate', 'experience', 'project', 'build', 'create',
                    'python', 'javascript', 'java', 'frontend', 'backend', 'machine', 'learning',
                    'ai', 'data', 'science', 'algorithm', 'web', 'design', 'ui', 'ux'
                }
                
                if word in important_keywords:
                    score *= 2.0  # Boost important terms
                
                if score > 0.001:  # Only include meaningful scores
                    sparse_dict[word] = float(score)
            
            # Normalize scores to prevent very large values
            if sparse_dict:
                max_score = max(sparse_dict.values())
                if max_score > 0:
                    sparse_dict = {k: v / max_score for k, v in sparse_dict.items()}
            
            return sparse_dict
            
        except Exception as e:
            print(f"TF-IDF sparse vector generation failed: {e}")
            return {}
    
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
        viewed_user_ids: List[str] = None,
        swiped_user_ids: List[str] = None
    ) -> Dict:
        """
        Complete intelligent search method - includes language detection, search scheduling and result generation
        
        Args:
            user_query: User query
            current_user: Current user's complete information (including demands and goals)
            referenced_users: Referenced user list
            viewed_user_ids: Viewed user ID list (excluded from initial search)
            swiped_user_ids: Swiped user ID list (filtered after getting 50 candidates)
            
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
            print(f"[info] Detected language: {language_code} (confidence: {confidence:.2f}) - Time: {performance_stats['language_detection']:.3f}s")
            
            # Step 2: Use passed current_user information
            current_user_info = current_user
            if current_user_info:
                print(f"[info] Using passed user information")
            
            # Step 3: Preprocessing phase - concurrent execution of independent components
            step_start = time.time()
            print("[info] Starting preprocessing phase...")
            
            # Execute preprocessing tasks concurrently
            tasks = [
                asyncio.create_task(self._async_optimize_dense_query(user_query, referenced_users)),
                asyncio.create_task(self._async_extract_sparse_tags(user_query, referenced_users))
            ]
            
            dense_query, sparse_query = await asyncio.gather(*tasks)
            performance_stats["preprocessing"] = time.time() - step_start
            
            print(f"[info] Preprocessing completed - Dense: {len(dense_query)}, Sparse: {len(sparse_query)} - Time: {performance_stats['preprocessing']:.3f}s")
            
            # Step 4: Three-phase search loop
            search_strategies = ["standard", "expanded", "custom"]
            all_candidates = []
            best_analysis = None
            
            for attempt, strategy in enumerate(search_strategies, 1):
                print(f"[info] Search attempt {attempt}/3: {strategy} strategy")
                
                # Execute search
                search_start = time.time()
                candidates = await self.hybrid_search(
                    dense_query=dense_query,
                    sparse_query=sparse_query,
                    search_strategy=strategy,
                    limit=10,
                    viewed_user_ids=viewed_user_ids or [],
                    swiped_user_ids=swiped_user_ids or [],
                    fetch_db_details=False  # Use VectorDB data only (no PostgreSQL API call)
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
                    
                    print(f"[info] Analysis result: {analysis.get('overall_quality', 'unknown')} - {analysis.get('candidate_count', 0)} candidates")
                    print(f"    Search time: {search_time:.3f}s, Analysis time: {analysis_time:.3f}s")
                    
                    # If quality is good or this is the last attempt, stop searching
                    if (analysis.get("overall_quality") in ["excellent", "good"] or 
                        not analysis.get("should_continue", True) or 
                        attempt == len(search_strategies)):
                        best_analysis = analysis
                        break
                else:
                    print(f"    Search time: {search_time:.3f}s, no candidates")
                
                print(f"[info] Continue to next search phase...")
            
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
            print(f"[info] Result processing completed - Time: {performance_stats['result_generation']:.3f}s")
            
            # Calculate search statistics
            end_time = time.time()
            search_time = end_time - total_start_time
            performance_stats["total_time"] = search_time
            self.stats["total_search_time"] += search_time
            
            # Print performance statistics summary
            print(f"\n[info] Performance Statistics Summary:")
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
            
            print(f"[info] Search completed: Found {len(result['candidates'])} recommended candidates")
            return result
            
        except Exception as e:
            performance_stats["total_time"] = time.time() - total_start_time
            print(f"[error] Search failed: {e}")
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
        swiped_user_ids: List[str] = None,
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
            swiped_user_ids: Swiped user ID list
            language_code: Language code for response ("zh" or "en")
            
        Returns:
            Processing result
        """
        intent = intent_result.get("intent", "chat")
        confidence = intent_result.get("confidence", 0.0)
        
        print(f"[info] Route to processor: {intent} (confidence: {confidence:.2f})")
        
        try:
            if intent == "search":
                # Search mode: Start complete intelligent search process
                return await self.intelligent_search(
                    user_query=user_input,
                    current_user=current_user,
                    referenced_users=referenced_users,
                    viewed_user_ids=viewed_user_ids,
                    swiped_user_ids=swiped_user_ids
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
                
            elif intent == "casual":
                # Casual request mode: Process social activity requests
                return await self.process_casual_request(
                    user_input=user_input,
                    current_user=current_user,
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
        viewed_user_ids: List[str] = None,
        swiped_user_ids: List[str] = None
    ) -> Dict:
        """
        Intelligent interaction unified entry point (integrates intent recognition and multi-mode processing)
        
        Args:
            user_input: User input text content
            user_id: User ID, used to get user's demands and goals information (optional)
            referenced_ids: Array of user IDs referenced by user, system will fetch complete user information from database (optional)
            viewed_user_ids: List of user IDs already viewed by user, used to exclude duplicate recommendations (optional)
            swiped_user_ids: List of user IDs already swiped by user, used for post-search filtering (optional)
        
        Returns:
            Interaction result: Intent-based personalized response, including result type tags
        """
        start_time = time.time()
        
        try:
            # Step 1: Language detection
            language_code, confidence = self.detect_language(user_input)
            print(f"[info] Detected language: {language_code} (confidence: {confidence:.2f})")
            
            # Step 2: Get current user information (if user_id provided)
            current_user = None
            if user_id:
                print(f"[info] Getting current user information: {user_id}")
                user_details = await self._fetch_user_details_from_db([user_id])
                current_user = user_details.get(str(user_id))
                if current_user and not current_user.get('error'):
                    print(f"[info] Successfully retrieved user information")
                else:
                    print(f"[warn] Unable to retrieve user information or user does not exist")
            
            # Step 3: Get referenced user information (if referenced_ids provided)
            referenced_users = None
            if referenced_ids:
                print(f"[info] Getting referenced user information: {referenced_ids}")
                referenced_details = await self._fetch_user_details_from_db(referenced_ids)
                referenced_users = []
                for ref_id in referenced_ids:
                    user_data = referenced_details.get(str(ref_id))
                    if user_data and not user_data.get('error'):
                        referenced_users.append(user_data)
                print(f"[info] Successfully retrieved {len(referenced_users)} referenced user information")
            
            # Step 4: Intent recognition
            intent_result = self.analyze_user_intent(
                user_input=user_input,
                referenced_user=referenced_users[0] if referenced_users else None,
                current_user=current_user
            )
            
            print(f"[info] Intent recognition result: {intent_result['intent']} (confidence: {intent_result['confidence']:.2f})")
            if intent_result.get('reasoning'):
                print(f"   Reasoning process: {intent_result['reasoning']}")
            
            # Step 5: Use route_to_processor to handle routing logic
            raw_result = await self.route_to_processor(
                intent_result=intent_result,
                user_input=user_input,
                referenced_users=referenced_users,
                current_user=current_user,
                viewed_user_ids=viewed_user_ids,
                swiped_user_ids=swiped_user_ids,
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
            
            print(f"[info] Intelligent interaction completed, processing time: {total_time:.3f}s")
            return result
            
        except Exception as e:
            total_time = time.time() - start_time
            print(f"[error] Intelligent interaction failed: {e}")
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
    vectordb_adapter=None,
    collection_name: str = "users_rawjson",
    glm_model: str = "glm-4-flash",
    api_base_url: str = "http://localhost:8000"
) -> SearchAgent:
    """
    Create search agent instance
    
    Args:
        glm_api_key: GLM-4 API key
        vectordb_adapter: VectorDB adapter instance (e.g., TencentVectorDBAdapter)
        collection_name: VectorDB collection name
        glm_model: GLM-4 model name
        api_base_url: Database API base URL
        
    Returns:
        SearchAgent instance
    """
    return SearchAgent(
        glm_api_key=glm_api_key,
        vectordb_adapter=vectordb_adapter,
        collection_name=collection_name,
        glm_model=glm_model,
        api_base_url=api_base_url
    )


async def quick_search(
    user_query: str,
    glm_api_key: str = None,
    vectordb_adapter=None,
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
    agent = create_search_agent(glm_api_key=glm_api_key, vectordb_adapter=vectordb_adapter)
    return await agent.intelligent_search(user_query=user_query, **kwargs)


if __name__ == "__main__":
    # Simple component functionality test
    print("=" * 60)
    print("Intelligent Search Agent - Component Functionality Test")
    print("=" * 60)
    
    # Initialize agent (no real API key needed for basic testing)
    agent = SearchAgent(glm_api_key="test_key")
    
    # Test language detection
    print("\n[info] Language Detection Test")
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
    print("\n[info] Hybrid Search Test")
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
    print("\n[info] Search Statistics")
    print("-" * 30)
    stats = agent.get_search_stats()
    for key, value in stats.items():
        print(f"{key}: {value}")
    
    print("\n[info] Component functionality test completed!")
    print("\n[info] To run complete intelligent search test, execute:")
    print("python test_intelligent_search.py")