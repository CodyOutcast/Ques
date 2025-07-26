#!/usr/bin/env python3
"""
Simple server test - start with basic functionality
"""

from fastapi import FastAPI

app = FastAPI(
    title="Project Tinder Backend - Test", 
    description="Testing basic server functionality",
    version="1.0.0"
)

@app.get("/")
def root():
    return {"message": "Server is running - Pages 3 & 4 coming soon!"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "message": "Server is operational"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
