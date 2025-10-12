"""
Sample test fixtures and data for testing
"""

# Sample user profiles for testing
SAMPLE_PROFILES = [
    {
        "name": "Alice Chen",
        "age": 24,
        "gender": "female",
        "location": "Shenzhen",
        "profile_photo": "https://example.com/alice.jpg",
        "one_sentence_intro": "AI researcher passionate about machine learning applications",
        "skills": ["Python", "TensorFlow", "PyTorch", "Data Science"],
        "resources": ["Research lab access", "GPU computing", "Academic network"],
        "goals": "Develop AI solutions for healthcare and contribute to open-source ML projects",
        "hobbies": ["reading", "hiking", "photography"],
        "languages": ["English", "Mandarin", "Japanese"],
        "demands": ["research collaborators", "industry mentorship"],
        "current_university": "Tsinghua University",
        "university_verified": True
    },
    {
        "name": "David Kim",
        "age": 28,
        "gender": "male", 
        "location": "Seoul",
        "profile_photo": None,  # Missing avatar - for testing incomplete profiles
        "one_sentence_intro": "Entrepreneur building fintech solutions",
        "skills": ["JavaScript", "React", "Node.js", "Blockchain"],
        "resources": [],  # Missing resources - for testing
        "goals": "Launch a successful fintech startup focused on micro-lending",
        "hobbies": ["gaming", "cooking"],
        "languages": ["Korean", "English"],
        "demands": ["technical co-founder", "seed funding"],
        "current_university": "KAIST",
        "university_verified": False
    },
    {
        "name": "Maria Santos",
        "age": 26,
        "gender": "female",
        "location": "São Paulo", 
        "profile_photo": "https://example.com/maria.jpg",
        "one_sentence_intro": "UX designer creating inclusive digital experiences",
        "skills": ["Figma", "Adobe Creative Suite", "User Research", "Prototyping"],
        "resources": ["Design team", "User testing lab", "Industry connections"],
        "goals": "Design accessible interfaces that serve underrepresented communities",
        "hobbies": ["art", "music", "volunteer work"],
        "languages": ["Portuguese", "English", "Spanish"],
        "demands": ["frontend developers", "accessibility experts"],
        "current_university": "USP",
        "university_verified": True
    }
]

# Sample project data
SAMPLE_PROJECTS = [
    {
        "title": "HealthTracker AI",
        "role": "Lead Developer",
        "description": "AI-powered health monitoring app using wearable device data",
        "reference_links": ["https://github.com/user/healthtracker"]
    },
    {
        "title": "EcoCommute",
        "role": "Co-founder",
        "description": "Carbon footprint tracking for daily commuting patterns",
        "reference_links": ["https://ecocommute.app"]
    }
]

# Sample API responses for mocking
SAMPLE_API_RESPONSES = {
    "profile_analysis": {
        "user_id": "12345",
        "completion_percentage": 85.0,
        "overall_assessment": "Very good profile with strong foundations",
        "suggestions": [
            {
                "field": "resources",
                "priority": "medium",
                "suggestion": "Add more specific resources you can offer",
                "impact": "Helps attract better collaboration matches"
            }
        ],
        "strengths": ["Clear goals", "Strong skill set", "Good introduction"],
        "critical_missing": [],
        "ai_reasoning": "Profile shows good completeness with room for minor improvements"
    }
}

# Test user credentials
TEST_CREDENTIALS = {
    "valid_user": {
        "email": "test@example.com",
        "password": "TestPassword123"
    },
    "invalid_user": {
        "email": "invalid@example.com", 
        "password": "wrongpassword"
    }
}

# Database test data
TEST_DATABASE_RECORDS = {
    "users": [
        {
            "id": 1,
            "email": "user1@test.com",
            "username": "testuser1",
            "is_verified": True
        },
        {
            "id": 2, 
            "email": "user2@test.com",
            "username": "testuser2",
            "is_verified": False
        }
    ],
    "profiles": [
        {
            "user_id": 1,
            "name": "Test User 1",
            "age": 25,
            "location": "Test City"
        }
    ]
}