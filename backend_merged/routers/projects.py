"""
Project router for project management API
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from dependencies.db import get_db
from dependencies.auth import get_current_user
from models.users import User
from services.project_service import ProjectService
from schemas.projects import (
    ProjectCreate, ProjectUpdate, ProjectResponse, 
    UserProjectCreate, UserProjectResponse, ProjectWithUsers, 
    UserWithProjects, ProjectListResponse
)

router = APIRouter(prefix="/api/projects", tags=["projects"])

@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(
    project_data: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new project
    The creator automatically becomes the project owner
    """
    try:
        return ProjectService.create_project(db, current_user.user_id, project_data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/{project_id}", response_model=ProjectWithUsers)
def get_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a project by ID with associated users
    """
    project = ProjectService.get_project(db, project_id, current_user.user_id)
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    return project

@router.put("/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: int,
    project_data: ProjectUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update a project
    Only owners and collaborators can update projects
    """
    try:
        project = ProjectService.update_project(db, project_id, current_user.user_id, project_data)
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        return project
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )

@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a project
    Only project owners can delete projects
    """
    try:
        success = ProjectService.delete_project(db, project_id, current_user.user_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )

@router.post("/{project_id}/users", response_model=UserProjectResponse, status_code=status.HTTP_201_CREATED)
def add_user_to_project(
    project_id: int,
    target_user_id: int,
    role: str = "Collaborator",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Add a user to a project
    Only owners and collaborators can add users
    """
    try:
        return ProjectService.add_user_to_project(
            db, project_id, current_user.user_id, target_user_id, role
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.delete("/{project_id}/users/{target_user_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_user_from_project(
    project_id: int,
    target_user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Remove a user from a project
    Owners can remove anyone, users can remove themselves
    """
    try:
        success = ProjectService.remove_user_from_project(
            db, project_id, current_user.user_id, target_user_id
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found in project"
            )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )

@router.get("/users/{user_id}/projects", response_model=UserWithProjects)
def get_user_projects(
    user_id: int,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all projects for a user
    Users can only see their own projects unless they're admin
    """
    # For now, users can only see their own projects
    if user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own projects"
        )
    
    try:
        return ProjectService.get_user_projects(db, user_id, limit, offset)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@router.get("/search/", response_model=ProjectListResponse)
def search_projects(
    query: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    my_projects_only: bool = Query(False, description="Search only in user's projects"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Search projects by description
    """
    user_id = current_user.user_id if my_projects_only else None
    
    return ProjectService.search_projects(db, query, user_id, limit, offset)

@router.get("/", response_model=UserWithProjects)
def get_my_projects(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current user's projects
    """
    try:
        return ProjectService.get_user_projects(db, current_user.user_id, limit, offset)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
