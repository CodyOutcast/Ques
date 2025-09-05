"""
Agent Cards Service
Service for managing AI-generated project idea cards and user interactions
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, not_, desc, func, text
from datetime import datetime, timedelta
import json
import random
import hashlib

from models.agent_cards import (
    AgentCard, AgentCardSwipe, AgentCardLike, AgentCardHistory, 
    UserAgentCardPreferences, DifficultyLevel, ProjectScope, SwipeAction
)
from models.users import User
from dependencies.db import get_db

logger = logging.getLogger(__name__)

class AgentCardsService:
    """
    Service for managing agent cards and user interactions
    """
    
    def __init__(self, db: Session = None):
        self.db = db or next(get_db())
    
    def create_agent_cards_from_json(self, cards_data: List[Dict[str, Any]], 
                                   generation_prompt: str = None, 
                                   ai_agent_id: str = None) -> List[int]:
        """
        Create agent cards from JSON data (like agent_card.json)
        
        Args:
            cards_data: List of card data dictionaries
            generation_prompt: Original user prompt that generated these cards
            ai_agent_id: ID from the AI system
        
        Returns:
            List of created card IDs
        """
        try:
            created_card_ids = []
            
            for card_data in cards_data:
                # Map project scope
                scope_mapping = {
                    "Small team (2-4 people)": ProjectScope.SMALL_TEAM,
                    "Medium team (5-8 people)": ProjectScope.MEDIUM_TEAM,
                    "Large team (9+ people)": ProjectScope.LARGE_TEAM,
                    "Solo project": ProjectScope.SOLO
                }
                
                project_scope = scope_mapping.get(
                    card_data.get("project_scope", "Small team (2-4 people)"),
                    ProjectScope.SMALL_TEAM
                )
                
                # Map difficulty level
                difficulty_mapping = {
                    "Beginner": DifficultyLevel.BEGINNER,
                    "Intermediate": DifficultyLevel.INTERMEDIATE,
                    "Advanced": DifficultyLevel.ADVANCED
                }
                
                difficulty = difficulty_mapping.get(
                    card_data.get("difficulty_level", "Intermediate"),
                    DifficultyLevel.INTERMEDIATE
                )
                
                # Create agent card
                agent_card = AgentCard(
                    project_idea_title=card_data.get("project_idea_title", ""),
                    project_scope=project_scope,
                    description=card_data.get("description", ""),
                    key_features=card_data.get("key_features", []),
                    estimated_timeline=card_data.get("estimated_timeline", ""),
                    difficulty_level=difficulty,
                    required_skills=card_data.get("required_skills", []),
                    similar_examples=card_data.get("similar_examples", []),
                    relevance_score=card_data.get("relevance_score", 0.5),
                    ai_agent_id=ai_agent_id,
                    generation_prompt=generation_prompt
                )
                
                self.db.add(agent_card)
                self.db.flush()  # Get the ID
                created_card_ids.append(agent_card.card_id)
            
            self.db.commit()
            logger.info(f"Created {len(created_card_ids)} agent cards")
            return created_card_ids
            
        except Exception as e:
            logger.error(f"Error creating agent cards: {str(e)}")
            self.db.rollback()
            return []
    
    def get_recommendations_for_user(self, user_id: int, limit: int = 10, 
                                   exclude_swiped: bool = True) -> List[Dict[str, Any]]:
        """
        Get agent card recommendations for a user
        
        Args:
            user_id: ID of the user
            limit: Maximum number of cards to return
            exclude_swiped: Whether to exclude previously swiped cards
        
        Returns:
            List of agent card recommendations
        """
        try:
            # Get user preferences
            preferences = self.db.query(UserAgentCardPreferences).filter(
                UserAgentCardPreferences.user_id == user_id
            ).first()
            
            # Build base query
            query = self.db.query(AgentCard).filter(
                AgentCard.is_active == True
            )
            
            # Apply preferences if they exist
            if preferences:
                # Filter by minimum relevance score
                query = query.filter(
                    AgentCard.relevance_score >= preferences.min_relevance_score
                )
                
                # Filter by preferred difficulty levels
                if preferences.preferred_difficulty_levels:
                    difficulty_enums = [
                        DifficultyLevel(level) for level in preferences.preferred_difficulty_levels
                        if level in [e.value for e in DifficultyLevel]
                    ]
                    if difficulty_enums:
                        query = query.filter(AgentCard.difficulty_level.in_(difficulty_enums))
                
                # Filter by preferred project scopes
                if preferences.preferred_project_scopes:
                    scope_enums = [
                        ProjectScope(scope) for scope in preferences.preferred_project_scopes
                        if scope in [e.value for e in ProjectScope]
                    ]
                    if scope_enums:
                        query = query.filter(AgentCard.project_scope.in_(scope_enums))
            
            # Exclude swiped cards if requested
            if exclude_swiped:
                swiped_card_ids = self.db.query(AgentCardSwipe.card_id).filter(
                    AgentCardSwipe.user_id == user_id
                ).subquery()
                
                query = query.filter(
                    not_(AgentCard.card_id.in_(
                        self.db.query(swiped_card_ids.c.card_id)
                    ))
                )
            
            # Order by relevance score and creation time
            cards = query.order_by(
                desc(AgentCard.relevance_score),
                desc(AgentCard.created_at)
            ).limit(limit * 2).all()  # Get more than needed for filtering
            
            # Convert to recommendation format
            recommendations = []
            for card in cards:
                recommendation = {
                    "card_id": card.card_id,
                    "project_idea_title": card.project_idea_title,
                    "project_scope": card.project_scope.value,
                    "description": card.description,
                    "key_features": card.key_features,
                    "estimated_timeline": card.estimated_timeline,
                    "difficulty_level": card.difficulty_level.value,
                    "required_skills": card.required_skills,
                    "similar_examples": card.similar_examples,
                    "relevance_score": card.relevance_score,
                    "ai_agent_id": card.ai_agent_id,
                    "generation_prompt": card.generation_prompt,
                    "created_at": card.created_at.isoformat() if card.created_at else None
                }
                recommendations.append(recommendation)
                
                if len(recommendations) >= limit:
                    break
            
            # Shuffle for variety
            random.shuffle(recommendations)
            
            logger.info(f"Generated {len(recommendations)} recommendations for user {user_id}")
            return recommendations
            
        except Exception as e:
            logger.error(f"Error getting recommendations for user {user_id}: {str(e)}")
            return []
    
    def record_swipe(self, user_id: int, card_id: int, action: str, 
                    swipe_context: Dict[str, Any] = None) -> bool:
        """
        Record a user swipe on an agent card
        
        Args:
            user_id: ID of the user
            card_id: ID of the agent card
            action: 'left' or 'right'
            swipe_context: Additional context about the swipe
        
        Returns:
            True if recorded successfully
        """
        try:
            # Validate action
            if action not in ['left', 'right']:
                logger.error(f"Invalid swipe action: {action}")
                return False
            
            swipe_action = SwipeAction.LEFT if action == 'left' else SwipeAction.RIGHT
            
            # Check if already swiped
            existing_swipe = self.db.query(AgentCardSwipe).filter(
                and_(
                    AgentCardSwipe.user_id == user_id,
                    AgentCardSwipe.card_id == card_id
                )
            ).first()
            
            if existing_swipe:
                logger.warning(f"User {user_id} already swiped on card {card_id}")
                return True  # Don't fail, just don't record duplicate
            
            # Create swipe record
            swipe = AgentCardSwipe(
                user_id=user_id,
                card_id=card_id,
                action=swipe_action,
                swipe_context=swipe_context
            )
            
            self.db.add(swipe)
            
            # Handle right swipe - create like
            if action == 'right':
                like = AgentCardLike(
                    user_id=user_id,
                    card_id=card_id,
                    interest_level=swipe_context.get('interest_level') if swipe_context else None,
                    notes=swipe_context.get('notes') if swipe_context else None
                )
                self.db.add(like)
            
            # Handle left swipe - create history record
            elif action == 'left':
                history = AgentCardHistory(
                    user_id=user_id,
                    card_id=card_id,
                    rejection_reason=swipe_context.get('rejection_reason') if swipe_context else None,
                    feedback=swipe_context.get('feedback') if swipe_context else None
                )
                self.db.add(history)
            
            self.db.commit()
            logger.info(f"Recorded {action} swipe for user {user_id} on card {card_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error recording swipe: {str(e)}")
            self.db.rollback()
            return False
    
    def get_user_likes(self, user_id: int, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get user's liked agent cards
        
        Args:
            user_id: ID of the user
            limit: Maximum number of likes to return
        
        Returns:
            List of liked cards with metadata
        """
        try:
            likes = self.db.query(AgentCardLike).filter(
                and_(
                    AgentCardLike.user_id == user_id,
                    AgentCardLike.is_active == True
                )
            ).order_by(desc(AgentCardLike.liked_at)).limit(limit).all()
            
            liked_cards = []
            for like in likes:
                card_data = {
                    "like_id": like.like_id,
                    "liked_at": like.liked_at.isoformat(),
                    "interest_level": like.interest_level,
                    "notes": like.notes,
                    "card": {
                        "card_id": like.card.card_id,
                        "project_idea_title": like.card.project_idea_title,
                        "project_scope": like.card.project_scope.value,
                        "description": like.card.description,
                        "key_features": like.card.key_features,
                        "estimated_timeline": like.card.estimated_timeline,
                        "difficulty_level": like.card.difficulty_level.value,
                        "required_skills": like.card.required_skills,
                        "similar_examples": like.card.similar_examples,
                        "relevance_score": like.card.relevance_score
                    }
                }
                liked_cards.append(card_data)
            
            return liked_cards
            
        except Exception as e:
            logger.error(f"Error getting user likes for user {user_id}: {str(e)}")
            return []
    
    def get_user_history(self, user_id: int, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get user's swiped-left history
        
        Args:
            user_id: ID of the user
            limit: Maximum number of history records to return
        
        Returns:
            List of history records with card data
        """
        try:
            history_records = self.db.query(AgentCardHistory).filter(
                AgentCardHistory.user_id == user_id
            ).order_by(desc(AgentCardHistory.added_at)).limit(limit).all()
            
            history = []
            for record in history_records:
                history_data = {
                    "history_id": record.history_id,
                    "added_at": record.added_at.isoformat(),
                    "rejection_reason": record.rejection_reason,
                    "feedback": record.feedback,
                    "card": {
                        "card_id": record.card.card_id,
                        "project_idea_title": record.card.project_idea_title,
                        "project_scope": record.card.project_scope.value,
                        "description": record.card.description,
                        "difficulty_level": record.card.difficulty_level.value,
                        "relevance_score": record.card.relevance_score
                    }
                }
                history.append(history_data)
            
            return history
            
        except Exception as e:
            logger.error(f"Error getting user history for user {user_id}: {str(e)}")
            return []
    
    def get_swipe_statistics(self, user_id: int) -> Dict[str, Any]:
        """
        Get user's swipe statistics
        
        Args:
            user_id: ID of the user
        
        Returns:
            Dictionary with swipe statistics
        """
        try:
            # Count total swipes
            total_swipes = self.db.query(func.count(AgentCardSwipe.swipe_id)).filter(
                AgentCardSwipe.user_id == user_id
            ).scalar()
            
            # Count by action
            left_swipes = self.db.query(func.count(AgentCardSwipe.swipe_id)).filter(
                and_(
                    AgentCardSwipe.user_id == user_id,
                    AgentCardSwipe.action == SwipeAction.LEFT
                )
            ).scalar()
            
            right_swipes = self.db.query(func.count(AgentCardSwipe.swipe_id)).filter(
                and_(
                    AgentCardSwipe.user_id == user_id,
                    AgentCardSwipe.action == SwipeAction.RIGHT
                )
            ).scalar()
            
            # Count active likes
            active_likes = self.db.query(func.count(AgentCardLike.like_id)).filter(
                and_(
                    AgentCardLike.user_id == user_id,
                    AgentCardLike.is_active == True
                )
            ).scalar()
            
            # Calculate percentages
            like_rate = (right_swipes / total_swipes * 100) if total_swipes > 0 else 0
            
            # Get recent activity (last 7 days)
            week_ago = datetime.utcnow() - timedelta(days=7)
            recent_swipes = self.db.query(func.count(AgentCardSwipe.swipe_id)).filter(
                and_(
                    AgentCardSwipe.user_id == user_id,
                    AgentCardSwipe.swiped_at >= week_ago
                )
            ).scalar()
            
            stats = {
                "total_swipes": total_swipes,
                "left_swipes": left_swipes,
                "right_swipes": right_swipes,
                "active_likes": active_likes,
                "like_rate_percentage": round(like_rate, 1),
                "recent_swipes_7_days": recent_swipes
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting swipe statistics for user {user_id}: {str(e)}")
            return {
                "total_swipes": 0,
                "left_swipes": 0,
                "right_swipes": 0,
                "active_likes": 0,
                "like_rate_percentage": 0,
                "recent_swipes_7_days": 0
            }
    
    def update_user_preferences(self, user_id: int, preferences: Dict[str, Any]) -> bool:
        """
        Update user's agent card preferences
        
        Args:
            user_id: ID of the user
            preferences: Dictionary of preference updates
        
        Returns:
            True if updated successfully
        """
        try:
            # Get existing preferences or create new ones
            user_prefs = self.db.query(UserAgentCardPreferences).filter(
                UserAgentCardPreferences.user_id == user_id
            ).first()
            
            if not user_prefs:
                user_prefs = UserAgentCardPreferences(user_id=user_id)
                self.db.add(user_prefs)
            
            # Update preferences
            updatable_fields = [
                'preferred_difficulty_levels', 'preferred_project_scopes',
                'preferred_skills', 'excluded_skills', 'min_relevance_score',
                'max_cards_per_day', 'preferred_timeline_min', 'preferred_timeline_max',
                'daily_cards_enabled', 'weekly_summary_enabled'
            ]
            
            for field, value in preferences.items():
                if field in updatable_fields and hasattr(user_prefs, field):
                    setattr(user_prefs, field, value)
            
            user_prefs.updated_at = datetime.utcnow()
            self.db.commit()
            
            logger.info(f"Updated preferences for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating preferences for user {user_id}: {str(e)}")
            self.db.rollback()
            return False
