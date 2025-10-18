"""
Project management router
Handles user projects, institutions, and external links
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from dependencies.db import get_db
from dependencies.auth import get_current_user, get_current_active_user
from models.users import User
from models.projects import Project, UserLink, ProjectStatus
from models.institutions import Institution, UserInstitution
from services.auth_service import AuthService
from datetime import datetime
from schemas.projects import (
    ProjectCreate, ProjectUpdate, ProjectResponse,
    InstitutionCreate, InstitutionUpdate, InstitutionResponse,
    UserLinkCreate, UserLinkUpdate, UserLinkResponse
)

router = APIRouter(tags=["projects"])
security = HTTPBearer()
logger = logging.getLogger(__name__)

# Initialize services
auth_service = AuthService()

# ===== PROJECT ENDPOINTS =====

@router.post("/profile/projects", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def add_project(
    project_data: ProjectCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Add a new project to user's profile
    """
    try:
        # Create new project
        project = Project(
            user_id=current_user.user_id,
            short_description=project_data.short_description,
            long_description=project_data.long_description,
            start_time=project_data.start_time,
            status=project_data.status or ProjectStatus.ONGOING,
            media_link_id=project_data.media_link_id
        )
        
        db.add(project)
        db.commit()
        db.refresh(project)
        
        logger.info(f"Project added for user {current_user.user_id}: {project.project_id}")
        
        return ProjectResponse(
            project_id=project.project_id,
            short_description=project.short_description,
            long_description=project.long_description,
            start_time=project.start_time,
            status=project.status.value,
            media_link_id=project.media_link_id,
            created_at=project.created_at,
            updated_at=project.updated_at
        )
        
    except Exception as e:
        logger.error(f"Error adding project: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add project"
        )

@router.get("/profile/projects", response_model=List[ProjectResponse])
async def get_projects(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get all projects for current user
    """
    try:
        projects = db.query(Project).filter(
            Project.user_id == current_user.user_id
        ).order_by(Project.created_at.desc()).all()
        
        return [
            ProjectResponse(
                project_id=p.project_id,
                short_description=p.short_description,
                long_description=p.long_description,
                start_time=p.start_time,
                status=p.status.value,
                media_link_id=p.media_link_id,
                created_at=p.created_at,
                updated_at=p.updated_at
            ) for p in projects
        ]
        
    except Exception as e:
        logger.error(f"Error getting projects: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get projects"
        )

@router.put("/profile/projects/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: int,
    project_data: ProjectUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update an existing project
    """
    try:
        project = db.query(Project).filter(
            Project.project_id == project_id,
            Project.user_id == current_user.user_id
        ).first()
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        # Update fields if provided
        if project_data.short_description is not None:
            project.short_description = project_data.short_description
        if project_data.long_description is not None:
            project.long_description = project_data.long_description
        if project_data.start_time is not None:
            project.start_time = project_data.start_time
        if project_data.status is not None:
            project.status = project_data.status
        
        project.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(project)
        
        return ProjectResponse(
            project_id=project.project_id,
            short_description=project.short_description,
            long_description=project.long_description,
            start_time=project.start_time,
            status=project.status.value,
            media_link_id=project.media_link_id,
            created_at=project.created_at,
            updated_at=project.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating project: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update project"
        )

@router.delete("/profile/projects/{project_id}")
async def delete_project(
    project_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete a project
    """
    try:
        project = db.query(Project).filter(
            Project.project_id == project_id,
            Project.user_id == current_user.user_id
        ).first()
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        db.delete(project)
        db.commit()
        
        return {"message": "Project deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting project: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete project"
        )

# ===== INSTITUTION ENDPOINTS =====

@router.post("/profile/institutions", response_model=InstitutionResponse, status_code=status.HTTP_201_CREATED)
async def add_institution(
    institution_data: InstitutionCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Add a new institution to user's profile
    """
    try:
        institution = Institution(
            user_id=current_user.user_id,
            name=institution_data.name,
            role=institution_data.role,
            description=institution_data.description,
            type=institution_data.type,
            verified=False  # Always start as unverified
        )
        
        db.add(institution)
        db.commit()
        db.refresh(institution)
        
        logger.info(f"Institution added for user {current_user.user_id}: {institution.institution_id}")
        
        return InstitutionResponse(
            institution_id=institution.institution_id,
            name=institution.name,
            role=institution.role,
            description=institution.description,
            type=institution.type,
            verified=institution.verified,
            created_at=institution.created_at,
            updated_at=institution.updated_at
        )
        
    except Exception as e:
        logger.error(f"Error adding institution: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add institution"
        )

@router.get("/profile/institutions", response_model=List[InstitutionResponse])
async def get_institutions(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get all institutions for current user
    """
    try:
        institutions = db.query(Institution).filter(
            Institution.user_id == current_user.user_id
        ).order_by(Institution.created_at.desc()).all()
        
        return [
            InstitutionResponse(
                institution_id=i.institution_id,
                name=i.name,
                role=i.role,
                description=i.description,
                type=i.type,
                verified=i.verified,
                created_at=i.created_at,
                updated_at=i.updated_at
            ) for i in institutions
        ]
        
    except Exception as e:
        logger.error(f"Error getting institutions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get institutions"
        )

@router.put("/profile/institutions/{institution_id}", response_model=InstitutionResponse)
async def update_institution(
    institution_id: int,
    institution_data: InstitutionUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update an existing institution
    """
    try:
        institution = db.query(Institution).filter(
            Institution.institution_id == institution_id,
            Institution.user_id == current_user.user_id
        ).first()
        
        if not institution:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Institution not found"
            )
        
        # Update fields if provided
        if institution_data.name is not None:
            institution.name = institution_data.name
        if institution_data.role is not None:
            institution.role = institution_data.role
        if institution_data.description is not None:
            institution.description = institution_data.description
        if institution_data.type is not None:
            institution.type = institution_data.type
        
        institution.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(institution)
        
        return InstitutionResponse(
            institution_id=institution.institution_id,
            name=institution.name,
            role=institution.role,
            description=institution.description,
            type=institution.type,
            verified=institution.verified,
            created_at=institution.created_at,
            updated_at=institution.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating institution: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update institution"
        )

@router.delete("/profile/institutions/{institution_id}")
async def delete_institution(
    institution_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete an institution
    """
    try:
        institution = db.query(Institution).filter(
            Institution.institution_id == institution_id,
            Institution.user_id == current_user.user_id
        ).first()
        
        if not institution:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Institution not found"
            )
        
        db.delete(institution)
        db.commit()
        
        return {"message": "Institution deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting institution: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete institution"
        )
