#!/usr/bin/env python3
"""
Complete test server for Page 3 (User Creation) and Page 4 (Chat)
This version uses in-memory storage for testing without database issues
"""

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

app = FastAPI(
    title="Project Tinder Backend - Pages 3 & 4 Test", 
    description="Testing Page 3 (User Creation) and Page 4 (Chat) functionality",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for testing
users_db: Dict[int, Dict[str, Any]] = {}
matches_db: Dict[int, Dict[str, Any]] = {}
messages_db: Dict[int, Dict[str, Any]] = {}
next_user_id = 1
next_match_id = 1
next_message_id = 1

# Pydantic models
class UserCreateRequest(BaseModel):
    name: str
    bio: Optional[str] = None
    feature_tags: Optional[List[str]] = []
    portfolio_links: Optional[List[str]] = []

class UserResponse(BaseModel):
    user_id: int
    name: str
    bio: Optional[str]
    verification_status: str
    is_active: bool
    created_at: datetime
    feature_tags: List[str]
    portfolio_links: List[str]

class MessageSendRequest(BaseModel):
    match_id: int
    message_text: str

class MessageResponse(BaseModel):
    message_id: int
    match_id: int
    sender_id: int
    sender_name: str
    message_text: str
    sent_at: datetime
    is_read: bool

class MatchResponse(BaseModel):
    match_id: int
    other_user_id: int
    other_user_name: str
    other_user_bio: Optional[str]
    matched_at: datetime
    last_message: Optional[str]
    last_message_at: Optional[datetime]
    unread_count: int

# Root endpoint
@app.get("/")
def root():
    return {"message": "Project Tinder Backend - Pages 3 & 4 Test Server Running!"}

# ============= PAGE 3: USER CREATION ENDPOINTS =============

@app.post("/users/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user_data: UserCreateRequest):
    """Page 3: Create a new user account with profile information"""
    global next_user_id
    
    user_id = next_user_id
    next_user_id += 1
    
    new_user = {
        "user_id": user_id,
        "name": user_data.name,
        "bio": user_data.bio,
        "verification_status": "pending",
        "is_active": True,
        "created_at": datetime.utcnow(),
        "feature_tags": user_data.feature_tags,
        "portfolio_links": user_data.portfolio_links
    }
    
    users_db[user_id] = new_user
    
    return UserResponse(**new_user)

@app.get("/users/profile/{user_id}", response_model=UserResponse)
def get_user_profile(user_id: int):
    """Get user profile information by user ID"""
    if user_id not in users_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserResponse(**users_db[user_id])

@app.get("/users/", response_model=Dict[str, Any])
def get_all_users(skip: int = 0, limit: int = 50):
    """Get list of all active users"""
    active_users = [user for user in users_db.values() if user["is_active"]]
    paginated_users = active_users[skip:skip + limit]
    
    user_responses = [UserResponse(**user) for user in paginated_users]
    
    return {"users": user_responses, "total": len(user_responses)}

# ============= PAGE 4: CHAT ENDPOINTS =============

@app.post("/test/create-match")
def create_test_match(user1_id: int, user2_id: int):
    """Helper endpoint to create test matches for testing chat functionality"""
    global next_match_id
    
    if user1_id not in users_db or user2_id not in users_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="One or both users not found"
        )
    
    match_id = next_match_id
    next_match_id += 1
    
    new_match = {
        "match_id": match_id,
        "user1_id": user1_id,
        "user2_id": user2_id,
        "matched_at": datetime.utcnow(),
        "is_active": True
    }
    
    matches_db[match_id] = new_match
    
    return {"message": f"Match created between users {user1_id} and {user2_id}", "match_id": match_id}

@app.get("/chat/matches/{user_id}", response_model=List[MatchResponse])
def get_user_matches(user_id: int):
    """Page 4: Get list of all matches for a user with last message preview"""
    if user_id not in users_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user_matches = []
    
    for match in matches_db.values():
        if not match["is_active"]:
            continue
            
        if match["user1_id"] == user_id or match["user2_id"] == user_id:
            # Determine the other user
            other_user_id = match["user2_id"] if match["user1_id"] == user_id else match["user1_id"]
            other_user = users_db.get(other_user_id)
            
            if not other_user:
                continue
            
            # Find last message and unread count
            match_messages = [msg for msg in messages_db.values() if msg["match_id"] == match["match_id"]]
            match_messages.sort(key=lambda x: x["sent_at"], reverse=True)
            
            last_message = match_messages[0] if match_messages else None
            unread_count = len([msg for msg in match_messages if msg["sender_id"] != user_id and not msg["is_read"]])
            
            match_response = MatchResponse(
                match_id=match["match_id"],
                other_user_id=other_user_id,
                other_user_name=other_user["name"],
                other_user_bio=other_user["bio"],
                matched_at=match["matched_at"],
                last_message=last_message["message_text"] if last_message else None,
                last_message_at=last_message["sent_at"] if last_message else None,
                unread_count=unread_count
            )
            user_matches.append(match_response)
    
    # Sort by last message time (most recent first)
    user_matches.sort(key=lambda x: x.last_message_at or x.matched_at, reverse=True)
    
    return user_matches

@app.post("/chat/send", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
def send_message(message_data: MessageSendRequest, user_id: int):
    """Page 4: Send a message in a chat"""
    global next_message_id
    
    if message_data.match_id not in matches_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Match not found"
        )
    
    match = matches_db[message_data.match_id]
    
    # Verify user is part of the match
    if user_id not in [match["user1_id"], match["user2_id"]]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not authorized for this match"
        )
    
    message_id = next_message_id
    next_message_id += 1
    
    new_message = {
        "message_id": message_id,
        "match_id": message_data.match_id,
        "sender_id": user_id,
        "message_text": message_data.message_text,
        "sent_at": datetime.utcnow(),
        "is_read": False
    }
    
    messages_db[message_id] = new_message
    
    sender = users_db.get(user_id)
    
    return MessageResponse(
        message_id=message_id,
        match_id=message_data.match_id,
        sender_id=user_id,
        sender_name=sender["name"] if sender else "Unknown",
        message_text=message_data.message_text,
        sent_at=new_message["sent_at"],
        is_read=False
    )

