"""
project_idea_agent_with_unifuncs.py - Fixed UniFuncs integration
"""

import os
import json
import time
import asyncio
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from openai import AsyncOpenAI

# Load environment variables
load_dotenv()

class AdvancedSearchAgent:
    """Agent class using UniFuncs deep research and generation API"""
    
    def __init__(self):
        self.api_key = os.environ.get("UNIFUNCS_API_KEY")
        if not self.api_key:
            raise ValueError("UNIFUNCS_API_KEY environment variable is required")
        
        # The OpenAI client automatically adds /v1 to the base URL
        self.base_url = os.environ.get("UNIFUNCS_BASE_URL", "https://api.unifuncs.com/deepresearch")
        
        # Create the AsyncOpenAI client
        self.client = AsyncOpenAI(
            base_url=self.base_url, 
            api_key=self.api_key,
            timeout=30.0
        )
        
        print(f"✅ UniFuncs agent initialized")
        print(f"   Base URL: {self.base_url}")
        print(f"   API Key: {'*' * (len(self.api_key) - 4) + self.api_key[-4:]}")

    async def generate_project_ideas(self, query: str, language: str = None, stream: bool = False) -> Dict[str, Any]:
        """Generate project ideas using UniFuncs API"""
        start_time = time.time()
        
        try:
            # Create the prompt in the format that works
            prompt = f"""Generate 3-5 innovative project ideas about: {query}

Return exactly a JSON array with this structure:
[
  {{
    "title": "Project Name",
    "description": "Detailed description of the project",
    "difficulty": "Beginner/Intermediate/Advanced", 
    "estimated_time": "1-2 weeks",
    "tags": ["relevant", "tags"]
  }}
]

Make the ideas practical, innovative, and well-detailed."""

            print(f"🚀 Generating ideas for: {query}")
            print(f"   Using base URL: {self.base_url}/v1")
            
            # Make the API call
            response = await self.client.chat.completions.create(
                model="deepresearch",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=1500,
                timeout=20
            )
            
            processing_time = time.time() - start_time
            
            print(f"✅ API call completed in {processing_time:.2f}s")
            print(f"   Model: {response.model}")
            print(f"   Usage: {response.usage}")
            
            # Process the response
            if response.choices and response.choices[0].message:
                content = response.choices[0].message.content.strip()
                print(f"   Content length: {len(content)}")
                
                # Parse JSON from the response
                ideas = self._extract_ideas_from_content(content)
                
                return {
                    "ideas": ideas,
                    "query": query,
                    "processing_time": processing_time,
                    "success": len(ideas) > 0
                }
            else:
                print("❌ No content in response")
                return {
                    "ideas": [],
                    "query": query,
                    "processing_time": processing_time,
                    "success": False,
                    "error": "No content in API response"
                }
                
        except asyncio.TimeoutError:
            print("⏰ API call timed out")
            return {
                "ideas": [],
                "query": query,
                "processing_time": time.time() - start_time,
                "success": False,
                "error": "API call timed out"
            }
        except Exception as e:
            print(f"❌ Error generating ideas: {e}")
            return {
                "ideas": [],
                "query": query,
                "processing_time": time.time() - start_time,
                "success": False,
                "error": str(e)
            }

    def _extract_ideas_from_content(self, content: str) -> list:
        """Extract project ideas from API response content"""
        try:
            print(f"📝 Processing content: {content[:200]}...")
            
            # First try to find JSON array
            start_idx = content.find('[')
            end_idx = content.rfind(']') + 1
            
            if start_idx >= 0 and end_idx > start_idx:
                json_str = content[start_idx:end_idx]
                print(f"🔍 Found JSON array: {json_str[:100]}...")
                ideas = json.loads(json_str)
                print(f"✅ Parsed {len(ideas)} ideas from array")
                return ideas
            
            # Try to find JSON object with ideas key
            start_idx = content.find('{')
            end_idx = content.rfind('}') + 1
            
            if start_idx >= 0 and end_idx > start_idx:
                json_str = content[start_idx:end_idx]
                print(f"🔍 Found JSON object: {json_str[:100]}...")
                data = json.loads(json_str)
                
                if isinstance(data, dict) and 'ideas' in data:
                    ideas = data['ideas']
                    print(f"✅ Parsed {len(ideas)} ideas from object")
                    return ideas
            
            # Try parsing entire content as JSON
            print("🔄 Trying to parse entire content as JSON...")
            data = json.loads(content)
            
            if isinstance(data, list):
                print(f"✅ Content is JSON array with {len(data)} items")
                return data
            elif isinstance(data, dict) and 'ideas' in data:
                ideas = data['ideas']
                print(f"✅ Content is JSON object with {len(ideas)} ideas")
                return ideas
            else:
                print(f"⚠️ JSON parsed but no ideas found: {type(data)}")
                return []
                
        except json.JSONDecodeError as e:
            print(f"❌ JSON parsing failed: {e}")
            print(f"   Content: {content[:300]}...")
            return []
        except Exception as e:
            print(f"❌ Error extracting ideas: {e}")
            return []

# For backward compatibility
class AdvancedSearchAgentStreaming:
    """Placeholder for streaming functionality"""
    async def generate_project_ideas_stream(self, query, user_id, include_reasoning=True):
        yield {"type": "progress", "step": "start", "message": "Streaming started"}
        yield {"type": "done", "ideas": []}
