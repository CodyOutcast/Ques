"""
User Reports API Endpoints
Handles user reporting functionality for inappropriate behavior and content
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum

from dependencies.db import get_db
from dependencies.auth import get_current_user
from models.users import User
from models.user_reports import UserReport, ReportType, ReportStatus, ReportAction
from services.user_reports_service import UserReportsService


router = APIRouter(prefix="/reports", tags=["User Reports"])


# Pydantic models for API
class ReportTypeEnum(str, Enum):
    """Report types for API"""
    INAPPROPRIATE_CONTENT = "inappropriate_content"
    HARASSMENT = "harassment"
    SPAM = "spam"
    FAKE_PROFILE = "fake_profile"
    HATE_SPEECH = "hate_speech"
    DRUG_RELATED = "drug_related"
    SCAM_FRAUD = "scam_fraud"
    VIOLENCE_THREATS = "violence_threats"
    UNDERAGE = "underage"
    INAPPROPRIATE_PHOTOS = "inappropriate_photos"
    CATFISHING = "catfishing"
    POLITICAL_CONTENT = "political_content"
    OTHER = "other"


class CreateReportRequest(BaseModel):
    """Request model for creating a new report"""
    reported_user_id: int = Field(..., description="ID of the user being reported")
    report_type: ReportTypeEnum = Field(..., description="Type of violation being reported")
    description: str = Field(..., min_length=10, max_length=1000, description="Detailed description of the violation")
    proof_text: Optional[str] = Field(None, max_length=2000, description="Text evidence (messages, profile content)")
    proof_image_urls: Optional[List[str]] = Field(None, description="URLs of image evidence")
    proof_chat_id: Optional[int] = Field(None, description="Chat ID if violation occurred in chat")
    proof_message_id: Optional[int] = Field(None, description="Message ID if reporting specific message")
    platform_location: Optional[str] = Field(None, max_length=100, description="Where violation occurred")
    is_anonymous: Optional[bool] = Field(False, description="Whether reporter wants to remain anonymous")


class ReportResponse(BaseModel):
    """Response model for report data"""
    id: int
    reporter_id: int
    reported_user_id: int
    report_type: str
    description: str
    status: str
    severity_score: int
    platform_location: Optional[str]
    is_anonymous: bool
    requires_urgent_review: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class ReportDetailResponse(ReportResponse):
    """Detailed report response for moderators"""
    proof_text: Optional[str]
    proof_image_urls: Optional[str]
    proof_chat_id: Optional[int]
    proof_message_id: Optional[int]
    moderator_id: Optional[int]
    moderator_notes: Optional[str]
    action_taken: Optional[str]
    reviewed_at: Optional[datetime]
    resolved_at: Optional[datetime]
    is_repeat_offender: bool


class ReportStatisticsResponse(BaseModel):
    """Report statistics response"""
    total_reports: int
    pending_reports: int
    resolved_reports: int
    dismissed_reports: int
    harassment_reports: int
    inappropriate_content_reports: int
    spam_reports: int
    fake_profile_reports: int
    average_severity: float
    average_resolution_time_hours: float
    period_days: int


class ResolveReportRequest(BaseModel):
    """Request model for resolving a report"""
    action_taken: str = Field(..., description="Action taken (warning_issued, content_removed, etc.)")
    moderator_notes: Optional[str] = Field(None, max_length=1000, description="Moderator notes")


@router.post("/create", response_model=ReportResponse)
async def create_report(
    request: CreateReportRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new user report"""
    try:
        service = UserReportsService(db)
        
        # Convert enum to model enum
        report_type = ReportType(request.report_type.value)
        
        report = await service.create_report(
            reporter_id=current_user.id,
            reported_user_id=request.reported_user_id,
            report_type=report_type,
            description=request.description,
            proof_text=request.proof_text,
            proof_image_urls=request.proof_image_urls,
            proof_chat_id=request.proof_chat_id,
            proof_message_id=request.proof_message_id,
            platform_location=request.platform_location,
            is_anonymous=request.is_anonymous
        )
        
        return ReportResponse.from_orm(report)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create report"
        )


