"""
project_idea_agent_with_unifuncs.py - Integration of UniFuncs deep research and creative generation API
"""

import os
import re
import json
import time
import asyncio
from typing import List, Dict, Any, Optional, Generator
from datetime import datetime
from dotenv import load_dotenv
from openai import AsyncOpenAI, OpenAI

# Load environment variables
load_dotenv()

class AdvancedSearchAgent:
    """Agent class using UniFuncs deep research and generation API"""
    
    def __init__(self):
        self.api_key = os.environ.get("UNIFUNCS_API_KEY")
        if not self.api_key:
            raise ValueError("UNIFUNCS_API_KEY environment variable is required")
            
        self.base_url = os.environ.get("UNIFUNCS_BASE_URL", 
                                      "https://api.unifuncs.com/deepresearch/v1")
        
        # Initialize client
        self.client = AsyncOpenAI(
            base_url=self.base_url,
            api_key=self.api_key
        )
        
    async def generate_project_ideas(self, query: str, language: str = None, stream: bool = False) -> Dict[str, Any]:
        """
        Generate project ideas using UniFuncs API
        
        Args:
            query: User's project query
            language: Language preference ('chinese' or 'english'), automatically detected if not specified
            stream: Whether to use streaming output
            
        Returns:
            Dictionary containing project ideas and metadata
        """
        start_time = time.time()
        
        # If language is not specified, detect query language
        if not language:
            # Simple language detection logic
            has_chinese = any('\u4e00' <= char <= '\u9fff' for char in query)
            language = 'chinese' if has_chinese else 'english'
        
        # Build prompts
        introduction = self._build_introduction(query)
        output_prompt = self._build_output_prompt(query, language)
        
        if stream:
            # Streaming response
            response_stream = await self._call_api_stream(query, introduction, output_prompt)
            return response_stream
        else:
            # Non-streaming response
            response = await self._call_api(query, introduction, output_prompt)
            
            # Process response
            processing_time = time.time() - start_time
            return self._process_response(response, query, processing_time)
        
    def _build_introduction(self, query: str) -> str:
        """Build the introduction part for UniFuncs API"""
        
        return f"""You are an advanced search and creative project idea generation agent. Your task is to find relevant information about "{query}" and generate 3 specific, actionable project ideas based on that information.

## Search Task
1. Search for up-to-date information about: "{query}"
2. Focus on finding diverse and high-quality sources:
   - Forums and community discussions
   - News articles and industry reports
   - Product showcases and case studies
   - Educational resources and tutorials
   - Real project examples and implementations
3. Filter out low-quality or blocked sources
4. Extract relevant content from these sources"""
        
    def _build_output_prompt(self, query: str, language: str) -> str:
        """Build the output_prompt part for UniFuncs API"""
        
        lang_condition = "Chinese" if language == "chinese" else "English"
        
        return f"""## Generation Task
Analyze the collected information and create 5 specific project ideas for: "{query}"

Generate 5 creative, actionable project ideas. Make them SPECIFIC with unique angles, not generic.

IMPORTANT: Respond in {lang_condition}. All fields must be in {lang_condition}.

# Output Format
CRITICAL: You must return a valid, well-formatted JSON object. The response MUST be parseable by Python's json.loads() function.

Your response must follow this JSON structure EXACTLY:

{{
  "search_summary": {{
    "query": "{query}",
    "sources_count": <integer>,
    "sources": [
      {{
        "url": "<source_url>",
        "title": "<source_title>",
        "relevance": <float between 0.1 and 1.0>
      }},
      ...
    ]
  }},
  "project_ideas": [
    {{
      "project_idea_title": "<specific title with target audience/technology>",
      "project_scope": "<team size like 'Small team (2-4 people)' or '小团队 (2-4人)'>",
      "description": "<what the project does + why it's interesting in ~30 words>",
      "key_features": [
        "<feature 1>",
        "<feature 2>",
        ...
      ],
      "estimated_timeline": "<like '4-6 weeks' or '4-6周'>",
      "difficulty_level": "<'Beginner', 'Intermediate', 'Advanced' or '初级', '中级', '高级'>",
      "required_skills": [
        "<skill 1>",
        "<skill 2>",
        ...
      ],
      "similar_examples": [
        "<url from sources>",
        ...
      ],
      "relevance_score": <float between 0.1 and 1.0>
    }},
    ...
  ]
}}

Return ONLY the valid JSON object without any additional text, markdown formatting, code blocks, or explanations. No ```json markers, just the raw JSON object.

Focus on practical, realistic projects that can be implemented by individuals or small teams."""

    async def _call_api(self, query: str, introduction: str, output_prompt: str) -> Dict[str, Any]:
        """Call UniFuncs API (non-streaming)"""
        try:
            response = await self.client.chat.completions.create(
                model="u1",
                messages=[{"role": "user", "content": query}],
                stream=False,
                extra_body={
                    "introduction": introduction,
                    "output_prompt": output_prompt
                }
            )
            # Check if response is valid
            if not response or not hasattr(response.choices[0].message, 'content') or not response.choices[0].message.content:
                error_msg = response.choices[0].message.content if (response and hasattr(response.choices[0].message, 'content')) else "Empty response"
                print(f"API returned error: {error_msg}")
                raise Exception(f"API returned invalid response: {error_msg}")
            return response
        except Exception as e:
            print(f"UniFuncs API error: {str(e)}")
            raise Exception(f"UniFuncs API error: {str(e)}")
                
    async def _call_api_stream(self, query: str, introduction: str, output_prompt: str) -> Generator:
        """Call UniFuncs API (streaming)"""
        try:
            print(f"🔄 Initiating API call: {datetime.now().isoformat()}")
            stream = await self.client.chat.completions.create(
                model="u1",
                messages=[{"role": "user", "content": query}],
                stream=True,
                extra_body={
                    "introduction": introduction,
                    "output_prompt": output_prompt,
                    "max_depth": 1, 
                }
            )
            print(f"✅ API call responded: {datetime.now().isoformat()}")
            return stream
        except Exception as e:
            raise Exception(f"UniFuncs API streaming error: {str(e)}")
                
    def _process_response(self, response: Any, query: str, processing_time: float) -> Dict[str, Any]:
        """Process API response and format as standard output format"""
        try:
            # Get the complete content
            content = response.choices[0].message.content
            
            # Try parsing JSON
            try:
                if "```json" in content:
                    start = content.find("```json") + 7
                    end = content.find("```", start)
                    if end != -1:
                        content = content[start:end].strip()
                elif "```" in content:
                    start = content.find("```") + 3
                    end = content.find("```", start)
                    if end != -1:
                        content = content[start:end].strip()
                
                # Parse JSON
                ideas_data = json.loads(content)
            except (json.JSONDecodeError, ValueError) as e:
                raise Exception(f"Failed to parse API response: {str(e)}")
            
            # 创建标准响应格式
            search_id = hash(query + str(datetime.now())) % 10000
            
            result = {
                "search_id": search_id,
                "original_query": query,
                "total_sources_found": len(ideas_data.get("search_summary", {}).get("sources", [])),
                "total_ideas_extracted": len(ideas_data.get("project_ideas", [])),
                "project_ideas": ideas_data.get("project_ideas", []),
                "processing_time_seconds": round(processing_time, 2),
                "created_at": datetime.now().isoformat(),
                "sources": ideas_data.get("search_summary", {}).get("sources", [])
            }
            
            return result
        except Exception as e:
            raise Exception(f"Error processing response: {str(e)}")

