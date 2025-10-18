"""
Revenue Analytics API Router
Provides endpoints for revenue tracking and analytics
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional, List
from pydantic import BaseModel
from datetime import datetime
import logging

from dependencies.db import get_db
from dependencies.auth import get_current_user
from models.users import User
from services.revenue_analytics_service import RevenueAnalyticsService

router = APIRouter(prefix="/api/v1/revenue", tags=["Revenue Analytics"])
logger = logging.getLogger(__name__)

# === RESPONSE MODELS ===

class RevenueOverviewResponse(BaseModel):
    """Revenue overview response model"""
    period_days: int
    total_revenue: float
    transaction_count: int
    avg_daily_revenue: float
    avg_transaction_value: float
    revenue_growth_percent: float
    start_date: str
    end_date: str

class DailyRevenuePoint(BaseModel):
    """Daily revenue chart point"""
    date: str
    revenue: float
    transactions: int

class MonthlyRevenuePoint(BaseModel):
    """Monthly revenue chart point"""
    year: int
    month: int
    month_name: str
    revenue: float
    transactions: int

class RevenueBreakdownItem(BaseModel):
    """Revenue breakdown item"""
    plan_type: Optional[str] = None
    payment_method: Optional[str] = None
    revenue: float
    transactions: int
    percentage: float

class UserRevenueAnalytics(BaseModel):
    """User revenue analytics"""
    paying_users: int
    total_users: int
    conversion_rate_percent: float
    avg_revenue_per_user: float
    max_revenue_per_user: float
    total_revenue: float

class RecurringRevenueMetrics(BaseModel):
    """Recurring revenue metrics"""
    monthly_recurring_revenue: float
    annual_recurring_revenue: float
    active_subscribers: int
    calculation_date: str

class ChurnRetentionMetrics(BaseModel):
    """Churn and retention metrics"""
    users_last_month: int
    retained_users: int
    retention_rate_percent: float
    churn_rate_percent: float
    calculation_period: str

# === AUTHENTICATION HELPER ===

def get_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Ensure current user has admin privileges to access revenue data
    For now, we'll allow all authenticated users. In production, add admin check.
    """
    # TODO: Add admin role check
    # if not current_user.is_admin:
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="Admin privileges required"
    #     )
    return current_user

# === REVENUE ANALYTICS ENDPOINTS ===

@router.get("/overview", response_model=RevenueOverviewResponse)
async def get_revenue_overview(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Get revenue overview for the specified period
    """
    try:
        overview = RevenueAnalyticsService.get_revenue_overview(db, days)
        return RevenueOverviewResponse(**overview)
    except Exception as e:
        logger.error(f"Error getting revenue overview: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve revenue overview"
        )

@router.get("/chart/daily", response_model=List[DailyRevenuePoint])
async def get_daily_revenue_chart(
    days: int = Query(30, ge=1, le=365, description="Number of days for chart"),
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Get daily revenue data for charting
    """
    try:
        chart_data = RevenueAnalyticsService.get_daily_revenue_chart(db, days)
        return [DailyRevenuePoint(**point) for point in chart_data]
    except Exception as e:
        logger.error(f"Error getting daily revenue chart: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve daily revenue chart"
        )

@router.get("/chart/monthly", response_model=List[MonthlyRevenuePoint])
async def get_monthly_revenue_chart(
    months: int = Query(12, ge=1, le=24, description="Number of months for chart"),
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Get monthly revenue data for charting
    """
    try:
        chart_data = RevenueAnalyticsService.get_monthly_revenue_chart(db, months)
        return [MonthlyRevenuePoint(**point) for point in chart_data]
    except Exception as e:
        logger.error(f"Error getting monthly revenue chart: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve monthly revenue chart"
        )

@router.get("/breakdown/membership")
async def get_revenue_by_membership_type(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Get revenue breakdown by membership type
    """
    try:
        breakdown = RevenueAnalyticsService.get_revenue_by_membership_type(db, days)
        return {
            "period_days": days,
            "breakdown": breakdown,
            "total_plans": len(breakdown)
        }
    except Exception as e:
        logger.error(f"Error getting membership revenue breakdown: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve membership revenue breakdown"
        )

@router.get("/breakdown/payment-method")
async def get_revenue_by_payment_method(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Get revenue breakdown by payment method
    """
    try:
        breakdown = RevenueAnalyticsService.get_revenue_by_payment_method(db, days)
        return {
            "period_days": days,
            "breakdown": breakdown,
            "total_methods": len(breakdown)
        }
    except Exception as e:
        logger.error(f"Error getting payment method revenue breakdown: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve payment method revenue breakdown"
        )

@router.get("/analytics/users", response_model=UserRevenueAnalytics)
async def get_user_revenue_analytics(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Get user-related revenue analytics
    """
    try:
        analytics = RevenueAnalyticsService.get_user_revenue_analytics(db, days)
        return UserRevenueAnalytics(**analytics)
    except Exception as e:
        logger.error(f"Error getting user revenue analytics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user revenue analytics"
        )

@router.get("/metrics/recurring", response_model=RecurringRevenueMetrics)
async def get_recurring_revenue_metrics(
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Get recurring revenue metrics (MRR, ARR)
    """
    try:
        metrics = RevenueAnalyticsService.get_recurring_revenue_metrics(db)
        return RecurringRevenueMetrics(**metrics)
    except Exception as e:
        logger.error(f"Error getting recurring revenue metrics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve recurring revenue metrics"
        )

@router.get("/metrics/churn-retention", response_model=ChurnRetentionMetrics)
async def get_churn_retention_metrics(
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Get customer churn and retention metrics
    """
    try:
        metrics = RevenueAnalyticsService.get_churn_and_retention_metrics(db)
        return ChurnRetentionMetrics(**metrics)
    except Exception as e:
        logger.error(f"Error getting churn retention metrics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve churn retention metrics"
        )

@router.get("/report/comprehensive")
async def get_comprehensive_revenue_report(
    days: int = Query(30, ge=1, le=365, description="Number of days for overview analysis"),
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Get a comprehensive revenue report with all metrics
    """
    try:
        report = RevenueAnalyticsService.get_comprehensive_revenue_report(db, days)
        return {
            "report_generated_at": report["generated_at"],
            "analysis_period_days": days,
            "data": report
        }
    except Exception as e:
        logger.error(f"Error generating comprehensive revenue report: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate comprehensive revenue report"
        )

# === ADDITIONAL UTILITY ENDPOINTS ===

@router.get("/health")
async def revenue_analytics_health():
    """
    Health check endpoint for revenue analytics service
    """
    return {
        "status": "healthy",
        "service": "revenue_analytics",
        "timestamp": datetime.utcnow().isoformat(),
        "available_endpoints": [
            "/overview",
            "/chart/daily",
            "/chart/monthly", 
            "/breakdown/membership",
            "/breakdown/payment-method",
            "/analytics/users",
            "/metrics/recurring",
            "/metrics/churn-retention",
            "/report/comprehensive"
        ]
    }

@router.get("/export/csv")
async def export_revenue_data_csv(
    days: int = Query(30, ge=1, le=365, description="Number of days to export"),
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Export revenue data as CSV
    TODO: Implement CSV export functionality
    """
    # This would be implemented with pandas or csv module
    # For now, return JSON data that can be converted to CSV
    try:
        daily_data = RevenueAnalyticsService.get_daily_revenue_chart(db, days)
        return {
            "message": "CSV export endpoint - implementation pending",
            "data_format": "json",
            "daily_revenue_data": daily_data,
            "export_timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error exporting revenue data: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to export revenue data"
        )
