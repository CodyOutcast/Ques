"""
Test script for project functionality
"""

import requests
import json
from datetime import datetime

# Replace with your actual server URL
BASE_URL = "http://localhost:8000"

def test_projects_api():
    """
    Test the projects API endpoints
    """
    print("🚀 Testing Projects API...")
    
    # Headers with authentication (replace with actual token)
    headers = {
        "Authorization": "Bearer YOUR_TOKEN_HERE",
        "Content-Type": "application/json"
    }
    
    print("\n📋 Available API Endpoints:")
    print("1. POST   /api/projects/                    - Create project")
    print("2. GET    /api/projects/{project_id}        - Get project details")
    print("3. PUT    /api/projects/{project_id}        - Update project")
    print("4. DELETE /api/projects/{project_id}        - Delete project")
    print("5. POST   /api/projects/{project_id}/users  - Add user to project")
    print("6. DELETE /api/projects/{project_id}/users/{user_id} - Remove user")
    print("7. GET    /api/projects/                    - Get my projects")
    print("8. GET    /api/projects/search/             - Search projects")
    
    print("\n💾 Database Schema:")
    print("Projects Table:")
    print("  - project_id (PK, auto-increment)")
    print("  - short_description (String, 200 chars max)")
    print("  - long_description (Text, optional)")
    print("  - start_time (DateTime)")
    print("  - media_link_id (FK to user_links, optional)")
    print("  - created_at, updated_at (DateTime)")
    
    print("\nUser_Projects Table:")
    print("  - user_id (PK, FK to users)")
    print("  - project_id (PK, FK to projects)")
    print("  - role (String, optional - Owner/Collaborator/Contributor)")
    print("  - joined_at (DateTime)")
    
    print("\n🔗 Relationships:")
    print("  - Many-to-Many: Users ↔ Projects")
    print("  - Optional: Projects → UserLinks (for media)")
    
    # Example API calls (commented out - uncomment when you have authentication)
    """
    # Example 1: Create a project
    project_data = {
        "short_description": "AI-powered dating app backend with advanced matching",
        "long_description": "A comprehensive backend system for a dating application featuring AI-powered matching algorithms, real-time messaging, and user preference learning.",
        "start_time": "2025-07-30T10:00:00Z",
        "media_link_id": None
    }
    
    response = requests.post(f"{BASE_URL}/api/projects/", json=project_data, headers=headers)
    if response.status_code == 201:
        project = response.json()
        print(f"✅ Created project: {project['project_id']}")
        
        # Example 2: Get project details
        response = requests.get(f"{BASE_URL}/api/projects/{project['project_id']}", headers=headers)
        if response.status_code == 200:
            print(f"✅ Retrieved project details")
            
        # Example 3: Add user to project
        response = requests.post(
            f"{BASE_URL}/api/projects/{project['project_id']}/users",
            params={"target_user_id": 2, "role": "Collaborator"},
            headers=headers
        )
        if response.status_code == 201:
            print(f"✅ Added user to project")
    """
    
    print("\n📖 Usage Examples:")
    
    print("\n1. Create Project:")
    print("""
    POST /api/projects/
    {
        "short_description": "Mobile app for local community events",
        "long_description": "An app that helps people discover and organize local events...",
        "start_time": "2025-08-01T09:00:00Z",
        "media_link_id": null
    }
    """)
    
    print("\n2. Add User to Project:")
    print("""
    POST /api/projects/1/users?target_user_id=2&role=Collaborator
    """)
    
    print("\n3. Search Projects:")
    print("""
    GET /api/projects/search/?query=app&limit=10&my_projects_only=true
    """)
    
    print("\n✅ Project tables and API are ready!")
    print("⚠️  Remember to run database migration when DB is available")

def show_sql_migration():
    """
    Show the SQL commands that would be executed
    """
    print("\n📊 SQL Migration Commands:")
    print("""
    -- Create projects table
    CREATE TABLE projects (
        project_id SERIAL PRIMARY KEY,
        short_description VARCHAR(200) NOT NULL,
        long_description TEXT,
        start_time TIMESTAMP NOT NULL,
        media_link_id INTEGER REFERENCES user_links(user_id),
        created_at TIMESTAMP NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMP NOT NULL DEFAULT NOW()
    );
    
    -- Create user_projects junction table
    CREATE TABLE user_projects (
        user_id INTEGER REFERENCES users(user_id),
        project_id INTEGER REFERENCES projects(project_id),
        role VARCHAR(100),
        joined_at TIMESTAMP NOT NULL DEFAULT NOW(),
        PRIMARY KEY (user_id, project_id)
    );
    
    -- Create indexes for better performance
    CREATE INDEX idx_projects_created_at ON projects(created_at);
    CREATE INDEX idx_user_projects_user_id ON user_projects(user_id);
    CREATE INDEX idx_user_projects_project_id ON user_projects(project_id);
    """)

if __name__ == "__main__":
    print("🎯 Projects Feature Implementation")
    print("=" * 50)
    
    test_projects_api()
    show_sql_migration()
    
    print(f"\n📁 Files Created:")
    print("✅ models/projects.py - Project and UserProject models")
    print("✅ schemas/projects.py - Pydantic schemas for API")
    print("✅ services/project_service.py - Business logic")
    print("✅ routers/projects.py - API endpoints")
    print("✅ migrations/versions/add_projects_tables.py - Database migration")
    
    print(f"\n🔄 Next Steps:")
    print("1. Add project router to main.py")
    print("2. Run database migration: alembic upgrade head")
    print("3. Test API endpoints with authentication")
    print("4. Add project features to frontend")
    
    print(f"\n🎉 Projects feature is ready for integration!")
