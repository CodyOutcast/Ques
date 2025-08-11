"""
Location service for handling user location operations
"""

import requests
import math
from sqlalchemy.orm import Session
from sqlalchemy import text, func
from typing import List, Optional, Tuple
from datetime import datetime

from models.users import User
from schemas.location import (
    LocationUpdate, LocationResponse, CoordinatesRequest, 
    AddressRequest, LocationSearchRequest, NearbyUsersResponse
)

class LocationService:
    """Service for handling location operations"""
    
    @staticmethod
    def update_user_location(db: Session, user_id: int, location_data: LocationUpdate) -> LocationResponse:
        """
        Update user's location information
        """
        user = db.query(User).filter(User.user_id == user_id).first()
        
        if not user:
            raise ValueError("User not found")
        
        # Update location fields
        if location_data.latitude is not None:
            user.latitude = location_data.latitude
        if location_data.longitude is not None:
            user.longitude = location_data.longitude
        if location_data.city is not None:
            user.city = location_data.city
        if location_data.state is not None:
            user.state = location_data.state
        if location_data.country is not None:
            user.country = location_data.country
        if location_data.postal_code is not None:
            user.postal_code = location_data.postal_code
        if location_data.address is not None:
            user.address = location_data.address
        
        db.commit()
        db.refresh(user)
        
        return LocationService._build_location_response(user)
    
    @staticmethod
    def update_location_from_coordinates(db: Session, user_id: int, coordinates: CoordinatesRequest) -> LocationResponse:
        """
        Update user location from GPS coordinates and reverse geocode
        """
        user = db.query(User).filter(User.user_id == user_id).first()
        
        if not user:
            raise ValueError("User not found")
        
        # Update coordinates
        user.latitude = str(coordinates.latitude)
        user.longitude = str(coordinates.longitude)
        
        # Try to reverse geocode to get address information
        try:
            location_info = LocationService._reverse_geocode(coordinates.latitude, coordinates.longitude)
            if location_info:
                user.city = location_info.get('city')
                user.state = location_info.get('state')
                user.country = location_info.get('country')
                user.postal_code = location_info.get('postal_code')
                user.address = location_info.get('address')
        except Exception as e:
            print(f"Reverse geocoding failed: {e}")
            # Continue without address info
        
        db.commit()
        db.refresh(user)
        
        return LocationService._build_location_response(user)
    
    @staticmethod
    def update_location_from_address(db: Session, user_id: int, address_data: AddressRequest) -> LocationResponse:
        """
        Update user location from address and forward geocode
        """
        user = db.query(User).filter(User.user_id == user_id).first()
        
        if not user:
            raise ValueError("User not found")
        
        # Try to geocode address to get coordinates
        try:
            coordinates = LocationService._forward_geocode(address_data.address)
            if coordinates:
                user.latitude = str(coordinates['latitude'])
                user.longitude = str(coordinates['longitude'])
                user.address = address_data.address
                
                # Also try to parse city/state from geocoding result
                location_info = LocationService._reverse_geocode(coordinates['latitude'], coordinates['longitude'])
                if location_info:
                    user.city = location_info.get('city')
                    user.state = location_info.get('state')
                    user.country = location_info.get('country')
                    user.postal_code = location_info.get('postal_code')
        except Exception as e:
            print(f"Geocoding failed: {e}")
            # Just store the address without coordinates
            user.address = address_data.address
        
        db.commit()
        db.refresh(user)
        
        return LocationService._build_location_response(user)
    
    @staticmethod
    def get_user_location(db: Session, user_id: int) -> Optional[LocationResponse]:
        """
        Get user's location information
        """
        user = db.query(User).filter(User.user_id == user_id).first()
        
        if not user:
            return None
        
        return LocationService._build_location_response(user)
    
    @staticmethod
    def find_nearby_users(db: Session, search_request: LocationSearchRequest, current_user_id: int) -> List[NearbyUsersResponse]:
        """
        Find users within a specified radius using Haversine formula
        """
        # Get users with location data (excluding current user)
        users_with_location = db.query(User).filter(
            User.user_id != current_user_id,
            User.latitude.isnot(None),
            User.longitude.isnot(None),
            User.is_active == True
        ).all()
        
        nearby_users = []
        
        for user in users_with_location:
            try:
                user_lat = float(user.latitude)
                user_lng = float(user.longitude)
                
                # Calculate distance using Haversine formula
                distance = LocationService._calculate_distance(
                    search_request.latitude, search_request.longitude,
                    user_lat, user_lng
                )
                
                # Check if within radius
                if distance <= search_request.radius_km:
                    nearby_users.append(NearbyUsersResponse(
                        user_id=user.user_id,
                        name=user.name,
                        bio=user.bio,
                        city=user.city,
                        state=user.state,
                        distance_km=round(distance, 2),
                        latitude=user.latitude,
                        longitude=user.longitude
                    ))
            except (ValueError, TypeError):
                # Skip users with invalid coordinates
                continue
        
        # Sort by distance and limit results
        nearby_users.sort(key=lambda x: x.distance_km or float('inf'))
        return nearby_users[:search_request.limit]
    
    @staticmethod
    def _calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calculate distance between two points using Haversine formula
        Returns distance in kilometers
        """
        R = 6371  # Earth's radius in kilometers
        
        # Convert to radians
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)
        
        # Haversine formula
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        
        a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        distance = R * c
        
        return distance
    
    @staticmethod
    def _reverse_geocode(latitude: float, longitude: float) -> Optional[dict]:
        """
        Convert coordinates to address using a geocoding service
        You can replace this with your preferred geocoding service
        """
        try:
            # Example using OpenStreetMap Nominatim (free service)
            url = f"https://nominatim.openstreetmap.org/reverse"
            params = {
                'format': 'json',
                'lat': latitude,
                'lon': longitude,
                'zoom': 18,
                'addressdetails': 1
            }
            
            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()
            
            data = response.json()
            address = data.get('address', {})
            
            return {
                'city': address.get('city') or address.get('town') or address.get('village'),
                'state': address.get('state'),
                'country': address.get('country'),
                'postal_code': address.get('postcode'),
                'address': data.get('display_name')
            }
        except Exception as e:
            print(f"Reverse geocoding error: {e}")
            return None
    
    @staticmethod
    def _forward_geocode(address: str) -> Optional[dict]:
        """
        Convert address to coordinates using a geocoding service
        """
        try:
            # Example using OpenStreetMap Nominatim (free service)
            url = "https://nominatim.openstreetmap.org/search"
            params = {
                'format': 'json',
                'q': address,
                'limit': 1
            }
            
            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()
            
            data = response.json()
            if data:
                result = data[0]
                return {
                    'latitude': float(result['lat']),
                    'longitude': float(result['lon'])
                }
            
            return None
        except Exception as e:
            print(f"Forward geocoding error: {e}")
            return None
    
    @staticmethod
    def _build_location_response(user: User) -> LocationResponse:
        """
        Build a LocationResponse from user data
        """
        formatted_location = None
        if user.city and user.state:
            formatted_location = f"{user.city}, {user.state}"
        elif user.city:
            formatted_location = user.city
        
        return LocationResponse(
            latitude=user.latitude,
            longitude=user.longitude,
            city=user.city,
            state=user.state,
            country=user.country,
            postal_code=user.postal_code,
            address=user.address,
            formatted_location=formatted_location
        )
