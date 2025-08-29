"""
project_idea_agent_adapter.py - Adapter to use UniFuncs API with original API interface
"""

import asyncio
import os
from typing import Dict, Any
from datetime import datetime

# Import quota management
from db_utils import check_quota, deduct_quota

# Import new implementation
from services.project_idea_agent_with_unifuncs import AdvancedSearchAgent

def generate_project_ideas(query: str, user_id: int) -> Dict[str, Any]:
    """
    Adapter function that maintains compatibility with the original API interface
    while using the new UniFuncs implementation
    
    Args:
        query: User's project query
        user_id: User ID (for quota checking)
        
    Returns:
        Dict containing project ideas and metadata
    """
    # Check quota
    if not check_quota(user_id):
        raise ValueError("Quota exceeded")
    
    try:
        # Initialize new Agent
        agent = AdvancedSearchAgent()
        
        # Call async function and wait for results
        # Standard approach to call async functions in a synchronous context
        result = asyncio.run(agent.generate_project_ideas(query))
        
        # Deduct quota
        deduct_quota(user_id, cost=1)
        
        return result
        
    except Exception as e:
        # Maintain consistent error handling with original implementation
        raise Exception(f"Project idea generation failed: {str(e)}")


class ProjectIdeaAgentStreaming:
    """Adapter class compatible with the original streaming API"""
    
    def __init__(self):
        self.agent = AdvancedSearchAgent()
    
    async def generate_project_ideas_stream(self, query: str, user_id: int):
        """
        Generate project ideas and return progress as a stream
        
        Args:
            query: User's project query
            user_id: User ID (for quota checking)
            
        Yields:
            Dict events with progress updates
        """
        # Check quota
        yield {
            'type': 'progress',
            'step': 'quota_check',
            'message': 'Checking user quota...',
            'timestamp': datetime.now().isoformat()
        }
        
        if not check_quota(user_id):
            raise ValueError("Quota exceeded")
            
        yield {
            'type': 'progress', 
            'step': 'quota_check',
            'message': '✅ Quota check passed',
            'timestamp': datetime.now().isoformat()
        }
        
        # Call the streaming interface of the new implementation with thinking process (include_reasoning=True)
        from services.project_idea_agent_with_unifuncs import AdvancedSearchAgentStreaming
        stream_agent = AdvancedSearchAgentStreaming()
        
        try:
            async for event in stream_agent.generate_project_ideas_stream(query, user_id, include_reasoning=True):
                # Pass through events directly
                yield event
                
            # Deduct quota after successful processing
            deduct_quota(user_id, cost=1)
            
        except Exception as e:
            yield {
                'type': 'error',
                'step': 'generation_failed',
                'message': f'❌ Generation failed: {str(e)}',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
            raise
