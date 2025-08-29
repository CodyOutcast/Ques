# Project Idea Agent with UniFuncs API

## Overview

The `project_idea_agent_with_unifuncs.py` module provides an integration with the UniFuncs deep research and creative generation API for generating project ideas. This module leverages a powerful AI model to search for relevant information, analyze it, and generate detailed project ideas based on user queries.

## Integration Methods

There are two ways to integrate the UniFuncs implementation:

1. **Direct usage**: Directly import and use `AdvancedSearchAgent` or `AdvancedSearchAgentStreaming` classes
2. **Adapter pattern**: Use the adapter in `project_idea_agent_adapter.py` to maintain compatibility with the original API interface
3. **Factory pattern**: Use the factory in `project_idea_agent_factory.py` to dynamically switch between implementations

### Using the Factory Pattern

The factory pattern allows switching between the original implementation and the UniFuncs implementation without changing import statements:

```python
from services.project_idea_agent_factory import get_project_idea_generator

# This will return either the original or UniFuncs implementation based on environment variables
generate_project_ideas = get_project_idea_generator()
result = generate_project_ideas(query, user_id)
```

For streaming API:
```python
from services.project_idea_agent_factory import get_streaming_agent_class

# Get the appropriate streaming class
ProjectIdeaAgentStreaming = get_streaming_agent_class()
streaming_agent = ProjectIdeaAgentStreaming()
```

## Key Components

### AdvancedSearchAgent

A base agent class for interfacing with the UniFuncs API in a non-streaming mode.

#### Key Methods:

- `generate_project_ideas(query, language, stream)`: Generate project ideas based on a query
- `_build_introduction(query)`: Build the introduction prompt for the API
- `_build_output_prompt(query, language)`: Build the output format prompt for the API
- `_call_api(query, introduction, output_prompt)`: Make a non-streaming API call
- `_call_api_stream(query, introduction, output_prompt)`: Make a streaming API call
- `_process_response(response, query, processing_time)`: Process API response into a standardized format

### AdvancedSearchAgentStreaming

An extended agent class that supports streaming responses from the UniFuncs API, providing real-time progress updates and partial results.

#### Key Methods:

- `generate_project_ideas_stream(query, user_id, include_reasoning)`: Generate project ideas with streaming updates
  - Yields various event types including progress updates, reasoning content, and final results

## Features

1. **Multilingual Support**: Automatically detects Chinese or English queries and generates responses in the corresponding language
2. **Streaming Generation**: Provides real-time progress updates during the generation process
3. **Thinking Process Visibility**: Option to include the AI's reasoning process in the output
4. **Robust Error Handling**: Multiple fallback mechanisms for handling JSON parsing errors
5. **Detailed Output**: Generates comprehensive project ideas with:
   - Project titles
   - Team size requirements
   - Project descriptions
   - Key features
   - Estimated timelines
   - Difficulty levels
   - Required skills
   - Similar examples
   - Relevance scores

## Input Format

The module accepts natural language queries describing the kind of project the user is interested in, for example:
- "Develop an AI-based health diet recommendation app"
- "Create a mobile application for plant identification"

## Output Format

The standard output format is a JSON structure containing:

```json
{
  "search_id": "<unique_identifier>",
  "original_query": "<user_query>",
  "total_sources_found": <number_of_sources>,
  "total_ideas_extracted": <number_of_ideas>,
  "project_ideas": [
    {
      "project_idea_title": "<specific title with target audience/technology>",
      "project_scope": "<team size>",
      "description": "<project description>",
      "key_features": ["<feature 1>", "<feature 2>", ...],
      "estimated_timeline": "<timeline>",
      "difficulty_level": "<difficulty>",
      "required_skills": ["<skill 1>", "<skill 2>", ...],
      "similar_examples": ["<url 1>", ...],
      "relevance_score": <score between 0.1 and 1.0>
    },
    ...
  ],
  "processing_time_seconds": <processing_time>,
  "created_at": "<timestamp>",
  "sources": [
    {
      "url": "<source_url>",
      "title": "<source_title>",
      "relevance": <score between 0.1 and 1.0>
    },
    ...
  ]
}
```

## Streaming Events

When using the streaming API, the following event types are emitted:

1. **Progress Updates**:
   ```json
   {
     "type": "progress",
     "step": "<current_step>",
     "message": "<progress_message>",
     "timestamp": "<timestamp>"
   }
   ```

