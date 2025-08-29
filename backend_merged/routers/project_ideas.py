"""
Project Idea Generation Router
API endpoints for generating creative project ideas
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import Dict, Any, AsyncGenerator
import logging
import json
import asyncio
from datetime import datetime

from dependencies.db import get_db
from dependencies.auth import get_current_user
from models.users import User
from models.subscriptions import SubscriptionType
from services.project_idea_agent_factory import get_project_idea_generator, get_streaming_agent_class
from services.quota_service import QuotaService
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api/v1/project-ideas", tags=["Project Ideas"])
logger = logging.getLogger(__name__)


class ProjectIdeaRequest(BaseModel):
    """Request model for project idea generation"""
    query: str = Field(..., min_length=5, max_length=500, description="User's project query")
    
    class Config:
        schema_extra = {
            "example": {
                "query": "Build a simple chatbot with Python"
            }
        }


class ProjectIdeaResponse(BaseModel):
    """Response model for generated project ideas"""
    search_id: int
    original_query: str
    generated_prompts: list
    total_sources_found: int
    total_ideas_extracted: int
    project_ideas: list
    processing_time_seconds: float
    created_at: str
    
    class Config:
        schema_extra = {
            "example": {
                "search_id": 1234,
                "original_query": "Build a simple chatbot with Python",
                "generated_prompts": [
                    {
                        "prompt": "simple python chatbot tutorial examples",
                        "engine": "bing",
                        "results_count": 10
                    }
                ],
                "total_sources_found": 15,
                "total_ideas_extracted": 5,
                "project_ideas": [
                    {
                        "project_idea_title": "AI-Powered Customer Service Chatbot",
                        "project_scope": "Small team (2-3 people)",
                        "description": "Build an intelligent chatbot using Python and NLP",
                        "key_features": ["Natural language processing", "Context awareness"],
                        "estimated_timeline": "4-6 weeks",
                        "difficulty_level": "Intermediate",
                        "required_skills": ["Python", "NLP", "API integration"],
                        "similar_examples": ["https://example.com"],
                        "relevance_score": 0.95
                    }
                ],
                "processing_time_seconds": 45.2,
                "created_at": "2025-08-13T12:00:00"
            }
        }


@router.post("/generate", response_model=ProjectIdeaResponse, status_code=status.HTTP_201_CREATED)
async def generate_project_idea(
    request: ProjectIdeaRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate creative project ideas based on user query
    
    This endpoint:
    1. Checks user quota (10 requests per day)
    2. Uses AI to refine the query into search prompts
    3. Searches multiple engines (Bing, Baidu, Google) for relevant content
    4. Scrapes and analyzes web content
    5. Generates 3 unique, creative project ideas
    6. Deducts quota on success
    
    **Rate Limit:** Monthly quota based on subscription (Free: 30, Pro: 300)
    """
    user_id: int = current_user.user_id  # type: ignore
    
    try:
        logger.info(f"Generating project ideas for user {user_id}, query: {request.query}")
        
        # Check quota using new quota service
        has_quota, quota_info = QuotaService.check_quota(user_id)
        
        if not has_quota:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "error": "Monthly quota exceeded",
                    "message": f"You have used {quota_info['current_usage']}/{quota_info['monthly_limit']} requests this month",
                    "subscription_type": quota_info['subscription_type'],
                    "quota_reset_date": quota_info['quota_reset_date'],
                    "upgrade_message": "Upgrade to Pro for 300 requests per month" if quota_info['subscription_type'] == 'free' else None
                }
            )
        
        # Generate project ideas using the agent
        start_time = datetime.now()
        # Get current active project idea generator through factory
        generate_project_ideas = get_project_idea_generator()
        result = generate_project_ideas(request.query, user_id)
        processing_time = (datetime.now() - start_time).total_seconds()
        
        # Consume quota and log the successful request
        QuotaService.consume_quota(
            user_id=user_id,
            query=request.query,
            success=True,
            processing_time=processing_time,
            sources_found=result.get('total_sources_found'),
            ideas_extracted=result.get('total_ideas_extracted')
        )
        
        logger.info(f"Successfully generated {len(result['project_ideas'])} project ideas for user {user_id}")
        
        return result
        
    except HTTPException:
        # Re-raise HTTP exceptions (like quota exceeded)
        raise
    except ValueError as e:
        # Handle quota exceeded or validation errors
        if "quota" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "error": "Quota exceeded",
                    "message": "You have reached your daily limit of 10 project idea generations. Try again tomorrow.",
                    "quota_reset": "Daily quota resets at midnight UTC"
                }
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "Invalid request",
                    "message": str(e)
                }
            )
    
    except Exception as e:
        # Handle API errors and other failures
        logger.error(f"Project idea generation failed for user {user_id}: {str(e)}")
        
        # Check if it's an API-related error
        if "API error" in str(e) or "failed" in str(e):
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={
                    "error": "Service temporarily unavailable",
                    "message": "One or more external services are currently unavailable. Please try again later.",
                    "technical_details": str(e) if user_id == 1 else None  # Only show to admin
                }
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "error": "Internal server error",
                    "message": "An unexpected error occurred while generating project ideas."
                }
            )


