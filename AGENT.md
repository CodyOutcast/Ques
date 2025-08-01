# AGENT.md - Ques: Tinder for Projects

## Build/Test Commands
- **Backend P12 (Main)**: `uvicorn main:app --reload` (port 8000)
- **Backend P34**: `uvicorn main:app --reload` 
- **Test Backend P12**: `python test_essential.py` (primary), `python test_api.py`
- **Test Backend P34**: `python test_pages_3_4.py`, `python check_db.py`
- **Database Setup**: `python setup_database.py` or `alembic upgrade head && python seed.py`
- **Single Test Run**: Use specific test files like `python test_recommendation_algorithm.py`

## Architecture 
**Project Structure**: Tinder-like app for matching people with projects
- **backend_p12/**: Main backend (Pages 1-2) - FastAPI, PostgreSQL, JWT auth, vector search, recommendations
- **backend_p34/**: Secondary backend (Pages 3-4) - Chat system, profile management
- **Dynamic Card Swiping Interface/**: React/TypeScript frontend with motion animations
- **Database**: PostgreSQL with Alembic migrations, Tencent VectorDB for embeddings
- **AI Services**: DeepSeek API for tag extraction, sentence-transformers for vector embeddings

## Code Style
- **Python**: FastAPI routers, Pydantic schemas, SQLAlchemy models
- **Database**: Use `postgresql+psycopg://` URLs (psycopg3 for Python 3.13+)
- **Authentication**: JWT tokens (30min expiry), refresh tokens (30-day), bcrypt password hashing
- **Error Handling**: Standardized error responses with codes, structured logging
- **File Structure**: `models/`, `routers/`, `services/`, `schemas/`, `dependencies/`
- **Frontend**: TypeScript, motion/react for animations, Lucide React icons
- **Environment**: `.env` files for config, never commit secrets
