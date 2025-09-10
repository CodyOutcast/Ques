# Project Card Slots System Documentation

## Overview

The **Project Card Slots System** is a feature that allows users to save AI-generated project recommendations to "slots" before deciding to publish them as actual project cards. Think of it as a draft/workspace system where users can collect, organize, and refine project ideas.

## Database Tables

### 1. `project_card_slots` Table
The main table that stores project content in user slots.

```sql
CREATE TABLE project_card_slots (
    slot_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    slot_number INTEGER NOT NULL,  -- 1, 2, 3, etc. per user
    slot_name VARCHAR(100),         -- User-defined name like "Startup Ideas"
    status VARCHAR(20) DEFAULT 'empty',  -- 'empty', 'occupied', 'published'
    source VARCHAR(20),             -- 'ai_recommendation', 'manual_entry', 'imported'
    
    -- Project Content (copied from AI recommendations)
    title VARCHAR(200),
    description TEXT,
    short_description VARCHAR(500),
    category VARCHAR(50),
    industry VARCHAR(50),
    project_type VARCHAR(50),
    stage VARCHAR(50),
    looking_for JSON,              -- ["CTO", "Marketing Lead", etc.]
    skills_needed JSON,            -- ["Python", "React", etc.]
    image_urls JSON,              -- ["url1.jpg", "url2.jpg"]
    video_url VARCHAR(512),
    demo_url VARCHAR(512),
    pitch_deck_url VARCHAR(512),
    funding_goal INTEGER,         -- In cents
    equity_offered INTEGER,       -- Percentage 0-100
    current_valuation INTEGER,    -- In cents
    revenue INTEGER,             -- In cents
    
    -- AI Metadata
    ai_recommendation_id VARCHAR(100),
    ai_confidence_score FLOAT,    -- 0.0 to 1.0
    ai_reasoning TEXT,           -- Why AI recommended this
    original_query VARCHAR(500), -- User's search query
    
    -- Publication Tracking
    published_project_id INTEGER REFERENCES projects(project_id),
    published_at TIMESTAMP,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(user_id, slot_number)
);
```

### 2. `user_slot_configurations` Table
Per-user settings for the slot system.

```sql
CREATE TABLE user_slot_configurations (
    config_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER UNIQUE NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    max_slots INTEGER DEFAULT 5,                    -- How many slots user can have
    auto_save_recommendations BOOLEAN DEFAULT true, -- Auto-save right swipes
    stop_recommendations_on_save BOOLEAN DEFAULT true, -- Stop showing recs when slot is full
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 3. `ai_recommendation_swipes` Table
Tracks user interactions with AI recommendations for learning and avoiding duplicates.

```sql
CREATE TABLE ai_recommendation_swipes (
    swipe_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    ai_recommendation_id VARCHAR(100) NOT NULL,
    direction VARCHAR(10) NOT NULL,      -- 'left' or 'right'
    query VARCHAR(500),                  -- Original search query
    saved_to_slot INTEGER,              -- Slot number if right swipe saved
    recommendation_data JSON,           -- Full recommendation for learning
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(user_id, ai_recommendation_id)
);
```

## Slot Status Lifecycle

### Status Flow:
```
EMPTY → OCCUPIED → PUBLISHED
  ↑        ↓
  └── CLEARED ←┘
