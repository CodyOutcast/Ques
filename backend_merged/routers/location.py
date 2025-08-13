"""
Location router for user location management
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from dependencies.db import get_db
from dependencies.auth import get_current_user
from models.users import User
from services.location_service import LocationService
from schemas.location import (
    LocationUpdate, LocationResponse, CoordinatesRequest,
    AddressRequest, LocationSearchRequest, NearbyUsersResponse
)

router = APIRouter(prefix="/api/location", tags=["location"])

@router.get("/me", response_model=LocationResponse)
def get_my_location(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current user's location information
    """
    location = LocationService.get_user_location(db, current_user.user_id)
    
    if not location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Location not found"
        )
    
    return location

@router.put("/me", response_model=LocationResponse)
def update_my_location(
    location_data: LocationUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update current user's location information
    """
    try:
        return LocationService.update_user_location(db, current_user.user_id, location_data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/me/coordinates", response_model=LocationResponse)
def update_location_from_gps(
    coordinates: CoordinatesRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update location from GPS coordinates
    Will attempt to reverse geocode to get address information
    """
    try:
        return LocationService.update_location_from_coordinates(db, current_user.user_id, coordinates)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/me/address", response_model=LocationResponse)
def update_location_from_address(
    address_data: AddressRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update location from address
    Will attempt to geocode to get coordinates
    """
    try:
        return LocationService.update_location_from_address(db, current_user.user_id, address_data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/nearby", response_model=List[NearbyUsersResponse])
def find_nearby_users(
    search_request: LocationSearchRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Find users within a specified radius
    """
    return LocationService.find_nearby_users(db, search_request, current_user.user_id)

@router.get("/user/{user_id}", response_model=LocationResponse)
def get_user_location(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get another user's location (for matching/chat purposes)
    Note: Consider privacy settings in production
    """
    location = LocationService.get_user_location(db, user_id)
    
    if not location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User location not found"
        )
    
    # In production, you might want to check if users are matched
    # or have permission to see each other's location
    return location