@router.post("/generate/stream", status_code=status.HTTP_200_OK)
async def generate_project_idea_stream(
    request: ProjectIdeaRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate creative project ideas with real-time streaming logs
    
    This endpoint streams the entire process in real-time:
    1. Query refinement progress
    2. Web search results
    3. Content scraping updates  
    4. AI analysis and idea generation
    5. Final results
    
    **Response Format:** Server-Sent Events (SSE)
    **Rate Limit:** Monthly quota based on subscription (Free: 30, Pro: 300)
    """
    user_id: int = current_user.user_id  # type: ignore
    
    async def generate_with_streaming():
        """Generator function that yields SSE events"""
        try:
            # Check quota using new quota service
            has_quota, quota_info = QuotaService.check_quota(user_id)
            
            if not has_quota:
                error_event = {
                    'type': 'error',
                    'error': 'quota_exceeded', 
                    'message': f'Monthly quota exceeded: {quota_info["current_usage"]}/{quota_info["monthly_limit"]} requests used',
                    'subscription_type': quota_info['subscription_type'],
                    'quota_reset_date': quota_info['quota_reset_date'],
                    'upgrade_message': 'Upgrade to Pro for 300 requests per month' if quota_info['subscription_type'] == 'free' else None,
                    'timestamp': datetime.now().isoformat()
                }
                yield f"data: {json.dumps(error_event)}\n\n"
                return
            
            # Import the streaming version of the agent
            ProjectIdeaAgentStreaming = get_streaming_agent_class()
            
            # Send initial status with quota info
            initial_status = {
                'type': 'status', 
                'message': 'Starting project idea generation...', 
                'quota_info': {
                    'remaining': quota_info['remaining_quota'],
                    'subscription_type': quota_info['subscription_type']
                },
                'timestamp': datetime.now().isoformat()
            }
            yield f"data: {json.dumps(initial_status)}\n\n"
            
            # Create streaming agent instance
            agent = ProjectIdeaAgentStreaming()
            
            # Track processing time
            start_time = datetime.now()
            
            # Generate project ideas with streaming
            result = None
            async for event in agent.generate_project_ideas_stream(request.query, user_id):
                if event.get('type') == 'complete':
                    result = event.get('data', {})
                yield f"data: {json.dumps(event)}\n\n"
            
            # Consume quota and log the successful request
            processing_time = (datetime.now() - start_time).total_seconds()
            QuotaService.consume_quota(
                user_id=user_id,
                query=request.query,
                success=True,
                processing_time=processing_time,
                sources_found=result.get('total_sources_found') if result else None,
                ideas_extracted=result.get('total_ideas_extracted') if result else None
            )
                
        except ValueError as e:
            # Handle quota exceeded
            if "quota" in str(e).lower():
                error_event = {
                    'type': 'error',
                    'error': 'quota_exceeded', 
                    'message': 'You have reached your monthly quota limit.',
                    'timestamp': datetime.now().isoformat()
                }
                yield f"data: {json.dumps(error_event)}\n\n"
            else:
                # Log failed request
                QuotaService.consume_quota(
                    user_id=user_id,
                    query=request.query,
                    success=False,
                    error_message=str(e)
                )
                error_event = {
                    'type': 'error',
                    'error': 'validation_error',
                    'message': str(e),
                    'timestamp': datetime.now().isoformat()
                }
                yield f"data: {json.dumps(error_event)}\n\n"
                
        except Exception as e:
            logger.error(f"Streaming project idea generation failed for user {user_id}: {str(e)}")
            error_event = {
                'type': 'error',
                'error': 'generation_failed',
                'message': 'Failed to generate project ideas. Please try again.',
                'timestamp': datetime.now().isoformat()
            }
            yield f"data: {json.dumps(error_event)}\n\n"
            
        finally:
            # Send completion event
            completion_event = {
                'type': 'complete',
                'message': 'Stream completed',
                'timestamp': datetime.now().isoformat()
            }
            yield f"data: {json.dumps(completion_event)}\n\n"
    
    return StreamingResponse(
        generate_with_streaming(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Cache-Control"
        }
    )


@router.get("/quota", status_code=status.HTTP_200_OK)
async def get_quota_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Check current user's quota status for project idea generation
    
    Returns information about:
    - Subscription type (free/pro)
    - Monthly quota limit
    - Current period usage
    - Remaining quota
    - Next reset time
    - Quota percentage used
    """
    user_id: int = current_user.user_id  # type: ignore
    
    try:
        quota_status = QuotaService.get_quota_status(user_id)
        return quota_status
        
    except Exception as e:
        logger.error(f"Failed to get quota status for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Failed to retrieve quota status",
                "message": "Please try again later"
            }
        )


