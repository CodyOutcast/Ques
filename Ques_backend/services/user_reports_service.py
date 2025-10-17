"""
User Reports Service
Handles user reporting business logic
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from models.user_reports import UserReport, ReportType, ReportStatus, ReportAction
from models.users import User


class UserReportsService:
    """Service for managing user reports"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def create_report(
        self,
        reporter_id: int,
        reported_user_id: int,
        report_type: ReportType,
        description: str,
        proof_text: Optional[str] = None,
        proof_image_urls: Optional[List[str]] = None,
        proof_chat_id: Optional[int] = None,
        proof_message_id: Optional[int] = None,
        platform_location: Optional[str] = None,
        is_anonymous: bool = False
    ) -> UserReport:
        """Create a new user report"""
        
        # Basic validation
        if reporter_id == reported_user_id:
            raise ValueError("Cannot report yourself")
        
        # Check if reported user exists
        reported_user = self.db.query(User).filter(User.id == reported_user_id).first()
        if not reported_user:
            raise ValueError("Reported user not found")
        
        # Create the report
        report = UserReport(
            reporter_id=reporter_id,
            reported_user_id=reported_user_id,
            report_type=report_type.value,
            description_text=description,
            proof_image_url=proof_image_urls[0] if proof_image_urls else None,
            proof_image_data=proof_text,
            status=ReportStatus.PENDING.value,
            created_at=datetime.utcnow()
        )
        
        self.db.add(report)
        self.db.commit()
        self.db.refresh(report)
        
        return report
    
    def get_reports_by_user(self, user_id: int, as_reporter: bool = True) -> List[UserReport]:
        """Get reports made by user (as_reporter=True) or against user (as_reporter=False)"""
        
        if as_reporter:
            return self.db.query(UserReport).filter(UserReport.reporter_id == user_id).all()
        else:
            return self.db.query(UserReport).filter(UserReport.reported_user_id == user_id).all()
    
    def get_pending_reports(self, limit: int = 50, urgent_only: bool = False) -> List[UserReport]:
        """Get pending reports for moderation"""
        
        query = self.db.query(UserReport).filter(UserReport.status == ReportStatus.PENDING.value)
        
        if urgent_only:
            # Define urgent report types
            urgent_types = [
                ReportType.VIOLENCE_THREATS.value,
                ReportType.HARASSMENT.value,
                ReportType.HATE_SPEECH.value
            ]
            query = query.filter(UserReport.report_type.in_(urgent_types))
        
        return query.order_by(UserReport.created_at.desc()).limit(limit).all()
    
    def assign_moderator(self, report_id: int, moderator_id: int) -> UserReport:
        """Assign a moderator to a report"""
        
        report = self.db.query(UserReport).filter(UserReport.id == report_id).first()
        if not report:
            raise ValueError("Report not found")
        
        if report.status != ReportStatus.PENDING.value:
            raise ValueError("Report is not pending")
        
        report.moderator_id = moderator_id
        report.status = ReportStatus.UNDER_REVIEW.value
        report.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(report)
        
        return report
    
    def resolve_report(
        self,
        report_id: int,
        action_taken: ReportAction,
        moderator_notes: Optional[str] = None,
        moderator_id: Optional[int] = None
    ) -> UserReport:
        """Resolve a report with an action"""
        
        report = self.db.query(UserReport).filter(UserReport.id == report_id).first()
        if not report:
            raise ValueError("Report not found")
        
        report.status = ReportStatus.RESOLVED.value
        report.moderator_action = action_taken.value
        report.moderator_notes = moderator_notes
        report.resolved_at = datetime.utcnow()
        report.updated_at = datetime.utcnow()
        
        if moderator_id:
            report.moderator_id = moderator_id
        
        self.db.commit()
        self.db.refresh(report)
        
        return report
    
    def dismiss_report(self, report_id: int, reason: str) -> UserReport:
        """Dismiss a report as invalid"""
        
        report = self.db.query(UserReport).filter(UserReport.id == report_id).first()
        if not report:
            raise ValueError("Report not found")
        
        report.status = ReportStatus.DISMISSED.value
        report.moderator_notes = f"Dismissed: {reason}"
        report.resolved_at = datetime.utcnow()
        report.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(report)
        
        return report
    
    def get_report_statistics(self, days: int = 30) -> Dict[str, Any]:
        """Get report statistics for the specified period"""
        
        since_date = datetime.utcnow() - timedelta(days=days)
        
        # Basic counts
        total_reports = self.db.query(UserReport).filter(UserReport.created_at >= since_date).count()
        pending_reports = self.db.query(UserReport).filter(
            UserReport.created_at >= since_date,
            UserReport.status == ReportStatus.PENDING.value
        ).count()
        resolved_reports = self.db.query(UserReport).filter(
            UserReport.created_at >= since_date,
            UserReport.status == ReportStatus.RESOLVED.value
        ).count()
        dismissed_reports = self.db.query(UserReport).filter(
            UserReport.created_at >= since_date,
            UserReport.status == ReportStatus.DISMISSED.value
        ).count()
        
        # Report type counts
        harassment_reports = self.db.query(UserReport).filter(
            UserReport.created_at >= since_date,
            UserReport.report_type == ReportType.HARASSMENT.value
        ).count()
        inappropriate_content_reports = self.db.query(UserReport).filter(
            UserReport.created_at >= since_date,
            UserReport.report_type == ReportType.INAPPROPRIATE_CONTENT.value
        ).count()
        spam_reports = self.db.query(UserReport).filter(
            UserReport.created_at >= since_date,
            UserReport.report_type == ReportType.SPAM.value
        ).count()
        fake_profile_reports = self.db.query(UserReport).filter(
            UserReport.created_at >= since_date,
            UserReport.report_type == ReportType.FAKE_PROFILE.value
        ).count()
        
        return {
            "total_reports": total_reports,
            "pending_reports": pending_reports,
            "resolved_reports": resolved_reports,
            "dismissed_reports": dismissed_reports,
            "harassment_reports": harassment_reports,
            "inappropriate_content_reports": inappropriate_content_reports,
            "spam_reports": spam_reports,
            "fake_profile_reports": fake_profile_reports,
            "average_severity": 3.5,  # Mock value
            "average_resolution_time_hours": 24.0,  # Mock value
            "period_days": days
        }
    
    def get_user_violation_history(self, user_id: int) -> List[UserReport]:
        """Get violation history for a user (reports against them that were resolved)"""
        
        return self.db.query(UserReport).filter(
            UserReport.reported_user_id == user_id,
            UserReport.status == ReportStatus.RESOLVED.value
        ).order_by(UserReport.resolved_at.desc()).all()