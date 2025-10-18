#!/usr/bin/env python3
"""
GLM-4 API Utility Class
Complete API client based on Zhipu AI GLM-4 model, supporting all LLM call requirements for the search agent system.
API Documentation: https://open.bigmodel.cn/dev/api/normal-model/glm-4
"""

import os
import json
import requests
import asyncio
import time
from datetime import datetime
from typing import Dict, List, Optional, Union, Any
from enum import Enum


class GLM4Model(Enum):
    """GLM-4 model series enumeration"""
    GLM_4_PLUS = "glm-4-plus"          # Most powerful version, complex reasoning
    GLM_4_0520 = "glm-4-0520"          # High performance version
    GLM_4 = "glm-4"                    # Standard version
    GLM_4_AIR = "glm-4-air"            # Lightweight version
    GLM_4_AIRX = "glm-4-airx"          # Enhanced lightweight version
    GLM_4_LONG = "glm-4-long"          # Long text version
    GLM_4_FLASH = "glm-4-flash"        # Fast version
    GLM_4_FLASH_250414 = "glm-4-flash-250414"  # Specific version fast model


class ResponseFormat(Enum):
    """Response format enumeration"""
    TEXT = "text"                      # Plain text output
    JSON_OBJECT = "json_object"        # JSON object output


class GLM4Exception(Exception):
    """GLM-4 API exception class"""
    def __init__(self, message: str, error_code: str = None, status_code: int = None):
        super().__init__(message)
        self.error_code = error_code
        self.status_code = status_code


