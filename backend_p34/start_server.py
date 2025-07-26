#!/usr/bin/env python3
"""
Simple test script to run the backend directly without uvicorn issues
"""

from main import app
import uvicorn

if __name__ == "__main__":
    print("🚀 Starting Project Tinder Backend API...")
    print("📖 Visit http://127.0.0.1:8000/docs for API documentation")
    uvicorn.run(app, host="127.0.0.1", port=8000)
