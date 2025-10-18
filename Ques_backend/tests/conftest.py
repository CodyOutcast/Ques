"""
Test configuration and fixtures for the Ques backend tests
"""

import pytest
import asyncio
from typing import Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from main import app
from dependencies.db import get_db
from models.base import Base

# Test database configuration
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create test database tables
Base.metadata.create_all(bind=engine)


def override_get_db():
    """Override database dependency for testing"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


# Override the database dependency
app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def client() -> Generator:
    """Create a test client for the FastAPI app"""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def db_session():
    """Create a database session for testing"""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()


# Sample test data fixtures
@pytest.fixture
def sample_user_data():
    """Sample user data for testing"""
    return {
        "email": "test@example.com",
        "password": "TestPassword123",
        "name": "Test User",
        "role": "student",
        "location": "Test City",
        "bio": "Test user bio",
        "skills": ["Python", "FastAPI"],
        "interests": ["AI", "Web Development"]
    }


@pytest.fixture
def sample_profile_data():
    """Sample profile data for testing"""
    return {
        "name": "John Doe",
        "age": 25,
        "gender": "male",
        "location": "Shenzhen",
        "skills": ["Python", "JavaScript", "React"],
        "resources": ["funding", "network"],
        "goals": "Build innovative mobile applications",
        "hobbies": ["coding", "gaming"],
        "languages": ["English", "Chinese"]
    }


@pytest.fixture
def auth_headers(client, sample_user_data):
    """Create authentication headers for testing"""
    # Register user
    response = client.post("/api/v1/auth/register", json=sample_user_data)
    
    # Login to get token
    login_data = {
        "username": sample_user_data["email"], 
        "password": sample_user_data["password"]
    }
    response = client.post("/api/v1/auth/login", data=login_data)
    token = response.json()["access_token"]
    
    return {"Authorization": f"Bearer {token}"}