2. **Reasoning Content** (when include_reasoning=True):
   ```json
   {
     "type": "reasoning",
     "step": "reasoning_content",
     "content": "<reasoning_text>",
     "timestamp": "<timestamp>"
   }
   ```

3. **Content Updates**:
   ```json
   {
     "type": "content",
     "step": "output_content",
     "content": "<content_chunk>",
     "timestamp": "<timestamp>"
   }
   ```

4. **Idea Generated**:
   ```json
   {
     "type": "idea_generated",
     "step": "idea_generation",
     "message": "✨ Generated idea N: <title>",
     "data": "<idea_object>",
     "timestamp": "<timestamp>"
   }
   ```

5. **Final Result**:
   ```json
   {
     "type": "result",
     "step": "completion",
     "message": "🎉 Generated <count> project ideas in <time>s",
     "data": "<full_result_object>",
     "timestamp": "<timestamp>"
   }
   ```

## Usage Examples

### Standard (Non-Streaming) Usage

```python
async def get_project_ideas():
    agent = AdvancedSearchAgent()
    response = await agent.generate_project_ideas("Develop an AI-based health diet recommendation app")
    
    print(f"Found {response['total_sources_found']} relevant sources")
    print(f"Generated {response['total_ideas_extracted']} project ideas")
    
    for i, idea in enumerate(response['project_ideas']):
        print(f"\nIdea {i+1}: {idea['project_idea_title']}")
        print(f"Description: {idea['description']}")
        print(f"Key features: {', '.join(idea['key_features'][:3])}...")
```

### Streaming Usage

```python
async def get_project_ideas_with_progress():
    agent = AdvancedSearchAgentStreaming()
    
    async for event in agent.generate_project_ideas_stream("Develop an AI-based health diet recommendation app"):
        if event['type'] == 'progress':
            print(f"Progress: {event['message']}")
        elif event['type'] == 'idea_generated':
            print(f"New idea: {event['data']['project_idea_title']}")
        elif event['type'] == 'result':
            print(f"Generation complete!")
```

### Streaming with Reasoning Process

```python
async def get_project_ideas_with_reasoning():
    agent = AdvancedSearchAgentStreaming()
    
    async for event in agent.generate_project_ideas_stream(
        "Develop an AI-based health diet recommendation app", 
        include_reasoning=True
    ):
        if event['type'] == 'progress':
            print(f"Progress: {event['message']}")
        elif event['type'] == 'reasoning':
            # Process AI's thinking process
            print(f"AI thinking: {event['content'][:100]}...")
        elif event['type'] == 'idea_generated':
            print(f"New idea: {event['data']['project_idea_title']}")
```

### Using the Adapter

```python
# Using the adapter with the original API interface
from services.project_idea_agent_adapter import generate_project_ideas

result = generate_project_ideas("Develop an AI-based health diet recommendation app", user_id=1)
print(f"Generated {len(result['project_ideas'])} project ideas")

# Using the streaming adapter
from services.project_idea_agent_adapter import ProjectIdeaAgentStreaming

async def stream_ideas():
    agent = ProjectIdeaAgentStreaming()
    async for event in agent.generate_project_ideas_stream("Develop an AI-based health diet recommendation app", user_id=1):
        print(f"Event type: {event['type']}, Message: {event.get('message', '')}")
```

### Using the Factory Pattern

```python
# The factory automatically selects the appropriate implementation based on ACTIVE_AGENT environment variable
from services.project_idea_agent_factory import get_project_idea_generator

generate_project_ideas = get_project_idea_generator()
result = generate_project_ideas("Develop an AI-based health diet recommendation app", user_id=1)
```

## Testing Tools

The module includes several test functions for validating the API integration:

1. `test_advanced_search()`: Tests the standard non-streaming API
2. `test_advanced_search_stream()`: Tests the streaming API without reasoning
3. `test_advanced_search_stream_with_reasoning()`: Tests the streaming API with reasoning included
4. `test_raw_api_stream()`: Tests the underlying raw API directly
5. `test_stream_to_file()`: Saves all API responses to file for detailed analysis

### Testing the Adapter

The project includes a specific test file for the adapter, which verifies that the adapter correctly integrates with the original API interface:

```bash
# Run the adapter test
python test_adapter.py
```

