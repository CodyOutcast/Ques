#!/usr/bin/env python3
"""
Minimal matches router for testing
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

router = APIRouter()

class SearchInput(BaseModel):
    query: str

@router.post("/query")
async def ai_search(search_input: SearchInput):
    """
    Temporary AI Search endpoint - returns placeholder
    """
    return {
        "message": "AI search temporarily unavailable - vector database not configured",
        "query": search_input.query,
        "results": []
    }

@router.get("/status")
async def search_status():
    """Status endpoint"""
    return {"status": "ok", "message": "AI search router is working"}
