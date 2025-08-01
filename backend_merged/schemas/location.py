"""
Location schemas for user location management
"""

from pydantic import BaseModel, Field, validator
from typing import Optional
import re

class LocationUpdate(BaseModel):
    """Schema for updating user location"""
    latitude: Optional[str] = Field(None, description="Latitude coordinate")
    longitude: Optional[str] = Field(None, description="Longitude coordinate")
    city: Optional[str] = Field(None, max_length=100, description="City name")
    state: Optional[str] = Field(None, max_length=100, description="State/Province")
    country: Optional[str] = Field(None, max_length=100, description="Country")
    postal_code: Optional[str] = Field(None, max_length=20, description="Postal/ZIP code")
    address: Optional[str] = Field(None, max_length=500, description="Full address")
    
    @validator('latitude')
    def validate_latitude(cls, v):
        if v is not None:
            try:
                lat = float(v)
                if not -90 <= lat <= 90:
                    raise ValueError('Latitude must be between -90 and 90')
            except ValueError:
                raise ValueError('Invalid latitude format')
        return v
    
    @validator('longitude')
    def validate_longitude(cls, v):
        if v is not None:
            try:
                lng = float(v)
                if not -180 <= lng <= 180:
                    raise ValueError('Longitude must be between -180 and 180')
            except ValueError:
                raise ValueError('Invalid longitude format')
        return v

class LocationResponse(BaseModel):
    """Schema for location responses"""
    latitude: Optional[str] = None
    longitude: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None
    address: Optional[str] = None
    formatted_location: Optional[str] = None  # Combined city, state format
    
    class Config:
        from_attributes = True

class CoordinatesRequest(BaseModel):
    """Schema for receiving GPS coordinates"""
    latitude: float = Field(..., ge=-90, le=90, description="Latitude coordinate")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude coordinate")
    accuracy: Optional[float] = Field(None, description="Accuracy in meters")

class AddressRequest(BaseModel):
    """Schema for receiving address information"""
    address: str = Field(..., min_length=1, max_length=500, description="Full address to geocode")

class LocationSearchRequest(BaseModel):
    """Schema for location-based user search"""
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    radius_km: float = Field(10, ge=0.1, le=100, description="Search radius in kilometers")
    limit: int = Field(20, ge=1, le=100, description="Maximum results")

class NearbyUsersResponse(BaseModel):
    """Schema for nearby users response"""
    user_id: int
    name: str
    bio: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    distance_km: Optional[float] = None  # Distance from search point
    latitude: Optional[str] = None
    longitude: Optional[str] = None
