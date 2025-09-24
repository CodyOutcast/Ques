"""
Project Ideas Router
Handles API endpoints for AI-powered project idea generation
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import json
import asyncio
from datetime import datetime

try:
    from dependencies.db import get_db
    from dependencies.auth import get_current_user
    from schemas.user import User
except ImportError:
    # Mock dependencies for standalone testing
    def get_db():
        return None
    def get_current_user():
        return {"id": 1}
    class User:
        id = 1

import os
from services.project_idea_agent import ProjectIdeaAgent, generate_project_ideas

router = APIRouter(prefix="/api/v1/project-ideas", tags=["project-ideas"])

# Lazy initialization of the agent
agent = None

def get_agent():
    """Get or initialize the project idea agent with proper error handling"""
    global agent
    if agent is None:
        try:
            # Check if required environment variables are set
            if not os.environ.get("SEARCHAPI_KEY") or not os.environ.get("DEEPSEEK_API_KEY_AGENT"):
                print("⚠️ Warning: SEARCHAPI_KEY and/or DEEPSEEK_API_KEY_AGENT not set. Project ideas service will be disabled.")
                return None
            agent = ProjectIdeaAgent()
            print("✅ Project Ideas Agent initialized successfully")
        except Exception as e:
            print(f"❌ Failed to initialize Project Ideas Agent: {e}")
            agent = None
    return agent

@router.post("/generate")
async def generate_ideas_endpoint(
    query: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate project ideas based on user query with membership limits"""
    try:
        # Check if agent is available
        current_agent = get_agent()
        if current_agent is None:
            raise HTTPException(
                status_code=503, 
                detail="Project ideas service is currently unavailable. Please contact administrator to configure SEARCHAPI_KEY and DEEPSEEK_API_KEY_AGENT environment variables."
            )
        
        if not query or len(query.strip()) < 3:
            raise HTTPException(status_code=400, detail="Query must be at least 3 characters long")
        
        # Check membership limits before processing
        from services.membership_service import MembershipService
        
        user_id = current_user.user_id if hasattr(current_user, 'user_id') else current_user.id
        can_generate, message, info = MembershipService.check_project_ideas_limit(db, user_id)
        
        if not can_generate:
            return {
                "error": "Generation limit reached",
                "message": message,
                "membership_info": info,
                "upgrade_required": info.get("membership_type") == "free"
            }
        
        # Generate ideas
        result = generate_project_ideas(query.strip(), user_id)
        
        # Log the usage for tracking
        MembershipService.log_usage(db, user_id, "project_ideas_generate", 1, {
            "query": query.strip(),
            "ideas_generated": len(result.get("project_ideas", [])) if result else 0
        })
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["message"])
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate ideas: {str(e)}")

@router.get("/test-scraping")
async def test_scraping_endpoint():
    """Test endpoint to verify scraping functionality"""
    try:
        current_agent = get_agent()
        if current_agent is None:
            raise HTTPException(
                status_code=503, 
                detail="Project ideas service is currently unavailable. Cannot run scraping test."
            )
        
        from services.project_idea_agent import test_scraping_anti_block
        
        # Run the test
        success = test_scraping_anti_block()
        
        return {
            "success": success,
            "message": "Scraping test completed successfully" if success else "Scraping test failed",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Test failed: {str(e)}")

@router.get("/health")
async def health_check():
    """Health check for the project ideas service"""
    try:
        current_agent = get_agent()
        if current_agent is None:
            return {
                "status": "service_disabled",
                "message": "Project ideas service is disabled due to missing environment variables",
                "services": {
                    "deepseek_api": "not_configured",
                    "search_api": "not_configured",
                    "crawl4ai": "not_available"
                },
                "timestamp": datetime.now().isoformat()
            }
        
        # Test API connections
        deepseek_ok = current_agent._test_deepseek_connection()
        
        return {
            "status": "healthy",
            "services": {
                "deepseek_api": "connected" if deepseek_ok else "disconnected",
                "search_api": "configured" if current_agent.searchapi_key else "not_configured",
                "crawl4ai": "available" if hasattr(current_agent, 'config') and current_agent.config else "not_available"
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")