@router.get("/usage-history", status_code=status.HTTP_200_OK)
async def get_usage_history(
    days: int = 30,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user's project idea generation usage history
    
    Query Parameters:
    - days: Number of days to look back (default: 30, max: 90)
    
    Returns:
    - Total requests in period
    - Success rate
    - Daily usage breakdown
    - Recent requests
    """
    user_id: int = current_user.user_id  # type: ignore
    
    # Limit days to reasonable range
    days = min(max(days, 1), 90)
    
    try:
        usage_history = QuotaService.get_usage_history(user_id, days)
        return usage_history
        
    except Exception as e:
        logger.error(f"Failed to get usage history for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Failed to retrieve usage history",
                "message": "Please try again later"
            }
        )


class SubscriptionUpgradeRequest(BaseModel):
    """Request model for subscription upgrade"""
    subscription_type: SubscriptionType = Field(..., description="Target subscription type")
    
    class Config:
        schema_extra = {
            "example": {
                "subscription_type": "pro"
            }
        }


@router.post("/upgrade-subscription", status_code=status.HTTP_200_OK)
async def upgrade_subscription(
    request: SubscriptionUpgradeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upgrade user subscription
    
    Available subscription types:
    - free: 30 requests per month
    - pro: 300 requests per month
    - enterprise: 1000 requests per month (contact support)
    
    Note: This is a simplified implementation. In production, this would
    integrate with payment processing before upgrading the subscription.
    """
    user_id: int = current_user.user_id  # type: ignore
    
    try:
        # In production, you would validate payment here
        success = QuotaService.upgrade_subscription(user_id, request.subscription_type)
        
        if success:
            # Get updated quota status
            quota_status = QuotaService.get_quota_status(user_id)
            
            return {
                "message": f"Successfully upgraded to {request.subscription_type.value}",
                "subscription_type": request.subscription_type.value,
                "new_monthly_limit": quota_status["monthly_limit"],
                "remaining_quota": quota_status["remaining_quota"],
                "quota_reset_date": quota_status["quota_reset_date"]
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "error": "Upgrade failed",
                    "message": "Unable to upgrade subscription at this time"
                }
            )
            
    except Exception as e:
        logger.error(f"Failed to upgrade subscription for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Upgrade failed",
                "message": "Please try again later"
            }
        )


@router.post("/reset-quota", status_code=status.HTTP_200_OK)
async def reset_quota(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Reset quota for current user (admin function or emergency reset)
    
    This endpoint resets the current period usage to 0.
    Use with caution as it allows users to exceed normal limits.
    """
    user_id: int = current_user.user_id  # type: ignore
    
    try:
        success = QuotaService.reset_quota(user_id)
        
        if success:
            quota_status = QuotaService.get_quota_status(user_id)
            return {
                "message": "Quota reset successfully",
                "remaining_quota": quota_status["remaining_quota"],
                "monthly_limit": quota_status["monthly_limit"]
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "error": "Reset failed",
                    "message": "Unable to reset quota at this time"
                }
            )
            
    except Exception as e:
        logger.error(f"Failed to reset quota for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Reset failed",
                "message": "Please try again later"
            }
        )