```

### Status Definitions:

1. **EMPTY** - Slot exists but has no content
2. **OCCUPIED** - Slot contains a saved AI recommendation or manual content
3. **PUBLISHED** - Slot content has been published as a real project card
4. **CLEARED** - Content removed, slot goes back to EMPTY

## API Endpoints

### Core Slot Management

#### `GET /api/project-slots/slots`
Get all slots for the current user.

**Response:**
```json
{
  "status": "success",
  "data": {
    "slots": [
      {
        "slot_id": 1,
        "slot_number": 1,
        "slot_name": "AI Startup Ideas",
        "status": "occupied",
        "source": "ai_recommendation",
        "title": "AI-Powered Food Delivery Platform",
        "description": "Revolutionary platform using ML for food recommendations...",
        "category": "Technology",
        "industry": "Food Tech",
        "created_at": "2025-09-05T12:00:00Z",
        "updated_at": "2025-09-05T12:30:00Z"
      }
    ],
    "statistics": {
      "total_slots": 5,
      "occupied_slots": 2,
      "empty_slots": 3,
      "published_slots": 1
    }
  }
}
```

#### `PUT /api/project-slots/slots/{slot_id}`
Update slot content (user can edit saved recommendations).

**Request:**
```json
{
  "title": "Updated Project Title",
  "description": "Modified description...",
  "category": "Updated Category"
}
```

#### `POST /api/project-slots/slots/{slot_id}/publish`
Convert slot content into a real project card.

**Response:**
```json
{
  "status": "success",
  "data": {
    "slot_id": 1,
    "project_id": 42,
    "published": true,
    "message": "Slot published as project card successfully"
  }
}
```

#### `DELETE /api/project-slots/slots/{slot_id}`
Clear slot content (make it empty again).

### AI Recommendations Integration

#### `GET /api/project-slots/recommendations`
Get AI-powered project recommendations.

**Parameters:**
- `query` - Search query (optional)
- `limit` - Max recommendations (1-50)
- `exclude_swiped` - Skip previously swiped recommendations

#### `POST /api/project-slots/swipe`
Swipe on an AI recommendation.

**Request:**
```json
{
  "ai_recommendation_id": "rec_123456",
  "direction": "right",
  "slot_number": 2,
  "recommendation_data": {
    "title": "AI Project Idea",
    "description": "Full project description...",
    "confidence_score": 0.85
  }
}
```

**Right Swipe (Like):**
- Saves recommendation to specified slot
- Slot status becomes "occupied"
- Tracks swipe in `ai_recommendation_swipes`

**Left Swipe (Dislike):**
- Only tracks swipe (for learning)
- Recommendation won't be shown again

## How Activation/Deactivation Works

### Slot Activation
Slots become "activated" (occupied) when:

1. **AI Recommendation Right Swipe:**
   ```python
   # User swipes right on AI recommendation
   POST /api/project-slots/swipe
   {
     "direction": "right",
     "slot_number": 3,
     "recommendation_data": { ... }
   }
   # → Slot 3 status changes from "empty" to "occupied"
   ```

2. **Manual Content Entry:**
   ```python
   # User manually fills an empty slot
   PUT /api/project-slots/slots/{slot_id}
   { "title": "My Project Idea", ... }
   # → Slot status changes from "empty" to "occupied"
   ```

### Slot Deactivation
Slots become "deactivated" when:

1. **Content Cleared:**
   ```python
   # Clear slot content
   DELETE /api/project-slots/slots/{slot_id}
   # → Slot status changes from "occupied" to "empty"
   # → All content fields set to NULL
   ```

2. **Published to Project:**
   ```python
   # Publish slot as project card
   POST /api/project-slots/slots/{slot_id}/publish
   # → Slot status changes from "occupied" to "published"
   # → New ProjectCard created
   # → Slot linked to published project
   ```

## User Experience Flow

### 1. First Time Setup
```python
# System automatically initializes 5 empty slots for new users
slots_service.initialize_user_slots(user_id=123, max_slots=5)
```

### 2. AI Recommendation Discovery
```python
# User searches for project ideas
GET /api/project-slots/recommendations?query="fintech startup"

# Returns AI-generated recommendations
[
  {
    "ai_recommendation_id": "rec_fintech_001",
    "title": "AI-Powered Investment Platform",
    "confidence_score": 0.92,
    "reasoning": "Based on your background in finance and AI..."
  }
]
```

### 3. Saving Recommendations (Activation)
```python
# User likes a recommendation (right swipe)
POST /api/project-slots/swipe
{
  "ai_recommendation_id": "rec_fintech_001",
  "direction": "right",
  "slot_number": 1  # Save to slot 1
}

# Slot 1 is now "occupied" with the recommendation content
```

### 4. Content Management
```python
# User can edit saved content
PUT /api/project-slots/slots/1
{
  "title": "My Improved Investment Platform",
  "description": "Enhanced description with my ideas..."
}

# Slot remains "occupied" but with updated content
```

### 5. Publishing (Final Activation)
```python
# User is ready to make it a real project
POST /api/project-slots/slots/1/publish

# → Creates new ProjectCard in projects table
# → Slot status becomes "published"
# → published_project_id links to new project
```

### 6. Slot Cleanup (Deactivation)
```python
# User wants to clear a slot for new recommendations
DELETE /api/project-slots/slots/1

# → Slot status becomes "empty"
# → All content cleared
# → Slot available for new recommendations
```

## Configuration Options

Users can customize their slot behavior:

```python
PUT /api/project-slots/configuration
{
  "max_slots": 10,                      # Increase from default 5
  "auto_save_recommendations": false,   # Manual save only
  "stop_recommendations_on_save": false # Keep showing recs even when slots full
}
```

## Membership Integration

Different membership tiers can have different slot limits:

- **Basic (Free):** 3 slots maximum
- **Pro:** 5 slots maximum  
- **AI-Powered:** 10 slots maximum

## Statistics & Analytics

Track slot usage patterns:

```python
GET /api/project-slots/statistics

{
  "total_slots": 5,
  "occupied_slots": 3,
  "empty_slots": 2,
  "published_slots": 2,
  "total_swipes": 47,
  "right_swipes": 12,
  "left_swipes": 35,
  "save_rate": 0.255  # 25.5% of recommendations saved
}
```

## Benefits of the Slot System

1. **Draft Management:** Users can save ideas without committing to publish
2. **AI Learning:** System learns from swipe patterns  
3. **Content Refinement:** Users can edit AI recommendations before publishing
4. **Organized Workflow:** Clear separation between exploration and creation
5. **Resource Management:** Prevents spam by limiting active project cards

This system provides a sophisticated workflow for managing project ideas from AI recommendation to published project card, with full activation/deactivation lifecycle management.
