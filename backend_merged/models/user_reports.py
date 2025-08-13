"""
User Reports Model
Handles user-generated reports for inappropriate be    # Moderator handling
    moderator_id = Column(Integer, ForeignKey("users.user_id"), nullable=True)  # Admin who handled the casevior, content violations, and community guidelines violations
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import enum

from models.base import Base


class ReportType(enum.Enum):
    """Types of reportable behavior"""
    INAPPROPRIATE_CONTENT = "inappropriate_content"      # Explicit or sexual content
    HARASSMENT = "harassment"                            # Bullying, threats, unwanted contact
    SPAM = "spam"                                       # Promotional content, repetitive messages
    FAKE_PROFILE = "fake_profile"                       # Impersonation, fake information
    HATE_SPEECH = "hate_speech"                         # Discriminatory language
    DRUG_RELATED = "drug_related"                       # Drug sales, usage promotion
    SCAM_FRAUD = "scam_fraud"                          # Financial scams, money requests
    VIOLENCE_THREATS = "violence_threats"               # Threats of violence, dangerous behavior
    UNDERAGE = "underage"                              # User appears to be under 18
    INAPPROPRIATE_PHOTOS = "inappropriate_photos"       # NSFW images, explicit photos
    CATFISHING = "catfishing"                          # Using someone else's photos
    POLITICAL_CONTENT = "political_content"             # Inappropriate political content
    OTHER = "other"                                     # Other violations


class ReportStatus(enum.Enum):
    """Status of report investigation"""
    PENDING = "pending"           # Report submitted, awaiting review
    UNDER_REVIEW = "under_review" # Being investigated by moderators
    RESOLVED = "resolved"         # Action taken, case closed
    DISMISSED = "dismissed"       # No violation found
    ESCALATED = "escalated"       # Requires higher-level review


class ReportAction(enum.Enum):
    """Actions taken after report investigation"""
    NO_ACTION = "no_action"              # No violation found
    WARNING_ISSUED = "warning_issued"     # Warning sent to user
    CONTENT_REMOVED = "content_removed"   # Specific content deleted
    PROFILE_SUSPENDED = "profile_suspended" # Temporary account suspension
    ACCOUNT_BANNED = "account_banned"     # Permanent account ban
    UNDER_INVESTIGATION = "under_investigation" # Still investigating


class UserReport(Base):
    """
    User Reports Table
    Tracks all user-generated reports for community violations
    """
    __tablename__ = "user_reports"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # User relationships
    reporter_id = Column(Integer, ForeignKey("users.user_id"), nullable=False, index=True)
    reported_user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False, index=True)
    
    # Report details
    report_type = Column(SQLEnum(ReportType), nullable=False, index=True)
    description = Column(Text, nullable=False)  # User's description of the issue
    
    # Evidence/Proof
    proof_text = Column(Text, nullable=True)     # Text evidence (messages, profile content)
    proof_image_urls = Column(Text, nullable=True)  # JSON array of image URLs as evidence
    proof_chat_id = Column(Integer, ForeignKey("chats.chat_id"), nullable=True)  # Reference to chat if applicable
    proof_message_id = Column(Integer, ForeignKey("messages.message_id"), nullable=True)  # Specific message
    
    # Investigation status
    status = Column(SQLEnum(ReportStatus), default=ReportStatus.PENDING, nullable=False, index=True)
    action_taken = Column(SQLEnum(ReportAction), default=ReportAction.UNDER_INVESTIGATION, nullable=True)
    
    # Moderator handling
    moderator_id = Column(Integer, ForeignKey("users.user_id"), nullable=True)  # Admin who handled the case
    moderator_notes = Column(Text, nullable=True)  # Internal notes for moderators
    
    # Additional context
    platform_location = Column(String(100), nullable=True)  # Where the violation occurred (chat, profile, etc.)
    severity_score = Column(Integer, default=1)  # 1-5 severity rating
    
    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, index=True)
    reviewed_at = Column(DateTime, nullable=True)  # When moderator first reviewed
    resolved_at = Column(DateTime, nullable=True)  # When case was closed
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Flags
    is_anonymous = Column(Boolean, default=False)  # Reporter wants to remain anonymous
    requires_urgent_review = Column(Boolean, default=False)  # High priority cases
    is_repeat_offender = Column(Boolean, default=False)  # Reported user has previous violations
    
    # Relationships
    reporter = relationship("User", foreign_keys=[reporter_id], back_populates="reports_made")
    reported_user = relationship("User", foreign_keys=[reported_user_id], back_populates="reports_received")
    moderator = relationship("User", foreign_keys=[moderator_id])
    
    # Optional relationships to specific content
    related_chat = relationship("Chat", foreign_keys=[proof_chat_id])
    related_message = relationship("Message", foreign_keys=[proof_message_id])
    
    def __repr__(self):
        return f"<UserReport(id={self.id}, type={self.report_type.value}, reporter={self.reporter_id}, reported={self.reported_user_id}, status={self.status.value})>"
    
    @property
    def is_pending(self) -> bool:
        """Check if report is still pending review"""
        return self.status == ReportStatus.PENDING
    
    @property
    def is_resolved(self) -> bool:
        """Check if report has been resolved"""
        return self.status in [ReportStatus.RESOLVED, ReportStatus.DISMISSED]
    
    @property
    def days_since_reported(self) -> int:
        """Calculate days since report was made"""
        return (datetime.now(timezone.utc) - self.created_at).days
    
    def mark_as_urgent(self):
        """Mark report as requiring urgent review"""
        self.requires_urgent_review = True
        self.updated_at = datetime.now(timezone.utc)
    
    def assign_moderator(self, moderator_id: int):
        """Assign a moderator to handle this report"""
        self.moderator_id = moderator_id
        self.status = ReportStatus.UNDER_REVIEW
        self.reviewed_at = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)
    
    def resolve_report(self, action_taken: ReportAction, moderator_notes: str = None):
        """Resolve the report with an action"""
        self.action_taken = action_taken
        self.status = ReportStatus.RESOLVED
        self.resolved_at = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)
        
        if moderator_notes:
            self.moderator_notes = moderator_notes
    
    def dismiss_report(self, reason: str = None):
        """Dismiss report as invalid"""
        self.status = ReportStatus.DISMISSED
        self.action_taken = ReportAction.NO_ACTION
        self.resolved_at = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)
        
        if reason:
            self.moderator_notes = f"Dismissed: {reason}"


class ReportStatistics(Base):
    """
    Report Statistics Table
    Tracks aggregated reporting data for analytics and trend analysis
    """
    __tablename__ = "report_statistics"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Date tracking
    date = Column(DateTime, nullable=False, index=True)
    
    # Report counts by type
    total_reports = Column(Integer, default=0)
    pending_reports = Column(Integer, default=0)
    resolved_reports = Column(Integer, default=0)
    dismissed_reports = Column(Integer, default=0)
    
    # Report type breakdown
    harassment_reports = Column(Integer, default=0)
    inappropriate_content_reports = Column(Integer, default=0)
    spam_reports = Column(Integer, default=0)
    fake_profile_reports = Column(Integer, default=0)
    
    # Action statistics
    warnings_issued = Column(Integer, default=0)
    content_removed = Column(Integer, default=0)
    accounts_suspended = Column(Integer, default=0)
    accounts_banned = Column(Integer, default=0)
    
    # Performance metrics
    average_resolution_time_hours = Column(Integer, default=0)
    repeat_offender_reports = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    
    def __repr__(self):
        return f"<ReportStatistics(date={self.date}, total={self.total_reports})>"
