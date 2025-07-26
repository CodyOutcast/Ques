from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.profile import router as profile_router  # Import the router
from routers.match import router as match_router
from routers.users import router as users_router  # Page 3: User Creation
from routers.chat import router as chat_router  # Page 4: Chat functionality

app = FastAPI(
    title="Project Tinder Backend",
    description="Backend API for project matchmaking app - All 4 Pages",
    version="1.0.0"
)

# Add CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(profile_router, prefix="/profile", tags=["Profile Management"])
app.include_router(match_router, prefix="/match", tags=["Matching & Discovery"])
app.include_router(users_router, prefix="/users", tags=["Page 3: User Creation"])
app.include_router(chat_router, prefix="/chat", tags=["Page 4: Chat & Messages"])

@app.get("/")
def root():
    return {"message": "Project Tinder Backend API - All 4 Pages Ready!"}