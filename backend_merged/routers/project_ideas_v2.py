"""
Enhanced project ideas router with membership limits and UniFuncs integration
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from pydantic import BaseModel

from dependencies.db import get_db
from dependencies.auth import get_current_user
from models.users import User
from services.membership_service import MembershipService

router = APIRouter(prefix="/api/v2/project-ideas", tags=["project-ideas-v2"])

class GenerateIdeasRequest(BaseModel):
    query: str
    language: Optional[str] = None  # "english" or "chinese", auto-detect if not provided
    agent_type: Optional[str] = "unifuncs"  # "unifuncs" or "legacy"
    stream: Optional[bool] = False  # Streaming response

class GenerateIdeasResponse(BaseModel):
    success: bool
    ideas: list = []
    query: str
    processing_time: float
    agent_used: str
    membership_info: Dict[str, Any]
    remaining_quota: Dict[str, Any]

@router.post("/generate", response_model=GenerateIdeasResponse)
async def generate_ideas_v2(
    request: GenerateIdeasRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate project ideas with membership limits and multiple agent support
    """
    try:
        # Validate query
        if not request.query or len(request.query.strip()) < 3:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Query must be at least 3 characters long"
            )
        
        user_id = current_user.user_id if hasattr(current_user, 'user_id') else current_user.id
        
        # Check membership limits
        can_generate, message, info = MembershipService.check_project_ideas_limit(db, user_id)
        
        if not can_generate:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "error": "Generation limit reached",
                    "message": message,
                    "membership_info": info,
                    "upgrade_required": info.get("membership_type") == "free"
                }
            )
        
        # Initialize result variables
        result = None
        agent_used = request.agent_type
        processing_time = 0
        
        # Generate ideas based on agent type
        if request.agent_type == "unifuncs":
            try:
                import time
                from robust_project_agent import RobustProjectIdeaAgent
                
                start_time = time.time()
                robust_agent = RobustProjectIdeaAgent()
                result = await robust_agent.generate_project_ideas(
                    query=request.query.strip(),
                    language=request.language,
                    stream=request.stream
                )
                processing_time = time.time() - start_time
                agent_used = result.get("agent", "unifuncs")
                
            except Exception as e:
                # Fallback to legacy agent if robust agent fails
                print(f"Robust agent failed: {e}, falling back to legacy agent")
                agent_used = "legacy_fallback"
                from services.project_idea_agent import generate_project_ideas
                result = generate_project_ideas(request.query.strip(), user_id)
                processing_time = result.get("processing_time", 0)
        
        else:  # legacy agent
            from services.project_idea_agent import generate_project_ideas
            result = generate_project_ideas(request.query.strip(), user_id)
            processing_time = result.get("processing_time", 0)
            agent_used = "legacy"
        
        # Extract ideas from result
        ideas = []
        if result:
            if isinstance(result, dict):
                ideas = result.get("ideas", []) or result.get("project_ideas", [])
            elif isinstance(result, list):
                ideas = result
        
        # Log the usage for tracking
        MembershipService.log_usage(db, user_id, "project_ideas_generate", 1, {
            "query": request.query.strip(),
            "agent_used": agent_used,
            "ideas_generated": len(ideas),
            "language": request.language,
            "success": len(ideas) > 0
        })
        
        # Get updated usage stats
        usage_stats = MembershipService.get_usage_stats(db, user_id)
        
        return GenerateIdeasResponse(
            success=len(ideas) > 0,
            ideas=ideas,
            query=request.query.strip(),
            processing_time=processing_time,
            agent_used=agent_used,
            membership_info={
                "membership_type": usage_stats["membership_type"],
                "is_paid": usage_stats["is_paid"]
            },
            remaining_quota={
                "can_generate_more": usage_stats["can_create_card"],  # Reuse this check
                "daily_usage": usage_stats["usage"]
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate project ideas: {str(e)}"
        )

@router.get("/quota")
async def get_quota_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current quota status for project ideas generation
    """
    try:
        user_id = current_user.user_id if hasattr(current_user, 'user_id') else current_user.id
        
        # Check current limits
        can_generate, message, info = MembershipService.check_project_ideas_limit(db, user_id)
        usage_stats = MembershipService.get_usage_stats(db, user_id)
        
        return {
            "can_generate": can_generate,
            "message": message,
            "quota_info": info,
            "membership": {
                "type": usage_stats["membership_type"],
                "is_paid": usage_stats["is_paid"],
                "limits": usage_stats["limits"]
            },
            "usage": usage_stats["usage"]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/agents")
async def get_available_agents():
    """
    Get list of available project idea generation agents
    """
    return {
        "agents": [
            {
                "name": "unifuncs",
                "display_name": "UniFuncs AI Agent",
                "description": "Advanced AI agent using UniFuncs deep research API for comprehensive project idea generation",
                "features": [
                    "Deep web research",
                    "Creative idea generation",
                    "Multiple language support",
                    "Real-time information gathering"
                ],
                "recommended": True
            },
            {
                "name": "legacy",
                "display_name": "Legacy Search Agent",
                "description": "Original project idea generation using DeepSeek API and web search",
                "features": [
                    "Web search integration",
                    "Structured idea format",
                    "Reliable performance"
                ],
                "recommended": False
            }
        ]
    }

@router.post("/test-unifuncs")
async def test_unifuncs_agent(
    query: str = "AI for education",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Test endpoint for UniFuncs agent (admin/testing only)
    """
    try:
        user_id = current_user.user_id if hasattr(current_user, 'user_id') else current_user.id
        
        # Check if this is a paid user or admin for testing
        membership = MembershipService.get_or_create_membership(db, user_id)
        
        from services.project_idea_agent_with_unifuncs import AdvancedSearchAgent
        import time
        
        start_time = time.time()
        agent = AdvancedSearchAgent()
        
        # Test the agent with a timeout
        try:
            result = await agent.generate_project_ideas(query, language="english", stream=False)
            processing_time = time.time() - start_time
            
            return {
                "status": "success",
                "result": result,
                "processing_time": processing_time,
                "membership_type": membership.membership_type.value,
                "query": query
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "processing_time": time.time() - start_time,
                "membership_type": membership.membership_type.value,
                "query": query
            }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
