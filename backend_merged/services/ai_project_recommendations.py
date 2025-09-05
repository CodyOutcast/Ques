"""
AI Project Card Recommendation Service
Generates project card recommendations that can be swiped by users
"""

import logging
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, not_, desc, text
from datetime import datetime, timedelta
import json
import random
import hashlib

from models.project_cards import ProjectCard
from models.project_slots import AIRecommendationSwipe, ProjectCardSlot, SlotStatus
from models.users import User
from dependencies.db import get_db

logger = logging.getLogger(__name__)

class AIProjectRecommendationService:
    """
    Service for generating AI-powered project card recommendations
    """
    
    def __init__(self):
        self.db_session = next(get_db())
    
    def generate_recommendations(
        self,
        user_id: int,
        query: Optional[str] = None,
        limit: int = 10,
        exclude_swiped: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Generate AI project card recommendations for a user
        
        Args:
            user_id: ID of the user requesting recommendations
            query: Optional search query to filter recommendations
            limit: Maximum number of recommendations to return
            exclude_swiped: Whether to exclude previously swiped cards
        
        Returns:
            List of recommendation dictionaries in project card format
        """
        try:
            # Get user profile for personalization
            user = self.db_session.query(User).filter(User.user_id == user_id).first()
            if not user:
                logger.warning(f"User {user_id} not found for recommendations")
                return []
            
            # Build base query for projects
            project_query = self.db_session.query(ProjectCard).filter(
                ProjectCard.creator_id != user_id  # Don't recommend user's own projects
            )
            
            # If query provided, filter by keywords
            if query and query.strip():
                search_terms = query.lower().strip().split()
                for term in search_terms:
                    project_query = project_query.filter(
                        or_(
                            ProjectCard.title.ilike(f"%{term}%"),
                            ProjectCard.description.ilike(f"%{term}%"),
                            ProjectCard.short_description.ilike(f"%{term}%"),
                            ProjectCard.category.ilike(f"%{term}%"),
                            ProjectCard.industry.ilike(f"%{term}%")
                        )
                    )
            
            # Exclude previously swiped projects if requested
            if exclude_swiped:
                swiped_ids = self.db_session.query(AIRecommendationSwipe.ai_recommendation_id).filter(
                    AIRecommendationSwipe.user_id == user_id
                ).subquery()
                
                project_query = project_query.filter(
                    not_(ProjectCard.project_id.in_(
                        self.db_session.query(swiped_ids.c.ai_recommendation_id)
                    ))
                )
            
            # Get projects ordered by relevance (newest first for now)
            projects = project_query.order_by(desc(ProjectCard.created_at)).limit(limit * 2).all()
            
            # Convert to recommendation format with AI scoring
            recommendations = []
            for project in projects:
                recommendation = self._create_recommendation_from_project(
                    project, user, query
                )
                if recommendation:
                    recommendations.append(recommendation)
                
                if len(recommendations) >= limit:
                    break
            
            # Add some AI-generated synthetic recommendations if we don't have enough
            if len(recommendations) < limit:
                synthetic_count = min(5, limit - len(recommendations))
                synthetic_recs = self._generate_synthetic_recommendations(
                    user, query, synthetic_count
                )
                recommendations.extend(synthetic_recs)
            
            # Shuffle to add randomness
            random.shuffle(recommendations)
            
            logger.info(f"Generated {len(recommendations)} recommendations for user {user_id}")
            return recommendations[:limit]
            
        except Exception as e:
            logger.error(f"Error generating recommendations for user {user_id}: {str(e)}")
            return []
    
    def _create_recommendation_from_project(
        self, 
        project: ProjectCard, 
        user: User, 
        query: Optional[str]
    ) -> Optional[Dict[str, Any]]:
        """
        Convert a ProjectCard to recommendation format
        """
        try:
            # Calculate AI confidence score based on matching criteria
            confidence_score = self._calculate_confidence_score(project, user, query)
            
            # Generate unique recommendation ID
            rec_id = self._generate_recommendation_id(project.project_id, user.user_id, query)
            
            # Create AI reasoning
            reasoning = self._generate_ai_reasoning(project, user, query, confidence_score)
            
            recommendation = {
                "ai_recommendation_id": rec_id,
                "source": "existing_project",
                "confidence_score": confidence_score,
                "ai_reasoning": reasoning,
                "original_query": query or "general_recommendations",
                
                # Project card data
                "title": project.title,
                "description": project.description,
                "short_description": project.short_description,
                "category": project.category,
                "industry": project.industry,
                "project_type": project.project_type,
                "stage": project.stage,
                "looking_for": project.looking_for or [],
                "skills_needed": project.skills_needed or [],
                "image_urls": project.image_urls or [],
                "video_url": project.video_url,
                "demo_url": project.demo_url,
                "pitch_deck_url": project.pitch_deck_url,
                "funding_goal": project.funding_goal,
                "equity_offered": project.equity_offered,
                "current_valuation": project.current_valuation,
                "revenue": project.revenue,
                
                # Metadata
                "created_at": project.created_at.isoformat() if project.created_at else None,
                "creator_name": project.creator.name if project.creator else "Anonymous",
                "original_project_id": project.project_id
            }
            
            return recommendation
            
        except Exception as e:
            logger.error(f"Error creating recommendation from project {project.project_id}: {str(e)}")
            return None
    
    def _generate_synthetic_recommendations(
        self, 
        user: User, 
        query: Optional[str], 
        count: int
    ) -> List[Dict[str, Any]]:
        """
        Generate synthetic AI project recommendations when not enough real projects exist
        """
        synthetic_recommendations = []
        
        # Template project ideas based on common categories
        project_templates = [
            {
                "title": "AI-Powered Personal Finance Assistant",
                "category": "fintech",
                "industry": "finance",
                "project_type": "mobile_app",
                "stage": "mvp",
                "looking_for": ["co-founder", "investor", "developer"],
                "skills_needed": ["python", "react-native", "machine-learning"],
                "short_description": "Smart budgeting app that uses AI to predict spending patterns and optimize savings."
            },
            {
                "title": "Sustainable Food Delivery Platform",
                "category": "marketplace",
                "industry": "food",
                "project_type": "web_platform",
                "stage": "concept",
                "looking_for": ["investor", "marketing", "operations"],
                "skills_needed": ["logistics", "sustainability", "marketing"],
                "short_description": "Eco-friendly food delivery focusing on local restaurants and biodegradable packaging."
            },
            {
                "title": "Remote Team Productivity Suite",
                "category": "saas",
                "industry": "productivity",
                "project_type": "web_app",
                "stage": "beta",
                "looking_for": ["sales", "marketing", "investor"],
                "skills_needed": ["sales", "b2b-marketing", "customer-success"],
                "short_description": "Comprehensive tool for remote team collaboration with AI-powered insights."
            },
            {
                "title": "Urban Vertical Farming System",
                "category": "hardware",
                "industry": "agriculture",
                "project_type": "physical_product",
                "stage": "prototype",
                "looking_for": ["investor", "technical-advisor", "co-founder"],
                "skills_needed": ["engineering", "agriculture", "iot"],
                "short_description": "Automated indoor farming system for fresh produce in urban environments."
            },
            {
                "title": "Blockchain Identity Verification",
                "category": "blockchain",
                "industry": "security",
                "project_type": "infrastructure",
                "stage": "development",
                "looking_for": ["developer", "security-expert", "investor"],
                "skills_needed": ["blockchain", "cryptography", "security"],
                "short_description": "Decentralized identity verification system for secure online transactions."
            }
        ]
        
        # Select templates that might match the query
        if query:
            filtered_templates = [
                t for t in project_templates 
                if any(term.lower() in str(t.values()).lower() for term in query.split())
            ]
            if not filtered_templates:
                filtered_templates = project_templates
        else:
            filtered_templates = project_templates
        
        # Generate synthetic recommendations
        for i in range(min(count, len(filtered_templates))):
            template = filtered_templates[i]
            rec_id = self._generate_recommendation_id(f"synthetic_{i}", user.user_id, query)
            
            # Add some randomization to make it feel more AI-generated
            funding_goals = [50000, 100000, 250000, 500000, 1000000]
            equity_offers = [5, 10, 15, 20, 25]
            
            synthetic_rec = {
                "ai_recommendation_id": rec_id,
                "source": "ai_generated",
                "confidence_score": random.randint(75, 95),
                "ai_reasoning": f"Generated based on market trends and your profile interests. This {template['category']} project aligns with current industry demand.",
                "original_query": query or "general_recommendations",
                
                # Project data with some randomization
                "title": template["title"],
                "description": f"Innovative {template['category']} solution in the {template['industry']} space. {template['short_description']} Looking for passionate team members to join this exciting venture.",
                "short_description": template["short_description"],
                "category": template["category"],
                "industry": template["industry"],
                "project_type": template["project_type"],
                "stage": template["stage"],
                "looking_for": template["looking_for"],
                "skills_needed": template["skills_needed"],
                "image_urls": [],
                "video_url": None,
                "demo_url": None,
                "pitch_deck_url": None,
                "funding_goal": random.choice(funding_goals),
                "equity_offered": random.choice(equity_offers),
                "current_valuation": None,
                "revenue": None,
                
                # Metadata
                "created_at": datetime.utcnow().isoformat(),
                "creator_name": "AI Assistant",
                "original_project_id": None
            }
            
            synthetic_recommendations.append(synthetic_rec)
        
        return synthetic_recommendations
    
    def _calculate_confidence_score(
        self, 
        project: ProjectCard, 
        user: User, 
        query: Optional[str]
    ) -> int:
        """
        Calculate AI confidence score for a recommendation (0-100)
        """
        score = 50  # Base score
        
        # Query matching
        if query and query.strip():
            query_terms = query.lower().split()
            project_text = f"{project.title} {project.description} {project.category} {project.industry}".lower()
            matches = sum(1 for term in query_terms if term in project_text)
            score += min(30, matches * 10)
        
        # Project completeness
        if project.short_description:
            score += 5
        if project.image_urls:
            score += 5
        if project.demo_url or project.video_url:
            score += 10
        if project.funding_goal:
            score += 5
        
        # Recency bonus
        if project.created_at:
            days_ago = (datetime.utcnow() - project.created_at).days
            if days_ago < 30:
                score += 10
            elif days_ago < 90:
                score += 5
        
        # Random factor for diversity
        score += random.randint(-10, 10)
        
        return max(10, min(100, score))
    
    def _generate_recommendation_id(
        self, 
        project_id: Any, 
        user_id: int, 
        query: Optional[str]
    ) -> str:
        """
        Generate unique recommendation ID
        """
        data = f"{project_id}_{user_id}_{query or ''}_{datetime.utcnow().date()}"
        return hashlib.md5(data.encode()).hexdigest()
    
    def _generate_ai_reasoning(
        self, 
        project: ProjectCard, 
        user: User, 
        query: Optional[str], 
        confidence_score: int
    ) -> str:
        """
        Generate AI reasoning for why this project was recommended
        """
        reasons = []
        
        if query:
            reasons.append(f"Matches your search for '{query}'")
        
        if project.category:
            reasons.append(f"Trending in {project.category}")
        
        if project.stage == "mvp" or project.stage == "beta":
            reasons.append("Active development stage - good timing to join")
        
        if project.looking_for:
            looking_for_text = ", ".join(project.looking_for)
            reasons.append(f"Seeking: {looking_for_text}")
        
        if confidence_score > 80:
            reasons.append("High compatibility with your profile")
        elif confidence_score > 60:
            reasons.append("Good match based on your interests")
        
        if not reasons:
            reasons.append("Selected based on current market trends")
        
        return " • ".join(reasons)
    
    def record_swipe(
        self,
        user_id: int,
        ai_recommendation_id: str,
        direction: str,
        recommendation_data: Dict[str, Any],
        query: Optional[str] = None,
        slot_id: Optional[int] = None
    ) -> bool:
        """
        Record a user's swipe on an AI recommendation
        
        Args:
            user_id: ID of the user who swiped
            ai_recommendation_id: ID of the AI recommendation
            direction: 'left' (reject) or 'right' (save)
            recommendation_data: Full recommendation data
            query: Original query that generated this recommendation
            slot_id: ID of slot if saved (for right swipes)
        
        Returns:
            True if recorded successfully
        """
        try:
            # Create swipe record
            swipe = AIRecommendationSwipe(
                user_id=user_id,
                ai_recommendation_id=ai_recommendation_id,
                direction=direction,
                query=query,
                recommendation_data=recommendation_data,
                saved_to_slot_id=slot_id
            )
            
            self.db_session.add(swipe)
            self.db_session.commit()
            
            logger.info(f"Recorded {direction} swipe for user {user_id} on recommendation {ai_recommendation_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error recording swipe: {str(e)}")
            self.db_session.rollback()
            return False
    
    def should_stop_recommendations(self, user_id: int) -> bool:
        """
        Check if recommendations should be stopped based on user's slot configuration
        """
        try:
            # Get user's slot configuration
            from models.project_slots import UserSlotConfiguration
            
            config = self.db_session.query(UserSlotConfiguration).filter(
                UserSlotConfiguration.user_id == user_id
            ).first()
            
            # If no config, default behavior is to stop after save
            if not config:
                return True
            
            return config.stop_recommendations_on_save
            
        except Exception as e:
            logger.error(f"Error checking recommendation stop condition: {str(e)}")
            return True  # Default to stopping recommendations
    
    def get_user_swipe_history(
        self, 
        user_id: int, 
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get user's swipe history for AI recommendations
        """
        try:
            swipes = self.db_session.query(AIRecommendationSwipe).filter(
                AIRecommendationSwipe.user_id == user_id
            ).order_by(desc(AIRecommendationSwipe.swiped_at)).limit(limit).all()
            
            history = []
            for swipe in swipes:
                history.append({
                    "swipe_id": swipe.swipe_id,
                    "ai_recommendation_id": swipe.ai_recommendation_id,
                    "direction": swipe.direction,
                    "query": swipe.query,
                    "swiped_at": swipe.swiped_at.isoformat(),
                    "saved_to_slot_id": swipe.saved_to_slot_id,
                    "recommendation_data": swipe.recommendation_data
                })
            
            return history
            
        except Exception as e:
            logger.error(f"Error getting swipe history for user {user_id}: {str(e)}")
            return []
