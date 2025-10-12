"""
Project Idea Generation Agent
Takes user queries and generates creative, up-to-date project ideas using web search and AI analysis.
"""

import os
import time
import json
import random
import re
import requests
import asyncio
import aiohttp
from datetime import datetime
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

# Crawl4AI Python library
try:
    from crawl4ai import AsyncWebCrawler
    CRAWL4AI_AVAILABLE = True
except ImportError:
    CRAWL4AI_AVAILABLE = False

# Fallback scraping libraries
try:
    from bs4 import BeautifulSoup
    BEAUTIFULSOUP_AVAILABLE = True
except ImportError:
    BEAUTIFULSOUP_AVAILABLE = False

# Load environment variables
load_dotenv()

# Import for unified quota management (using membership system)
from services.membership_service import MembershipService

class ProjectIdeaAgent:
    """Agent for generating creative project ideas from user queries"""
    
    def __init__(self):
        # Load API keys from environment
        self.searchapi_key = os.environ.get("SEARCHAPI_KEY")
        self.deepseek_api_key = os.environ.get("DEEPSEEK_API_KEY_AGENT")
        
        # Don't validate at initialization - only when actually used
        # This allows the server to start even if these APIs aren't configured
        
        # API endpoints
        self.searchapi_url = "https://www.searchapi.io/api/v1/search"
        self.deepseek_url = "https://api.deepseek.com/v1/chat/completions"
        
        # Search engines to rotate through
        self.search_engines = ["baidu", "google"]
    
    def _test_deepseek_connection(self) -> bool:
        """Test Deepseek API connection with a simple request"""
        try:
            headers = {
                "Authorization": f"Bearer {self.deepseek_api_key}",
                "Content-Type": "application/json"
            }
            
            test_data = {
                "model": "deepseek-chat",
                "messages": [
                    {"role": "user", "content": "Say 'test' in JSON format: {\"result\": \"test\"}"}
                ],
                "temperature": 0.1,
                "max_tokens": 50
            }
            
            response = requests.post(self.deepseek_url, headers=headers, json=test_data, timeout=10)
            
            if response.status_code == 200:
                print("✅ Deepseek API connection: OK")
                return True
            else:
                print(f"⚠️  Deepseek API test failed: {response.status_code}")
                print(f"Response: {response.text[:200]}")
                return False
                
        except Exception as e:
            print(f"⚠️  Deepseek API test error: {str(e)}")
            return False
    
    def _detect_language(self, text: str) -> str:
        """
        Detect if text is primarily Chinese or English
        
        Args:
            text: Input text to analyze
            
        Returns:
            'chinese' if text contains Chinese characters, 'english' otherwise
        """
        import re
        
        # Check for Chinese characters (CJK Unified Ideographs)
        # This pattern covers most common Chinese characters
        chinese_pattern = r'[\u4e00-\u9fff]'
        chinese_matches = re.findall(chinese_pattern, text)
        
        # Count total characters (excluding spaces)
        non_space_text = re.sub(r'\s', '', text)
        total_chars = len(non_space_text)
        chinese_char_count = len(chinese_matches)
        
        # If any Chinese characters are found and they make up more than 30% of content
        if total_chars > 0 and chinese_char_count > 0:
            ratio = chinese_char_count / total_chars
            if ratio > 0.3:  # More than 30% Chinese characters
                return 'chinese'
        
        return 'english'
    
    def generate_project_ideas(self, query: str, user_id: int) -> Dict[str, Any]:
        """
        Main function to generate project ideas from user query
        
        Args:
            query: User's rough project query
            user_id: User ID for logging and tracking
            
        Returns:
            Dict containing project ideas and metadata in specified JSON format
        """
        start_time = time.time()
        
        # Note: Quota checking is now handled in the router via MembershipService
        
        try:
            # Step 1: Refine query into search prompts
            generated_prompts = self.refine_query(query)
            
            # Step 2: Search web for each prompt
            all_urls = []
            prompt_results = []
            
            for i, prompt in enumerate(generated_prompts):
                engine = self.search_engines[i % len(self.search_engines)]
                urls = self.search_web(prompt, engine)
                all_urls.extend(urls[:5])  # Limit to top 5 per search
                
                prompt_results.append({
                    "prompt": prompt,
                    "engine": engine,
                    "results_count": len(urls)
                })
            
            # Step 3: Scrape content from URLs
            scraped_content = self.scrape_pages(all_urls)
            total_sources_found = len(scraped_content)
            
            # Step 4: Generate project ideas from scraped content
            project_ideas, total_ideas_extracted = self.generate_ideas(scraped_content, query)
            
            # Step 5: Compile response
            processing_time = time.time() - start_time
            search_id = random.randint(1000, 9999)
            
            response = {
                "search_id": search_id,
                "original_query": query,
                "generated_prompts": prompt_results,
                "total_sources_found": total_sources_found,
                "total_ideas_extracted": total_ideas_extracted,
                "project_ideas": project_ideas,
                "processing_time_seconds": round(processing_time, 2),
                "created_at": datetime.now().isoformat()
            }
            
            # Usage logging is now handled in the router via MembershipService.log_usage()
            
            return response
            
        except Exception as e:
            # Re-raise any API errors without fallbacks
            raise Exception(f"Project idea generation failed: {str(e)}")
    
    def refine_query(self, query: str) -> List[str]:
        """
        Use Deepseek API to generate 3-5 search prompts based on the query
        
        Args:
            query: Original user query
            
        Returns:
            List of refined search prompts
        """
        prompt = f"""Generate 3-5 creative search queries to find diverse project ideas related to: "{query}". 
        
IMPORTANT: If the query is in Chinese, generate Chinese search terms. If it's in English, generate English search terms. Match the language of the input query.
        
Focus on finding content from:
        - Forums and community discussions
        - News articles and industry reports  
        - Product showcases and case studies
        - Educational resources and tutorials
        - Real project examples and implementations
        
        The projects can be software/tech, physical products, business ventures, research, creative works, or any other type of project.
        
        Each query should be specific, search-engine optimized, and designed to find different perspectives and approaches.
        Avoid queries that would primarily return websites blocked by Chinese firewall (like Google, Facebook, YouTube, Reddit, Medium, etc.).
        
        Return only the queries as a JSON array of strings."""
        
        headers = {
            "Authorization": f"Bearer {self.deepseek_api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 500
        }
        
        try:
            response = requests.post(self.deepseek_url, headers=headers, json=data, timeout=30)
            
            # Debug: Print response details
            print(f"Deepseek API Status Code: {response.status_code}")
            print(f"Deepseek API Response Headers: {dict(response.headers)}")
            print(f"Deepseek API Response Content: {response.text[:500]}...")
            
            response.raise_for_status()
            
            if not response.text.strip():
                raise Exception("Empty response from Deepseek API")
            
            result = response.json()
            
            if "choices" not in result or not result["choices"]:
                raise Exception(f"Invalid Deepseek response format: {result}")
            
            content = result["choices"][0]["message"]["content"]
            
            if not content.strip():
                raise Exception("Empty content from Deepseek API")
            
            print(f"Deepseek returned content: {content}")
            
            # Extract JSON from markdown code blocks if present
            json_content = content
            if '```json' in content:
                # Find the JSON content between ```json and ```
                start = content.find('```json') + 7
                end = content.find('```', start)
                if end != -1:
                    json_content = content[start:end].strip()
                    print(f"Extracted JSON from markdown: {json_content}")
            
            # Parse JSON response
            search_prompts = json.loads(json_content)
            return search_prompts
            
        except json.JSONDecodeError as e:
            raise Exception(f"Deepseek query refinement failed - invalid JSON response: {str(e)}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Deepseek API connection failed during query refinement: {str(e)}")
        except Exception as e:
            raise Exception(f"Query refinement failed: {str(e)}")
    
    def _filter_chinese_blocked_urls(self, urls: List[str]) -> List[str]:
        """
        Filter out URLs that might be blocked by Chinese firewall using Deepseek API
        
        Args:
            urls: List of URLs to check
            
        Returns:
            List of URLs that are likely accessible in China
        """
        if not urls:
            return urls
        
        # Common domains known to be blocked in China
        blocked_domains = [
            'facebook.com', 'twitter.com', 'youtube.com', 'instagram.com',
            'google.com', 'gmail.com', 'reddit.com', 'pinterest.com',
            'linkedin.com', 'snapchat.com', 'tiktok.com', 'whatsapp.com',
            'telegram.org', 'discord.com', 'medium.com', 'quora.com'
        ]
        
        # Quick filter for known blocked domains
        filtered_urls = []
        for url in urls:
            is_blocked = any(domain in url.lower() for domain in blocked_domains)
            if not is_blocked:
                filtered_urls.append(url)
        
        return filtered_urls
    
    def search_web(self, prompt: str, engine: str) -> List[str]:
        """
        Use SearchAPI.io to search for URLs
        
        Args:
            prompt: Search query
            engine: Search engine (bing, baidu, google)
            
        Returns:
            List of URLs from search results
        """
        params = {
            "api_key": self.searchapi_key,
            "engine": engine,
            "q": prompt,
            "num": 10
        }
        
        try:
            response = requests.get(self.searchapi_url, params=params, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            urls = []
            
            # Extract URLs from different engines' response formats
            if engine == "google":
                organic_results = result.get("organic_results", [])
                urls = [item.get("link") for item in organic_results if item.get("link")]
            elif engine == "baidu":
                organic_results = result.get("organic_results", [])
                urls = [item.get("link") for item in organic_results if item.get("link")]
            
            # Filter out URLs that might be blocked by Chinese firewall
            filtered_urls = self._filter_chinese_blocked_urls(urls)
            
            return filtered_urls[:10]  # Limit to top 10
            
        except Exception as e:
            raise Exception(f"Web search failed for {engine}: {str(e)}")
    
    def scrape_pages(self, urls: List[str]) -> List[str]:
        """
        Use Crawl4AI Python library to extract text content from URLs
        
        Args:
            urls: List of URLs to scrape
            
        Returns:
            List of cleaned text snippets
        """
        if CRAWL4AI_AVAILABLE:
            print("Using Crawl4AI Python library for web scraping")
            try:
                import asyncio
                return asyncio.run(self._scrape_with_crawl4ai(urls))
            except Exception as e:
                print(f"Crawl4AI failed, falling back to requests-based scraping: {str(e)}")
        else:
            print("Crawl4AI not available, using requests-based scraping")
        
        # Fallback to requests-based scraping
        return self._scrape_with_requests(urls)
    
    async def _scrape_with_crawl4ai(self, urls: List[str]) -> List[str]:
        """Scrape using Crawl4AI async library with parallel processing"""
        from crawl4ai import AsyncWebCrawler
        import asyncio
        scraped_content = []
        
        async def scrape_single_url(crawler, url):
            """Scrape a single URL"""
            try:
                print(f"Crawling {url}...")
                result = await crawler.arun(
                    url=url,
                    word_count_threshold=10,
                    extraction_strategy="NoExtractionStrategy",
                    chunking_strategy="RegexChunking",
                    bypass_cache=True
                )
                
                if result.success and result.markdown:
                    # Clean up the markdown content
                    content = result.markdown
                    # Remove excessive whitespace and newlines
                    content = ' '.join(content.split())
                    
                    if len(content) > 100:
                        # Limit content length
                        cleaned_content = content[:2000]
                        print(f"✅ Successfully scraped {url} ({len(cleaned_content)} chars)")
                        return cleaned_content
                    else:
                        print(f"⚠️ Content too short from {url}")
                        return None
                else:
                    print(f"❌ Failed to scrape {url}: {result.error_message if hasattr(result, 'error_message') else 'Unknown error'}")
                    return None
                    
            except Exception as e:
                print(f"❌ Failed to scrape {url}: {str(e)}")
                return None
        
        async with AsyncWebCrawler(verbose=False) as crawler:
            # Process URLs in batches of 10 for optimal performance
            batch_size = 10
            total_batches = (len(urls) + batch_size - 1) // batch_size
            
            for i in range(0, len(urls), batch_size):
                batch_urls = urls[i:i + batch_size]
                batch_num = i//batch_size + 1
                print(f"Processing batch {batch_num}/{total_batches} with {len(batch_urls)} URLs...")
                
                # Run batch in parallel
                tasks = [scrape_single_url(crawler, url) for url in batch_urls]
                batch_results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Collect successful results
                batch_success_count = 0
                for result in batch_results:
                    if isinstance(result, str) and result:  # Valid content
                        scraped_content.append(result)
                        batch_success_count += 1
                    elif isinstance(result, Exception):
                        print(f"Exception in batch: {str(result)}")
                
                print(f"Batch {batch_num} completed: {batch_success_count}/{len(batch_urls)} successful. Total content: {len(scraped_content)}")
                
                # Stop early if we have enough content (optimization)
                if len(scraped_content) >= 15:
                    print(f"Collected enough content ({len(scraped_content)} pieces), stopping early...")
                    break
        
        return scraped_content
    
    def _scrape_with_requests(self, urls: List[str]) -> List[str]:
        """Fallback scraping using requests and BeautifulSoup"""
        scraped_content = []
        
        if not BEAUTIFULSOUP_AVAILABLE:
            # Very basic text extraction without BeautifulSoup
            for url in urls:
                try:
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                    }
                    
                    response = requests.get(url, headers=headers, timeout=30)
                    response.raise_for_status()
                    
                    # Basic text extraction - just get plain text
                    text = response.text
                    # Simple cleanup - remove HTML tags using regex
                    import re
                    text = re.sub(r'<[^>]+>', '', text)
                    text = re.sub(r'\s+', ' ', text).strip()
                    
                    if text and len(text) > 100:
                        cleaned_content = text[:2000]
                        scraped_content.append(cleaned_content)
                        
                except Exception as e:
                    print(f"Failed to scrape {url}: {str(e)}")
                    continue
            
            return scraped_content
        
        # Use BeautifulSoup for better parsing
        for url in urls:
            try:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                
                response = requests.get(url, headers=headers, timeout=30)
                response.raise_for_status()
                
                # Parse with BeautifulSoup
                from bs4 import BeautifulSoup  # Import here to avoid import errors
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Remove script and style elements
                for script in soup(["script", "style"]):
                    script.decompose()
                
                # Get text content
                text = soup.get_text()
                
                # Clean up whitespace
                lines = (line.strip() for line in text.splitlines())
                chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                text = ' '.join(chunk for chunk in chunks if chunk)
                
                if text and len(text) > 100:
                    cleaned_content = text[:2000]
                    scraped_content.append(cleaned_content)
                    
            except Exception as e:
                print(f"Failed to scrape {url}: {str(e)}")
                continue
        
        return scraped_content
    
    def generate_ideas(self, scraped_content: List[str], original_query: str) -> tuple[List[Dict[str, Any]], int]:
        """
        Use Deepseek to analyze content and generate project ideas using parallel processing
        
        Args:
            scraped_content: List of scraped text content
            original_query: Original user query
            
        Returns:
            Tuple of (top 3 project ideas, total ideas extracted)
        """
        # Split content into 3 chunks for parallel processing
        chunk_size = max(1, len(scraped_content) // 3)
        content_chunks = [
            scraped_content[i:i + chunk_size] for i in range(0, len(scraped_content), chunk_size)
        ]
        
        # Ensure we have exactly 3 chunks (pad if necessary)
        while len(content_chunks) < 3:
            content_chunks.append([])
        content_chunks = content_chunks[:3]  # Limit to 3 chunks
        
        print(f"Split content into 3 chunks: {[len(chunk) for chunk in content_chunks]} sources each")
        
        # Run parallel idea generation
        try:
            import asyncio
            all_ideas = asyncio.run(self._generate_ideas_parallel(content_chunks, original_query))
            
            # Filter out None results and flatten
            valid_ideas = [idea for idea in all_ideas if idea is not None]
            total_ideas_extracted = len(valid_ideas)
            
            print(f"✅ Successfully generated {total_ideas_extracted} ideas from parallel processing")
            
            # Sort by relevance score and return all valid ideas (should be 3 or fewer)
            sorted_ideas = sorted(valid_ideas, key=lambda x: x.get("relevance_score", 0), reverse=True)
            
            return sorted_ideas, total_ideas_extracted
            
        except Exception as e:
            print(f"Parallel processing failed, falling back to sequential: {str(e)}")
            return self._generate_ideas_sequential(scraped_content, original_query)
    
    async def _generate_ideas_parallel(self, content_chunks: List[List[str]], original_query: str) -> List[Dict[str, Any]]:
        """Generate ideas from content chunks in parallel"""
        
        # Detect query language
        query_language = self._detect_language(original_query)
        print(f"Detected query language: {query_language}")
        
        async def generate_single_idea(session, chunk: List[str], chunk_index: int) -> Optional[Dict[str, Any]]:
            """Generate one idea from a content chunk"""
            if not chunk:
                print(f"Chunk {chunk_index + 1}: Empty chunk, skipping")
                return None
                
            # Combine chunk content
            combined_content = "\n\n---\n\n".join(chunk)
            
            # Ensure content isn't too long for API
            if len(combined_content) > 3000:  # Smaller limit for parallel chunks
                combined_content = combined_content[:3000] + "\n\n[Content truncated for processing...]"
            
            print(f"Chunk {chunk_index + 1}: Processing {len(chunk)} sources, {len(combined_content)} characters")
            
            # Create prompt for single idea generation
            prompt = f"""Analyze the following content and create 1 specific project idea for: "{original_query}"

Content:
{combined_content}

Generate 1 creative, actionable project idea. Make it SPECIFIC with unique angles, not generic.

IMPORTANT: Respond in {"Chinese" if query_language == "chinese" else "English"}. All fields must be in {"Chinese" if query_language == "chinese" else "English"}.

The idea must be a JSON object with exactly these fields:
- project_idea_title: string (specific title with target audience/technology)
- project_scope: string (team size like "Small team (2-4 people)" or "小团队 (2-4人)")  
- description: string (what the project does + why it's interesting in ~30 words)
- key_features: array of strings (specific actionable features)
- estimated_timeline: string (like "4-6 weeks" or "4-6周")
- difficulty_level: string ("Beginner", "Intermediate", "Advanced" or "初级", "中级", "高级")
- required_skills: array of strings (learnable skills, not too technical)
- similar_examples: array of URLs (from the provided content above)
- relevance_score: float (0.1 to 1.0)

Return only the JSON object. No other text."""
            
            headers = {
                "Authorization": f"Bearer {self.deepseek_api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "deepseek-chat",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.8,
                "max_tokens": 800  # Reduced for single idea
            }
            
            try:
                async with session.post(self.deepseek_url, headers=headers, json=data, timeout=60) as response:
                    if response.status != 200:
                        print(f"Chunk {chunk_index + 1}: API error {response.status}")
                        return None
                    
                    result = await response.json()
                    content = result["choices"][0]["message"]["content"]
                    
                    # Extract JSON from markdown code blocks if present
                    json_content = content
                    if '```json' in content:
                        start = content.find('```json') + 7
                        end = content.find('```', start)
                        if end != -1:
                            json_content = content[start:end].strip()
                    elif '```' in content:
                        start = content.find('```') + 3
                        end = content.find('```', start)
                        if end != -1:
                            potential_json = content[start:end].strip()
                            if potential_json.startswith('{'):
                                json_content = potential_json
                    
                    # Parse JSON response
                    idea = json.loads(json_content)
                    print(f"Chunk {chunk_index + 1}: ✅ Generated idea: {idea.get('project_idea_title', 'Unknown')}")
                    return idea
                    
            except Exception as e:
                print(f"Chunk {chunk_index + 1}: Failed to generate idea: {str(e)}")
                return None
        
        # Create async session and run parallel requests
        async with aiohttp.ClientSession() as session:
            tasks = [
                generate_single_idea(session, chunk, i) 
                for i, chunk in enumerate(content_chunks)
            ]
            
            print("Starting parallel idea generation...")
            start_time = time.time()
            results = await asyncio.gather(*tasks, return_exceptions=True)
            end_time = time.time()
            
            print(f"Parallel generation completed in {end_time - start_time:.2f} seconds")
            
            # Filter out exceptions and None results
            valid_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    print(f"Chunk {i + 1}: Exception occurred: {str(result)}")
                elif result is not None:
                    valid_results.append(result)
            
            return valid_results
    
    def _generate_ideas_sequential(self, scraped_content: List[str], original_query: str) -> tuple[List[Dict[str, Any]], int]:
        """Fallback sequential idea generation (original method)"""
        # Detect query language
        query_language = self._detect_language(original_query)
        print(f"Sequential processing - Detected query language: {query_language}")
        
        combined_content = "\n\n---\n\n".join(scraped_content[:5])  # Limit to 5 sources only
        
        # Ensure content isn't too long for API (be more conservative)
        if len(combined_content) > 8000:  # Much smaller limit - 8k characters
            combined_content = combined_content[:8000] + "\n\n[Content truncated for processing...]"
        
        print(f"Processing {len(scraped_content)} sources, using top 5, combined content: {len(combined_content)} characters")
        
        prompt = f"""Analyze the following content and create 5 specific project ideas for: "{original_query}"

Content:
{combined_content}

Generate 5 creative, actionable project ideas. Make them SPECIFIC with unique angles, not generic.

IMPORTANT: Respond in {"Chinese" if query_language == "chinese" else "English"}. All fields must be in {"Chinese" if query_language == "chinese" else "English"}.

Each idea must be a JSON object with exactly these fields:
- project_idea_title: string (specific title with target audience/technology)
- project_scope: string (team size like "Small team (2-4 people)" or "小团队 (2-4人)")  
- description: string (what the project does + why it's interesting in ~30 words)
- key_features: array of strings (specific actionable features)
- estimated_timeline: string (like "4-6 weeks" or "4-6周")
- difficulty_level: string ("Beginner", "Intermediate", "Advanced" or "初级", "中级", "高级")
- required_skills: array of strings (learnable skills, not too technical)
- similar_examples: array of URLs (from the provided content above)
- relevance_score: float (0.1 to 1.0)

Return only a JSON array of 5 ideas. No other text."""
        
        headers = {
            "Authorization": f"Bearer {self.deepseek_api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.8,
            "max_tokens": 2000
        }
        
        try:
            # First attempt with normal timeout
            response = requests.post(self.deepseek_url, headers=headers, json=data, timeout=90)
            
            # Debug: Print response details
            print(f"Deepseek Idea Generation Status: {response.status_code}")
            
            response.raise_for_status()
            
            if not response.text.strip():
                raise Exception("Empty response from Deepseek API")
            
            print(f"Response length: {len(response.text)} characters")
            
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            
            print(f"Generated content length: {len(content)} characters")
            
            # Extract JSON from markdown code blocks if present
            json_content = content
            if '```json' in content:
                # Find the JSON content between ```json and ```
                start = content.find('```json') + 7
                end = content.find('```', start)
                if end != -1:
                    json_content = content[start:end].strip()
                    print(f"Extracted JSON from markdown: {json_content[:200]}..." if len(json_content) > 200 else f"Extracted JSON from markdown: {json_content}")
                else:
                    print("Warning: Found ```json but no closing ``` - using full content")
            elif '```' in content:
                # Handle cases where JSON is in code blocks without 'json' language specifier
                start = content.find('```') + 3
                end = content.find('```', start)
                if end != -1:
                    potential_json = content[start:end].strip()
                    # Check if it looks like JSON
                    if potential_json.startswith('[') or potential_json.startswith('{'):
                        json_content = potential_json
                        print(f"Extracted JSON from generic code block: {json_content[:200]}..." if len(json_content) > 200 else f"Extracted JSON from generic code block: {json_content}")
            
            # Additional cleanup for common JSON parsing issues
            json_content = json_content.strip()
            if not json_content:
                raise Exception("Empty JSON content after extraction")
                
            print(f"Final JSON content length: {len(json_content)} characters")

            # Parse JSON response with better error handling
            try:
                all_ideas = json.loads(json_content)
            except json.JSONDecodeError as json_err:
                print(f"JSON parsing failed: {str(json_err)}")
                print(f"Problematic JSON content: {json_content[:500]}...")
                
                # Try to clean up common JSON issues
                cleaned_json = json_content
                # Remove any trailing commas
                cleaned_json = re.sub(r',(\s*[}\]])', r'\1', cleaned_json)
                # Try parsing again
                try:
                    all_ideas = json.loads(cleaned_json)
                    print("✅ Successfully parsed JSON after cleanup")
                except json.JSONDecodeError:
                    raise Exception(f"Failed to parse JSON even after cleanup: {str(json_err)}")
            
            if not isinstance(all_ideas, list):
                raise Exception(f"Expected JSON array but got {type(all_ideas)}")
                
            total_ideas_extracted = len(all_ideas)
            print(f"✅ Successfully generated {total_ideas_extracted} ideas from scraped content")
            
            # Sort by relevance score and take top 3
            sorted_ideas = sorted(all_ideas, key=lambda x: x.get("relevance_score", 0), reverse=True)
            top_3_ideas = sorted_ideas[:3]
            
            return top_3_ideas, total_ideas_extracted
            
        except requests.exceptions.Timeout:
            raise Exception("Deepseek API timeout - please try again later")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Deepseek API connection failed: {str(e)}")
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse Deepseek response: {str(e)}")
        except Exception as e:
            raise Exception(f"Project idea generation failed: {str(e)}")


class ProjectIdeaAgentStreaming(ProjectIdeaAgent):
    """Streaming version of ProjectIdeaAgent that emits real-time progress events"""
    
    async def generate_project_ideas_stream(self, query: str, user_id: int):
        """
        Generate project ideas with streaming progress updates
        
        Args:
            query: User's rough project query
            user_id: User ID for quota checking
            
        Yields:
            Dict events with progress updates
        """
        start_time = time.time()
        
        # Check quota first
        # Note: Quota checking is now handled in the router via MembershipService
        yield {
            'type': 'progress',
            'step': 'initialization',
            'message': '🚀 Starting project idea generation...',
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            # Step 1: Refine query into search prompts
            yield {
                'type': 'progress',
                'step': 'query_refinement',
                'message': f'🔍 Refining query: "{query}"',
                'timestamp': datetime.now().isoformat()
            }
            
            generated_prompts = await self.refine_query_stream(query)
            
            yield {
                'type': 'progress',
                'step': 'query_refinement',
                'message': f'✅ Generated {len(generated_prompts)} search prompts',
                'data': {'prompts': generated_prompts},
                'timestamp': datetime.now().isoformat()
            }
            
            # Step 2: Search web for each prompt
            yield {
                'type': 'progress',
                'step': 'web_search',
                'message': '🌐 Starting web search across multiple engines...',
                'timestamp': datetime.now().isoformat()
            }
            
            all_urls = []
            prompt_results = []
            
            for i, prompt in enumerate(generated_prompts):
                engine = self.search_engines[i % len(self.search_engines)]
                
                yield {
                    'type': 'progress',
                    'step': 'web_search',
                    'message': f'Searching {engine} for: "{prompt}"',
                    'timestamp': datetime.now().isoformat()
                }
                
                urls = self.search_web(prompt, engine)
                all_urls.extend(urls[:5])  # Limit to top 5 per search
                
                prompt_results.append({
                    "prompt": prompt,
                    "engine": engine,
                    "results_count": len(urls)
                })
                
                yield {
                    'type': 'progress',
                    'step': 'web_search',
                    'message': f'✅ Found {len(urls)} results from {engine}',
                    'timestamp': datetime.now().isoformat()
                }
            
            yield {
                'type': 'progress',
                'step': 'web_search',
                'message': f'✅ Web search complete. Total URLs: {len(all_urls)}',
                'data': {'total_urls': len(all_urls), 'search_results': prompt_results},
                'timestamp': datetime.now().isoformat()
            }
            
            # Step 3: Scrape content from URLs
            yield {
                'type': 'progress',
                'step': 'content_scraping',
                'message': f'📄 Starting content extraction from {len(all_urls)} sources...',
                'timestamp': datetime.now().isoformat()
            }
            
            scraped_content = []
            total_sources_found = 0
            
            async for scrape_event in self.scrape_pages_stream(all_urls):
                yield scrape_event
                if scrape_event.get('type') == 'scrape_success':
                    content_data = scrape_event.get('data', {})
                    if isinstance(content_data, dict) and 'content' in content_data:
                        scraped_content.append(content_data['content'])
                        total_sources_found += 1
            
            yield {
                'type': 'progress',
                'step': 'content_scraping',
                'message': f'✅ Content extraction complete. {total_sources_found} sources processed',
                'data': {'sources_found': total_sources_found},
                'timestamp': datetime.now().isoformat()
            }
            
            # Step 4: Generate project ideas from scraped content
            yield {
                'type': 'progress',
                'step': 'idea_generation',
                'message': '🤖 Starting AI-powered idea generation...',
                'timestamp': datetime.now().isoformat()
            }
            
            project_ideas = []
            total_ideas_extracted = 0
            
            async for idea_event in self.generate_ideas_stream(scraped_content, query):
                if idea_event['type'] == 'idea_generated':
                    project_ideas.append(idea_event['data'])
                    total_ideas_extracted += 1
                    
                yield idea_event
                
            # Step 5: Final compilation and results
            processing_time = time.time() - start_time
            search_id = random.randint(1000, 9999)
            
            final_result = {
                "search_id": search_id,
                "original_query": query,
                "generated_prompts": prompt_results,
                "total_sources_found": total_sources_found,
                "total_ideas_extracted": total_ideas_extracted,
                "project_ideas": project_ideas,
                "processing_time_seconds": round(processing_time, 2),
                "created_at": datetime.now().isoformat()
            }
            
            yield {
                'type': 'result',
                'step': 'completion',
                'message': f'🎉 Generated {total_ideas_extracted} project ideas in {processing_time:.1f}s',
                'data': final_result,
                'timestamp': datetime.now().isoformat()
            }
            
            # Usage logging is now handled in the router via MembershipService.log_usage()
            
        except Exception as e:
            yield {
                'type': 'error',
                'step': 'generation_failed',
                'message': f'❌ Generation failed: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }
            raise
    
    async def refine_query_stream(self, query: str) -> List[str]:
        """Streaming version of query refinement"""
        # Use the same logic as the parent class but could add progress updates
        return self.refine_query(query)
    
    async def scrape_pages_stream(self, urls: List[str]):
        """
        Streaming version of content scraping with detailed progress updates for each URL
        """
        if CRAWL4AI_AVAILABLE:
            yield {
                'type': 'progress',
                'step': 'content_scraping',
                'message': f'🌐 Using Crawl4AI Python library for web scraping',
                'timestamp': datetime.now().isoformat()
            }
            
            try:
                async for event in self._scrape_with_crawl4ai_stream(urls):
                    yield event
                return
            except Exception as e:
                yield {
                    'type': 'progress', 
                    'step': 'content_scraping',
                    'message': f'⚠️ Crawl4AI failed, falling back to requests-based scraping: {str(e)}',
                    'timestamp': datetime.now().isoformat()
                }
        else:
            yield {
                'type': 'progress',
                'step': 'content_scraping',
                'message': f'📝 Crawl4AI not available, using requests-based scraping',
                'timestamp': datetime.now().isoformat()
            }
        
        # Fallback to requests-based scraping with streaming
        async for event in self._scrape_with_requests_stream(urls):
            yield event
    
    async def _scrape_with_crawl4ai_stream(self, urls: List[str]):
        """Detailed streaming scraping using Crawl4AI with verbose-style progress"""
        from crawl4ai import AsyncWebCrawler
        
        async def scrape_single_url_verbose(crawler, url, url_index):
            """Scrape a single URL with detailed progress updates"""
            url_num = url_index + 1
            short_url = url[:60] + "..." if len(url) > 60 else url
            
            # [FETCH] phase
            fetch_start = time.time()
            yield {
                'type': 'progress',
                'step': 'content_scraping',
                'message': f'[FETCH]... ↓ {url}',
                'timestamp': datetime.now().isoformat()
            }
            
            try:
                result = await crawler.arun(
                    url=url,
                    word_count_threshold=10,
                    extraction_strategy="NoExtractionStrategy",
                    chunking_strategy="RegexChunking", 
                    bypass_cache=True
                )
                
                fetch_time = time.time() - fetch_start
                
                if not result.success:
                    yield {
                        'type': 'progress',
                        'step': 'content_scraping',
                        'message': f'| ✗ | ⏱: {fetch_time:.2f}s - [FETCH] Failed for {short_url}',
                        'timestamp': datetime.now().isoformat()
                    }
                    return
                
                yield {
                    'type': 'progress',
                    'step': 'content_scraping', 
                    'message': f'| ✓ | ⏱: {fetch_time:.2f}s',
                    'timestamp': datetime.now().isoformat()
                }
                
                # [SCRAPE] phase
                scrape_start = time.time()
                yield {
                    'type': 'progress',
                    'step': 'content_scraping',
                    'message': f'[SCRAPE].. ◆ {url}',
                    'timestamp': datetime.now().isoformat()
                }
                
                # Process the content
                if result.markdown:
                    content = result.markdown.strip()
                    # Clean up the content
                    content = ' '.join(content.split())
                    
                    if len(content) > 100:
                        char_count = len(content)
                        truncated_content = content[:1000] + "..." if len(content) > 1000 else content
                        
                        scrape_time = time.time() - scrape_start
                        total_time = time.time() - fetch_start
                        
                        yield {
                            'type': 'progress',
                            'step': 'content_scraping',
                            'message': f'| ✓ | ⏱: {scrape_time:.2f}s',
                            'timestamp': datetime.now().isoformat()
                        }
                        
                        # [COMPLETE] phase
                        yield {
                            'type': 'progress',
                            'step': 'content_scraping',
                            'message': f'[COMPLETE] ● {url}',
                            'timestamp': datetime.now().isoformat()
                        }
                        
                        yield {
                            'type': 'progress',
                            'step': 'content_scraping',
                            'message': f'| ✓ | ⏱: {total_time:.2f}s',
                            'timestamp': datetime.now().isoformat()
                        }
                        
                        # Success event with content
                        yield {
                            'type': 'scrape_success',
                            'step': 'content_scraping',
                            'message': f'✅ Successfully scraped {short_url} ({char_count} chars)',
                            'data': {
                                'url': url,
                                'content': truncated_content,
                                'char_count': char_count,
                                'fetch_time': fetch_time,
                                'scrape_time': scrape_time,
                                'total_time': total_time
                            },
                            'timestamp': datetime.now().isoformat()
                        }
                        return
                
                # Failed to get meaningful content
                total_time = time.time() - fetch_start
                yield {
                    'type': 'progress',
                    'step': 'content_scraping',
                    'message': f'| ✗ | ⏱: {total_time:.2f}s - No meaningful content extracted',
                    'timestamp': datetime.now().isoformat()
                }
                
            except Exception as e:
                fetch_time = time.time() - fetch_start
                yield {
                    'type': 'progress',
                    'step': 'content_scraping',
                    'message': f'| ✗ | ⏱: {fetch_time:.2f}s - Error: {str(e)[:50]}...',
                    'timestamp': datetime.now().isoformat()
                }
        
        async with AsyncWebCrawler(verbose=False) as crawler:
            # Process URLs in batches of 8 for optimal performance
            batch_size = 8
            total_batches = (len(urls) + batch_size - 1) // batch_size
            
            for i in range(0, len(urls), batch_size):
                batch_urls = urls[i:i + batch_size]
                batch_num = i//batch_size + 1
                
                yield {
                    'type': 'progress',
                    'step': 'content_scraping',
                    'message': f'📦 Processing batch {batch_num}/{total_batches} ({len(batch_urls)} URLs)...',
                    'timestamp': datetime.now().isoformat()
                }
                
                # Create tasks for all URLs in this batch
                for url_index, url in enumerate(batch_urls):
                    async for event in scrape_single_url_verbose(crawler, url, i + url_index):
                        yield event
                
                # Stop early if we have enough content (optimization)
                successful_count = sum(1 for _ in range(i+len(batch_urls)) if _ < len(urls))
                if successful_count >= 15:
                    yield {
                        'type': 'progress',
                        'step': 'content_scraping',
                        'message': f'🎯 Early stopping: Collected sufficient content ({successful_count} sources)',
                        'timestamp': datetime.now().isoformat()
                    }
                    break
    
    async def _scrape_with_requests_stream(self, urls: List[str]):
        """Fallback streaming scraping using requests with verbose-style progress"""
        
        for url_index, url in enumerate(urls):
            url_num = url_index + 1
            short_url = url[:60] + "..." if len(url) > 60 else url
            
            # [FETCH] phase
            fetch_start = time.time()
            yield {
                'type': 'progress',
                'step': 'content_scraping',
                'message': f'[FETCH]... ↓ {url}',
                'timestamp': datetime.now().isoformat()
            }
            
            try:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                
                # Simulate async with run_in_executor for requests
                import asyncio
                response = await asyncio.get_event_loop().run_in_executor(
                    None, 
                    lambda: requests.get(url, headers=headers, timeout=30)
                )
                response.raise_for_status()
                
                fetch_time = time.time() - fetch_start
                yield {
                    'type': 'progress',
                    'step': 'content_scraping',
                    'message': f'| ✓ | ⏱: {fetch_time:.2f}s',
                    'timestamp': datetime.now().isoformat()
                }
                
                # [SCRAPE] phase
                scrape_start = time.time()
                yield {
                    'type': 'progress',
                    'step': 'content_scraping',
                    'message': f'[SCRAPE].. ◆ {url}',
                    'timestamp': datetime.now().isoformat()
                }
                
                # Parse content
                if BEAUTIFULSOUP_AVAILABLE:
                    from bs4 import BeautifulSoup
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Remove script and style elements
                    for script in soup(["script", "style"]):
                        script.decompose()
                    
                    # Get text content
                    text = soup.get_text()
                    
                    # Clean up whitespace
                    lines = (line.strip() for line in text.splitlines())
                    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                    content = ' '.join(chunk for chunk in chunks if chunk)
                else:
                    # Basic text extraction without BeautifulSoup
                    content = response.text
                    # Basic cleanup
                    content = ' '.join(content.split())
                
                scrape_time = time.time() - scrape_start
                total_time = time.time() - fetch_start
                
                if content and len(content) > 100:
                    char_count = len(content)
                    truncated_content = content[:1000] + "..." if len(content) > 1000 else content
                    
                    yield {
                        'type': 'progress',
                        'step': 'content_scraping',
                        'message': f'| ✓ | ⏱: {scrape_time:.2f}s',
                        'timestamp': datetime.now().isoformat()
                    }
                    
                    # [COMPLETE] phase
                    yield {
                        'type': 'progress',
                        'step': 'content_scraping',
                        'message': f'[COMPLETE] ● {url}',
                        'timestamp': datetime.now().isoformat()
                    }
                    
                    yield {
                        'type': 'progress',
                        'step': 'content_scraping',
                        'message': f'| ✓ | ⏱: {total_time:.2f}s',
                        'timestamp': datetime.now().isoformat()
                    }
                    
                    # Success event with content
                    yield {
                        'type': 'scrape_success',
                        'step': 'content_scraping',
                        'message': f'✅ Successfully scraped {short_url} ({char_count} chars)',
                        'data': {
                            'url': url,
                            'content': truncated_content,
                            'char_count': char_count,
                            'fetch_time': fetch_time,
                            'scrape_time': scrape_time,
                            'total_time': total_time
                        },
                        'timestamp': datetime.now().isoformat()
                    }
                else:
                    yield {
                        'type': 'progress',
                        'step': 'content_scraping',
                        'message': f'| ✗ | ⏱: {total_time:.2f}s - No meaningful content found',
                        'timestamp': datetime.now().isoformat()
                    }
                
            except Exception as e:
                fetch_time = time.time() - fetch_start
                yield {
                    'type': 'progress',
                    'step': 'content_scraping',
                    'message': f'| ✗ | ⏱: {fetch_time:.2f}s - Error: {str(e)[:50]}...',
                    'timestamp': datetime.now().isoformat()
                }
    
    async def generate_ideas_stream(self, scraped_content: List[str], original_query: str):
        """
        Streaming version of idea generation with real-time progress
        
        Yields:
            Progress events for each step of the parallel processing
        """
        # Detect language
        query_language = self._detect_language(original_query)
        
        yield {
            'type': 'progress',
            'step': 'idea_generation',
            'message': f'🌐 Detected query language: {query_language}',
            'timestamp': datetime.now().isoformat()
        }
        
        # Split content into 3 chunks for parallel processing
        chunk_size = max(1, len(scraped_content) // 3)
        content_chunks = [
            scraped_content[i:i + chunk_size] for i in range(0, len(scraped_content), chunk_size)
        ]
        
        # Ensure we have exactly 3 chunks (pad if necessary)
        while len(content_chunks) < 3:
            content_chunks.append([])
        content_chunks = content_chunks[:3]  # Limit to 3 chunks
        
        yield {
            'type': 'progress',
            'step': 'idea_generation',
            'message': f'📊 Split content into 3 chunks: {[len(chunk) for chunk in content_chunks]} sources each',
            'timestamp': datetime.now().isoformat()
        }
        
        # Run parallel idea generation with streaming
        try:
            yield {
                'type': 'progress',
                'step': 'idea_generation',
                'message': '⚡ Starting parallel AI processing (3 concurrent calls)...',
                'timestamp': datetime.now().isoformat()
            }
            
            async for event in self._generate_ideas_parallel_stream(content_chunks, original_query, query_language):
                yield event
                
        except Exception as e:
            yield {
                'type': 'progress',
                'step': 'idea_generation',
                'message': f'⚠️ Parallel processing failed, falling back to sequential: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }
            
            # Fallback to sequential processing
            ideas, total = self._generate_ideas_sequential(scraped_content, original_query)
            for idea in ideas:
                yield {
                    'type': 'idea_generated',
                    'step': 'idea_generation',
                    'message': f'💡 Generated idea: {idea.get("project_idea_title", "Unknown")}',
                    'data': idea,
                    'timestamp': datetime.now().isoformat()
                }
    
    async def _generate_ideas_parallel_stream(self, content_chunks: List[List[str]], original_query: str, query_language: str):
        """
        Parallel idea generation with streaming progress updates
        """
        import asyncio
        import aiohttp
        
        generated_ideas = []
        
        async def generate_single_idea(session, chunk: List[str], chunk_index: int):
            """Generate one idea from a content chunk"""
            chunk_num = chunk_index + 1
            
            if not chunk:
                return None, {
                    'type': 'progress',
                    'step': 'idea_generation',
                    'message': f'Chunk {chunk_num}: Empty chunk, skipping',
                    'timestamp': datetime.now().isoformat()
                }
                
            # Combine chunk content
            combined_content = "\n\n---\n\n".join(chunk)
            
            # Ensure content isn't too long for API
            if len(combined_content) > 3000:
                combined_content = combined_content[:3000] + "\n\n[Content truncated for processing...]"
            
            progress_event = {
                'type': 'progress',
                'step': 'idea_generation',
                'message': f'Chunk {chunk_num}: Processing {len(chunk)} sources, {len(combined_content)} characters',
                'timestamp': datetime.now().isoformat()
            }
            
            # Create prompt for single idea generation
            prompt = f"""Analyze the following content and create 1 specific project idea for: "{original_query}"

Content:
{combined_content}

Generate 1 creative, actionable project idea. Make it SPECIFIC with unique angles, not generic.

IMPORTANT: Respond in {"Chinese" if query_language == "chinese" else "English"}. All fields must be in {"Chinese" if query_language == "chinese" else "English"}.

The idea must be a JSON object with exactly these fields:
- project_idea_title: string (specific title with target audience/technology)
- project_scope: string (team size like "Small team (2-4 people)" or "小团队 (2-4人)")  
- description: string (what the project does + why it's interesting in ~30 words)
- key_features: array of strings (specific actionable features)
- estimated_timeline: string (like "4-6 weeks" or "4-6周")
- difficulty_level: string ("Beginner", "Intermediate", "Advanced" or "初级", "中级", "高级")
- required_skills: array of strings (learnable skills, not too technical)
- similar_examples: array of URLs (from the provided content above)
- relevance_score: float (0.1 to 1.0)

Return only the JSON object. No other text."""
            
            headers = {
                "Authorization": f"Bearer {self.deepseek_api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "deepseek-chat",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.8,
                "max_tokens": 800
            }
            
            try:
                async with session.post(self.deepseek_url, headers=headers, json=data, timeout=60) as response:
                    if response.status != 200:
                        error_event = {
                            'type': 'progress',
                            'step': 'idea_generation',
                            'message': f'Chunk {chunk_num}: ❌ API error {response.status}',
                            'timestamp': datetime.now().isoformat()
                        }
                        return None, error_event
                    
                    result = await response.json()
                    content = result["choices"][0]["message"]["content"]
                    
                    # Extract JSON from markdown code blocks if present
                    json_content = content
                    if '```json' in content:
                        start = content.find('```json') + 7
                        end = content.find('```', start)
                        if end != -1:
                            json_content = content[start:end].strip()
                    elif '```' in content:
                        start = content.find('```') + 3
                        end = content.find('```', start)
                        if end != -1:
                            potential_json = content[start:end].strip()
                            if potential_json.startswith('{'):
                                json_content = potential_json
                    
                    # Parse JSON response
                    idea = json.loads(json_content)
                    
                    success_event = {
                        'type': 'idea_generated',
                        'step': 'idea_generation',
                        'message': f'Chunk {chunk_num}: ✅ Generated idea: {idea.get("project_idea_title", "Unknown")}',
                        'data': idea,
                        'timestamp': datetime.now().isoformat()
                    }
                    
                    return idea, success_event
                    
            except Exception as e:
                error_event = {
                    'type': 'progress',
                    'step': 'idea_generation',
                    'message': f'Chunk {chunk_num}: ❌ Failed to generate idea: {str(e)}',
                    'timestamp': datetime.now().isoformat()
                }
                return None, error_event
        
        # Create async session and run parallel requests
        start_time = time.time()
        
        async with aiohttp.ClientSession() as session:
            # Create tasks for all chunks
            tasks = [
                generate_single_idea(session, chunk, i) 
                for i, chunk in enumerate(content_chunks)
            ]
            
            # Run all tasks concurrently and emit events as they complete
            for coro in asyncio.as_completed(tasks):
                idea, event = await coro
                yield event
                if idea is not None:
                    generated_ideas.append(idea)
                    
        end_time = time.time()
        
        yield {
            'type': 'progress',
            'step': 'idea_generation',
            'message': f'⚡ Parallel generation completed in {end_time - start_time:.2f} seconds',
            'timestamp': datetime.now().isoformat()
        }


# Main function for external use
def generate_project_ideas(query: str, user_id: int) -> Dict[str, Any]:
    """
    Generate project ideas from a user query
    
    Args:
        query: User's rough project query
        user_id: User ID for quota checking
        
    Returns:
        Dict containing project ideas and metadata
    """
    agent = ProjectIdeaAgent()
    return agent.generate_project_ideas(query, user_id)
