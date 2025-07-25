from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.recommendations import router as recommendations_router
from routers.match import router as match_router
from routers.auth import router as auth_router

app = FastAPI(
    title="Project Tinder Backend", 
    description="Backend API for project matchmaking app - Pages 1 & 2",
    version="1.0.0"
)

# Add CORS middleware for React Native frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(recommendations_router, prefix="/recommendations", tags=["Recommendations"])
app.include_router(match_router, prefix="/search", tags=["AI Search"])

@app.get("/")
def root():
    return {"message": "Project Tinder Backend API - Ready for Pages 1 & 2"}