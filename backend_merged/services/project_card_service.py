"""
Project Card service for handling project card operations with limits
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func
from typing import List, Optional
from datetime import datetime

from models.project_cards import ProjectCard, UserProject, ProjectType, ProjectStatus, ModerationStatus
from models.users import User


class ProjectCardService:
    """Service for handling project card operations"""
    
    @staticmethod
    def check_user_card_limit(db: Session, user_id: int) -> bool:
        """
        Check if user has reached the maximum card limit based on membership
        Returns True if user can create more cards, False if limit reached
        """
        # Import here to avoid circular imports
        from services.membership_service import MembershipService
        
        can_create, message, info = MembershipService.check_project_card_limit(db, user_id)
        return can_create
    
    @staticmethod
    def get_user_card_count(db: Session, user_id: int) -> int:
        """
        Get the current number of active cards owned by a user
        """
        return db.query(ProjectCard).filter(
            ProjectCard.creator_id == user_id,
            ProjectCard.is_active == True
        ).count()
    
    @staticmethod
    def create_project_card(db: Session, user_id: int, card_data: dict) -> Optional[ProjectCard]:
        """
        Create a new project card with membership-based limit validation
        """
        # Import here to avoid circular imports
        from services.membership_service import MembershipService
        
        # Check if user can create a project card based on membership limits
        can_create, message, info = MembershipService.check_project_card_limit(db, user_id)
        if not can_create:
            raise ValueError(message)
        
        # Create the project card
        new_card = ProjectCard(
            creator_id=user_id,
            title=card_data.get('title'),
            description=card_data.get('description'),
            short_description=card_data.get('short_description'),
            category=card_data.get('category'),
            industry=card_data.get('industry'),
            project_type=card_data.get('project_type', ProjectType.STARTUP),
            stage=card_data.get('stage'),
            looking_for=card_data.get('looking_for'),
            skills_needed=card_data.get('skills_needed'),
            image_urls=card_data.get('image_urls'),
            video_url=card_data.get('video_url'),
            demo_url=card_data.get('demo_url'),
            pitch_deck_url=card_data.get('pitch_deck_url'),
            funding_goal=card_data.get('funding_goal'),
            equity_offered=card_data.get('equity_offered'),
            current_valuation=card_data.get('current_valuation'),
            revenue=card_data.get('revenue'),
            feature_tags=card_data.get('feature_tags'),
            is_active=True,
            moderation_status=ModerationStatus.PENDING,
            status=ProjectStatus.ONGOING,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.add(new_card)
        db.commit()
        db.refresh(new_card)
        
        # Log the usage for tracking
        MembershipService.log_usage(db, user_id, "project_card_create", 1, {
            "card_id": new_card.project_id,
            "title": new_card.title
        })
        
        # Create owner relationship in UserProject table
        user_project = UserProject(
            user_id=user_id,
            project_id=new_card.project_id,
            role="Owner",
            joined_at=datetime.utcnow()
        )
        
        db.add(user_project)
        db.commit()
        
        return new_card
    
    @staticmethod
    def deactivate_project_card(db: Session, user_id: int, card_id: int) -> bool:
        """
        Deactivate (soft delete) a project card to free up a slot for new cards
        """
        card = db.query(ProjectCard).filter(
            ProjectCard.project_id == card_id,
            ProjectCard.creator_id == user_id,
            ProjectCard.is_active == True
        ).first()
        
        if not card:
            return False
        
        card.is_active = False
        card.updated_at = datetime.utcnow()
        db.commit()
        
        return True
    
    @staticmethod
    def get_user_cards(db: Session, user_id: int, include_inactive: bool = False) -> List[ProjectCard]:
        """
        Get all cards owned by a user
        """
        query = db.query(ProjectCard).filter(ProjectCard.creator_id == user_id)
        
        if not include_inactive:
            query = query.filter(ProjectCard.is_active == True)
        
        return query.order_by(desc(ProjectCard.created_at)).all()
