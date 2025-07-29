#!/usr/bin/env python3
"""
Simple server starter that handles imports properly
"""

import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    try:
        print("🚀 Starting Ques Backend Server...")
        print("📍 Current directory:", os.getcwd())
        
        # Test imports first
        print("🔍 Testing imports...")
        import main
        print("✅ Main module imported successfully")
        
        # Start the server
        print("🌐 Starting FastAPI server on http://localhost:8000")
        print("📚 API Documentation: http://localhost:8000/docs")
        print("🛑 Press Ctrl+C to stop the server")
        print("-" * 50)
        
        import uvicorn
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
        
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
