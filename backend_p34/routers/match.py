"""
Basic Match Router (Placeholder)
This can be expanded later for swiping and matching functionality
"""

from fastapi import APIRouter

router = APIRouter()

@router.get("/test")
def test_match():
    return {"message": "Match router is working"}
