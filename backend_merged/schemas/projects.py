"""
Project schemas for API requests and responses
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class ProjectStatus(str, Enum):
    """Project status enumeration"""
    ONGOING = "ONGOING"
    ON_HOLD = "ON_HOLD"
    FINISHED = "FINISHED"

class ProjectCreate(BaseModel):
    """Schema for creating a new project"""
    short_description: str = Field(..., min_length=1, max_length=200, description="Short project description (max 20 words)")
    long_description: Optional[str] = Field(None, description="Detailed project description")
    start_time: datetime = Field(..., description="Project start time")
    status: Optional[ProjectStatus] = Field(ProjectStatus.ONGOING, description="Project status")
    media_link_id: Optional[int] = Field(None, description="Optional media link from user_links table")

class ProjectUpdate(BaseModel):
    """Schema for updating a project"""
    short_description: Optional[str] = Field(None, min_length=1, max_length=200)
    long_description: Optional[str] = None
    start_time: Optional[datetime] = None
    status: Optional[ProjectStatus] = None
    media_link_id: Optional[int] = None

class ProjectResponse(BaseModel):
    """Schema for project responses"""
    project_id: int
    short_description: str
    long_description: Optional[str] = None
    start_time: datetime
    status: ProjectStatus
    media_link_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class UserProjectCreate(BaseModel):
    """Schema for adding a user to a project"""
    project_id: int
    user_id: int
    role: Optional[str] = Field(None, max_length=100, description="User role in project (e.g., Owner, Collaborator)")

class UserProjectResponse(BaseModel):
    """Schema for user-project relationship responses"""
    user_id: int
    project_id: int
    role: Optional[str] = None
    joined_at: datetime
    
    # Include user and project details
    user_name: Optional[str] = None
    project_short_description: Optional[str] = None
    
    class Config:
        from_attributes = True

class ProjectWithUsers(BaseModel):
    """Schema for project with associated users"""
    project_id: int
    short_description: str
    long_description: Optional[str] = None
    start_time: datetime
    status: ProjectStatus
    media_link_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    users: List[UserProjectResponse] = []

class UserWithProjects(BaseModel):
    """Schema for user with associated projects"""
    user_id: int
    user_name: str
    projects: List[UserProjectResponse] = []

class ProjectListResponse(BaseModel):
    """Schema for paginated project lists"""
    projects: List[ProjectResponse]
    total: int
    page: int
    per_page: int