class GLM4Client:
    """
    GLM-4 API Client
    
    Supported features:
    - Synchronous/asynchronous calls
    - Streaming output
    - JSON format control
    - Function Calling
    - Web Search
    - Complete error handling
    - Automatic retry mechanism
    """
    
    def __init__(
        self,
        api_key: str = None,
        base_url: str = "https://open.bigmodel.cn/api/paas/v4",
        model: Union[str, GLM4Model] = GLM4Model.GLM_4_FLASH,
        timeout: int = 30,
        max_retries: int = 3,
        retry_delay: float = 1.0
    ):
        """
        Initialize GLM-4 client
        
        Args:
            api_key: API key, if not provided, get from environment variable ZHIPUAI_API_KEY
            base_url: API base URL
            model: Default model to use
            timeout: Request timeout (seconds)
            max_retries: Maximum retry attempts
            retry_delay: Retry delay time (seconds)
        """
        self.api_key = api_key or os.getenv('ZHIPUAI_API_KEY')
        if not self.api_key:
            raise GLM4Exception("Please provide API key or set environment variable ZHIPUAI_API_KEY")
        
        self.base_url = base_url.rstrip('/')
        self.default_model = model.value if isinstance(model, GLM4Model) else model
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        
        # Request statistics
        self.request_count = 0
        self.total_tokens = 0
        self.total_cost = 0.0
    
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers"""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "GLM4Client/1.0"
        }
    
    def _make_request(
        self,
        endpoint: str,
        payload: Dict[str, Any],
        stream: bool = False
    ) -> Union[Dict, requests.Response]:
        """
        Send HTTP request to GLM-4 API
        
        Args:
            endpoint: API endpoint
            payload: Request data
            stream: Whether to use streaming request
        
        Returns:
            API response or streaming response object
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        headers = self._get_headers()
        
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                self.request_count += 1
                
                response = requests.post(
                    url,
                    headers=headers,
                    json=payload,
                    timeout=self.timeout,
                    stream=stream
                )
                
                # Check HTTP status code
                if response.status_code == 200:
                    if stream:
                        return response
                    return response.json()
                else:
                    # Parse error information
                    try:
                        error_data = response.json()
                        error_message = error_data.get('error', {}).get('message', f'HTTP {response.status_code}')
                        error_code = error_data.get('error', {}).get('code', 'unknown')
                    except:
                        error_message = f"HTTP {response.status_code}: {response.text}"
                        error_code = str(response.status_code)
                    
                    raise GLM4Exception(
                        error_message,
                        error_code=error_code,
                        status_code=response.status_code
                    )
                    
            except requests.RequestException as e:
                last_exception = GLM4Exception(f"Network request failed: {str(e)}")
                
                if attempt < self.max_retries:
                    time.sleep(self.retry_delay * (2 ** attempt))  # Exponential backoff
                    continue
                break
        
        # All retries failed
        raise last_exception or GLM4Exception("Request failed")
    
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = None,
        temperature: float = 0.95,
        top_p: float = 0.7,
        max_tokens: int = 1024,
        stream: bool = False,
        stop: List[str] = None,
        response_format: Union[str, ResponseFormat] = None,
        tools: List[Dict] = None,
        tool_choice: str = "auto",
        user_id: str = None,
        request_id: str = None,
        do_sample: bool = True
    ) -> Union[Dict, requests.Response]:
        """
        Chat completion API call
        
        Args:
            messages: Conversation message list, format: [{"role": "user", "content": "hello"}]
            model: Model name, use default model if not specified
            temperature: Sampling temperature (0.0-1.0)
            top_p: Nucleus sampling parameter (0.0-1.0)
            max_tokens: Maximum output token count
            stream: Whether to enable streaming output
            stop: Stop words list
            response_format: Response format, "text" or "json_object"
            tools: Tool list (function calling)
            tool_choice: Tool selection strategy
            user_id: User ID (6-128 characters)
            request_id: Request ID (for idempotency)
            do_sample: Whether to enable sampling
        
        Returns:
            API response result or streaming response object
        """
        payload = {
            "model": model or self.default_model,
            "messages": messages,
            "temperature": temperature,
            "top_p": top_p,
            "max_tokens": max_tokens,
            "stream": stream,
            "do_sample": do_sample
        }
        
        # Optional parameters
        if stop:
            payload["stop"] = stop
        if response_format:
            format_value = response_format.value if isinstance(response_format, ResponseFormat) else response_format
            payload["response_format"] = {"type": format_value}
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = tool_choice
        if user_id:
            payload["user_id"] = user_id
        if request_id:
            payload["request_id"] = request_id
        
        return self._make_request("chat/completions", payload, stream=stream)
    
    def simple_chat(
        self,
        content: str,
        system_prompt: str = None,
        temperature: float = 0.95,
        max_tokens: int = 1024,
        response_format: Union[str, ResponseFormat] = None
    ) -> str:
        """
        Simple chat interface
        
        Args:
            content: User input content
            system_prompt: System prompt
            temperature: Sampling temperature
            max_tokens: Maximum output tokens
            response_format: Response format
        
        Returns:
            Model reply content
        """
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": content})
        
        response = self.chat_completion(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            response_format=response_format
        )
        
        # Update statistics
        if "usage" in response:
            self.total_tokens += response["usage"].get("total_tokens", 0)
        
        return response["choices"][0]["message"]["content"]
    
    def json_chat(
        self,
        content: str,
        system_prompt: str = None,
        temperature: float = 0.1,
        max_tokens: int = 1024
    ) -> Dict:
        """
        JSON format chat interface
        
        Args:
            content: User input content
            system_prompt: System prompt
            temperature: Sampling temperature (lower recommended for JSON output)
            max_tokens: Maximum output tokens
        
        Returns:
            Parsed JSON object
        """
        if not system_prompt:
            system_prompt = "You are a professional assistant, please always reply in JSON format."
        else:
            system_prompt += "\n\nPlease reply in JSON format."
        
        response_text = self.simple_chat(
            content=content,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            response_format=ResponseFormat.JSON_OBJECT
        )
        
        try:
            return json.loads(response_text)
        except json.JSONDecodeError as e:
            raise GLM4Exception(f"JSON parsing failed: {e}\nOriginal reply: {response_text}")
    
    def stream_chat(
        self,
        messages: List[Dict[str, str]],
        model: str = None,
        temperature: float = 0.95,
        max_tokens: int = 1024,
        **kwargs
    ):
        """
        Streaming chat interface
        
        Args:
            messages: Conversation message list
            model: Model name
            temperature: Sampling temperature
            max_tokens: Maximum output tokens
            **kwargs: Other parameters
        
        Yields:
            Content of each data chunk
        """
        response = self.chat_completion(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
            **kwargs
        )
        
        for line in response.iter_lines():
            if line:
                line_text = line.decode('utf-8')
                if line_text.startswith('data: '):
                    data_text = line_text[6:]  # Remove 'data: ' prefix
                    
                    if data_text.strip() == '[DONE]':
                        break
                    
                    try:
                        chunk = json.loads(data_text)
                        if "choices" in chunk and chunk["choices"]:
                            delta = chunk["choices"][0].get("delta", {})
                            if "content" in delta:
                                yield delta["content"]
                    except json.JSONDecodeError:
                        continue
    
    async def async_chat_completion(
        self,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> Dict:
        """
        Asynchronous chat completion
        
        Args:
            messages: Conversation message list
            **kwargs: Other parameters
        
        Returns:
            API response result
        """
        return await asyncio.to_thread(self.chat_completion, messages, **kwargs)
    
    def function_call(
        self,
        messages: List[Dict[str, str]],
        functions: List[Dict],
        model: str = None,
        temperature: float = 0.1
    ) -> Dict:
        """
        Function Calling feature
        
        Args:
            messages: Conversation message list
            functions: Function definition list
            model: Model name
            temperature: Sampling temperature
        
        Returns:
            API response result
        """
        tools = [{"type": "function", "function": func} for func in functions]
        
        return self.chat_completion(
            messages=messages,
            model=model,
            temperature=temperature,
            tools=tools,
            tool_choice="auto"
        )
    
    def web_search_chat(
        self,
        messages: List[Dict[str, str]],
        search_engine: str = "search_std",
        enable_search: bool = True,
        count: int = 10,
        model: str = None
    ) -> Dict:
        """
        Chat with Web search enabled
        
        Args:
            messages: Conversation message list
            search_engine: Search engine type
            enable_search: Whether to enable search
            count: Number of search results
            model: Model name
        
        Returns:
            API response result
        """
        tools = [{
            "type": "web_search",
            "enable": enable_search,
            "search_engine": search_engine,
            "count": count
        }]
        
        return self.chat_completion(
            messages=messages,
            model=model,
            tools=tools
        )
    
    # === Search Agent Dedicated Methods ===
    
    def extract_search_tags(
        self,
        user_query: str,
        schema_description: str = None,
        referenced_users: List[Dict] = None
    ) -> Dict:
        """
        Extract search tags - Search Agent dedicated
        
        Args:
            user_query: User search query
            schema_description: Database schema description
            referenced_users: Referenced user information
        
        Returns:
            Extracted tags and weight information
        """
        system_prompt = f"""
        You are a professional data analyst responsible for extracting keywords from user search queries and mapping them to database fields.
        
        Database Schema:
        {schema_description or "Schema description omitted"}
        
        Please extract tags from user queries and calculate weights, return in JSON format.
        """
        
        referenced_info = ""
        if referenced_users:
            referenced_info = "\n\nReferenced user information:\n"
            for i, user in enumerate(referenced_users, 1):
                referenced_info += f"{i}. {json.dumps(user, ensure_ascii=False)}\n"
        
        user_prompt = f"""
        User search query: {user_query}
        {referenced_info}
        
        Please extract tags and calculate weights, return in JSON format.
        """
        
        return self.json_chat(
            content=user_prompt,
            system_prompt=system_prompt,
            temperature=0.1
        )
    
    def generate_search_filters(
        self,
        user_query: str,
        referenced_users: List[Dict] = None
    ) -> Dict:
        """
        Generate search filter conditions - Search Agent dedicated
        
        Args:
            user_query: User search query
            referenced_users: Referenced user information
        
        Returns:
            Structured filter conditions
        """
        system_prompt = """
        You are a filter condition analyst for Qdrant vector database. Please extract clear, filterable conditions from user search queries.
        
        Only extract the following clearly defined fields:
        - gender: Gender ("male", "female", "男", "女")
        - age_range: Age range {"min": 20, "max": 30}
        - current_university: University name (convert to Chinese standard name)
        - province_id: Province (convert to Chinese province name)
        - city_id: City (convert to Chinese city name)
        - project_count_min: Minimum project count
        - institution_count_min: Minimum institutional experience
        
        If there is no clear filter information, return empty object {}
        """
        
        referenced_info = ""
        if referenced_users:
            referenced_info = "\n\nReferenced user information:\n"
            for i, user in enumerate(referenced_users, 1):
                referenced_info += f"{i}. {json.dumps(user, ensure_ascii=False)}\n"
        
        user_prompt = f"""
        User search query: {user_query}
        {referenced_info}
        
        Please extract clear filter conditions for precise database filtering. Return in JSON format.
        """
        
        return self.json_chat(
            content=user_prompt,
            system_prompt=system_prompt,
            temperature=0.1
        )
    
    def optimize_dense_query(
        self,
        user_query: str,
        referenced_users: List[Dict] = None
    ) -> str:
        """
        Optimize dense vector query - Search Agent dedicated
        
        Args:
            user_query: Original user query
            referenced_users: Referenced user information
        
        Returns:
            Optimized query description
        """
        system_prompt = """
        You are a search query optimizer. Please understand what kind of person the user is looking for and generate clear character descriptions for semantic matching.
        
        Guiding principles:
        1. Use natural, conversational language
        2. Focus on character traits, skills and personality
        3. Include both technical abilities and personal qualities
        4. Be specific but not overly complex
        5. Maintain humanity and relevance
        """
        
        referenced_info = ""
        if referenced_users:
            referenced_info = "\n\nReferenced user information:\n"
            for i, user in enumerate(referenced_users, 1):
                referenced_info += f"{i}. {json.dumps(user, ensure_ascii=False)}\n"
        
        user_prompt = f"""
        User query: {user_query}
        {referenced_info}
        
        Please describe the ideal candidate the user is looking for, generating clear and natural descriptions.
        """
        
        return self.simple_chat(
            content=user_prompt,
            system_prompt=system_prompt,
            temperature=0.3
        )
    
    def analyze_candidates(
        self,
        user_query: str,
        candidates: List[Dict],
        max_candidates: int = 3
    ) -> Dict:
        """
        Intelligent candidate analysis and selection - Search Agent dedicated
        
        Args:
            user_query: User search requirements
            candidates: Candidate list
            max_candidates: Maximum number of candidates to return
        
        Returns:
            Candidate selection decision
        """
        system_prompt = f"""
        You are a professional candidate matching analyst. Please select the top {max_candidates} candidates from the candidate list that best meet user requirements.
        
        Selection criteria:
        1. Skill matching degree
        2. Experience relevance
        3. Geographic location suitability
        4. Candidate diversity
        
        Return in JSON format, including:
        {{
            "action": "return_results" or "expand_search",
            "selected_candidates": [
                {{
                    "candidate_id": "Candidate ID",
                    "match_reason": "Matching reason",
                    "match_score": score(1-10)
                }}
            ],
            "analysis": "Analysis description"
        }}
        """
        
        candidates_info = "\n\nCandidate list:\n"
        for i, candidate in enumerate(candidates, 1):
            candidates_info += f"{i}. {json.dumps(candidate, ensure_ascii=False)}\n"
        
        user_prompt = f"""
        User requirements: {user_query}
        {candidates_info}
        
        Please select the top {max_candidates} candidates that best meet the requirements and return the decision.
        """
        
        return self.json_chat(
            content=user_prompt,
            system_prompt=system_prompt,
            temperature=0.2
        )
    
    def generate_match_reason(
        self,
        user_query: str,
        candidate_info: Dict,
        max_length: int = 50
    ) -> str:
        """
        Generate matching reason - Search Agent dedicated
        
        Args:
            user_query: User query
            candidate_info: Candidate information
            max_length: Maximum character length
        
        Returns:
            Matching reason description
        """
        system_prompt = f"""
        You are a professional talent matching expert. Please generate a concise matching reason for the candidate.
        
        Requirements:
        - No more than {max_length} characters
        - Highlight the most important matching points
        - Use third person
        - Concise and powerful language
        """
        
        user_prompt = f"""
        User query: {user_query}
        Candidate information: {json.dumps(candidate_info, ensure_ascii=False)}
        
        Please generate matching reason:
        """
        
        return self.simple_chat(
            content=user_prompt,
            system_prompt=system_prompt,
            temperature=0.3,
            max_tokens=100
        ).strip()
    
    def generate_intro_response(
        self,
        user_query: str,
        selected_users: List[Dict],
        language: str = "zh"
    ) -> str:
        """
        Generate introductory response - Search Agent dedicated
        
        Args:
            user_query: Original query
            selected_users: Selected user list
            language: Language code
        
        Returns:
            Introductory response content
        """
        if language == "zh":
            system_prompt = """
            You are a friendly AI assistant. Please generate a brief introductory response for the user's search results.
            The response should be friendly and natural, like the beginning of a conversation with the user.
            The response should be 50-80 characters, don't list users, just mention that relevant candidates have been found and invite the user to check them out.
            """
        else:
            system_prompt = """
            You are a friendly AI assistant. Generate a brief introductory response for the user's search results.
            The response should be friendly and natural, like the beginning of a conversation with the user.
            The response should be 50-80 characters, don't list users, just mention that relevant candidates have been found and invite the user to check them out.
            """
        
        users_summary = []
        for i, user in enumerate(selected_users, 1):
            user_info = user.get('user_info', user)
            match_reason = user.get('match_reason', 'relevant match')
            users_summary.append(f"{i}. {user_info.get('name', 'User')} - {match_reason}")
        
        users_summary_text = "\n".join(users_summary)
        
        user_prompt = f"""
        User search requirements: {user_query}
        
        Found matching users:
        {users_summary_text}
        
        Please generate a brief and friendly introductory response.
        """
        
        return self.simple_chat(
            content=user_prompt,
            system_prompt=system_prompt,
            temperature=0.7,
            max_tokens=150
        ).strip()
    
    # === Utility Methods ===
    
    def get_stats(self) -> Dict:
        """Get client statistics"""
        return {
            "request_count": self.request_count,
            "total_tokens": self.total_tokens,
            "total_cost": self.total_cost,
            "default_model": self.default_model,
            "api_key_masked": f"{self.api_key[:8]}***{self.api_key[-4:]}" if self.api_key else None
        }
    
    def reset_stats(self):
        """Reset statistics"""
        self.request_count = 0
        self.total_tokens = 0
        self.total_cost = 0
    
    def test_connection(self) -> bool:
        """Test API connection"""
        try:
            response = self.simple_chat("Test connection", max_tokens=10)
            return len(response) > 0
        except Exception:
            return False


# === Convenience Functions ===

def create_glm4_client(
    api_key: str = None,
    model: Union[str, GLM4Model] = GLM4Model.GLM_4_FLASH
) -> GLM4Client:
    """
    Convenience function to create GLM-4 client
    
    Args:
        api_key: API key
        model: Model to use
    
    Returns:
        GLM4Client instance
    """
    return GLM4Client(api_key=api_key, model=model)


def quick_chat(
    content: str,
    system_prompt: str = None,
    api_key: str = None,
    model: Union[str, GLM4Model] = GLM4Model.GLM_4_FLASH,
    temperature: float = 0.95
) -> str:
    """
    Quick chat convenience function
    
    Args:
        content: User input
        system_prompt: System prompt
        api_key: API key
        model: Model to use
        temperature: Sampling temperature
    
    Returns:
        Model reply
    """
    client = GLM4Client(api_key=api_key, model=model)
    return client.simple_chat(
        content=content,
        system_prompt=system_prompt,
        temperature=temperature
    )


def quick_json_chat(
    content: str,
    system_prompt: str = None,
    api_key: str = None,
    model: Union[str, GLM4Model] = GLM4Model.GLM_4_FLASH,
    temperature: float = 0.1
) -> Dict:
    """
    Quick JSON chat convenience function
    
    Args:
        content: User input
        system_prompt: System prompt
        api_key: API key
        model: Model to use
        temperature: Sampling temperature
    
    Returns:
        Parsed JSON object
    """
    client = GLM4Client(api_key=api_key, model=model)
    return client.json_chat(
        content=content,
        system_prompt=system_prompt,
        temperature=temperature
    )


# === Main Function for Testing ===

def main():
    """Test various functionalities of GLM-4 client"""
    print("GLM-4 API Client Test")
    print("=" * 50)
    
    try:
        # Create client
        client = GLM4Client()
        
        # 1. Basic chat test
        print("\n1. Basic chat test:")
        response = client.simple_chat("Hello, please introduce yourself")
        print(f"Reply: {response}")
        
        # 2. JSON format test
        print("\n2. JSON format test:")
        json_response = client.json_chat(
            "Please analyze this user query: looking for Python developers in Beijing",
            "You are a search analysis expert, please extract skills, location and other information"
        )
        print(f"JSON reply: {json.dumps(json_response, ensure_ascii=False, indent=2)}")
        
        # 3. Search Agent functionality test
        print("\n3. Search Agent functionality test:")
        filters = client.generate_search_filters("Looking for 25-year-old Tsinghua University Python engineers")
        print(f"Filter conditions: {json.dumps(filters, ensure_ascii=False, indent=2)}")
        
        optimized_query = client.optimize_dense_query("Looking for a product manager who knows Python")
        print(f"Optimized query: {optimized_query}")
        
        match_reason = client.generate_match_reason(
            "Looking for technical co-founder",
            {"name": "Zhang San", "skills": ["Python", "entrepreneurship"], "role": "CTO"}
        )
        print(f"Match reason: {match_reason}")
        
        # 4. Statistics
        print("\n4. Statistics:")
        stats = client.get_stats()
        print(f"Statistics: {json.dumps(stats, ensure_ascii=False, indent=2)}")
        
        print("\n✅ All tests completed!")
        
    except GLM4Exception as e:
        print(f"❌ GLM-4 API error: {e}")
        if e.error_code:
            print(f"Error code: {e.error_code}")
    except Exception as e:
        print(f"❌ Other error: {e}")


if __name__ == "__main__":
    main()