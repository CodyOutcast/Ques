"""
Project schemas for API requests and responses
Following DATABASE_STRUCTURE_UPDATE.md specifications
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date
from enum import Enum

class ProjectStatus(str, Enum):
    """Project status enumeration"""
    ONGOING = "ONGOING"
    ON_HOLD = "ON_HOLD"
    FINISHED = "FINISHED"

class InstitutionType(str, Enum):
    """Institution type enumeration"""
    UNIVERSITY = "university"
    COMPANY = "company"
    GOVERNMENT = "government"
    NGO = "ngo"
    STARTUP = "startup"
    OTHER = "other"

class UserRole(str, Enum):
    """User role in institutions"""
    STUDENT = "student"
    EMPLOYEE = "employee"
    VOLUNTEER = "volunteer"
    INTERN = "intern"
    RESEARCHER = "researcher"
    PROFESSOR = "professor"
    MANAGER = "manager"
    OTHER = "other"

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

# Institution Schemas based on DATABASE_STRUCTURE_UPDATE.md

class InstitutionCreate(BaseModel):
    """Schema for creating a new institution"""
    name: str = Field(..., min_length=1, max_length=255, description="Institution name")
    name_en: Optional[str] = Field(None, max_length=255, description="English name")
    type: InstitutionType = Field(..., description="Institution type")
    city_id: int = Field(..., description="City ID from cities table")
    province_id: int = Field(..., description="Province ID from provinces table")
    description: Optional[str] = Field(None, description="Institution description")
    website: Optional[str] = Field(None, max_length=512, description="Website URL")
    logo_url: Optional[str] = Field(None, max_length=512, description="Logo image URL")

class InstitutionUpdate(BaseModel):
    """Schema for updating an institution"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    name_en: Optional[str] = Field(None, max_length=255)
    type: Optional[InstitutionType] = None
    city_id: Optional[int] = None
    province_id: Optional[int] = None
    description: Optional[str] = None
    website: Optional[str] = Field(None, max_length=512)
    logo_url: Optional[str] = Field(None, max_length=512)

class InstitutionResponse(BaseModel):
    """Schema for institution responses"""
    institution_id: int
    name: str
    role: str
    description: Optional[str] = None
    type: Optional[str] = None
    verified: bool = False
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class UserInstitutionCreate(BaseModel):
    """Schema for linking user to institution"""
    institution_id: int = Field(..., description="Institution ID")
    role: UserRole = Field(..., description="User role in institution")
    start_date: date = Field(..., description="Start date")
    end_date: Optional[date] = Field(None, description="End date (null if current)")
    is_current: bool = Field(True, description="Whether this is current")
    position: Optional[str] = Field(None, max_length=100, description="Job title, degree, etc.")
    department: Optional[str] = Field(None, max_length=100, description="Department or major")
    description: Optional[str] = Field(None, description="Additional details")

class UserInstitutionUpdate(BaseModel):
    """Schema for updating user-institution relationship"""
    role: Optional[UserRole] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_current: Optional[bool] = None
    position: Optional[str] = Field(None, max_length=100)
    department: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None

class UserInstitutionResponse(BaseModel):
    """Schema for user-institution relationship responses"""
    user_id: int
    institution_id: int
    role: UserRole
    start_date: date
    end_date: Optional[date] = None
    is_current: bool
    position: Optional[str] = None
    department: Optional[str] = None
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    # Institution details
    institution: Optional[InstitutionResponse] = None

    class Config:
        from_attributes = True

class UserStatisticsResponse(BaseModel):
    """Schema for user statistics responses"""
    user_id: int
    
    # Project statistics
    owned_projects: int = 0
    collaborated_projects: int = 0
    total_projects: int = 0
    
    # Institution statistics  
    educational_institutions: int = 0
    work_institutions: int = 0
    other_institutions: int = 0
    total_institutions: int = 0
    
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class UserLinkCreate(BaseModel):
    """Schema for creating user links"""
    url: str = Field(..., max_length=500, description="Link URL")
    title: Optional[str] = Field(None, max_length=100, description="Link title")
    description: Optional[str] = Field(None, description="Link description")
    link_type: Optional[str] = Field(None, max_length=50, description="Link type (portfolio, github, etc.)")

class UserLinkUpdate(BaseModel):
    """Schema for updating user links"""
    url: Optional[str] = Field(None, max_length=500)
    title: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    link_type: Optional[str] = Field(None, max_length=50)

class UserLinkResponse(BaseModel):
    """Schema for user link responses"""
    link_id: int
    url: str
    title: Optional[str] = None
    description: Optional[str] = None
    link_type: Optional[str] = None
    is_verified: bool = False
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
