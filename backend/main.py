from fastapi import FastAPI
from routers.profile import router as profile_router  # Import the router
from routers.match import router as match_router

app = FastAPI()  # The main app

app.include_router(profile_router, prefix="/profile")  # Plug in profile at /profile/summarize
app.include_router(match_router, prefix="/match")  # Plug in match at /match/summarize

# Later, add more like: from routers.likes import router as likes_router
# app.include_router(likes_router, prefix="/likes")