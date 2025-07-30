"""
Startup script for the merged backend application
"""

import uvicorn
import os
from dotenv import load_dotenv

load_dotenv()

if __name__ == "__main__":
    print("🚀 Starting Merged Backend Application...")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("📋 Health Check: http://localhost:8000/health")
    print("ℹ️  API Info: http://localhost:8000/api/v1/info")
    print("=" * 50)
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
        access_log=True
    )
