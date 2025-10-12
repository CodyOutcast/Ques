"""
Card Tracking Router
Complete card tracking and analytics system for monitoring
user interactions with cards, swiping patterns, and engagement metrics.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
import logging

from dependencies.db import get_db
from models.users import User
from services.auth_service import AuthService
from services.monitoring import log_security_event

router = APIRouter()
security = HTTPBearer()
logger = logging.getLogger(__name__)
auth_service = AuthService()

# ==================== Pydantic Models ====================

class CardInteraction(BaseModel):
    """Card interaction tracking model"""
    id: str
    user_id: str
    card_id: str
    card_type: str = Field(..., description="Type: profile, project, ai_recommendation")
    interaction_type: str = Field(..., description="Type: view, swipe_right, swipe_left, share, save, report")
    duration_seconds: Optional[int] = None
    position_in_stack: Optional[int] = None
    session_id: str
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None

class CardInteractionsResponse(BaseModel):
    """Response model for card interactions"""
    interactions: List[CardInteraction]
    total_count: int
    page: int
    limit: int
    has_more: bool

class TrackInteractionRequest(BaseModel):
    """Request model for tracking card interaction"""
    cardId: str
    cardType: str = Field(..., regex="^(profile|project|ai_recommendation)$")
    interactionType: str = Field(..., regex="^(view|swipe_right|swipe_left|share|save|report|skip)$")
    durationSeconds: Optional[int] = Field(None, ge=0, le=3600)
    positionInStack: Optional[int] = Field(None, ge=0)
    sessionId: str
    metadata: Optional[Dict[str, Any]] = None

class SwipingPattern(BaseModel):
    """User swiping pattern analysis"""
    user_id: str
    total_swipes: int
    right_swipes: int
    left_swipes: int
    swipe_ratio: float  # right/(right+left)
    avg_decision_time: float  # seconds
    peak_activity_hours: List[int]
    most_active_day: str
    cards_per_session: float
    engagement_score: float  # 0-100

class SwipingPatternsResponse(BaseModel):
    """Response model for swiping patterns"""
    patterns: SwipingPattern
    comparison_data: Optional[Dict[str, Any]] = None
    recommendations: List[str]

class CardPerformance(BaseModel):
    """Card performance metrics"""
    card_id: str
    card_type: str
    total_views: int
    right_swipes: int
    left_swipes: int
    shares: int
    saves: int
    reports: int
    engagement_rate: float
    avg_view_duration: float
    conversion_rate: float  # actions/views
    popularity_rank: Optional[int] = None

class CardPerformanceResponse(BaseModel):
    """Response model for card performance"""
    performances: List[CardPerformance]
    total_count: int
    page: int
    limit: int
    has_more: bool

class EngagementMetrics(BaseModel):
    """User engagement metrics"""
    daily_active_sessions: int
    avg_session_duration: float
    total_cards_viewed: int
    total_interactions: int
    engagement_trends: Dict[str, float]  # last 7 days
    retention_score: float
    activity_score: float

class EngagementMetricsResponse(BaseModel):
    """Response model for engagement metrics"""
    metrics: EngagementMetrics
    period: str
    comparison_period: Optional[EngagementMetrics] = None

class HeatmapData(BaseModel):
    """Heatmap data for card positions"""
    position: int
    interactions: int
    swipe_right_rate: float
    avg_duration: float

class HeatmapResponse(BaseModel):
    """Response model for interaction heatmap"""
    heatmap_data: List[HeatmapData]
    total_positions: int
    optimal_positions: List[int]

class SessionTracking(BaseModel):
    """Session tracking model"""
    session_id: str
    user_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    cards_viewed: int
    interactions_count: int
    duration_seconds: Optional[int] = None
    device_type: Optional[str] = None
    source: Optional[str] = None

class SessionTrackingResponse(BaseModel):
    """Response model for session tracking"""
    sessions: List[SessionTracking]
    total_count: int
    avg_session_duration: float
    total_cards_viewed: int

class ConversionFunnel(BaseModel):
    """Conversion funnel analysis"""
    step_name: str
    users_count: int
    conversion_rate: float
    drop_off_rate: float

class ConversionFunnelResponse(BaseModel):
    """Response model for conversion funnel"""
    funnel_steps: List[ConversionFunnel]
    overall_conversion: float
    bottleneck_step: str

# ==================== Endpoints ====================

@router.post("/interactions")
async def track_card_interaction(
    request: TrackInteractionRequest,
    token: str = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Track a card interaction event
    """
    try:
        current_user = auth_service.get_current_user(db, token.credentials)
        if not current_user:
            raise HTTPException(status_code=401, detail="Invalid token")

        # Create interaction record (mock implementation)
        interaction_id = f"int_{current_user.id}_{request.cardId}_{int(datetime.now().timestamp())}"
        
        # Log security event for suspicious patterns
        if request.interactionType == "report":
            log_security_event(
                current_user.id,
                "card_reported",
                {"card_id": request.cardId, "card_type": request.cardType}
            )
        
        logger.info(f"Tracked interaction: {request.interactionType} on {request.cardType} card {request.cardId} by user {current_user.id}")
        
        return {
            "interaction_id": interaction_id,
            "message": "Interaction tracked successfully",
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error tracking interaction: {e}")
        raise HTTPException(status_code=500, detail="Failed to track interaction")

@router.get("/interactions", response_model=CardInteractionsResponse)
async def get_card_interactions(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=200, description="Items per page"),
    card_type: Optional[str] = Query(None, description="Filter by card type"),
    interaction_type: Optional[str] = Query(None, description="Filter by interaction type"),
    start_date: Optional[datetime] = Query(None, description="Start date filter"),
    end_date: Optional[datetime] = Query(None, description="End date filter"),
    token: str = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Get user's card interaction history
    """
    try:
        current_user = auth_service.get_current_user(db, token.credentials)
        if not current_user:
            raise HTTPException(status_code=401, detail="Invalid token")

        # Calculate offset
        offset = (page - 1) * limit
        
        # Mock interactions data
        card_types = ["profile", "project", "ai_recommendation"]
        interaction_types = ["view", "swipe_right", "swipe_left", "share", "save", "report"]
        
        mock_interactions = []
        for i in range(1, 201):  # 200 mock interactions
            mock_interactions.append({
                "id": f"int_{i:06d}",
                "user_id": current_user.id,
                "card_id": f"card_{i % 50 + 1}",
                "card_type": card_types[i % len(card_types)],
                "interaction_type": interaction_types[i % len(interaction_types)],
                "duration_seconds": max(1, 30 - (i % 30)) if i % 3 == 0 else None,
                "position_in_stack": i % 10,
                "session_id": f"sess_{(i // 10) + 1}",
                "timestamp": datetime.now() - timedelta(hours=i),
                "metadata": {"source": "mobile_app"} if i % 4 == 0 else None
            })
        
        # Apply filters
        filtered_interactions = mock_interactions
        if card_type:
            filtered_interactions = [i for i in filtered_interactions if i["card_type"] == card_type]
        if interaction_type:
            filtered_interactions = [i for i in filtered_interactions if i["interaction_type"] == interaction_type]
        if start_date:
            filtered_interactions = [i for i in filtered_interactions if i["timestamp"] >= start_date]
        if end_date:
            filtered_interactions = [i for i in filtered_interactions if i["timestamp"] <= end_date]
        
        # Apply pagination
        total_count = len(filtered_interactions)
        paginated_interactions = filtered_interactions[offset:offset + limit]
        
        return CardInteractionsResponse(
            interactions=[CardInteraction(**i) for i in paginated_interactions],
            total_count=total_count,
            page=page,
            limit=limit,
            has_more=offset + limit < total_count
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting interactions: {e}")
        raise HTTPException(status_code=500, detail="Failed to get interactions")

@router.get("/patterns", response_model=SwipingPatternsResponse)
async def get_swiping_patterns(
    period_days: int = Query(30, ge=1, le=365, description="Analysis period in days"),
    token: str = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Get user's swiping pattern analysis
    """
    try:
        current_user = auth_service.get_current_user(db, token.credentials)
        if not current_user:
            raise HTTPException(status_code=401, detail="Invalid token")

        # Mock swiping pattern analysis
        total_swipes = 450
        right_swipes = 180
        left_swipes = 270
        
        patterns = SwipingPattern(
            user_id=current_user.id,
            total_swipes=total_swipes,
            right_swipes=right_swipes,
            left_swipes=left_swipes,
            swipe_ratio=round(right_swipes / total_swipes, 3),
            avg_decision_time=3.2,
            peak_activity_hours=[19, 20, 21, 22],  # 7-10 PM
            most_active_day="Saturday",
            cards_per_session=12.5,
            engagement_score=78.5
        )
        
        recommendations = [
            "You're most active in the evenings - consider using the app during peak hours for better matches",
            "Your decision time is average - take a moment to read profiles more carefully",
            "You have a balanced swiping ratio, showing good selectivity"
        ]
        
        return SwipingPatternsResponse(
            patterns=patterns,
            comparison_data={
                "avg_swipe_ratio": 0.35,
                "avg_decision_time": 4.1,
                "avg_engagement_score": 65.2
            },
            recommendations=recommendations
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting swiping patterns: {e}")
        raise HTTPException(status_code=500, detail="Failed to get swiping patterns")

@router.get("/performance", response_model=CardPerformanceResponse)
async def get_card_performance(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    card_type: Optional[str] = Query(None, description="Filter by card type"),
    sort_by: str = Query("engagement_rate", description="Sort by: engagement_rate, total_views, conversion_rate"),
    sort_order: str = Query("desc", regex="^(asc|desc)$"),
    token: str = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Get card performance metrics (for cards owned by user)
    """
    try:
        current_user = auth_service.get_current_user(db, token.credentials)
        if not current_user:
            raise HTTPException(status_code=401, detail="Invalid token")

        # Calculate offset
        offset = (page - 1) * limit
        
        # Mock card performance data
        mock_performances = []
        card_types = ["profile", "project", "ai_recommendation"]
        
        for i in range(1, 51):  # 50 mock cards
            total_views = max(50, 500 - i * 8)
            right_swipes = int(total_views * (0.1 + (i % 20) / 100))
            left_swipes = total_views - right_swipes
            
            mock_performances.append({
                "card_id": f"card_{i}",
                "card_type": card_types[i % len(card_types)],
                "total_views": total_views,
                "right_swipes": right_swipes,
                "left_swipes": left_swipes,
                "shares": max(0, right_swipes // 10),
                "saves": max(0, right_swipes // 8),
                "reports": max(0, total_views // 200),
                "engagement_rate": round((right_swipes + left_swipes) / total_views * 100, 2),
                "avg_view_duration": round(2.5 + (i % 10) * 0.3, 1),
                "conversion_rate": round(right_swipes / total_views * 100, 2),
                "popularity_rank": i
            })
        
        # Apply filters
        filtered_performances = mock_performances
        if card_type:
            filtered_performances = [p for p in filtered_performances if p["card_type"] == card_type]
        
        # Apply sorting
        reverse_order = sort_order == "desc"
        if sort_by in ["engagement_rate", "total_views", "conversion_rate"]:
            filtered_performances.sort(key=lambda x: x[sort_by], reverse=reverse_order)
        
        # Apply pagination
        total_count = len(filtered_performances)
        paginated_performances = filtered_performances[offset:offset + limit]
        
        return CardPerformanceResponse(
            performances=[CardPerformance(**p) for p in paginated_performances],
            total_count=total_count,
            page=page,
            limit=limit,
            has_more=offset + limit < total_count
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting card performance: {e}")
        raise HTTPException(status_code=500, detail="Failed to get card performance")

@router.get("/engagement", response_model=EngagementMetricsResponse)
async def get_engagement_metrics(
    period: str = Query("week", regex="^(day|week|month|quarter)$"),
    token: str = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Get user engagement metrics for specified period
    """
    try:
        current_user = auth_service.get_current_user(db, token.credentials)
        if not current_user:
            raise HTTPException(status_code=401, detail="Invalid token")

        # Mock engagement metrics
        metrics = EngagementMetrics(
            daily_active_sessions=3.2,
            avg_session_duration=8.5,  # minutes
            total_cards_viewed=145,
            total_interactions=89,
            engagement_trends={
                "day_1": 85.2,
                "day_2": 78.1,
                "day_3": 92.3,
                "day_4": 76.8,
                "day_5": 88.9,
                "day_6": 91.4,
                "day_7": 82.7
            },
            retention_score=87.5,
            activity_score=82.1
        )
        
        # Mock comparison data for previous period
        comparison_metrics = EngagementMetrics(
            daily_active_sessions=2.8,
            avg_session_duration=7.9,
            total_cards_viewed=132,
            total_interactions=76,
            engagement_trends={},  # Previous period trends
            retention_score=84.2,
            activity_score=79.3
        )
        
        return EngagementMetricsResponse(
            metrics=metrics,
            period=period,
            comparison_period=comparison_metrics
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting engagement metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get engagement metrics")

@router.get("/heatmap", response_model=HeatmapResponse)
async def get_interaction_heatmap(
    card_type: Optional[str] = Query(None, description="Filter by card type"),
    token: str = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Get interaction heatmap showing engagement by card position
    """
    try:
        current_user = auth_service.get_current_user(db, token.credentials)
        if not current_user:
            raise HTTPException(status_code=401, detail="Invalid token")

        # Mock heatmap data (positions 0-9)
        heatmap_data = []
        for position in range(10):
            interactions = max(20, 100 - position * 8)
            swipe_right_rate = max(0.05, 0.3 - position * 0.02)
            avg_duration = max(1.0, 5.0 - position * 0.3)
            
            heatmap_data.append({
                "position": position,
                "interactions": interactions,
                "swipe_right_rate": round(swipe_right_rate, 3),
                "avg_duration": round(avg_duration, 1)
            })
        
        # Identify optimal positions (top 3 by swipe_right_rate)
        sorted_positions = sorted(heatmap_data, key=lambda x: x["swipe_right_rate"], reverse=True)
        optimal_positions = [p["position"] for p in sorted_positions[:3]]
        
        return HeatmapResponse(
            heatmap_data=[HeatmapData(**h) for h in heatmap_data],
            total_positions=10,
            optimal_positions=optimal_positions
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting interaction heatmap: {e}")
        raise HTTPException(status_code=500, detail="Failed to get interaction heatmap")

@router.get("/sessions", response_model=SessionTrackingResponse)
async def get_session_tracking(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    days: int = Query(7, ge=1, le=90, description="Days to look back"),
    token: str = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Get session tracking data for user activity analysis
    """
    try:
        current_user = auth_service.get_current_user(db, token.credentials)
        if not current_user:
            raise HTTPException(status_code=401, detail="Invalid token")

        # Calculate offset
        offset = (page - 1) * limit
        
        # Mock session data
        mock_sessions = []
        device_types = ["mobile", "web", "tablet"]
        sources = ["app", "web", "social_link"]
        
        total_cards = 0
        total_duration = 0
        
        for i in range(1, 101):  # 100 mock sessions
            start_time = datetime.now() - timedelta(hours=i, minutes=i*2)
            duration = max(60, 600 - i * 4)  # seconds
            cards_viewed = max(1, 15 - i // 10)
            interactions = max(1, cards_viewed // 2)
            
            total_cards += cards_viewed
            total_duration += duration
            
            mock_sessions.append({
                "session_id": f"sess_{i:04d}",
                "user_id": current_user.id,
                "start_time": start_time,
                "end_time": start_time + timedelta(seconds=duration),
                "cards_viewed": cards_viewed,
                "interactions_count": interactions,
                "duration_seconds": duration,
                "device_type": device_types[i % len(device_types)],
                "source": sources[i % len(sources)]
            })
        
        # Apply pagination
        total_count = len(mock_sessions)
        paginated_sessions = mock_sessions[offset:offset + limit]
        
        return SessionTrackingResponse(
            sessions=[SessionTracking(**s) for s in paginated_sessions],
            total_count=total_count,
            avg_session_duration=round(total_duration / total_count / 60, 1),  # minutes
            total_cards_viewed=total_cards
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting session tracking: {e}")
        raise HTTPException(status_code=500, detail="Failed to get session tracking")

@router.get("/funnel", response_model=ConversionFunnelResponse)
async def get_conversion_funnel(
    period_days: int = Query(30, ge=1, le=365, description="Analysis period in days"),
    token: str = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Get conversion funnel analysis showing user journey
    """
    try:
        current_user = auth_service.get_current_user(db, token.credentials)
        if not current_user:
            raise HTTPException(status_code=401, detail="Invalid token")

        # Mock funnel data
        funnel_steps = [
            {"step_name": "Card Views", "users_count": 1000, "conversion_rate": 100.0, "drop_off_rate": 0.0},
            {"step_name": "Interactions", "users_count": 650, "conversion_rate": 65.0, "drop_off_rate": 35.0},
            {"step_name": "Right Swipes", "users_count": 320, "conversion_rate": 32.0, "drop_off_rate": 68.0},
            {"step_name": "Matches", "users_count": 95, "conversion_rate": 9.5, "drop_off_rate": 90.5},
            {"step_name": "Messages", "users_count": 42, "conversion_rate": 4.2, "drop_off_rate": 95.8},
        ]
        
        # Find bottleneck (largest drop-off)
        max_drop_off = 0
        bottleneck_step = ""
        for i in range(1, len(funnel_steps)):
            current_drop = funnel_steps[i-1]["users_count"] - funnel_steps[i]["users_count"]
            if current_drop > max_drop_off:
                max_drop_off = current_drop
                bottleneck_step = funnel_steps[i]["step_name"]
        
        return ConversionFunnelResponse(
            funnel_steps=[ConversionFunnel(**step) for step in funnel_steps],
            overall_conversion=4.2,  # Final step conversion rate
            bottleneck_step=bottleneck_step or "Right Swipes"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting conversion funnel: {e}")
        raise HTTPException(status_code=500, detail="Failed to get conversion funnel")