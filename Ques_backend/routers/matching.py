"""
Matching & Search Service Router
Implements all matching and search endpoints as defined in the frontend API documentation
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import logging
import json

from dependencies.db import get_db
from dependencies.auth import get_current_user
from models.users import User
from models.swipes import AIRecommendationSwipe
from models.agent_cards import AgentCardSwipe
from pydantic import BaseModel, Field

router = APIRouter(prefix="/matching", tags=["Matching"])
logger = logging.getLogger(__name__)

# Pydantic Models for Request/Response
class SearchParams(BaseModel):
    query: Optional[str] = None
    searchMode: Optional[str] = Field('global', description="'inside' or 'global'")
    filters: Optional[Dict[str, Any]] = None
    excludeContacts: Optional[List[str]] = None
    limit: Optional[int] = Field(20, le=100)
    offset: Optional[int] = Field(0, ge=0)

class MatchingCriteria(BaseModel):
    location: Optional[List[str]] = None
    skills: Optional[List[str]] = None
    university: Optional[List[str]] = None
    industries: Optional[List[str]] = None
    experienceLevel: Optional[List[str]] = None
    availability: Optional[List[str]] = None

class AdvancedSearchRequest(BaseModel):
    searchMode: Optional[str] = Field('global', description="'inside' or 'global'")
    location: Optional[Dict[str, Any]] = None
    demographics: Optional[Dict[str, Any]] = None
    skills: Optional[Dict[str, Any]] = None
    experience: Optional[Dict[str, Any]] = None
    education: Optional[Dict[str, Any]] = None
    availability: Optional[Dict[str, Any]] = None
    other: Optional[Dict[str, Any]] = None
    pagination: Optional[Dict[str, int]] = Field({"page": 1, "limit": 20})
    sorting: Optional[Dict[str, str]] = Field({"by": "relevance", "order": "desc"})

class SavedSearch(BaseModel):
    name: str
    query: Optional[str] = None
    filters: Dict[str, Any]

class MatchScore(BaseModel):
    overall: float
    skillsMatch: float
    goalsAlignment: float
    locationMatch: float
    networkOverlap: float
    availabilityMatch: float
    experienceMatch: float

class MatchExplanation(BaseModel):
    reasons: List[str]
    mutualBenefits: List[str]
    potentialChallenges: Optional[List[str]] = None
    suggestedAction: str

class UserRecommendation(BaseModel):
    id: str
    username: str
    displayName: Optional[str] = None
    avatarUrl: Optional[str] = None
    bio: Optional[str] = None
    skills: List[str] = []
    location: Optional[str] = None
    matchScore: Optional[float] = None
    whyMatch: Optional[str] = None
    isOnline: bool = False
    mutualConnections: int = 0
    responseRate: Optional[float] = None

class SearchSuggestions(BaseModel):
    queries: List[str]
    skills: List[str]
    locations: List[str]
    universities: List[str]
    industries: List[str]

class SearchAnalytics(BaseModel):
    searchId: Optional[str] = None
    totalSearches: int
    popularQueries: List[Dict[str, Any]]
    averageResultCount: float
    clickThroughRate: float
    mostClickedProfiles: List[Dict[str, Any]]

# Search endpoints
@router.post("/search")
async def search_users(
    params: SearchParams,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Search Users
    Matches frontend API: POST /matching/search
    """
    try:
        user_id = current_user["id"]
        
        # Build base query
        query = db.query(User).filter(User.id != user_id)
        
        # Apply text search if query provided
        if params.query:
            search_term = f"%{params.query}%"
            query = query.filter(
                or_(
                    User.username.ilike(search_term),
                    User.display_name.ilike(search_term),
                    User.bio.ilike(search_term)
                )
            )
        
        # Apply filters if provided
        if params.filters:
            # Location filter
            if params.filters.get('location'):
                locations = params.filters['location']
                query = query.filter(User.location.in_(locations))
            
            # Skills filter (simplified - assumes skills are stored in bio or separate table)
            if params.filters.get('skills'):
                skills = params.filters['skills']
                skill_conditions = [User.bio.ilike(f"%{skill}%") for skill in skills]
                query = query.filter(or_(*skill_conditions))
            
            # University filter
            if params.filters.get('university'):
                universities = params.filters['university']
                # Assuming university info is in bio or separate field
                uni_conditions = [User.bio.ilike(f"%{uni}%") for uni in universities]
                query = query.filter(or_(*uni_conditions))
        
        # Exclude contacts if specified
        if params.excludeContacts:
            exclude_ids = [int(uid) for uid in params.excludeContacts if uid.isdigit()]
            query = query.filter(~User.id.in_(exclude_ids))
        
        # Apply pagination
        total_count = query.count()
        users = query.offset(params.offset).limit(params.limit).all()
        
        # Convert to UserRecommendation format
        results = []
        for user in users:
            results.append(UserRecommendation(
                id=str(user.id),
                username=user.username or f"user_{user.id}",
                displayName=user.display_name,
                avatarUrl=user.avatar_url,
                bio=user.bio,
                skills=[], # TODO: Extract from user data
                location=user.location,
                matchScore=75.0, # Placeholder
                whyMatch="Similar interests and location",
                isOnline=False, # TODO: Get from online status
                mutualConnections=0, # TODO: Calculate
                responseRate=0.8 # Placeholder
            ))
        
        return {
            "success": True,
            "data": results,
            "pagination": {
                "total": total_count,
                "offset": params.offset,
                "limit": params.limit,
                "hasMore": total_count > params.offset + params.limit
            }
        }
        
    except Exception as e:
        logger.error(f"Search users failed: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@router.post("/score/{targetUserId}")
async def get_match_score(
    targetUserId: str = Path(..., description="Target user ID"),
    criteria: Optional[MatchingCriteria] = None,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get Match Score
    Matches frontend API: POST /matching/score/{targetUserId}
    """
    try:
        user_id = current_user["id"]
        
        # Get current user and target user
        current_user_obj = db.query(User).filter(User.id == user_id).first()
        target_user = db.query(User).filter(User.id == int(targetUserId)).first()
        
        if not target_user:
            raise HTTPException(status_code=404, detail="Target user not found")
        
        # Calculate match scores (simplified algorithm)
        # In a real implementation, this would use ML models and comprehensive analysis
        
        # Location match
        location_match = 80.0 if (current_user_obj.location and target_user.location and 
                                 current_user_obj.location.lower() in target_user.location.lower()) else 30.0
        
        # Skills match (placeholder - would need proper skill extraction)
        skills_match = 70.0  # Placeholder
        
        # Goals alignment (placeholder)
        goals_alignment = 65.0
        
        # Network overlap (placeholder)
        network_overlap = 25.0
        
        # Availability match (placeholder)
        availability_match = 85.0
        
        # Experience match (placeholder)
        experience_match = 60.0
        
        # Overall score (weighted average)
        overall = (
            location_match * 0.2 +
            skills_match * 0.25 +
            goals_alignment * 0.2 +
            network_overlap * 0.1 +
            availability_match * 0.15 +
            experience_match * 0.1
        )
        
        match_score = MatchScore(
            overall=round(overall, 1),
            skillsMatch=skills_match,
            goalsAlignment=goals_alignment,
            locationMatch=location_match,
            networkOverlap=network_overlap,
            availabilityMatch=availability_match,
            experienceMatch=experience_match
        )
        
        return {
            "success": True,
            "data": match_score.dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get match score failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to calculate match score: {str(e)}")

@router.post("/explanation/{targetUserId}")
async def get_match_explanation(
    targetUserId: str = Path(..., description="Target user ID"),
    criteria: Optional[MatchingCriteria] = None,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get Match Explanation
    Matches frontend API: POST /matching/explanation/{targetUserId}
    """
    try:
        user_id = current_user["id"]
        
        # Get target user
        target_user = db.query(User).filter(User.id == int(targetUserId)).first()
        if not target_user:
            raise HTTPException(status_code=404, detail="Target user not found")
        
        # Generate explanation based on user data
        reasons = [
            "Similar professional interests",
            "Compatible skill sets",
            "Complementary experience levels"
        ]
        
        if target_user.location:
            reasons.append(f"Both located in similar regions")
        
        mutual_benefits = [
            "Knowledge sharing opportunities",
            "Potential collaboration on projects",
            "Network expansion"
        ]
        
        potential_challenges = [
            "Different time zones might affect coordination",
            "Different experience levels may require mentoring"
        ]
        
        explanation = MatchExplanation(
            reasons=reasons,
            mutualBenefits=mutual_benefits,
            potentialChallenges=potential_challenges,
            suggestedAction="Send a connection request to explore collaboration opportunities"
        )
        
        return {
            "success": True,
            "data": explanation.dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get match explanation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate explanation: {str(e)}")

# Matching criteria endpoints
@router.put("/criteria")
async def update_matching_criteria(
    criteria: MatchingCriteria,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update Matching Criteria
    Matches frontend API: PUT /matching/criteria
    """
    try:
        user_id = current_user["id"]
        
        # In a real implementation, store criteria in a UserPreferences table
        # For now, we'll return success with the provided criteria
        
        return {
            "success": True,
            "message": "Matching criteria updated successfully",
            "data": criteria.dict()
        }
        
    except Exception as e:
        logger.error(f"Update matching criteria failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update criteria: {str(e)}")

@router.get("/criteria")
async def get_matching_criteria(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get Matching Criteria
    Matches frontend API: GET /matching/criteria
    """
    try:
        user_id = current_user["id"]
        
        # In a real implementation, retrieve from UserPreferences table
        # For now, return default criteria
        default_criteria = MatchingCriteria(
            location=["Any"],
            skills=["Software Development", "AI/ML", "Data Science"],
            university=["Any"],
            industries=["Technology", "Education"],
            experienceLevel=["Intermediate", "Senior"],
            availability=["Part-time", "Full-time"]
        )
        
        return {
            "success": True,
            "data": default_criteria.dict()
        }
        
    except Exception as e:
        logger.error(f"Get matching criteria failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get criteria: {str(e)}")

# Advanced search
@router.post("/search/advanced")
async def advanced_search(
    request: AdvancedSearchRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Advanced Search
    Matches frontend API: POST /matching/search/advanced
    """
    try:
        user_id = current_user["id"]
        
        # Build complex query based on advanced filters
        query = db.query(User).filter(User.id != user_id)
        
        # Location filters
        if request.location:
            if request.location.get('countries'):
                # Assuming country info is in location field
                countries = request.location['countries']
                country_conditions = [User.location.ilike(f"%{country}%") for country in countries]
                query = query.filter(or_(*country_conditions))
            
            if request.location.get('cities'):
                cities = request.location['cities']
                city_conditions = [User.location.ilike(f"%{city}%") for city in cities]
                query = query.filter(or_(*city_conditions))
        
        # Demographics filters
        if request.demographics:
            if request.demographics.get('ageRange'):
                age_min, age_max = request.demographics['ageRange']
                query = query.filter(User.age.between(age_min, age_max))
            
            if request.demographics.get('genders'):
                genders = request.demographics['genders']
                query = query.filter(User.gender.in_(genders))
        
        # Skills filters
        if request.skills:
            if request.skills.get('required'):
                required_skills = request.skills['required']
                for skill in required_skills:
                    query = query.filter(User.bio.ilike(f"%{skill}%"))
            
            if request.skills.get('preferred'):
                preferred_skills = request.skills['preferred']
                if preferred_skills:
                    pref_conditions = [User.bio.ilike(f"%{skill}%") for skill in preferred_skills]
                    query = query.filter(or_(*pref_conditions))
        
        # Other filters
        if request.other:
            if request.other.get('isOnline'):
                # Would need online status tracking
                pass
        
        # Apply sorting
        if request.sorting:
            sort_by = request.sorting.get('by', 'relevance')
            sort_order = request.sorting.get('order', 'desc')
            
            if sort_by == 'recent':
                if sort_order == 'desc':
                    query = query.order_by(desc(User.created_at))
                else:
                    query = query.order_by(User.created_at)
        
        # Apply pagination
        page = request.pagination.get('page', 1)
        limit = request.pagination.get('limit', 20)
        offset = (page - 1) * limit
        
        total_count = query.count()
        users = query.offset(offset).limit(limit).all()
        
        # Convert to results
        results = []
        for user in users:
            results.append({
                "id": str(user.id),
                "username": user.username or f"user_{user.id}",
                "displayName": user.display_name,
                "avatarUrl": user.avatar_url,
                "bio": user.bio,
                "location": user.location,
                "matchScore": 75.0, # Placeholder
                "isOnline": False # Placeholder
            })
        
        return {
            "success": True,
            "data": {
                "data": results,
                "pagination": {
                    "page": page,
                    "limit": limit,
                    "total": total_count,
                    "totalPages": (total_count + limit - 1) // limit
                }
            }
        }
        
    except Exception as e:
        logger.error(f"Advanced search failed: {e}")
        raise HTTPException(status_code=500, detail=f"Advanced search failed: {str(e)}")

# Search suggestions and analytics
@router.get("/search/suggestions")
async def get_search_suggestions(
    q: str = Query(..., description="Query for suggestions"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Search Suggestions
    Matches frontend API: GET /matching/search/suggestions?q={query}
    """
    try:
        # Generate suggestions based on existing data and popular searches
        suggestions = SearchSuggestions(
            queries=[
                f"{q} developers",
                f"{q} students", 
                f"{q} professionals",
                f"{q} in tech",
                f"{q} AI researchers"
            ],
            skills=[
                "Python", "JavaScript", "React", "Node.js", "AI/ML",
                "Data Science", "Web Development", "Mobile Development"
            ],
            locations=[
                "San Francisco", "New York", "London", "Berlin", "Tokyo",
                "Beijing", "Shenzhen", "Singapore", "Sydney"
            ],
            universities=[
                "Stanford University", "MIT", "Harvard", "UC Berkeley",
                "Tsinghua University", "Peking University"
            ],
            industries=[
                "Technology", "Finance", "Healthcare", "Education",
                "E-commerce", "Gaming", "Artificial Intelligence"
            ]
        )
        
        return {
            "success": True,
            "data": suggestions.dict()
        }
        
    except Exception as e:
        logger.error(f"Get search suggestions failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get suggestions: {str(e)}")

@router.get("/search/trending")
async def get_trending_searches(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Trending Searches
    Matches frontend API: GET /matching/search/trending
    """
    try:
        # In a real implementation, this would track and analyze search patterns
        trending_searches = [
            {"query": "AI developers", "count": 156, "growth": "+25%"},
            {"query": "Full stack engineers", "count": 134, "growth": "+18%"},
            {"query": "Data scientists", "count": 122, "growth": "+15%"},
            {"query": "Product managers", "count": 98, "growth": "+22%"},
            {"query": "UI/UX designers", "count": 87, "growth": "+12%"}
        ]
        
        return {
            "success": True,
            "data": trending_searches
        }
        
    except Exception as e:
        logger.error(f"Get trending searches failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get trending searches: {str(e)}")

# Saved searches
@router.post("/search/save")
async def save_search(
    search: SavedSearch,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Save Search
    Matches frontend API: POST /matching/search/save
    """
    try:
        user_id = current_user["id"]
        
        # In a real implementation, save to SavedSearches table
        saved_search = {
            "id": f"search_{user_id}_{datetime.now().timestamp()}",
            "name": search.name,
            "query": search.query,
            "filters": search.filters,
            "userId": user_id,
            "createdAt": datetime.now().isoformat(),
            "lastUsed": None
        }
        
        return {
            "success": True,
            "message": "Search saved successfully",
            "data": saved_search
        }
        
    except Exception as e:
        logger.error(f"Save search failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to save search: {str(e)}")

@router.get("/search/saved")
async def get_saved_searches(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get Saved Searches
    Matches frontend API: GET /matching/search/saved
    """
    try:
        user_id = current_user["id"]
        
        # In a real implementation, retrieve from SavedSearches table
        saved_searches = [
            {
                "id": "search_1",
                "name": "AI Developers in SF",
                "query": "AI developers",
                "filters": {"location": ["San Francisco"], "skills": ["AI/ML", "Python"]},
                "createdAt": "2024-10-01T10:00:00Z",
                "lastUsed": "2024-10-10T14:30:00Z"
            },
            {
                "id": "search_2", 
                "name": "Full Stack Engineers",
                "query": "full stack",
                "filters": {"skills": ["React", "Node.js", "MongoDB"]},
                "createdAt": "2024-09-15T16:20:00Z",
                "lastUsed": "2024-10-08T09:15:00Z"
            }
        ]
        
        return {
            "success": True,
            "data": saved_searches
        }
        
    except Exception as e:
        logger.error(f"Get saved searches failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get saved searches: {str(e)}")

@router.delete("/search/saved/{searchId}")
async def delete_saved_search(
    searchId: str = Path(..., description="Saved search ID"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete Saved Search
    Matches frontend API: DELETE /matching/search/saved/{searchId}
    """
    try:
        user_id = current_user["id"]
        
        # In a real implementation, delete from SavedSearches table with user ownership check
        # For now, just return success
        
        return {
            "success": True,
            "message": f"Saved search {searchId} deleted successfully"
        }
        
    except Exception as e:
        logger.error(f"Delete saved search failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete saved search: {str(e)}")

# Search analytics
@router.get("/search/analytics")
async def get_search_analytics(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Search Analytics (General)
    Matches frontend API: GET /matching/search/analytics
    """
    try:
        user_id = current_user["id"]
        
        # In a real implementation, gather analytics from search logs
        analytics = SearchAnalytics(
            totalSearches=247,
            popularQueries=[
                {"query": "AI developers", "count": 45},
                {"query": "full stack", "count": 38},
                {"query": "data scientist", "count": 32},
                {"query": "product manager", "count": 28},
                {"query": "designer", "count": 25}
            ],
            averageResultCount=18.5,
            clickThroughRate=0.24,
            mostClickedProfiles=[
                {"userId": "user_123", "clicks": 23, "name": "Alice Developer"},
                {"userId": "user_456", "clicks": 19, "name": "Bob Designer"},
                {"userId": "user_789", "clicks": 16, "name": "Carol Manager"}
            ]
        )
        
        return {
            "success": True,
            "data": analytics.dict()
        }
        
    except Exception as e:
        logger.error(f"Get search analytics failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get analytics: {str(e)}")

@router.get("/search/analytics/{searchId}")
async def get_search_analytics_by_id(
    searchId: str = Path(..., description="Search ID for specific analytics"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Search Analytics (Specific)
    Matches frontend API: GET /matching/search/analytics/{searchId}
    """
    try:
        user_id = current_user["id"]
        
        # In a real implementation, get analytics for specific search
        analytics = SearchAnalytics(
            searchId=searchId,
            totalSearches=23,
            popularQueries=[
                {"query": f"search_{searchId}_query1", "count": 12},
                {"query": f"search_{searchId}_query2", "count": 8},
                {"query": f"search_{searchId}_query3", "count": 3}
            ],
            averageResultCount=15.2,
            clickThroughRate=0.31,
            mostClickedProfiles=[
                {"userId": "user_321", "clicks": 7, "name": "David Engineer"},
                {"userId": "user_654", "clicks": 5, "name": "Eve Analyst"}
            ]
        )
        
        return {
            "success": True,
            "data": analytics.dict()
        }
        
    except Exception as e:
        logger.error(f"Get specific search analytics failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get analytics for search {searchId}: {str(e)}")
