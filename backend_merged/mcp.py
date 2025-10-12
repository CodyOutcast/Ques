# backend/mcp_server.py
from mcp.server.fastmcp import FastMCP
from qdrant_client.http.models import Distance, PointStruct, Filter, FieldCondition, MatchValue
from sentence_transformers import SentenceTransformer
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

# Reuse your project configs
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/dbname")
QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", 6333))
COLLECTION_NAME = "user_profile_embeddings"
EMBEDDING_MODEL = SentenceTransformer('all-MiniLM-L6-v2')  # Dimension 384, as in app.py

# DB setup (reuse from app.py)
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Qdrant client (reuse from app.py)
from qdrant_client import QdrantClient
qdrant_client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)

# Initialize MCP server
mcp = FastMCP("User Discovery MCP Server")  # Name for your server

@mcp.tool()
def user_search(prompt: str, limit: int = 10, min_score: float = 0.7) -> list[dict]:
    """Search for matching users based on a natural language prompt. Converts prompt to embedding and performs vector similarity search. Returns list of user profiles with scores."""
    # Generate embedding (reuse your generate_embedding function)
    embedding = EMBEDDING_MODEL.encode(prompt).tolist()

    # Search in Qdrant (reuse logic from app.py /search/users)
    search_result = qdrant_client.search(
        collection_name=COLLECTION_NAME,
        query_vector=embedding,
        limit=limit,
        score_threshold=min_score,
        query_filter=Filter(
            must=[FieldCondition(key="profile_visibility", match=MatchValue(value="public"))]
        )
    )

    # Fetch profiles from PostgreSQL
    db = SessionLocal()
    try:
        users = []
        for hit in search_result:
            user_id = int(hit.id)
            from .app import UserProfile  # Import your UserProfile model from app.py
            profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
            if profile:
                users.append({
                    "user_id": user_id,
                    "score": hit.score,
                    "name": profile.name,
                    "age": profile.age,
                    "gender": profile.gender,
                    "location": profile.location,
                    "one_sentence_intro": profile.one_sentence_intro,
                    # Add more fields as needed, but avoid sensitive data
                })
        return users
    finally:
        db.close()

# Optional: Add a resource for quotas (example of non-tool capability)
@mcp.resource("quota://check/{user_id}")
def check_user_quota(user_id: int) -> dict:
    """Check a user's AI search quota."""
    db = SessionLocal()
    try:
        from .app import UserQuota  # Import model
        quota = db.query(UserQuota).filter(UserQuota.user_id == user_id).first()
        if quota:
            return {
                "ai_searches_today": quota.ai_searches_today,
                "ai_searches_limit": quota.ai_searches_limit
            }
        return {"error": "Quota not found"}
    finally:
        db.close()

# Optional: Add a prompt template for user search
@mcp.prompt()
def user_search_prompt(query: str) -> str:
    """Template prompt for initiating a user search."""
    return f"Find users matching: {query}. Use the user_search tool to get results."

if __name__ == "__main__":
    mcp.run()  # Run as standalone for testing: python mcp_server.py