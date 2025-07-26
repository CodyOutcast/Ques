"""
Basic Profile Router (Placeholder)
This can be expanded later for additional profile functionality
"""

from fastapi import APIRouter

router = APIRouter()

@router.get("/test")
def test_profile():
    return {"message": "Profile router is working"}
