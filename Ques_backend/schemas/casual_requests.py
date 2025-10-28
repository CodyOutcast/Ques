"""
Casual Requests Pydantic Schemas
Data validation and serialization for casual requests API
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List
from datetime import datetime

class CasualRequestBase(BaseModel):
    """Base schema for casual requests"""
    query: str = Field(..., min_length=10, max_length=500, description="The original request text")
    province_id: Optional[int] = Field(None, ge=1, description="Province ID for the activity location")
    city_id: Optional[int] = Field(None, ge=1, description="City ID for the activity location")
    preferences: Optional[Dict[str, Any]] = Field(None, description="User preferences as JSON object")

    @validator('query')
    def validate_query(cls, v):
        if not v.strip():
            raise ValueError('Query cannot be empty or just whitespace')
        return v.strip()

    @validator('city_id')
    def validate_city_requires_province(cls, v, values):
        if v is not None and 'province_id' in values and values['province_id'] is None:
            raise ValueError('City ID requires province ID to be set')
        return v

class CasualRequestCreate(CasualRequestBase):
    """Schema for creating a casual request"""
    
    class Config:
        schema_extra = {
            "example": {
                "query": "Looking for someone to grab coffee and discuss startup ideas this weekend",
                "province_id": 19,  # Guangdong Province
                "city_id": 308,     # Shenzhen City  
                "preferences": {
                    "activity_type": "social", 
                    "timing": "weekend", 
                    "interests": ["startups", "coffee", "networking"]
                }
            }
        }

class CasualRequestUpdate(BaseModel):
    """Schema for updating a casual request"""
    query: Optional[str] = Field(None, min_length=10, max_length=500)
    province_id: Optional[int] = Field(None, ge=1)
    city_id: Optional[int] = Field(None, ge=1) 
    preferences: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None

    @validator('query')
    def validate_query(cls, v):
        if v is not None and not v.strip():
            raise ValueError('Query cannot be empty or just whitespace')
        return v.strip() if v else v
        
    @validator('city_id')
    def validate_city_requires_province(cls, v, values):
        if v is not None and 'province_id' in values and values['province_id'] is None:
            raise ValueError('City ID requires province ID to be set')
        return v

class CasualRequestResponse(BaseModel):
    """Schema for casual request responses"""
    id: int
    user_id: str
    query: str
    optimized_query: str
    is_active: bool
    province_id: Optional[int]
    city_id: Optional[int]
    province_name: Optional[str] = Field(None, description="Province name (populated from relationships)")
    city_name: Optional[str] = Field(None, description="City name (populated from relationships)")
    preferences: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime
    last_activity_at: datetime

    class Config:
        from_attributes = True
        schema_extra = {
            "example": {
                "id": 1,
                "user_id": "user_123",
                "query": "Looking for hiking partners this weekend",
                "optimized_query": "Seeking outdoor enthusiasts for weekend hiking adventure in local trails",
                "is_active": True,
                "province_id": 19,
                "city_id": 308,
                "province_name": "Guangdong",
                "city_name": "Shenzhen",
                "preferences": {"activity_type": "outdoor", "timing": "weekend", "group_size": "2-5"},
                "created_at": "2024-01-15T10:30:00Z",
                "updated_at": "2024-01-15T10:30:00Z",
                "last_activity_at": "2024-01-15T10:30:00Z"
            }
        }

class CasualRequestSearch(BaseModel):
    """Schema for searching casual requests"""
    province_id: Optional[int] = Field(None, ge=1, description="Filter by province ID")
    city_id: Optional[int] = Field(None, ge=1, description="Filter by city ID")
    limit: Optional[int] = Field(20, ge=1, le=100, description="Number of results to return")
    
    class Config:
        schema_extra = {
            "example": {
                "province_id": 19,  # Guangdong
                "city_id": 308,     # Shenzhen
                "limit": 10
            }
        }

class CasualRequestMatch(BaseModel):
    """Schema for potential matches"""
    request: CasualRequestResponse
    similarity_score: float = Field(..., ge=0.0, le=1.0, description="Similarity score between 0-1")
    match_reasons: List[str] = Field(..., description="Reasons why this is a potential match")

    class Config:
        schema_extra = {
            "example": {
                "request": {
                    "id": 2,
                    "user_id": "user_456", 
                    "query": "Want to explore hiking trails around Shenzhen",
                    "optimized_query": "Seeking hiking companions for trail exploration in Shenzhen area",
                    "is_active": True,
                    "province_id": 19,
                    "city_id": 308,
                    "province_name": "Guangdong",
                    "city_name": "Shenzhen",
                    "preferences": {"activity_type": "outdoor", "timing": "flexible"},
                    "created_at": "2024-01-15T12:00:00Z",
                    "updated_at": "2024-01-15T12:00:00Z", 
                    "last_activity_at": "2024-01-15T12:00:00Z"
                },
                "similarity_score": 0.85,
                "match_reasons": ["Same province", "Same city", "Similar outdoor activity interest", "Compatible timing"]
            }
        }

class CasualRequestStats(BaseModel):
    """Schema for casual request statistics"""
    total_active_requests: int
    requests_by_location: Dict[str, int]
    recent_activity_count: int
    average_requests_per_day: float

    class Config:
        schema_extra = {
            "example": {
                "total_active_requests": 150,
                "requests_by_location": {"province_19": 45, "province_11": 32, "province_31": 28, "province_44": 20},
                "recent_activity_count": 25,
                "average_requests_per_day": 12.5
            }
        }

class CasualRequestList(BaseModel):
    """Schema for paginated list of casual requests"""
    requests: List[CasualRequestResponse]
    total_count: int
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)
    has_next: bool

    class Config:
        schema_extra = {
            "example": {
                "requests": [],
                "total_count": 150,
                "page": 1,
                "page_size": 20,
                "has_next": True
            }
        }