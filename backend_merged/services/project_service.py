"""
Project service for handling project operations
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
from typing import List, Optional
from datetime import datetime

from models.project_cards import ProjectCard, UserProject
from models.users import User
from schemas.projects import (
    ProjectCreate, ProjectUpdate, ProjectResponse, 
    UserProjectCreate, UserProjectResponse, ProjectWithUsers, 
    UserWithProjects, ProjectListResponse
)

class ProjectService:
    """Service for handling project operations"""
    
    @staticmethod
    def create_project(db: Session, user_id: int, project_data: ProjectCreate) -> ProjectResponse:
        """
        Create a new project and associate the creator as owner
        """
        # Check if user already has the maximum number of cards (2)
        existing_cards_count = db.query(ProjectCard).filter(
            ProjectCard.creator_id == user_id
        ).count()
        
        if existing_cards_count >= 2:
            raise ValueError("You can only create a maximum of 2 project cards. Please delete an existing card to create a new one.")
        
        # Create the project
        new_project = ProjectCard(
            creator_id=user_id,
            title=project_data.short_description[:200] if project_data.short_description else "Untitled Project",
            description=project_data.long_description or project_data.short_description or "No description provided",
            short_description=project_data.short_description,
            long_description=project_data.long_description,
            start_time=project_data.start_time,
            media_link_id=project_data.media_link_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.add(new_project)
        db.commit()
        db.refresh(new_project)
        
        # Add creator as project owner
        user_project = UserProject(
            user_id=user_id,
            project_id=new_ProjectCard.project_id,
            role="Owner",
            joined_at=datetime.utcnow()
        )
        
        db.add(user_project)
        db.commit()
        
        return ProjectResponse.from_orm(new_project)
    
    @staticmethod
    def get_project(db: Session, project_id: int, user_id: Optional[int] = None) -> Optional[ProjectWithUsers]:
        """
        Get a project by ID with associated users
        """
        project = db.query(ProjectCard).filter(ProjectCard.project_id == project_id).first()
        
        if not project:
            return None
        
        # Get associated users
        user_projects = db.query(UserProject).join(User).filter(
            UserProjectCard.project_id == project_id
        ).all()
        
        users_data = []
        for up in user_projects:
            user = db.query(User).filter(User.user_id == up.user_id).first()
            users_data.append(UserProjectResponse(
                user_id=up.user_id,
                project_id=up.project_id,
                role=up.role,
                joined_at=up.joined_at,
                user_name=user.name if user else "Unknown",
                project_short_description=ProjectCard.short_description
            ))
        
        return ProjectWithUsers(
            project_id=ProjectCard.project_id,
            short_description=ProjectCard.short_description,
            long_description=ProjectCard.long_description,
            start_time=ProjectCard.start_time,
            media_link_id=ProjectCard.media_link_id,
            created_at=ProjectCard.created_at,
            updated_at=ProjectCard.updated_at,
            users=users_data
        )
    
    @staticmethod
    def update_project(db: Session, project_id: int, user_id: int, project_data: ProjectUpdate) -> Optional[ProjectResponse]:
        """
        Update a project (only if user is owner or collaborator)
        """
        # Check if user has permission to update
        user_project = db.query(UserProject).filter(
            UserProjectCard.project_id == project_id,
            UserProjectCard.user_id == user_id,
            UserProjectCard.role.in_(["Owner", "Collaborator"])
        ).first()
        
        if not user_project:
            raise ValueError("You don't have permission to update this project")
        
        project = db.query(ProjectCard).filter(ProjectCard.project_id == project_id).first()
        
        if not project:
            return None
        
        # Update fields if provided
        if project_data.short_description is not None:
            ProjectCard.short_description = project_data.short_description
        if project_data.long_description is not None:
            ProjectCard.long_description = project_data.long_description
        if project_data.start_time is not None:
            ProjectCard.start_time = project_data.start_time
        if project_data.media_link_id is not None:
            ProjectCard.media_link_id = project_data.media_link_id
        
        ProjectCard.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(project)
        
        return ProjectResponse.from_orm(project)
    
    @staticmethod
    def delete_project(db: Session, project_id: int, user_id: int) -> bool:
        """
        Delete a project (only if user is owner)
        """
        # Check if user is owner
        user_project = db.query(UserProject).filter(
            UserProjectCard.project_id == project_id,
            UserProjectCard.user_id == user_id,
            UserProjectCard.role == "Owner"
        ).first()
        
        if not user_project:
            raise ValueError("Only project owners can delete projects")
        
        # Delete all user-project relationships
        db.query(UserProject).filter(UserProjectCard.project_id == project_id).delete()
        
        # Delete the project
        project = db.query(ProjectCard).filter(ProjectCard.project_id == project_id).first()
        if project:
            db.delete(project)
            db.commit()
            return True
        
        return False
    
    @staticmethod
    def add_user_to_project(db: Session, project_id: int, user_id: int, target_user_id: int, role: str = "Collaborator") -> UserProjectResponse:
        """
        Add a user to a project (only if requester is owner or collaborator)
        """
        # Check if requester has permission
        requester_project = db.query(UserProject).filter(
            UserProjectCard.project_id == project_id,
            UserProjectCard.user_id == user_id,
            UserProjectCard.role.in_(["Owner", "Collaborator"])
        ).first()
        
        if not requester_project:
            raise ValueError("You don't have permission to add users to this project")
        
        # Check if user is already in project
        existing = db.query(UserProject).filter(
            UserProjectCard.project_id == project_id,
            UserProjectCard.user_id == target_user_id
        ).first()
        
        if existing:
            raise ValueError("User is already part of this project")
        
        # Add user to project
        user_project = UserProject(
            user_id=target_user_id,
            project_id=project_id,
            role=role,
            joined_at=datetime.utcnow()
        )
        
        db.add(user_project)
        db.commit()
        
        # Get user and project details for response
        user = db.query(User).filter(User.user_id == target_user_id).first()
        project = db.query(ProjectCard).filter(ProjectCard.project_id == project_id).first()
        
        return UserProjectResponse(
            user_id=target_user_id,
            project_id=project_id,
            role=role,
            joined_at=user_ProjectCard.joined_at,
            user_name=user.name if user else "Unknown",
            project_short_description=ProjectCard.short_description if project else "Unknown"
        )
    
    @staticmethod
    def remove_user_from_project(db: Session, project_id: int, user_id: int, target_user_id: int) -> bool:
        """
        Remove a user from a project (only if requester is owner, or user is removing themselves)
        """
        # Check permissions
        if user_id != target_user_id:
            # Only owners can remove other users
            requester_project = db.query(UserProject).filter(
                UserProjectCard.project_id == project_id,
                UserProjectCard.user_id == user_id,
                UserProjectCard.role == "Owner"
            ).first()
            
            if not requester_project:
                raise ValueError("Only project owners can remove other users")
        
        # Cannot remove the last owner
        if user_id == target_user_id:
            user_project = db.query(UserProject).filter(
                UserProjectCard.project_id == project_id,
                UserProjectCard.user_id == target_user_id
            ).first()
            
            if user_project and user_ProjectCard.role == "Owner":
                owner_count = db.query(UserProject).filter(
                    UserProjectCard.project_id == project_id,
                    UserProjectCard.role == "Owner"
                ).count()
                
                if owner_count <= 1:
                    raise ValueError("Cannot remove the last owner from the project")
        
        # Remove user from project
        result = db.query(UserProject).filter(
            UserProjectCard.project_id == project_id,
            UserProjectCard.user_id == target_user_id
        ).delete()
        
        db.commit()
        return result > 0
    
    @staticmethod
    def get_user_projects(db: Session, user_id: int, limit: int = 50, offset: int = 0) -> UserWithProjects:
        """
        Get all projects for a user
        """
        user = db.query(User).filter(User.user_id == user_id).first()
        
        if not user:
            raise ValueError("User not found")
        
        user_projects = db.query(UserProject).join(ProjectCard).filter(
            UserProjectCard.user_id == user_id
        ).order_by(desc(ProjectCard.created_at)).offset(offset).limit(limit).all()
        
        projects_data = []
        for up in user_projects:
            project = db.query(ProjectCard).filter(ProjectCard.project_id == up.project_id).first()
            projects_data.append(UserProjectResponse(
                user_id=up.user_id,
                project_id=up.project_id,
                role=up.role,
                joined_at=up.joined_at,
                user_name=user.name,
                project_short_description=ProjectCard.short_description if project else "Unknown"
            ))
        
        return UserWithProjects(
            user_id=user_id,
            user_name=user.name,
            projects=projects_data
        )
    
    @staticmethod
    def search_projects(db: Session, query: str, user_id: Optional[int] = None, limit: int = 20, offset: int = 0) -> ProjectListResponse:
        """
        Search projects by description
        """
        search_query = db.query(ProjectCard).filter(
            or_(
                ProjectCard.short_description.ilike(f"%{query}%"),
                ProjectCard.long_description.ilike(f"%{query}%")
            )
        )
        
        # If user_id provided, only search projects they have access to
        if user_id:
            search_query = search_query.join(UserProject).filter(
                UserProjectCard.user_id == user_id
            )
        
        total = search_query.count()
        projects = search_query.order_by(desc(ProjectCard.created_at)).offset(offset).limit(limit).all()
        
        project_responses = [ProjectResponse.from_orm(project) for project in projects]
        
        return ProjectListResponse(
            projects=project_responses,
            total=total,
            page=(offset // limit) + 1,
            per_page=limit
        )