class AdvancedSearchAgentStreaming:
    """Streaming-capable UniFuncs deep search and generation API agent class"""
    
    def __init__(self):
        self.agent = AdvancedSearchAgent()
    
    async def generate_project_ideas_stream(self, query: str, user_id: int = None, include_reasoning: bool = False):
        """
        Generate project ideas using UniFuncs API and return progress as stream
        
        Args:
            query: User's project query
            user_id: User ID (optional)
            include_reasoning: Whether to include thinking process in output (default False)
            
        Yields:
            Dict events with progress updates
        """
        start_time = time.time()
        
        # Detect language
        has_chinese = any('\u4e00' <= char <= '\u9fff' for char in query)
        language = 'chinese' if has_chinese else 'english'
        
        # Build prompts
        introduction = self.agent._build_introduction(query)
        output_prompt = self.agent._build_output_prompt(query, language)
        
        # First send progress message
        yield {
            'type': 'progress',
            'step': 'start',
            'message': f'🔍 Starting deep research for: "{query}"',
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            # Get streaming response
            stream = await self.agent._call_api_stream(query, introduction, output_prompt)
            
            # Process thinking process and final results
            thinking = False
            thinking_content = []
            final_content = []
            thinking_chunk_count = 0
            searching = True

            async for chunk in stream:
                if hasattr(chunk.choices[0].delta, 'reasoning_content') and chunk.choices[0].delta.reasoning_content:
                    # Collect thinking content
                    if not thinking:
                        thinking = True
                        yield {
                            'type': 'progress',
                            'step': 'thinking',
                            'message': '🧠 Researching and analyzing information...',
                            'timestamp': datetime.now().isoformat()
                        }
                    
                    thinking_content.append(chunk.choices[0].delta.reasoning_content)
                    thinking_chunk_count += 1
                    
                    # If reasoning should be included, return this content block
                    if include_reasoning:
                        yield {
                            'type': 'reasoning',
                            'step': 'reasoning_content',
                            'content': chunk.choices[0].delta.reasoning_content,
                            'timestamp': datetime.now().isoformat()
                        }
                    
                    # Removed logic for sending updates after accumulating a certain amount of thinking content
                    # Only send progress update when thinking process starts
                        
                elif chunk.choices[0].delta.content:
                    # Collect final content
                    if thinking:
                        thinking = False
                        if searching:
                            searching = False
                            yield {
                                'type': 'progress',
                                'step': 'searching',
                                'message': '📊 Evaluating research data and creating project concepts...',
                                'timestamp': datetime.now().isoformat()
                            }
                        else:
                            yield {
                                'type': 'progress',
                                'step': 'generation',
                                'message': '🧩 Synthesizing findings into concrete project ideas...',
                                'timestamp': datetime.now().isoformat()
                            }
                    
                    final_content.append(chunk.choices[0].delta.content)
                    
                    # Return content block
                    yield {
                        'type': 'content',
                        'step': 'output_content',
                        'content': chunk.choices[0].delta.content,
                        'timestamp': datetime.now().isoformat()
                    }
            
            # Complete final content
            complete_content = ''.join(final_content)
            
            # Parse JSON content
            try:
                # Extract JSON content
                json_content = complete_content
                
                # Extract from code blocks
                if "```json" in complete_content:
                    start = complete_content.find("```json") + 7
                    end = complete_content.find("```", start)
                    if end != -1:
                        json_content = complete_content[start:end].strip()
                        print(f"Extracted from markdown JSON block: {len(json_content)} characters")
                    else:
                        print("Warning: Found ```json but no closing ``` - using complete content")
                elif "```" in complete_content:
                    start = complete_content.find("```") + 3
                    end = complete_content.find("```", start)
                    if end != -1:
                        potential_json = complete_content[start:end].strip()
                        # Check if it looks like JSON
                        if potential_json.startswith('{') or potential_json.startswith('['):
                            json_content = potential_json
                            print(f"Extracted from generic code block: {len(json_content)} characters")
                
                # Clean JSON content - handle common issues
                json_content = json_content.strip()
                
                # Ensure content starts with { and ends with }
                if not json_content.startswith('{'):
                    first_brace = json_content.find('{')
                    if first_brace != -1:
                        json_content = json_content[first_brace:]
                        print(f"Fix: Removed {first_brace} characters before JSON start")
                
                if not json_content.endswith('}'):
                    last_brace = json_content.rfind('}')
                    if last_brace != -1:
                        json_content = json_content[:last_brace+1]
                        print(f"Fix: Removed content after JSON end")
                
                # Handle common JSON errors
                # Fix trailing commas
                import re  # Ensure re module is imported before use
                json_content = re.sub(r',(\s*[}\]])', r'\1', json_content)
                
                # Check if empty
                if not json_content.strip():
                    raise Exception("Extracted JSON content is empty")
                
                # Parse JSON
                ideas_data = json.loads(json_content)
                
                # Process search summary
                search_summary = ideas_data.get("search_summary", {})
                sources = search_summary.get("sources", [])
                sources_count = len(sources)
                
                yield {
                    'type': 'progress',
                    'step': 'search_complete',
                    'message': f'✅ Found {sources_count} relevant sources',
                    'data': {'sources_count': sources_count},
                    'timestamp': datetime.now().isoformat()
                }
                
                # Process project ideas
                project_ideas = ideas_data.get("project_ideas", [])
                for i, idea in enumerate(project_ideas):
                    yield {
                        'type': 'idea_generated',
                        'step': 'idea_generation',
                        'message': f'✨ Generated idea {i+1}: {idea.get("project_idea_title", "Unknown")}',
                        'data': idea,
                        'timestamp': datetime.now().isoformat()
                    }
                
                # Final result
                processing_time = time.time() - start_time
                search_id = hash(query + str(datetime.now())) % 10000
                
                final_result = {
                    "search_id": search_id,
                    "original_query": query,
                    "total_sources_found": sources_count,
                    "total_ideas_extracted": len(project_ideas),
                    "project_ideas": project_ideas,
                    "processing_time_seconds": round(processing_time, 2),
                    "created_at": datetime.now().isoformat(),
                    "sources": sources,
                    "thinking_chunks_count": thinking_chunk_count
                }
                
                yield {
                    'type': 'result',
                    'step': 'completion',
                    'message': f'🎉 Generated {len(project_ideas)} project ideas in {processing_time:.1f}s',
                    'data': final_result,
                    'timestamp': datetime.now().isoformat()
                }
                
            except json.JSONDecodeError as e:
                # Try to further fix JSON content
                error_pos = int(str(e).split('char ')[-1]) if 'char ' in str(e) else 0
                
                # Record error information
                error_message = f"JSON parsing error: {str(e)}"
                
                # Extract content around the error
                error_context_start = max(0, error_pos - 50)
                error_context_end = min(len(json_content), error_pos + 50)
                error_context = f"...{json_content[error_context_start:error_pos]}[ERROR POSITION]{json_content[error_pos:error_context_end]}..."
                
                # Try additional JSON fixing methods
                fixed_json = None
                try:
                    # 1. Try removing content before and after the error
                    if error_pos > 0:
                        # Find the nearest closing brace after error position
                        next_close_brace = json_content.find('}', error_pos)
                        if next_close_brace != -1:
                            fixed_json = json_content[:next_close_brace+1]
                            print(f"Trying fix method 1: Truncate to position {next_close_brace+1}")
                            ideas_data = json.loads(fixed_json)
                            print("✅ JSON fix successful! (Method 1)")
                except Exception:
                    try:
                        # 2. Check for escape character issues
                        fixed_json = json_content.replace('\\"', '"').replace('\\\\', '\\')
                        ideas_data = json.loads(fixed_json)
                        print("✅ JSON fix successful! (Method 2 - escape character fix)")
                    except Exception:
                        try:
                            # 3. Try using regex to find valid JSON objects
                            import re
                            json_pattern = r'({[^{}]*({[^{}]*})*[^{}]*})'
                            matches = re.findall(json_pattern, json_content)
                            if matches:
                                for potential_json in matches:
                                    if isinstance(potential_json, tuple):
                                        potential_json = potential_json[0]
                                    try:
                                        ideas_data = json.loads(potential_json)
                                        fixed_json = potential_json
                                        print("✅ JSON fix successful! (Method 3 - regex extraction)")
                                        break
                                    except:
                                        continue
                        except Exception:
                            # All fixing methods failed, return original error
                            fixed_json = None
                
                if fixed_json:
                    # Successfully parsed fixed JSON, continue processing
                    search_summary = ideas_data.get("search_summary", {})
                    sources = search_summary.get("sources", [])
                    sources_count = len(sources)
                    
                    # Continue normal flow...
                    yield {
                        'type': 'progress',
                        'step': 'search_complete',
                        'message': f'✅ Found {sources_count} relevant sources (after JSON fix)',
                        'data': {'sources_count': sources_count},
                        'timestamp': datetime.now().isoformat()
                    }
                    
                    # Process project ideas
                    project_ideas = ideas_data.get("project_ideas", [])
                    # Continue with original processing...
                else:
                    # Could not fix, report error
                    yield {
                        'type': 'error',
                        'step': 'json_parsing',
                        'message': f'❌ Failed to parse response JSON: {error_message}',
                        'error': str(e),
                        'error_context': error_context,
                        'raw_content': complete_content[:500] + "..." if len(complete_content) > 500 else complete_content,
                        'timestamp': datetime.now().isoformat()
                    }
                    raise
                
        except Exception as e:
            yield {
                'type': 'error',
                'step': 'generation_failed',
                'message': f'❌ Generation failed: {str(e)}',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
            raise


# Test code - Standard version
async def test_advanced_search():
    agent = AdvancedSearchAgent()
    response = await agent.generate_project_ideas("开发一个基于AI的健康饮食建议APP")
    
    print(f"\n===== Generation Results =====")
    print(f"Found {response['total_sources_found']} relevant sources")
    print(f"Generated {response['total_ideas_extracted']} project ideas")
    print(f"Processing time: {response['processing_time_seconds']} seconds")
    
    for i, idea in enumerate(response['project_ideas']):
        print(f"\n----- Idea {i+1}: {idea['project_idea_title']} -----")
        print(f"Description: {idea['description']}")
        print(f"Key features: {', '.join(idea['key_features'][:3])}...")
        print(f"Difficulty: {idea['difficulty_level']}")
        print(f"Timeline: {idea['estimated_timeline']}")
    
    return response


# Test code - Streaming version
async def test_advanced_search_stream():
    agent = AdvancedSearchAgentStreaming()
    
    print("Starting streaming generation of project ideas...")
    
    async for event in agent.generate_project_ideas_stream("开发一个基于AI的健康饮食建议APP"):
        if event['type'] == 'progress':
            print(f"Progress: {event['message']}")
        elif event['type'] == 'idea_generated':
            print(f"New idea: {event['data']['project_idea_title']}")
        elif event['type'] == 'result':
            print(f"Streaming generation complete!")
    
    return "Streaming generation complete!"


# Test code - Streaming version with reasoning process
async def test_advanced_search_stream_with_reasoning():
    agent = AdvancedSearchAgentStreaming()
    
    print("Starting streaming generation of project ideas (including thinking process)...")
    
    async for event in agent.generate_project_ideas_stream("开发一个基于AI的健康饮食建议APP", include_reasoning=True):
        if event['type'] == 'progress':
            print(f"Progress: {event['message']}")
        elif event['type'] == 'reasoning':
            # Only print the first 100 characters of the thinking process
            content_preview = event['content'][:100] + "..." if len(event['content']) > 100 else event['content']
            print(f"Thinking: {content_preview}")
        elif event['type'] == 'idea_generated':
            print(f"New idea: {event['data']['project_idea_title']}")
        elif event['type'] == 'result':
            print(f"Streaming generation complete!")
    
    return "Streaming generation complete!"


# Test underlying API (directly view thinking process)
async def test_raw_api_stream():
    agent = AdvancedSearchAgent()
    
    # Build prompts
    introduction = agent._build_introduction("开发一个基于AI的健康饮食建议APP")
    output_prompt = agent._build_output_prompt("开发一个基于AI的健康饮食建议APP", "chinese")
    
    # Call API
    try:
        client = OpenAI(
            base_url=agent.base_url,
            api_key=agent.api_key
        )
        
        print(f"Connecting to API: {agent.base_url}")
        print(f"API key: {agent.api_key[:6]}...{agent.api_key[-4:]}")
        
        stream = client.chat.completions.create(
            model="u1",
            messages=[{"role": "user", "content": "开发一个基于AI的健康饮食建议APP"}],
            stream=True,
            extra_body={
                "introduction": introduction,
                "output_prompt": output_prompt,
                "max_depth": 1
            }
        )
        
        thinking = False
        content_received = False
        
        for chunk in stream:
            content_received = True
            if hasattr(chunk.choices[0].delta, 'reasoning_content') and chunk.choices[0].delta.reasoning_content:
                if not thinking:
                    print("<Thinking Process>\n")
                    thinking = True
                print(chunk.choices[0].delta.reasoning_content, end="")
            elif chunk.choices[0].delta.content:
                if thinking:
                    print("\n</Thinking Process>\n")
                    thinking = False
                print(chunk.choices[0].delta.content or "", end="")
        
        if not content_received:
            print("Warning: API did not return any content")
    except Exception as e:
        print(f"Error: {str(e)}")
        print("API call failed. Please check the following possible issues:")
        print("1. Is the API key correct?")
        print("2. Is the API service available?")
        print("3. Is the network connection working properly?")
        print("4. Is the API base URL correct?")

# Test code - Save all asynchronous messages to file
async def test_stream_to_file():
    agent = AdvancedSearchAgentStreaming()
    output_file_path = "project_ideas_stream_output.txt"
    json_file_path = f"api_responses_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.json"
    
    print(f"Saving all API responses to file...")
    
    # List to collect all API responses
    all_api_responses = []
    
    with open(output_file_path, "w", encoding="utf-8") as f:
        f.write("=== Project Idea Generation Stream Output ===\n\n")
        f.write(f"Query: Develop an AI-based health diet recommendation app\n")
        f.write(f"Time: {datetime.now().isoformat()}\n\n")
        f.write("=== Recording all events ===\n\n")
        
        reasoning_content = []
        output_content = []
        thinking_content_with_progress = []  # Store the actual thinking content flow displayed in the UI (API returned thinking flow plus progress)
        progress_messages = []  # Store progress messages
        has_error = False
        event_count = 0
        
        try:
            async for event in agent.generate_project_ideas_stream("开发一个基于AI的健康饮食建议APP", include_reasoning=True):
                event_count += 1
                # Collect API responses
                all_api_responses.append(event)
                
                # Record complete information for each event
                f.write(f"Event #{event_count} - Type: {event['type']}\n")
                if 'step' in event:
                    f.write(f"Step: {event['step']}\n")
                if 'message' in event:
                    f.write(f"Message: {event['message']}\n")
                    print(f"Event #{event_count}: {event['message']}")
                    # If it's a progress message, record it to the progress list
                    if event['type'] == 'progress':
                        progress_messages.append({
                            'message': event['message'],
                            'timestamp': event.get('timestamp', datetime.now().isoformat())
                        })
                        # Also add to thinking content flow, simulating user interface display
                        thinking_content_with_progress.append(f"\n--- {event['message']} ---\n")
                if 'content' in event:
                    content_preview = event['content'][:100] + "..." if len(event['content']) > 100 else event['content']
                    f.write(f"Content fragment: {content_preview}\n")
                    if event['type'] == 'reasoning':
                        reasoning_content.append(event['content'])
                        # Add thinking content to thinking content flow
                        thinking_content_with_progress.append(event['content'])
                    elif event['type'] == 'content':
                        output_content.append(event['content'])
                if 'data' in event:
                    f.write(f"Data: {json.dumps(event['data'], ensure_ascii=False)[:200]}...\n" if len(json.dumps(event['data'], ensure_ascii=False)) > 200 else f"Data: {json.dumps(event['data'], ensure_ascii=False)}\n")
                if 'timestamp' in event:
                    f.write(f"Timestamp: {event['timestamp']}\n")
                f.write("\n" + "-"*50 + "\n\n")
                
            # Record completion information
            f.write("\n=== Generation Complete ===\n\n")
            f.write(f"Total events: {event_count}\n")
            f.write(f"Thinking content blocks: {len(reasoning_content)}\n")
            f.write(f"Output content blocks: {len(output_content)}\n")
            f.write(f"Progress messages: {len(progress_messages)}\n\n")
            
            # Record complete thinking content
            f.write("=== Complete Thinking Content ===\n\n")
            f.write(''.join(reasoning_content))
            f.write("\n\n")
            
            # Record complete output content
            f.write("=== Complete Output Content ===\n\n")
            output_text = ''.join(output_content)
            f.write(output_text)
            f.write("\n\n")
            
            # Record complete thinking content flow (with progress)
            f.write("=== User Interface Thinking Content Flow (with progress info) ===\n\n")
            thinking_flow = ''.join(thinking_content_with_progress)
            f.write(thinking_flow)
            f.write("\n\n")
            
            # Save thinking content flow to separate file
            thinking_flow_file = f"thinking_flow_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.txt"
            with open(thinking_flow_file, "w", encoding="utf-8") as tf:
                tf.write(f"=== User Interface Thinking Content Flow (with progress info) ===\n")
                tf.write(f"Query: Develop an AI-based health diet recommendation app\n")
                tf.write(f"Time: {datetime.now().isoformat()}\n\n")
                tf.write(thinking_flow)
            
            f.write(f"Thinking content flow saved separately to: {thinking_flow_file}\n\n")
            
            # Try to parse JSON
            f.write("=== Trying to Parse JSON ===\n\n")
            try:
                json_content = output_text
                if "```json" in output_text:
                    start = output_text.find("```json") + 7
                    end = output_text.find("```", start)
                    if end != -1:
                        json_content = output_text[start:end].strip()
                        f.write(f"Extracted from ```json code block: {len(json_content)} characters\n")
                elif "```" in output_text:
                    start = output_text.find("```") + 3
                    end = output_text.find("```", start)
                    if end != -1:
                        json_content = output_text[start:end].strip()
                        f.write(f"Extracted from generic code block: {len(json_content)} characters\n")
                
                # Clean JSON content
                import re
                json_content = json_content.strip()
                if not json_content.startswith('{'):
                    first_brace = json_content.find('{')
                    if first_brace != -1:
                        json_content = json_content[first_brace:]
                        f.write(f"Fix: Removed {first_brace} characters before JSON start\n")
                
                if not json_content.endswith('}'):
                    last_brace = json_content.rfind('}')
                    if last_brace != -1:
                        json_content = json_content[:last_brace+1]
                        f.write(f"Fix: Removed content after JSON end\n")
                
                # Fix common JSON errors
                json_content = re.sub(r',(\s*[}\]])', r'\1', json_content)
                
                # Parse JSON
                ideas_data = json.loads(json_content)
                f.write(f"JSON parsing successful!\n")
                f.write(f"Number of project ideas: {len(ideas_data.get('project_ideas', []))}\n")
                for i, idea in enumerate(ideas_data.get('project_ideas', [])):
                    f.write(f"\nIdea #{i+1}: {idea.get('project_idea_title', 'Unknown')}\n")
                
            except json.JSONDecodeError as e:
                f.write(f"JSON parsing failed: {str(e)}\n")
                error_pos = int(str(e).split('char ')[-1]) if 'char ' in str(e) else 0
                error_context_start = max(0, error_pos - 50)
                error_context_end = min(len(json_content), error_pos + 50)
                f.write(f"Content near error position: ...{json_content[error_context_start:error_pos]}[ERROR POSITION]{json_content[error_pos:error_context_end]}...\n")
                has_error = True
                
        except Exception as e:
            f.write(f"\n❌ Error: {str(e)}\n")
            import traceback
            f.write(traceback.format_exc())
            print(f"\n❌ Exception: {str(e)}")
            has_error = True
    
    # Save all API responses to JSON file
    with open(json_file_path, 'w', encoding='utf-8') as json_file:
        json.dump(all_api_responses, json_file, ensure_ascii=False, indent=2)
    
    print(f"\nStream generation complete! {'Error occurred' if has_error else 'Success'}")
    print(f"Results saved to file: {output_file_path}")
    print(f"All responses saved to file: {json_file_path}")
    
    return output_file_path


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "stream":
            print("Running stream version test...")
            asyncio.run(test_advanced_search_stream())
        elif sys.argv[1] == "stream_reasoning":
            print("Running stream version with reasoning test...")
            asyncio.run(test_advanced_search_stream_with_reasoning())
        elif sys.argv[1] == "file":
            print("Saving all API responses to file...")
            asyncio.run(test_stream_to_file())
        elif sys.argv[1] == "raw":
            print("Running raw API test...")
            asyncio.run(test_raw_api_stream())
        else:
            print(f"Unknown parameter: {sys.argv[1]}")
            print("Available parameters: stream, stream_reasoning, file, raw")
    else:
        print("Running standard version test...")
        asyncio.run(test_advanced_search())