This test verifies:
1. The adapter preserves the same API interface
2. Quota management is properly integrated
3. Error handling is consistent with the original implementation
4. Output format is compatible with the rest of the system

### Running the UniFuncs Tests

```bash
# Standard test
python project_idea_agent_with_unifuncs.py

# Streaming test
python project_idea_agent_with_unifuncs.py stream

# Streaming with reasoning test
python project_idea_agent_with_unifuncs.py stream_reasoning

# Save all API responses to file
python project_idea_agent_with_unifuncs.py file

# Test raw API directly
python project_idea_agent_with_unifuncs.py raw
```

### Example Output Files

The `file` test option generates several output files that provide detailed insights into the API's behavior and response data. Example output files can be found in the `example` folder, including:

- `project_ideas_stream_output.txt`: Complete record of all events, thinking content, and output
- `api_responses_YYYY-MM-DD_HH-MM-SS.json`: JSON file containing all raw API responses
- `thinking_flow_YYYY-MM-DD_HH-MM-SS.txt`: User interface thinking content flow with progress information

These example files are useful for understanding the API's behavior, debugging issues, and analyzing the quality of generated project ideas.

## Configuration

The module requires the following environment variables:

- `UNIFUNCS_API_KEY`: Your UniFuncs API key
- `UNIFUNCS_BASE_URL` (optional): The base URL for the UniFuncs API (defaults to "https://api.unifuncs.com/deepresearch/v1")
- `ACTIVE_AGENT` (optional): Set to "unifuncs" to use the UniFuncs implementation, or "original" to use the original implementation (defaults to "original")

### Configuration in settings.py

To properly integrate with your project's settings, add the following to your `config/settings.py` file:

```python
# UniFuncs deep research and generation API settings
UNIFUNCS_API_KEY: str = os.environ.get("UNIFUNCS_API_KEY", "")
UNIFUNCS_BASE_URL: str = os.environ.get("UNIFUNCS_BASE_URL", "https://api.unifuncs.com/deepresearch/v1")

# Ensure valid validation
@validator("UNIFUNCS_API_KEY", pre=True)
def validate_unifuncs_api_key(cls, v):
    if not v and os.environ.get("ACTIVE_AGENT") == "unifuncs":
        raise ValueError("UNIFUNCS_API_KEY is required when ACTIVE_AGENT=unifuncs")
    return v
```

### Environment Variables

In your `.env` file or environment configuration:

```
# API Keys
UNIFUNCS_API_KEY=your_api_key_here

# Optional settings
UNIFUNCS_BASE_URL=https://api.unifuncs.com/deepresearch/v1
ACTIVE_AGENT=unifuncs  # Use "unifuncs" or "original"
```

## Error Handling

The module includes robust error handling for:

1. JSON parsing errors with multiple recovery strategies
2. API connection errors
3. Empty or invalid responses
4. Network issues

## Dependencies

- Python 3.6+
- `asyncio`: For asynchronous processing
- `openai`: Client library for API communication
- `dotenv`: For loading environment variables
- Standard libraries: `os`, `re`, `json`, `time`, `datetime`, `typing`

## Integration with Existing Project

### Files Structure

The integration consists of the following files:

1. `services/project_idea_agent_with_unifuncs.py`: Core implementation using UniFuncs API
2. `services/project_idea_agent_adapter.py`: Adapter to maintain compatibility with original API
3. `services/project_idea_agent_factory.py`: Factory to switch between implementations
4. `test_adapter.py`: Test script to validate the adapter functionality

### Updating Import Statements

To update your project to use the factory pattern:

1. Find all instances of:
   ```python
   from services.project_idea_agent import generate_project_ideas
   ```
   
   Replace with:
   ```python
   from services.project_idea_agent_factory import get_project_idea_generator
   ```
   
   And update usage:
   ```python
   generate_project_ideas = get_project_idea_generator()
   ```

2. Find all instances of:
   ```python
   from services.project_idea_agent import ProjectIdeaAgentStreaming
   ```
   
   Replace with:
   ```python
   from services.project_idea_agent_factory import get_streaming_agent_class
   ```
   
   And update usage:
   ```python
   ProjectIdeaAgentStreaming = get_streaming_agent_class()
   ```

### Quota Management

Both the original implementation and the adapter maintain compatibility with the quota system:

- `check_quota(user_id)`: Checks if the user has available quota
- `deduct_quota(user_id, cost)`: Deducts from the user's quota after successful generation
