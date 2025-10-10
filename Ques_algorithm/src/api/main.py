#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FastAPI Backend Service
Provides RESTful API endpoints for user information
"""

from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import sqlite3
import json
from datetime import datetime, date
import logging
from contextlib import contextmanager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database configuration
DB_FILE = "quesai_test.db"

# FastAPI application
app = FastAPI(
    title="QuesAI Backend Test API",
    description="User information API for search functionality testing",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic model definitions
class UserProject(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    role: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    is_current: bool = False
    skills_used: List[str] = []
    reference_links: List[str] = []

class UserInstitution(BaseModel):
    institution_id: int
    institution_name: str
    institution_type: str
    role: Optional[str] = None
    position: Optional[str] = None
    department: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    is_current: bool = True
    description: Optional[str] = None

class UserProfile(BaseModel):
    id: int
    name: Optional[str] = None
    age: Optional[int] = None
    birthday: Optional[str] = None
    gender: Optional[str] = None
    province_id: Optional[int] = None
    city_id: Optional[int] = None
    province_name: Optional[str] = None
    city_name: Optional[str] = None
    location: Optional[str] = None
    profile_photo: Optional[str] = None
    one_sentence_intro: Optional[str] = None
    hobbies: List[str] = []
    languages: List[str] = []
    skills: List[str] = []
    resources: List[str] = []
    goals: Optional[str] = None
    demands: List[str] = []
    current_university: Optional[str] = None
    university_email: Optional[str] = None
    university_verified: bool = False
    wechat_id: Optional[str] = None
    wechat_verified: bool = False
    is_profile_complete: bool = False
    profile_visibility: str = "public"
    project_count: int = 0
    institution_count: int = 0
    last_active: Optional[str] = None
    projects: List[UserProject] = []
    institutions: List[UserInstitution] = []

class UserListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    users: List[UserProfile]

class Province(BaseModel):
    id: int
    name_en: str
    name_cn: str

class City(BaseModel):
    id: int
    province_id: int
    name_en: str
    name_cn: str

class Institution(BaseModel):
    id: int
    name: str
    name_en: Optional[str] = None
    type: str
    description: Optional[str] = None
    location: Optional[str] = None

# Database connection management
@contextmanager
def get_db_connection():
    """Get database connection context manager"""
    conn = None
    try:
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row  # Return rows in dictionary format
        yield conn
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Database connection error: {e}")
        raise
    finally:
        if conn:
            conn.close()

def safe_json_loads(json_str: str, default=None) -> Any:
    """Safe JSON parsing"""
    if not json_str:
        return default or []
    try:
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError):
        return default or []

def format_date(date_obj) -> Optional[str]:
    """Format date"""
    if date_obj is None:
        return None
    if isinstance(date_obj, str):
        return date_obj
    return date_obj.strftime("%Y-%m-%d") if hasattr(date_obj, 'strftime') else str(date_obj)

# API routes

@app.get("/", summary="Root path", description="API service status check")
async def root():
    """API root path"""
    return {
        "message": "QuesAI Backend Test API",
        "version": "1.0.0",
        "status": "active",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health", summary="Health check", description="Check API and database connection status")
async def health_check():
    """Health check endpoint"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM users")
            user_count = cursor.fetchone()[0]
            
        return {
            "status": "healthy",
            "database": "connected",
            "user_count": user_count,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")

@app.get("/users", response_model=UserListResponse, summary="Get user list", description="Get paginated user list")
async def get_users(
    page: int = Query(1, ge=1, description="Page number, starts from 1"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page, maximum 100"),
    search: Optional[str] = Query(None, description="Search keywords (name, skills, intro)"),
    province: Optional[str] = Query(None, description="Province filter"),
    city: Optional[str] = Query(None, description="City filter"),
    skill: Optional[str] = Query(None, description="Skill filter"),
    university: Optional[str] = Query(None, description="University filter"),
    min_age: Optional[int] = Query(None, ge=16, le=80, description="Minimum age"),
    max_age: Optional[int] = Query(None, ge=16, le=80, description="Maximum age")
):
    """Get user list"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Build WHERE conditions
            where_conditions = ["up.profile_visibility = 'public'"]
            params = []
            
            if search:
                where_conditions.append("""
                    (u.name LIKE ? OR up.one_sentence_intro LIKE ? OR up.skills LIKE ?)
                """)
                search_param = f"%{search}%"
                params.extend([search_param, search_param, search_param])
            
            if province:
                where_conditions.append("up.province_name_cn LIKE ?")
                params.append(f"%{province}%")
            
            if city:
                where_conditions.append("up.city_name_cn LIKE ?")
                params.append(f"%{city}%")
            
            if skill:
                where_conditions.append("up.skills LIKE ?")
                params.append(f"%{skill}%")
            
            if university:
                where_conditions.append("up.current_university LIKE ?")
                params.append(f"%{university}%")
            
            if min_age:
                where_conditions.append("up.age >= ?")
                params.append(min_age)
            
            if max_age:
                where_conditions.append("up.age <= ?")
                params.append(max_age)
            
            where_clause = " AND ".join(where_conditions)
            
            # Get total count
            count_query = f"""
                SELECT COUNT(*)
                FROM users u
                JOIN user_profiles up ON u.id = up.user_id
                WHERE {where_clause}
            """
            cursor.execute(count_query, params)
            total = cursor.fetchone()[0]
            
            # Get paginated data
            offset = (page - 1) * page_size
            query = f"""
                SELECT u.id, u.name, up.*,
                       p.name_cn as province_name_cn,
                       c.name_cn as city_name_cn
                FROM users u
                JOIN user_profiles up ON u.id = up.user_id
                LEFT JOIN provinces p ON up.province_id = p.id
                LEFT JOIN cities c ON up.city_id = c.id
                WHERE {where_clause}
                ORDER BY up.last_active DESC, u.created_at DESC
                LIMIT ? OFFSET ?
            """
            cursor.execute(query, params + [page_size, offset])
            rows = cursor.fetchall()
            
            # Get project and institution information for each user
            users = []
            for row in rows:
                user_data = dict(row)
                user_id = user_data['id']
                
                # Get project information
                projects = get_user_projects(cursor, user_id)
                
                # Get institution information
                institutions = get_user_institutions(cursor, user_id)
                
                # Build user object
                user_profile = build_user_profile(user_data, projects, institutions)
                users.append(user_profile)
            
            return UserListResponse(
                total=total,
                page=page,
                page_size=page_size,
                users=users
            )
            
    except Exception as e:
        logger.error(f"Failed to get user list: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get user list: {str(e)}")

@app.get("/users/{user_id}", response_model=UserProfile, summary="Get user details", description="Get complete user information by user ID")
async def get_user_detail(user_id: int):
    """Get user details"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Get user basic information
            query = """
                SELECT u.id, u.name, up.*,
                       p.name_cn as province_name_cn,
                       c.name_cn as city_name_cn
                FROM users u
                JOIN user_profiles up ON u.id = up.user_id
                LEFT JOIN provinces p ON up.province_id = p.id
                LEFT JOIN cities c ON up.city_id = c.id
                WHERE u.id = ?
            """
            cursor.execute(query, (user_id,))
            row = cursor.fetchone()
            
            if not row:
                raise HTTPException(status_code=404, detail="User not found")
            
            user_data = dict(row)
            
            # Get project and institution information
            projects = get_user_projects(cursor, user_id)
            institutions = get_user_institutions(cursor, user_id)
            
            # Build complete user profile
            user_profile = build_user_profile(user_data, projects, institutions)
            
            return user_profile
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get user details: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get user details: {str(e)}")

def get_user_projects(cursor, user_id: int) -> List[UserProject]:
    """Get user project list"""
    cursor.execute("""
        SELECT id, title, description, role, start_date, end_date, is_current, skills_used, reference_links
        FROM user_projects
        WHERE user_id = ?
        ORDER BY is_current DESC, start_date DESC
    """, (user_id,))
    
    projects = []
    for row in cursor.fetchall():
        project_data = dict(row)
        projects.append(UserProject(
            id=project_data['id'],
            title=project_data['title'],
            description=project_data['description'],
            role=project_data['role'],
            start_date=format_date(project_data['start_date']),
            end_date=format_date(project_data['end_date']),
            is_current=bool(project_data['is_current']),
            skills_used=safe_json_loads(project_data['skills_used']),
            reference_links=safe_json_loads(project_data['reference_links'])
        ))
    
    return projects

def get_user_institutions(cursor, user_id: int) -> List[UserInstitution]:
    """Get user institution association list"""
    cursor.execute("""
        SELECT ui.*, i.name as institution_name, i.type as institution_type
        FROM user_institutions ui
        JOIN institutions i ON ui.institution_id = i.id
        WHERE ui.user_id = ?
        ORDER BY ui.is_current DESC, ui.start_date DESC
    """, (user_id,))
    
    institutions = []
    for row in cursor.fetchall():
        inst_data = dict(row)
        institutions.append(UserInstitution(
            institution_id=inst_data['institution_id'],
            institution_name=inst_data['institution_name'],
            institution_type=inst_data['institution_type'],
            role=inst_data['role'],
            position=inst_data['position'],
            department=inst_data['department'],
            start_date=format_date(inst_data['start_date']),
            end_date=format_date(inst_data['end_date']),
            is_current=bool(inst_data['is_current']),
            description=inst_data['description']
        ))
    
    return institutions

def build_user_profile(user_data: dict, projects: List[UserProject], institutions: List[UserInstitution]) -> UserProfile:
    """Build complete user profile object"""
    return UserProfile(
        id=user_data['id'],
        name=user_data['name'],
        age=user_data['age'],
        birthday=format_date(user_data['birthday']),
        gender=user_data['gender'],
        province_id=user_data['province_id'],
        city_id=user_data['city_id'],
        province_name=user_data.get('province_name_cn'),
        city_name=user_data.get('city_name_cn'),
        location=user_data['location'],
        profile_photo=user_data['profile_photo'],
        one_sentence_intro=user_data['one_sentence_intro'],
        hobbies=safe_json_loads(user_data['hobbies']),
        languages=safe_json_loads(user_data['languages']),
        skills=safe_json_loads(user_data['skills']),
        resources=safe_json_loads(user_data['resources']),
        goals=user_data['goals'],
        demands=safe_json_loads(user_data['demands']),
        current_university=user_data['current_university'],
        university_email=user_data['university_email'],
        university_verified=bool(user_data['university_verified']),
        wechat_id=user_data['wechat_id'],
        wechat_verified=bool(user_data['wechat_verified']),
        is_profile_complete=bool(user_data['is_profile_complete']),
        profile_visibility=user_data['profile_visibility'],
        project_count=user_data['project_count'],
        institution_count=user_data['institution_count'],
        last_active=user_data['last_active'],
        projects=projects,
        institutions=institutions
    )

@app.get("/provinces", response_model=List[Province], summary="Get province list", description="Get all province information")
async def get_provinces():
    """Get province list"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name_en, name_cn FROM provinces ORDER BY id")
            rows = cursor.fetchall()
            
            return [Province(**dict(row)) for row in rows]
            
    except Exception as e:
        logger.error(f"Failed to get province list: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get province list: {str(e)}")

@app.get("/cities", response_model=List[City], summary="Get city list", description="Get city information, can filter by province")
async def get_cities(province_id: Optional[int] = Query(None, description="Province ID filter")):
    """Get city list"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            if province_id:
                cursor.execute("""
                    SELECT id, province_id, name_en, name_cn 
                    FROM cities 
                    WHERE province_id = ?
                    ORDER BY id
                """, (province_id,))
            else:
                cursor.execute("SELECT id, province_id, name_en, name_cn FROM cities ORDER BY province_id, id")
            
            rows = cursor.fetchall()
            return [City(**dict(row)) for row in rows]
            
    except Exception as e:
        logger.error(f"Failed to get city list: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get city list: {str(e)}")

@app.get("/institutions", response_model=List[Institution], summary="Get institution list", description="Get institution information, can filter by type")
async def get_institutions(
    type: Optional[str] = Query(None, description="Institution type filter"),
    search: Optional[str] = Query(None, description="Institution name search")
):
    """Get institution list"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            where_conditions = []
            params = []
            
            if type:
                where_conditions.append("type = ?")
                params.append(type)
            
            if search:
                where_conditions.append("(name LIKE ? OR name_en LIKE ?)")
                search_param = f"%{search}%"
                params.extend([search_param, search_param])
            
            where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"
            
            query = f"""
                SELECT id, name, name_en, type, description, location
                FROM institutions
                WHERE {where_clause}
                ORDER BY type, name
            """
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            return [Institution(**dict(row)) for row in rows]
            
    except Exception as e:
        logger.error(f"Failed to get institution list: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get institution list: {str(e)}")

@app.get("/stats", summary="Get statistics", description="Get user and data statistics")
async def get_stats():
    """Get statistics"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Basic statistics
            cursor.execute("SELECT COUNT(*) FROM users")
            total_users = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM user_profiles WHERE is_profile_complete = 1")
            complete_profiles = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM user_projects")
            total_projects = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM institutions")
            total_institutions = cursor.fetchone()[0]
            
            # Statistics by gender
            cursor.execute("""
                SELECT gender, COUNT(*) as count
                FROM user_profiles
                WHERE gender IS NOT NULL
                GROUP BY gender
            """)
            gender_stats = {row[0]: row[1] for row in cursor.fetchall()}
            
            # Statistics by age group
            cursor.execute("""
                SELECT 
                    CASE 
                        WHEN age < 25 THEN '18-24'
                        WHEN age < 30 THEN '25-29'
                        WHEN age < 35 THEN '30-34'
                        WHEN age < 40 THEN '35-39'
                        ELSE '40+'
                    END as age_group,
                    COUNT(*) as count
                FROM user_profiles
                WHERE age IS NOT NULL
                GROUP BY age_group
                ORDER BY age_group
            """)
            age_stats = {row[0]: row[1] for row in cursor.fetchall()}
            
            # Statistics by province
            cursor.execute("""
                SELECT p.name_cn, COUNT(*) as count
                FROM user_profiles up
                JOIN provinces p ON up.province_id = p.id
                GROUP BY p.id, p.name_cn
                ORDER BY count DESC
                LIMIT 10
            """)
            province_stats = {row[0]: row[1] for row in cursor.fetchall()}
            
            return {
                "total_users": total_users,
                "complete_profiles": complete_profiles,
                "completion_rate": round(complete_profiles / total_users * 100, 2) if total_users > 0 else 0,
                "total_projects": total_projects,
                "total_institutions": total_institutions,
                "gender_distribution": gender_stats,
                "age_distribution": age_stats,
                "top_provinces": province_stats,
                "timestamp": datetime.now().isoformat()
            }
            
    except Exception as e:
        logger.error(f"Failed to get statistics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get statistics: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)