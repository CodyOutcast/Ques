"""
Vector-based recommendation service for matching users with project cards
"""

import json
import logging
import numpy as np
from typing import List, Dict, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import text, and_, or_

from models.project_cards import ProjectCard, ModerationStatus
from models.users import User

try:
    from db_utils import (
        embed_text, query_vector_db, get_user_vector, 
        insert_to_vector_db, store_user_tags, SessionLocal
    )
    DB_UTILS_AVAILABLE = True
except ImportError as e:
    logging.warning(f"db_utils not available: {e}")
    DB_UTILS_AVAILABLE = False

from models.project_cards import ProjectCard, UserProject
from models.users import User

logger = logging.getLogger(__name__)

class VectorRecommendationService:
    """Service for vector-based project card recommendations"""
    
    @staticmethod
    def get_user_vector_text(user: User) -> str:
        """Convert user profile to text for vector embedding"""
        text_parts = []
        
        # Add user bio
        if user.bio:
            text_parts.append(user.bio)
        
        # Add feature tags
        if user.feature_tags:
            if isinstance(user.feature_tags, list):
                tags = user.feature_tags
            else:
                try:
                    tags = json.loads(user.feature_tags)
                except:
                    tags = []
            text_parts.append(" ".join(tags))
        
        # Add location context
        if user.location:
            text_parts.append(f"Location: {user.location}")
        
        return " ".join(text_parts)
    
    @staticmethod 
    def get_project_vector_text(project: ProjectCard) -> str:
        """Convert project to text for vector embedding"""
        text_parts = []
        
        # Add project title and description
        if project.title:
            text_parts.append(project.title)
        if project.description:
            text_parts.append(project.description)
        
        # Add category and industry
        if project.category:
            text_parts.append(f"Category: {project.category}")
        if project.industry:
            text_parts.append(f"Industry: {project.industry}")
        
        # Add what they're looking for
        if project.looking_for:
            looking_for_text = " ".join(project.looking_for)
            text_parts.append(f"Looking for: {looking_for_text}")
        
        # Add skills needed
        if project.skills_needed:
            skills_text = " ".join(project.skills_needed)
            text_parts.append(f"Skills needed: {skills_text}")
        
        # Add feature tags
        if project.feature_tags:
            if isinstance(project.feature_tags, list):
                tags = project.feature_tags
            else:
                try:
                    tags = json.loads(project.feature_tags)
                except:
                    tags = []
            text_parts.append(" ".join(tags))
        
        # Add stage and type
        if project.stage:
            text_parts.append(f"Stage: {project.stage}")
        if project.project_type:
            text_parts.append(f"Type: {project.project_type.value}")
        
        return " ".join(text_parts)
    
    @staticmethod
    def update_user_vector(db: Session, user_id: int) -> Optional[str]:
        """Update user's vector in the vector database"""
        if not DB_UTILS_AVAILABLE:
            logger.warning("Vector database not available")
            return None
        
        try:
            # Get user
            user = db.query(User).filter(User.user_id == user_id).first()
            if not user:
                logger.error(f"User {user_id} not found")
                return None
            
            # Generate vector text
            vector_text = VectorRecommendationService.get_user_vector_text(user)
            if not vector_text.strip():
                logger.warning(f"No vector text for user {user_id}")
                return None
            
            # Insert to vector database
            vector_id = insert_to_vector_db(vector_text, {"user_id": user_id})
            
            # Update user's vector_id in PostgreSQL
            if vector_id:
                user.vector_id = vector_id
                db.commit()
                logger.info(f"Updated vector for user {user_id}")
            
            return vector_id
            
        except Exception as e:
            logger.error(f"Error updating user vector: {e}")
            db.rollback()
            return None
    
    @staticmethod
    def update_project_vector(db: Session, project_id: int) -> Optional[str]:
        """Update project's vector in the vector database"""
        if not DB_UTILS_AVAILABLE:
            logger.warning("Vector database not available")
            return None
        
        try:
            # Get project
            project = db.query(ProjectCard).filter(ProjectCard.project_id == project_id).first()
            if not project:
                logger.error(f"Project {project_id} not found")
                return None
            
            # Generate vector text
            vector_text = VectorRecommendationService.get_project_vector_text(project)
            if not vector_text.strip():
                logger.warning(f"No vector text for project {project_id}")
                return None
            
            # Insert to vector database with project prefix
            vector_id = insert_to_vector_db(vector_text, {"project_id": project_id})
            
            # Update project's vector_id in PostgreSQL
            if vector_id:
                project.vector_id = vector_id
                db.commit()
                logger.info(f"Updated vector for project {project_id}")
            
            return vector_id
            
        except Exception as e:
            logger.error(f"Error updating project vector: {e}")
            db.rollback()
            return None
    
    @staticmethod
    def get_recommended_projects_for_user(
        user_id: int, 
        limit: int = 20,
        exclude_own_projects: bool = True
    ) -> List[Dict]:
        """Get recommended project cards for a user based on vector similarity"""
        
        db = SessionLocal()
        try:
            # Always try to get vector-based recommendations first
            vector_project_cards = []
            
            if DB_UTILS_AVAILABLE:
                # Get user's vector
                user_vector = get_user_vector(user_id)
                if not user_vector:
                    logger.warning(f"No vector found for user {user_id}, updating...")
                    VectorRecommendationService.update_user_vector(db, user_id)
                    user_vector = get_user_vector(user_id)
                
                if user_vector:
                    # Query vector database for similar items (get more results to ensure we have enough)
                    similar_results = query_vector_db(user_vector, top_k=100)
                    
                    if similar_results:
                        # Extract project IDs from vector results
                        # Vector IDs are stored as "project_X" for projects and "X" for users
                        project_ids = []
                        
                        for result in similar_results:
                            vector_id = result.get('id', str(result)) if isinstance(result, dict) else str(result)
                            
                            # Look for project vectors (they have "project_" prefix)
                            if vector_id.startswith("project_"):
                                try:
                                    project_id = int(vector_id.replace("project_", ""))
                                    project_ids.append(project_id)
                                except ValueError:
                                    continue
                        
                        if project_ids:
                            # Get projects from PostgreSQL in the order of similarity
                            projects_query = db.query(ProjectCard).filter(
                                and_(
                                    ProjectCard.project_id.in_(project_ids),
                                    ProjectCard.is_active == True,
                                    ProjectCard.moderation_status == ModerationStatus.APPROVED
                                )
                            )
                            
                            # Exclude user's own projects if requested
                            if exclude_own_projects:
                                projects_query = projects_query.filter(ProjectCard.creator_id != user_id)
                            
                            # Get all matching projects
                            projects = projects_query.all()
                            
                            # Sort projects by the order they appeared in vector results
                            projects_dict = {p.project_id: p for p in projects}
                            sorted_projects = []
                            for pid in project_ids:
                                if pid in projects_dict:
                                    sorted_projects.append(projects_dict[pid])
                            
                            # Convert to card format
                            for project in sorted_projects:
                                try:
                                    card_dict = project.to_card_dict()
                                    vector_project_cards.append(card_dict)
                                except Exception as e:
                                    logger.error(f"Error converting project {project.project_id} to card: {e}")
                                    continue
                            
                            logger.info(f"Found {len(vector_project_cards)} vector-based projects for user {user_id}")

            # Always ensure we have at least 'limit' projects
            # If vector recommendations are insufficient, supplement with recent/popular projects
            if len(vector_project_cards) < limit:
                exclude_ids = [p['id'] for p in vector_project_cards]
                fallback_needed = limit - len(vector_project_cards)
                
                fallback_cards = VectorRecommendationService._get_fallback_projects(
                    user_id, 
                    fallback_needed,
                    exclude_ids=exclude_ids
                )
                vector_project_cards.extend(fallback_cards)
                logger.info(f"Added {len(fallback_cards)} fallback projects to ensure {limit} total recommendations")
            
            final_recommendations = vector_project_cards[:limit]
            logger.info(f"Returning {len(final_recommendations)} total recommendations for user {user_id}")
            return final_recommendations
            
        except Exception as e:
            logger.error(f"Error getting recommendations for user {user_id}: {e}")
            # Fallback to random projects if everything fails
            return VectorRecommendationService._get_fallback_projects(user_id, limit)
        finally:
            db.close()

    @staticmethod
    def _get_fallback_projects(
        user_id: int, 
        limit: int, 
        exclude_ids: List[int] = None
    ) -> List[Dict]:
        """Fallback method to get projects using multiple strategies to ensure we have enough"""
        db = SessionLocal()
        try:
            base_query = db.query(ProjectCard).filter(
                and_(
                    ProjectCard.is_active == True,
                    ProjectCard.moderation_status == ModerationStatus.APPROVED,
                    ProjectCard.creator_id != user_id
                )
            )
            
            if exclude_ids:
                base_query = base_query.filter(~ProjectCard.project_id.in_(exclude_ids))
            
            project_cards = []
            
            # Strategy 1: Recent projects (most recently created)
            recent_projects = base_query.order_by(ProjectCard.created_at.desc()).limit(limit // 2).all()
            for project in recent_projects:
                try:
                    card_dict = project.to_card_dict()
                    project_cards.append(card_dict)
                except Exception as e:
                    logger.error(f"Error converting project {project.project_id} to card: {e}")
                    continue
            
            # Strategy 2: Popular projects (most likes/interests)
            if len(project_cards) < limit:
                already_included = [p['id'] for p in project_cards]
                popular_query = base_query.filter(~ProjectCard.project_id.in_(already_included))
                popular_projects = popular_query.order_by(
                    (ProjectCard.like_count + ProjectCard.interest_count).desc()
                ).limit(limit - len(project_cards)).all()
                
                for project in popular_projects:
                    try:
                        card_dict = project.to_card_dict()
                        project_cards.append(card_dict)
                    except Exception as e:
                        logger.error(f"Error converting project {project.project_id} to card: {e}")
                        continue
            
            # Strategy 3: If still not enough, get any remaining projects
            if len(project_cards) < limit:
                already_included = [p['id'] for p in project_cards]
                remaining_query = base_query.filter(~ProjectCard.project_id.in_(already_included))
                remaining_projects = remaining_query.order_by(ProjectCard.project_id.asc()).limit(limit - len(project_cards)).all()
                
                for project in remaining_projects:
                    try:
                        card_dict = project.to_card_dict()
                        project_cards.append(card_dict)
                    except Exception as e:
                        logger.error(f"Error converting project {project.project_id} to card: {e}")
                        continue
            
            logger.info(f"Fallback returned {len(project_cards)} projects for user {user_id}")
            return project_cards
            
        except Exception as e:
            logger.error(f"Error getting fallback projects: {e}")
            return []
        finally:
            db.close()
