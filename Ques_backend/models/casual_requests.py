"""
Casual Requests Database Model
Stores casual social activity requests from users
Only one active request per user is maintained
"""

from sqlalchemy import Column, String, Text, Boolean, DateTime, Integer, UniqueConstraint, Index, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Session, relationship
from sqlalchemy.sql import func
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any

from .base import Base


class CasualRequest(Base):
    """
    Casual Request Model
    
    Stores social activity requests from users. Each user can only have one active
    request at a time (enforced by unique constraint on user_id).
    
    Based on casual_request_integration_guide_en.md specifications:
    - user_id: VARCHAR(50) with UNIQUE constraint 
    - query: Original request text
    - optimized_query: AI-optimized version for better matching
    - is_active: Boolean flag for request status
    - location: Optional location information  
    - preferences: JSONB for flexible user preferences
    - Automatic cleanup of requests older than 7 days with no activity
    """
    __tablename__ = "casual_requests"

    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # User identification - UNIQUE to ensure only one record per user
    user_id = Column(String(50), nullable=False, unique=True, index=True)
    
    # Request content
    query = Column(Text, nullable=False, comment="Original request text")
    optimized_query = Column(Text, nullable=False, comment="AI-optimized request text for better matching")
    
    # Status and metadata
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    
    # Location using foreign keys (matching user_profiles pattern)
    province_id = Column(Integer, ForeignKey('provinces.id'), nullable=True, comment="Province ID referencing provinces table")
    city_id = Column(Integer, ForeignKey('cities.id'), nullable=True, comment="City ID referencing cities table")
    
    preferences = Column(JSONB, nullable=True, comment="User preferences as JSON object")
    
    # Relationships
    province = relationship("Province", foreign_keys=[province_id])
    city = relationship("City", foreign_keys=[city_id])
    
    # Timestamps for lifecycle management
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    last_activity_at = Column(DateTime, default=func.now(), nullable=False, index=True, 
                             comment="Used for cleaning up expired data")

    # Database constraints and indexes
    __table_args__ = (
        # Unique constraint on user_id to ensure one request per user
        UniqueConstraint('user_id', name='uq_casual_requests_user_id'),
        
        # Index on last_activity_at for efficient cleanup queries
        Index('idx_casual_requests_last_activity', 'last_activity_at'),
        
        # Indexes for location-based searches  
        Index('idx_casual_requests_province_id', 'province_id'),
        Index('idx_casual_requests_city_id', 'city_id'),
        Index('idx_casual_requests_location_combo', 'province_id', 'city_id'),
        
        # Composite index for active status and location
        Index('idx_casual_requests_active_location', 'is_active', 'province_id', 'city_id'),
    )

    def __repr__(self):
        return f"<CasualRequest(id={self.id}, user_id='{self.user_id}', active={self.is_active})>"

    def update_activity(self, db: Session):
        """Update the last_activity_at timestamp"""
        self.last_activity_at = datetime.utcnow()
        db.commit()

    def deactivate(self, db: Session):
        """Deactivate this casual request"""
        self.is_active = False
        self.updated_at = datetime.utcnow()
        db.commit()

    @classmethod
    def upsert_request(
        cls,
        db: Session,
        user_id: str,
        query: str,
        optimized_query: str,
        province_id: Optional[int] = None,
        city_id: Optional[int] = None,
        preferences: Optional[Dict[str, Any]] = None
    ) -> 'CasualRequest':
        """
        Create new request or update existing one for user
        
        Args:
            db: Database session
            user_id: User identifier
            query: Original request text
            optimized_query: AI-optimized version
            location: Optional location
            preferences: Optional preferences JSON
            
        Returns:
            CasualRequest: The created or updated request
        """
        # Try to find existing request
        existing = db.query(cls).filter(cls.user_id == user_id).first()
        
        if existing:
            # Update existing request
            existing.query = query
            existing.optimized_query = optimized_query
            existing.province_id = province_id
            existing.city_id = city_id
            existing.preferences = preferences
            existing.is_active = True
            existing.updated_at = datetime.utcnow()
            existing.last_activity_at = datetime.utcnow()
        else:
            # Create new request
            existing = cls(
                user_id=user_id,
                query=query,
                optimized_query=optimized_query,
                province_id=province_id,
                city_id=city_id,
                preferences=preferences,
                is_active=True
            )
            db.add(existing)
        
        db.commit()
        db.refresh(existing)
        return existing

    @classmethod
    def get_active_by_user(cls, db: Session, user_id: str) -> Optional['CasualRequest']:
        """Get the active casual request for a specific user"""
        return db.query(cls).filter(
            cls.user_id == user_id,
            cls.is_active == True
        ).first()

    @classmethod
    def get_active_requests(cls, db: Session, limit: int = 50) -> List['CasualRequest']:
        """Get all active casual requests"""
        return db.query(cls).filter(
            cls.is_active == True
        ).order_by(
            cls.last_activity_at.desc()
        ).limit(limit).all()

    @classmethod
    def search_by_location(cls, db: Session, province_id: Optional[int] = None, city_id: Optional[int] = None, limit: int = 50) -> List['CasualRequest']:
        """Search active requests by province and/or city"""
        query = db.query(cls).filter(cls.is_active == True)
        
        if province_id is not None:
            query = query.filter(cls.province_id == province_id)
        if city_id is not None:
            query = query.filter(cls.city_id == city_id)
            
        return query.order_by(
            cls.last_activity_at.desc()
        ).limit(limit).all()

    @classmethod
    def cleanup_expired(cls, db: Session, days_threshold: int = 7) -> int:
        """
        Clean up expired casual requests
        
        Deletes requests that have been inactive for more than the specified number of days.
        This implements the cleanup mechanism described in the integration guide.
        
        Args:
            db: Database session
            days_threshold: Number of days of inactivity before cleanup (default: 7)
            
        Returns:
            int: Number of requests deleted
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days_threshold)
        
        # Find expired requests
        expired_requests = db.query(cls).filter(
            cls.last_activity_at < cutoff_date
        )
        
        deleted_count = expired_requests.count()
        
        # Delete expired requests
        expired_requests.delete(synchronize_session=False)
        db.commit()
        
        return deleted_count

    @classmethod
    def get_recent_activity(cls, db: Session, hours: int = 24) -> int:
        """Get count of requests with recent activity"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        return db.query(cls).filter(
            cls.last_activity_at >= cutoff_time
        ).count()

    @classmethod
    def get_location_statistics(cls, db: Session) -> Dict[str, int]:
        """Get statistics by location"""
        results = db.query(
            cls.location,
            func.count(cls.id).label('count')
        ).filter(
            cls.is_active == True,
            cls.location.isnot(None)
        ).group_by(cls.location).all()
        
        return {location: count for location, count in results if location}

    @classmethod
    def get_user_request_history(cls, db: Session, user_id: str, limit: int = 10) -> List['CasualRequest']:
        """Get historical requests for a user"""
        return db.query(cls).filter(
            cls.user_id == user_id
        ).order_by(
            cls.created_at.desc()
        ).limit(limit).all()

    def to_dict(self) -> Dict[str, Any]:
        """Convert request to dictionary format"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'query': self.query,
            'optimized_query': self.optimized_query,
            'is_active': self.is_active,
            'province_id': self.province_id,
            'city_id': self.city_id,
            'province_name': self.province.name_en if self.province else None,
            'city_name': self.city.name_en if self.city else None,
            'preferences': self.preferences,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'last_activity_at': self.last_activity_at.isoformat() if self.last_activity_at else None
        }

    def matches_preferences(self, other_preferences: Dict[str, Any]) -> bool:
        """
        Check if this request's preferences match with another set of preferences
        
        Args:
            other_preferences: Other user's preferences to compare against
            
        Returns:
            bool: True if preferences are compatible
        """
        if not self.preferences or not other_preferences:
            return False
        
        # Check activity type matching
        my_activity = self.preferences.get('activity_type')
        their_activity = other_preferences.get('activity_type')
        
        if my_activity and their_activity:
            if my_activity == their_activity:
                return True
        
        # Check timing compatibility
        my_timing = self.preferences.get('timing')
        their_timing = other_preferences.get('timing')
        
        if my_timing and their_timing:
            # Simple compatibility check - can be enhanced
            compatible_timings = {
                'weekend': ['weekend', 'flexible'],
                'weekday': ['weekday', 'flexible'],
                'evening': ['evening', 'flexible'],
                'flexible': ['weekend', 'weekday', 'evening', 'flexible']
            }
            
            if their_timing in compatible_timings.get(my_timing, []):
                return True
        
        return False

    def calculate_similarity_score(self, other: 'CasualRequest') -> float:
        """
        Calculate similarity score with another casual request
        
        Args:
            other: Another CasualRequest to compare with
            
        Returns:
            float: Similarity score between 0.0 and 1.0
        """
        score = 0.0
        
        # Location similarity (40% weight)
        if self.location and other.location:
            if self.location.lower() in other.location.lower() or \
               other.location.lower() in self.location.lower():
                score += 0.4
        
        # Preferences matching (30% weight)
        if self.preferences and other.preferences:
            if self.matches_preferences(other.preferences):
                score += 0.3
        
        # Query text similarity (30% weight) - simple keyword matching
        my_words = set(self.query.lower().split())
        their_words = set(other.query.lower().split())
        common_words = my_words.intersection(their_words)
        
        if my_words and their_words:
            text_similarity = len(common_words) / len(my_words.union(their_words))
            score += text_similarity * 0.3
        
        return min(1.0, score)  # Cap at 1.0