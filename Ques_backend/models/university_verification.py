"""
University verification model following DATABASE_STRUCTURE_UPDATE.md
"""

from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, ForeignKey, BigInteger
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
import uuid

from .base import Base


class UniversityVerification(Base):
    """Model for managing university email verifications"""
    
    __tablename__ = "university_verifications"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    email = Column(String(255), nullable=False, index=True)
    university_name = Column(String(255), nullable=False)
    domain = Column(String(100), nullable=False, index=True)
    verification_token = Column(String(255), nullable=False, unique=True, index=True)
    verified = Column(Boolean, nullable=False, default=False)
    expires_at = Column(TIMESTAMP, nullable=False)
    verified_at = Column(TIMESTAMP, nullable=True)
    attempts = Column(Integer, nullable=False, default=0)
    
    # Relationship
    user = relationship("User", back_populates="university_verification")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.expires_at:
            # Token expires in 24 hours
            self.expires_at = datetime.utcnow() + timedelta(hours=24)
    
    def is_expired(self) -> bool:
        """Check if the verification token has expired"""
        return datetime.utcnow() > self.expires_at
    
    def can_resend(self) -> bool:
        """Check if verification email can be resent (limit attempts)"""
        return self.attempts < 3 and not self.verified
    
    def mark_verified(self):
        """Mark the verification as completed"""
        self.verified = True
        self.verified_at = datetime.utcnow()
    
    def __repr__(self):
        return f"<UniversityVerification(id={self.id}, email={self.email}, verified={self.verified})>"