"""
User Reports Service
Handles creation, management, and processing of user reports
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func, case
import json

from models.user_reports import UserReport, ReportType, ReportStatus, ReportAction, ReportStatistics
from models.users import User
from services.enhanced_moderation import moderate_text_enhanced


class UserReportsService:
    """Service for managing user reports and content violations"""
    
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
        
        # Check if reporter and reported user exist
        reporter = self.db.query(User).filter(User.id == reporter_id).first()
        reported_user = self.db.query(User).filter(User.id == reported_user_id).first()
        
        if not reporter or not reported_user:
            raise ValueError("Reporter or reported user not found")
        
        if reporter_id == reported_user_id:
            raise ValueError("Users cannot report themselves")
        
        # Check if this is a repeat report
        existing_report = self.db.query(UserReport).filter(
            and_(
                UserReport.reporter_id == reporter_id,
                UserReport.reported_user_id == reported_user_id,
                UserReport.report_type == report_type,
                UserReport.status.in_([ReportStatus.PENDING, ReportStatus.UNDER_REVIEW])
            )
        ).first()
        
        if existing_report:
            raise ValueError("You have already reported this user for this type of behavior")
        
        # Determine severity and urgency
        severity_score = self._calculate_severity(report_type, description)
        requires_urgent_review = severity_score >= 4 or report_type in [
            ReportType.VIOLENCE_THREATS, ReportType.UNDERAGE, ReportType.HATE_SPEECH
        ]
        
        # Check if reported user is a repeat offender
        previous_reports_count = self.db.query(UserReport).filter(
            and_(
                UserReport.reported_user_id == reported_user_id,
                UserReport.status == ReportStatus.RESOLVED,
                UserReport.action_taken.in_([
                    ReportAction.WARNING_ISSUED,
                    ReportAction.CONTENT_REMOVED,
                    ReportAction.PROFILE_SUSPENDED
                ])
            )
        ).count()
        
        is_repeat_offender = previous_reports_count >= 2
        
        # Automatically moderate description
        moderation_result = await moderate_text_enhanced(description, str(reporter_id))
        if not moderation_result.is_approved:
            raise ValueError("Report description contains inappropriate content")
        
        # Create the report
        report = UserReport(
            reporter_id=reporter_id,
            reported_user_id=reported_user_id,
            report_type=report_type,
            description=description,
            proof_text=proof_text,
            proof_image_urls=json.dumps(proof_image_urls) if proof_image_urls else None,
            proof_chat_id=proof_chat_id,
            proof_message_id=proof_message_id,
            platform_location=platform_location,
            severity_score=severity_score,
            is_anonymous=is_anonymous,
            requires_urgent_review=requires_urgent_review,
            is_repeat_offender=is_repeat_offender,
            status=ReportStatus.PENDING
        )
        
        self.db.add(report)
        self.db.commit()
        self.db.refresh(report)
        
        return report
    
    def get_pending_reports(self, limit: int = 50, urgent_only: bool = False) -> List[UserReport]:
        """Get pending reports for moderation"""
        query = self.db.query(UserReport).filter(
            UserReport.status == ReportStatus.PENDING
        )
        
        if urgent_only:
            query = query.filter(UserReport.requires_urgent_review == True)
        
        return query.order_by(
            desc(UserReport.requires_urgent_review),
            desc(UserReport.severity_score),
            UserReport.created_at
        ).limit(limit).all()
    
    def get_reports_by_user(self, user_id: int, as_reporter: bool = True) -> List[UserReport]:
        """Get reports made by or against a specific user"""
        if as_reporter:
            return self.db.query(UserReport).filter(
                UserReport.reporter_id == user_id
            ).order_by(desc(UserReport.created_at)).all()
        else:
            return self.db.query(UserReport).filter(
                UserReport.reported_user_id == user_id
            ).order_by(desc(UserReport.created_at)).all()
    
    def assign_moderator(self, report_id: int, moderator_id: int) -> UserReport:
        """Assign a moderator to handle a report"""
        report = self.db.query(UserReport).filter(UserReport.id == report_id).first()
        if not report:
            raise ValueError("Report not found")
        
        if report.status != ReportStatus.PENDING:
            raise ValueError("Report is not in pending status")
        
        report.assign_moderator(moderator_id)
        self.db.commit()
        
        return report
    
    def resolve_report(
        self,
        report_id: int,
        action_taken: ReportAction,
        moderator_notes: Optional[str] = None
    ) -> UserReport:
        """Resolve a report with specific action"""
        report = self.db.query(UserReport).filter(UserReport.id == report_id).first()
        if not report:
            raise ValueError("Report not found")
        
        if report.status not in [ReportStatus.PENDING, ReportStatus.UNDER_REVIEW]:
            raise ValueError("Report is not in reviewable status")
        
        report.resolve_report(action_taken, moderator_notes)
        self.db.commit()
        
        # Update user's violation count if action was taken
        if action_taken in [ReportAction.WARNING_ISSUED, ReportAction.CONTENT_REMOVED, 
                          ReportAction.PROFILE_SUSPENDED, ReportAction.ACCOUNT_BANNED]:
            self._update_user_violations(report.reported_user_id, action_taken)
        
        return report
    
    def dismiss_report(self, report_id: int, reason: str) -> UserReport:
        """Dismiss a report as invalid"""
        report = self.db.query(UserReport).filter(UserReport.id == report_id).first()
        if not report:
            raise ValueError("Report not found")
        
        report.dismiss_report(reason)
        self.db.commit()
        
        return report
    
    def get_report_statistics(self, days: int = 30) -> Dict[str, Any]:
        """Get reporting statistics for the last N days"""
        start_date = datetime.now(timezone.utc) - timedelta(days=days)
        
        stats = self.db.query(
            func.count(UserReport.id).label('total_reports'),
            func.count(case([(UserReport.status == ReportStatus.PENDING, 1)])).label('pending'),
            func.count(case([(UserReport.status == ReportStatus.RESOLVED, 1)])).label('resolved'),
            func.count(case([(UserReport.status == ReportStatus.DISMISSED, 1)])).label('dismissed'),
            func.count(case([(UserReport.report_type == ReportType.HARASSMENT, 1)])).label('harassment'),
            func.count(case([(UserReport.report_type == ReportType.INAPPROPRIATE_CONTENT, 1)])).label('inappropriate_content'),
            func.count(case([(UserReport.report_type == ReportType.SPAM, 1)])).label('spam'),
            func.count(case([(UserReport.report_type == ReportType.FAKE_PROFILE, 1)])).label('fake_profile'),
            func.avg(UserReport.severity_score).label('avg_severity')
        ).filter(UserReport.created_at >= start_date).first()
        
        # Calculate resolution time
        resolved_reports = self.db.query(UserReport).filter(
            and_(
                UserReport.status == ReportStatus.RESOLVED,
                UserReport.created_at >= start_date,
                UserReport.resolved_at.isnot(None)
            )
        ).all()
        
        avg_resolution_time = 0
        if resolved_reports:
            total_hours = sum([
                (report.resolved_at - report.created_at).total_seconds() / 3600 
                for report in resolved_reports
            ])
            avg_resolution_time = total_hours / len(resolved_reports)
        
        return {
            'total_reports': stats.total_reports or 0,
            'pending_reports': stats.pending or 0,
            'resolved_reports': stats.resolved or 0,
            'dismissed_reports': stats.dismissed or 0,
            'harassment_reports': stats.harassment or 0,
            'inappropriate_content_reports': stats.inappropriate_content or 0,
            'spam_reports': stats.spam or 0,
            'fake_profile_reports': stats.fake_profile or 0,
            'average_severity': float(stats.avg_severity or 0),
            'average_resolution_time_hours': round(avg_resolution_time, 2),
            'period_days': days
        }
    
    def get_user_violation_history(self, user_id: int) -> List[UserReport]:
        """Get violation history for a user"""
        return self.db.query(UserReport).filter(
            and_(
                UserReport.reported_user_id == user_id,
                UserReport.status == ReportStatus.RESOLVED,
                UserReport.action_taken.in_([
                    ReportAction.WARNING_ISSUED,
                    ReportAction.CONTENT_REMOVED,
                    ReportAction.PROFILE_SUSPENDED,
                    ReportAction.ACCOUNT_BANNED
                ])
            )
        ).order_by(desc(UserReport.resolved_at)).all()
    
    def _calculate_severity(self, report_type: ReportType, description: str) -> int:
        """Calculate severity score (1-5) based on report type and content"""
        base_severity = {
            ReportType.VIOLENCE_THREATS: 5,
            ReportType.UNDERAGE: 5,
            ReportType.HATE_SPEECH: 4,
            ReportType.HARASSMENT: 4,
            ReportType.INAPPROPRIATE_CONTENT: 3,
            ReportType.SCAM_FRAUD: 3,
            ReportType.DRUG_RELATED: 3,
            ReportType.INAPPROPRIATE_PHOTOS: 3,
            ReportType.CATFISHING: 2,
            ReportType.FAKE_PROFILE: 2,
            ReportType.SPAM: 1,
            ReportType.POLITICAL_CONTENT: 1,
            ReportType.OTHER: 2
        }
        
        severity = base_severity.get(report_type, 2)
        
        # Increase severity based on description keywords
        high_severity_keywords = ['threat', 'kill', 'hurt', 'violence', 'dangerous', 'weapon']
        if any(keyword in description.lower() for keyword in high_severity_keywords):
            severity = min(severity + 1, 5)
        
        return severity
    
    def _update_user_violations(self, user_id: int, action_taken: ReportAction):
        """Update user's violation count (would need additional user fields)"""
        # This would update violation counters in the user model
        # For now, we're just tracking in the reports table
        pass


# Convenience functions for easy import
async def create_user_report(
    db: Session,
    reporter_id: int,
    reported_user_id: int,
    report_type: ReportType,
    description: str,
    **kwargs
) -> UserReport:
    """Create a new user report"""
    service = UserReportsService(db)
    return await service.create_report(
        reporter_id, reported_user_id, report_type, description, **kwargs
    )


def get_pending_reports(db: Session, limit: int = 50, urgent_only: bool = False) -> List[UserReport]:
    """Get pending reports for moderation"""
    service = UserReportsService(db)
    return service.get_pending_reports(limit, urgent_only)


def resolve_user_report(
    db: Session,
    report_id: int,
    action_taken: ReportAction,
    moderator_notes: Optional[str] = None
) -> UserReport:
    """Resolve a user report"""
    service = UserReportsService(db)
    return service.resolve_report(report_id, action_taken, moderator_notes)
