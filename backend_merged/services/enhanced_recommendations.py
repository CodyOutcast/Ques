"""
Enhanced vector-based recommendation service with mutual like prioritization
"""

import json
import logging
import numpy as np
from typing import List, Dict, Optional, Tuple, Set
from sqlalchemy.orm import Session
from sqlalchemy import text, and_, or_

from models.project_cards import ProjectCard, ModerationStatus
from models.users import User
from models.likes import UserSwipe

try:
    from db_utils import (
        embed_text, query_vector_db, get_user_vector, 
        insert_to_vector_db, store_user_tags, SessionLocal
    )
    DB_UTILS_AVAILABLE = True
except ImportError as e:
    logging.warning(f"db_utils not available: {e}")
    DB_UTILS_AVAILABLE = False


from models.users import User

logger = logging.getLogger(__name__)

class EnhancedRecommendationService:
    """Enhanced recommendation service with mutual like prioritization"""
    
    @staticmethod
    def get_mutual_like_pairs(db: Session) -> Set[Tuple[int, int]]:
        """Get all mutual like pairs (user_id1, user_id2) where both users liked each other"""
        mutual_pairs = set()
        
        # Find mutual likes from UserSwipe table
        query = text("""
            SELECT DISTINCT s1.swiper_id, s1.target_id
            FROM user_swipes s1
            JOIN user_swipes s2 ON s1.swiper_id = s2.target_id 
                                AND s1.target_id = s2.swiper_id
            WHERE s1.direction = 'like' AND s2.direction = 'like'
        """)
        
        result = db.execute(query)
        for row in result.fetchall():
            user1, user2 = sorted([row[0], row[1]])  # Ensure consistent ordering
            mutual_pairs.add((user1, user2))
        
        logger.info(f"Found {len(mutual_pairs)} mutual like pairs")
        return mutual_pairs
    
    @staticmethod
    def get_users_who_liked_my_projects(db: Session, user_id: int) -> List[Dict]:
        """Get users who have liked any of the current user's projects"""
        # Get all projects created by the user
        user_projects = db.query(ProjectCard).filter(
            ProjectCard.creator_id == user_id
        ).all()
        
        if not user_projects:
            return []
        
        project_ids = [p.project_id for p in user_projects]
        
        # Find users who liked these projects
        liked_users_query = text("""
            SELECT DISTINCT 
                l.liker_id as user_id,
                l.liked_item_id as project_id,
                u.name,
                u.bio,
                u.feature_tags,
                u.profile_image_url,
                p.short_description as title,
                p.long_description as description
            FROM likes l
            JOIN users u ON l.liker_id = u.user_id
            JOIN projects p ON l.liked_item_id = p.project_id
            WHERE l.liked_item_type = 'PROJECT' 
                AND l.liked_item_id = ANY(:project_ids)
                AND l.liker_id != :user_id
            ORDER BY l.created_at DESC
        """)
        
        result = db.execute(liked_users_query, {
            "project_ids": project_ids,
            "user_id": user_id
        })
        
        users_data = []
        for row in result.fetchall():
            user_data = {
                "user_id": row.user_id,
                "project_id": row.project_id,
                "name": row.name,
                "bio": row.bio,
                "feature_tags": row.feature_tags,
                "profile_image_url": row.profile_image_url,
                "liked_project_title": row.title,
                "liked_project_description": row.description
            }
            users_data.append(user_data)
        
        logger.info(f"Found {len(users_data)} users who liked user {user_id}'s projects")
        return users_data
    
    @staticmethod
    def get_closest_project_for_user(db: Session, target_user_id: int, current_user_id: int) -> Optional[Dict]:
        """
        Find the project card from target_user that is most similar to current_user's profile
        """
        if not DB_UTILS_AVAILABLE:
            # Fallback: get the most recent project
            project = db.query(ProjectCard).filter(
                ProjectCard.creator_id == target_user_id
            ).order_by(ProjectCard.created_at.desc()).first()
            
            return project.to_card_dict() if project else None
        
        # Get current user's vector
        current_user_vector = get_user_vector(current_user_id)
        if not current_user_vector:
            logger.warning(f"No vector for user {current_user_id}")
            return None
        
        # Get all projects from target user
        target_projects = db.query(ProjectCard).filter(
            ProjectCard.creator_id == target_user_id
        ).all()
        
        if not target_projects:
            return None
        
        best_project = None
        best_similarity = -1
        
        for project in target_projects:
            try:
                # Get project vector text
                project_text = f"{project.title} {project.description} {project.category} {project.industry}"
                if project.skills_needed:
                    project_text += f" {' '.join(project.skills_needed)}"
                
                # Get similarity score (this would need actual vector comparison)
                # For now, use the first project as fallback
                if best_project is None:
                    best_project = project
                
            except Exception as e:
                logger.error(f"Error processing project {project.project_id}: {e}")
                continue
        
        return best_project.to_card_dict() if best_project else None
    
    @staticmethod
    def get_enhanced_recommendations(
        user_id: int, 
        limit: int = 20,
        exclude_own_projects: bool = True
    ) -> List[Dict]:
        """
        Enhanced recommendation algorithm:
        1. Get vector-based similar projects
        2. Fill remaining with projects from users who liked current user's projects
        3. Exclude projects from mutual like pairs
        """
        db = SessionLocal()
        try:
            logger.info(f"Getting enhanced recommendations for user {user_id}")
            
            # Step 1: Get mutual like pairs to exclude their projects
            mutual_pairs = EnhancedRecommendationService.get_mutual_like_pairs(db)
            mutual_users = set()
            for pair in mutual_pairs:
                if user_id in pair:
                    other_user = pair[1] if pair[0] == user_id else pair[0]
                    mutual_users.add(other_user)
            
            logger.info(f"User {user_id} has mutual likes with {len(mutual_users)} users")
            
            # Step 2: Get vector-based recommendations first
            vector_project_cards = []
            exclude_creator_ids = list(mutual_users)
            
            if exclude_own_projects:
                exclude_creator_ids.append(user_id)
            
            if DB_UTILS_AVAILABLE:
                user_vector = get_user_vector(user_id)
                if user_vector:
                    # Query vector database for similar projects
                    similar_results = query_vector_db(user_vector, top_k=100)
                    
                    if similar_results:
                        project_ids = []
                        for result in similar_results:
                            vector_id = result.get('id', str(result)) if isinstance(result, dict) else str(result)
                            if vector_id.startswith("project_"):
                                try:
                                    project_id = int(vector_id.replace("project_", ""))
                                    project_ids.append(project_id)
                                except ValueError:
                                    continue
                        
                        if project_ids:
                            # Get projects excluding mutual like users
                            projects_query = db.query(ProjectCard).filter(
                                and_(
                                    ProjectCard.project_id.in_(project_ids),
                                    ~ProjectCard.creator_id.in_(exclude_creator_ids)
                                )
                            )
                            
                            projects = projects_query.all()
                            
                            # Sort by vector similarity order
                            projects_dict = {p.project_id: p for p in projects}
                            for pid in project_ids:
                                if pid in projects_dict and len(vector_project_cards) < limit:
                                    try:
                                        card_dict = projects_dict[pid].to_card_dict()
                                        vector_project_cards.append(card_dict)
                                    except Exception as e:
                                        logger.error(f"Error converting project {pid} to card: {e}")
                                        continue
            
            logger.info(f"Found {len(vector_project_cards)} vector-based projects")
            
            # Step 3: Fill remaining slots with projects from users who liked current user's projects
            if len(vector_project_cards) < limit:
                remaining_slots = limit - len(vector_project_cards)
                used_project_ids = {p['id'] for p in vector_project_cards}
                
                # Get users who liked current user's projects
                users_who_liked_my_projects = EnhancedRecommendationService.get_users_who_liked_my_projects(db, user_id)
                
                like_based_cards = []
                processed_users = set()
                
                for user_data in users_who_liked_my_projects:
                    if len(like_based_cards) >= remaining_slots:
                        break
                    
                    liker_user_id = user_data["user_id"]
                    
                    # Skip if already processed or if it's a mutual like
                    if liker_user_id in processed_users or liker_user_id in mutual_users:
                        continue
                    
                    # Get the closest project from this user
                    closest_project = EnhancedRecommendationService.get_closest_project_for_user(
                        db, liker_user_id, user_id
                    )
                    
                    if closest_project and closest_project['id'] not in used_project_ids:
                        # Enhance the project card with like context
                        closest_project['recommendation_reason'] = f"This user liked your project: {user_data['liked_project_title']}"
                        closest_project['liker_context'] = {
                            "user_name": user_data["name"],
                            "liked_project": user_data["liked_project_title"]
                        }
                        
                        like_based_cards.append(closest_project)
                        used_project_ids.add(closest_project['id'])
                        processed_users.add(liker_user_id)
                
                logger.info(f"Added {len(like_based_cards)} like-based project recommendations")
                vector_project_cards.extend(like_based_cards)
            
            # Step 4: Fill any remaining slots with fallback projects
            if len(vector_project_cards) < limit:
                remaining_needed = limit - len(vector_project_cards)
                used_project_ids = {p['id'] for p in vector_project_cards}
                
                # Get fallback projects (recent/popular) excluding mutual likes
                fallback_query = db.query(ProjectCard).filter(
                    and_(
                        ~ProjectCard.creator_id.in_(exclude_creator_ids),
                        ~ProjectCard.project_id.in_(used_project_ids)
                    )
                ).order_by(ProjectCard.created_at.desc()).limit(remaining_needed)
                
                fallback_projects = fallback_query.all()
                for project in fallback_projects:
                    try:
                        card_dict = project.to_card_dict()
                        vector_project_cards.append(card_dict)
                    except Exception as e:
                        logger.error(f"Error converting fallback project {project.project_id}: {e}")
                        continue
                
                logger.info(f"Added {len(fallback_projects)} fallback projects")
            
            final_recommendations = vector_project_cards[:limit]
            logger.info(f"Returning {len(final_recommendations)} enhanced recommendations for user {user_id}")
            return final_recommendations
            
        except Exception as e:
            logger.error(f"Error getting enhanced recommendations for user {user_id}: {e}")
            return []
        finally:
            db.close()
