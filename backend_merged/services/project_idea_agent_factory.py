"""
project_idea_agent_factory.py - Factory pattern to choose between original and UniFuncs implementations
"""

import os
from typing import Dict, Any, Callable, Type

# Default to original implementation unless environment variable specifies UniFuncs
ACTIVE_AGENT = os.environ.get("ACTIVE_AGENT", "original").lower()

def get_project_idea_generator() -> Callable:
    """
    Returns the appropriate project idea generator function based on environment variables
    
    Returns:
        The original or adapter version of the generate_project_ideas function
    """
    if ACTIVE_AGENT == "unifuncs":
        try:
            from services.project_idea_agent_adapter import generate_project_ideas
            print("🔄 Using UniFuncs API for project idea generation")
            return generate_project_ideas
        except ImportError:
            from services.project_idea_agent import generate_project_ideas
            print("⚠️ UniFuncs adapter failed to load, falling back to original implementation")
            return generate_project_ideas
    else:
        from services.project_idea_agent import generate_project_ideas
        print("🔄 Using original API for project idea generation")
        return generate_project_ideas

def get_streaming_agent_class():
    """
    Returns the appropriate streaming agent class based on environment variables
    
    Returns:
        The original or adapter version of the ProjectIdeaAgentStreaming class
    """
    if ACTIVE_AGENT == "unifuncs":
        try:
            from services.project_idea_agent_adapter import ProjectIdeaAgentStreaming
            print("🔄 Using UniFuncs API for streaming project idea generation")
            return ProjectIdeaAgentStreaming
        except ImportError:
            from services.project_idea_agent import ProjectIdeaAgentStreaming
            print("⚠️ UniFuncs streaming adapter failed to load, falling back to original implementation")
            return ProjectIdeaAgentStreaming
    else:
        from services.project_idea_agent import ProjectIdeaAgentStreaming
        print("🔄 Using original API for streaming project idea generation")
        return ProjectIdeaAgentStreaming
