"""
Project Management Router
Handles user project CRUD operations as part of profile management
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging

from dependencies.db import get_db
from dependencies.auth import get_current_user
from models.users import User
from models.user_projects import UserProject

router = APIRouter(prefix="/profile/projects", tags=["Project Management"])
logger = logging.getLogger(__name__)

# Pydantic models for request/response
class ProjectRequest(BaseModel):
    """Request model for project operations"""
    title: str = Field(..., min_length=1, max_length=200, description="Project title")
    role: Optional[str] = Field(None, max_length=100, description="Your role in the project")
    description: Optional[str] = Field(None, description="Project description")
    reference_links: Optional[List[str]] = Field(default_factory=list, description="Reference links/URLs")

class ProjectUpdateRequest(BaseModel):
    """Request model for updating projects"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    role: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    reference_links: Optional[List[str]] = None
    project_order: Optional[int] = Field(None, ge=0)
    is_featured: Optional[bool] = None

class ProjectResponse(BaseModel):
    """Response model for project data"""
    id: int
    user_id: int
    title: str
    role: Optional[str]
    description: Optional[str]
    reference_links: Optional[List[str]]
    project_order: int
    is_featured: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ProjectCreateRequest(BaseModel):
    """Request wrapper for creating projects"""
    project: ProjectRequest

class ProjectUpdateWrapper(BaseModel):
    """Request wrapper for updating projects"""
    project: ProjectUpdateRequest

@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def add_project(
    request: ProjectCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Add a new project to user's profile
    Frontend endpoint: POST /profile/projects
    """
    try:
        project_data = request.project
        
        # Get current maximum order for user's projects
        max_order = db.query(UserProject).filter(
            UserProject.user_id == current_user.id
        ).count()
        
        # Create new project
        new_project = UserProject(
            user_id=current_user.id,
            title=project_data.title,
            role=project_data.role,
            description=project_data.description,
            reference_links=project_data.reference_links or [],
            project_order=max_order,
            is_featured=False
        )
        
        db.add(new_project)
        db.commit()
        db.refresh(new_project)
        
        logger.info(f"Added new project '{new_project.title}' for user {current_user.id}")
        
        return new_project
        
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to add project for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add project"
        )

@router.get("", response_model=List[ProjectResponse])
async def get_user_projects(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all projects for the current user
    """
    try:
        projects = db.query(UserProject).filter(
            UserProject.user_id == current_user.id
        ).order_by(UserProject.project_order.asc(), UserProject.created_at.desc()).all()
        
        return projects
        
    except Exception as e:
        logger.error(f"Failed to get projects for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get projects"
        )

@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: int,
    request: ProjectUpdateWrapper,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update an existing project
    Frontend endpoint: PUT /profile/projects/{projectId}
    """
    try:
        # Find the project
        project = db.query(UserProject).filter(
            UserProject.id == project_id,
            UserProject.user_id == current_user.id
        ).first()
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        # Update project fields
        update_data = request.project.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(project, field, value)
        
        project.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(project)
        
        logger.info(f"Updated project {project_id} for user {current_user.id}")
        
        return project
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to update project {project_id} for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update project"
        )

@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a project
    Frontend endpoint: DELETE /profile/projects/{projectId}
    """
    try:
        # Find the project
        project = db.query(UserProject).filter(
            UserProject.id == project_id,
            UserProject.user_id == current_user.id
        ).first()
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        db.delete(project)
        db.commit()
        
        logger.info(f"Deleted project {project_id} for user {current_user.id}")
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to delete project {project_id} for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete project"
        )

@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific project by ID
    """
    try:
        project = db.query(UserProject).filter(
            UserProject.id == project_id,
            UserProject.user_id == current_user.id
        ).first()
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        return project
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get project {project_id} for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get project"
        )

@router.post("/reorder", status_code=status.HTTP_200_OK)
async def reorder_projects(
    project_orders: Dict[int, int],  # project_id -> new_order
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Reorder user's projects
    Request body: { "project_id": new_order, ... }
    """
    try:
        # Get all user's projects
        user_projects = db.query(UserProject).filter(
            UserProject.user_id == current_user.id
        ).all()
        
        project_dict = {p.id: p for p in user_projects}
        
        # Update orders
        for project_id, new_order in project_orders.items():
            if project_id in project_dict:
                project_dict[project_id].project_order = new_order
                project_dict[project_id].updated_at = datetime.utcnow()
        
        db.commit()
        
        logger.info(f"Reordered projects for user {current_user.id}")
        
        return {"message": "Projects reordered successfully"}
        
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to reorder projects for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reorder projects"
        )

@router.patch("/{project_id}/featured", response_model=ProjectResponse)
async def toggle_featured_project(
    project_id: int,
    is_featured: bool,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Mark/unmark a project as featured
    """
    try:
        project = db.query(UserProject).filter(
            UserProject.id == project_id,
            UserProject.user_id == current_user.id
        ).first()
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        project.is_featured = is_featured
        project.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(project)
        
        logger.info(f"Toggled featured status for project {project_id}: {is_featured}")
        
        return project
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to toggle featured for project {project_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update project featured status"
        )

@router.get("/featured/list", response_model=List[ProjectResponse])
async def get_featured_projects(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all featured projects for the user
    """
    try:
        projects = db.query(UserProject).filter(
            UserProject.user_id == current_user.id,
            UserProject.is_featured == True
        ).order_by(UserProject.project_order.asc()).all()
        
        return projects
        
    except Exception as e:
        logger.error(f"Failed to get featured projects for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get featured projects"
        )