from sqlalchemy import Column, BigInteger, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from .base import Base

class ReportType(str, enum.Enum):
    """Types of reportable behavior"""
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

class ReportStatus(str, enum.Enum):
    """Status of report investigation"""
    PENDING = "pending"
    UNDER_REVIEW = "under_review"
    RESOLVED = "resolved"
    DISMISSED = "dismissed"

class ReportAction(str, enum.Enum):
    """Actions taken on reports"""
    WARNING = "warning"
    TEMPORARY_BAN = "temporary_ban"
    PERMANENT_BAN = "permanent_ban"
    CONTENT_REMOVED = "content_removed"
    NO_ACTION = "no_action"

class UserReport(Base):
    __tablename__ = "user_reports"
    
    id = Column(BigInteger, primary_key=True)
    reporter_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    reported_user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    report_type = Column(String(50), nullable=False)
    description_text = Column(Text, nullable=False)
    proof_image_url = Column(String(500))
    proof_image_data = Column(Text)
    status = Column(String(20), default='pending', nullable=False)
    moderator_id = Column(BigInteger, ForeignKey("users.id"))
    moderator_notes = Column(Text)
    moderator_action = Column(String(100))
    resolved_at = Column(DateTime)
    created_at = Column(DateTime, nullable=False, server_default=func.current_timestamp())
    updated_at = Column(DateTime, nullable=False, server_default=func.current_timestamp())
    
    reporter = relationship("User", foreign_keys=[reporter_id], back_populates="reports_made")
    reported_user = relationship("User", foreign_keys=[reported_user_id], back_populates="reports_received")
    moderator = relationship("User", foreign_keys=[moderator_id], back_populates="moderated_reports")