@app.get("/chat/unread-count/{user_id}")
def get_unread_message_count(user_id: int):
    """Get total count of unread messages for a user across all chats"""
    if user_id not in users_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Get all matches for this user
    user_match_ids = []
    for match in matches_db.values():
        if match["is_active"] and (match["user1_id"] == user_id or match["user2_id"] == user_id):
            user_match_ids.append(match["match_id"])
    
    # Count unread messages from other users
    unread_count = 0
    for message in messages_db.values():
        if (message["match_id"] in user_match_ids and 
            message["sender_id"] != user_id and 
            not message["is_read"]):
            unread_count += 1
    
    return {"unread_count": unread_count}

# ============= TEST DATA ENDPOINTS =============

@app.post("/test/setup")
def setup_test_data():
    """Create test users and matches for demonstration"""
    global next_user_id, next_match_id
    
    # Clear existing data
    users_db.clear()
    matches_db.clear()
    messages_db.clear()
    next_user_id = 1
    next_match_id = 1
    
    # Create test users
    test_users = [
        {
            "name": "Alice Chen",
            "bio": "UI/UX Designer passionate about fintech",
            "feature_tags": ["Design", "Fintech", "Mobile Apps"],
            "portfolio_links": ["https://behance.net/alicechen"]
        },
        {
            "name": "Bob Smith", 
            "bio": "Backend developer with blockchain expertise",
            "feature_tags": ["Blockchain", "Backend", "Crypto"],
            "portfolio_links": ["https://github.com/bobsmith"]
        },
        {
            "name": "Carol Johnson",
            "bio": "Marketing specialist for tech startups",
            "feature_tags": ["Marketing", "Growth Hacking", "B2B"],
            "portfolio_links": ["https://linkedin.com/in/caroljohnson"]
        }
    ]
    
    created_users = []
    for user_data in test_users:
        user_id = next_user_id
        next_user_id += 1
        
        new_user = {
            "user_id": user_id,
            "name": user_data["name"],
            "bio": user_data["bio"],
            "verification_status": "pending",
            "is_active": True,
            "created_at": datetime.utcnow(),
            "feature_tags": user_data["feature_tags"],
            "portfolio_links": user_data["portfolio_links"]
        }
        
        users_db[user_id] = new_user
        created_users.append(user_id)
    
    # Create test matches
    match1_id = next_match_id
    next_match_id += 1
    matches_db[match1_id] = {
        "match_id": match1_id,
        "user1_id": created_users[0],  # Alice & Bob
        "user2_id": created_users[1],
        "matched_at": datetime.utcnow(),
        "is_active": True
    }
    
    match2_id = next_match_id
    next_match_id += 1
    matches_db[match2_id] = {
        "match_id": match2_id,
        "user1_id": created_users[0],  # Alice & Carol
        "user2_id": created_users[2],
        "matched_at": datetime.utcnow(),
        "is_active": True
    }
    
    return {
        "message": "Test data created successfully",
        "users": created_users,
        "matches": [match1_id, match2_id]
    }

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Project Tinder Backend - Pages 3 & 4 Test Server")
    print("📖 Visit http://127.0.0.1:8000/docs for API documentation")
    uvicorn.run(app, host="127.0.0.1", port=8000)