@router.get("/my-reports", response_model=List[ReportResponse])
async def get_my_reports(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get reports made by the current user"""
    service = UserReportsService(db)
    reports = service.get_reports_by_user(current_user.id, as_reporter=True)
    
    return [ReportResponse.from_orm(report) for report in reports]


@router.get("/against-me", response_model=List[ReportResponse])
async def get_reports_against_me(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get reports made against the current user (limited info)"""
    service = UserReportsService(db)
    reports = service.get_reports_by_user(current_user.id, as_reporter=False)
    
    # Filter sensitive information for reported users
    filtered_reports = []
    for report in reports:
        if report.status in [ReportStatus.RESOLVED, ReportStatus.DISMISSED]:
            filtered_reports.append(report)
    
    return [ReportResponse.from_orm(report) for report in filtered_reports]


# Moderator endpoints (would need admin permissions)
@router.get("/pending", response_model=List[ReportDetailResponse])
async def get_pending_reports(
    urgent_only: bool = Query(False, description="Only return urgent reports"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of reports to return"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get pending reports for moderation (Admin only)"""
    # TODO: Add admin role check
    # if not current_user.is_admin:
    #     raise HTTPException(status_code=403, detail="Admin access required")
    
    service = UserReportsService(db)
    reports = service.get_pending_reports(limit=limit, urgent_only=urgent_only)
    
    return [ReportDetailResponse.from_orm(report) for report in reports]


@router.get("/{report_id}", response_model=ReportDetailResponse)
async def get_report_details(
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed information about a specific report (Admin only)"""
    # TODO: Add admin role check
    # if not current_user.is_admin:
    #     raise HTTPException(status_code=403, detail="Admin access required")
    
    report = db.query(UserReport).filter(UserReport.id == report_id).first()
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    return ReportDetailResponse.from_orm(report)


@router.post("/{report_id}/assign", response_model=ReportDetailResponse)
async def assign_moderator(
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Assign current user as moderator for a report (Admin only)"""
    # TODO: Add admin role check
    # if not current_user.is_admin:
    #     raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        service = UserReportsService(db)
        report = service.assign_moderator(report_id, current_user.id)
        return ReportDetailResponse.from_orm(report)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{report_id}/resolve", response_model=ReportDetailResponse)
async def resolve_report(
    report_id: int,
    request: ResolveReportRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Resolve a report with specific action (Admin only)"""
    # TODO: Add admin role check
    # if not current_user.is_admin:
    #     raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        # Validate action
        action_taken = ReportAction(request.action_taken)
        
        service = UserReportsService(db)
        report = service.resolve_report(
            report_id=report_id,
            action_taken=action_taken,
            moderator_notes=request.moderator_notes
        )
        
        return ReportDetailResponse.from_orm(report)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


class DismissReportRequest(BaseModel):
    """Request model for dismissing a report"""
    reason: str = Field(..., min_length=5, max_length=500, description="Reason for dismissal")


@router.post("/{report_id}/dismiss", response_model=ReportDetailResponse)
async def dismiss_report(
    report_id: int,
    request: DismissReportRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Dismiss a report as invalid (Admin only)"""
    # TODO: Add admin role check
    # if not current_user.is_admin:
    #     raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        service = UserReportsService(db)
        report = service.dismiss_report(report_id, request.reason)
        return ReportDetailResponse.from_orm(report)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/statistics/overview", response_model=ReportStatisticsResponse)
async def get_report_statistics(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get reporting statistics for the last N days (Admin only)"""
    # TODO: Add admin role check
    # if not current_user.is_admin:
    #     raise HTTPException(status_code=403, detail="Admin access required")
    
    service = UserReportsService(db)
    stats = service.get_report_statistics(days=days)
    
    return ReportStatisticsResponse(**stats)


@router.get("/user/{user_id}/violations", response_model=List[ReportDetailResponse])
async def get_user_violations(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get violation history for a specific user (Admin only)"""
    # TODO: Add admin role check
    # if not current_user.is_admin:
    #     raise HTTPException(status_code=403, detail="Admin access required")
    
    service = UserReportsService(db)
    violations = service.get_user_violation_history(user_id)
    
    return [ReportDetailResponse.from_orm(violation) for violation in violations]
