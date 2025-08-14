# Backend Merged API Contract

## Overview
This is the comprehensive API contract for the merged dating app backend, combining features from backend_p12 and backend_p34.

**Base URL:** `http://localhost:8000`  
**API Version:** `v1`  
**Documentation:** `/docs` (Swagger UI)

## Core Information Endpoints

### System Status
- `GET /` - Root endpoint with basic API info
- `GET /health` - Health check with database status
- `GET /api/v1/info` - Detailed API information and features

## Authentication Endpoints (`/api/v1/auth`)

### Registration & Login
- `POST /api/v1/auth/register/email` - Register with email/password
- `POST /api/v1/auth/login/email` - Login with email/password
- `POST /api/v1/auth/verify-email` - Verify email with code
- `POST /api/v1/auth/resend-verification` - Resend verification code

### Token Management
- `POST /api/v1/auth/refresh` - Refresh access token
- `POST /api/v1/auth/logout` - Logout (invalidate tokens)
- `GET /api/v1/auth/me` - Get current user profile

### Password Recovery
- `POST /api/v1/auth/forgot-password` - Request password reset
- `POST /api/v1/auth/reset-password` - Reset password with code

## User Management (`/api/v1/users`)

### Profile Management
- `GET /api/v1/users/profile` - Get current user profile
- `PUT /api/v1/users/profile` - Update user profile
- `GET /api/v1/users/{user_id}` - Get specific user profile

### User Discovery & Search
- `GET /api/v1/users/discover` - Discover users for swiping
- `GET /api/v1/users/search/` - Search users with filters
- `POST /api/v1/users/swipe` - Record swipe action (like/dislike)

### Account Management
- `GET /api/v1/users/account/deletion-preview` - Preview what data will be deleted
- `POST /api/v1/users/account/deactivate` - Deactivate account (soft delete)
- `DELETE /api/v1/users/account` - Permanently delete user account

### Matching & Likes
- `GET /api/v1/users/liked` - Get users you've liked
- `GET /api/v1/users/liked/mutual` - Get mutual likes (matches)

## AI Search (`/api/v1/search`)
- `POST /api/v1/search/query` - AI-powered user search with natural language

## User Reports (`/api/v1/reports`)

### Report Management
- `POST /api/v1/reports/create` - Create a new user report
- `GET /api/v1/reports/my-reports` - Get reports submitted by current user
- `GET /api/v1/reports/against-me` - Get reports filed against current user
- `GET /api/v1/reports/{report_id}` - Get specific report details

### Administrative (Admin/Moderator only)
- `GET /api/v1/reports/pending` - Get pending reports requiring review
- `POST /api/v1/reports/{report_id}/assign` - Assign report to moderator
- `POST /api/v1/reports/{report_id}/resolve` - Resolve report with action
- `POST /api/v1/reports/{report_id}/dismiss` - Dismiss report as invalid
- `GET /api/v1/reports/statistics/overview` - Get moderation statistics
- `GET /api/v1/reports/user/{user_id}/violations` - Get user's violation history

## Messaging (`/api/v1/messages`)

### Conversation Management
- `GET /api/v1/messages/conversations` - Get all conversations
- `GET /api/v1/messages/{match_id}/messages` - Get messages for a match
- `POST /api/v1/messages/{match_id}/messages` - Send a message
- `DELETE /api/v1/messages/{message_id}` - Delete a message

### Message Search (NEW)
- `GET /api/v1/messages/{match_id}/search` - Search within a specific conversation
- `GET /api/v1/messages/search/global` - Global message search across all conversations
- `GET /api/v1/messages/{message_id}/context` - Get message context

## Real-time Chat (`/api/chats`)
*Note: This is a separate system from regular messaging with greeting/acceptance flow*

### Chat Initialization
- `POST /api/chats/greeting` - Send initial greeting to start chat (requires mutual like)
- `POST /api/chats/{chat_id}/accept` - Accept greeting to enable full chat
- `POST /api/chats/{chat_id}/decline` - Decline greeting

### Chat Messaging
- `GET /api/chats/` - Get all active chats
- `GET /api/chats/{chat_id}` - Get specific chat details
- `GET /api/chats/{chat_id}/messages` - Get chat messages
- `POST /api/chats/{chat_id}/messages` - Send message in chat
- `POST /api/chats/{chat_id}/read` - Mark messages as read

### Chat Search
- `POST /api/chats/search` - Search across all chats

## Recommendations (`/api/v1/recommendations`)
*Available if recommendation service is running*

### User Recommendations
- `GET /api/v1/recommendations/users` - Get 20 recommended user profiles for swiping/matching

### Project Cards  
- `GET /api/v1/recommendations/cards` - Get project cards with rich information (matches card.json structure)

### Swipe Actions
- `POST /api/v1/recommendations/swipe` - Record swipe action on users (like/dislike)

## SMS Verification (`/api/v1/sms`)

### SMS Code Management
- `POST /api/v1/sms/send-code` - Send SMS verification code
- `POST /api/v1/sms/verify-code` - Verify SMS verification code
- `GET /api/v1/sms/status` - Check SMS verification status

### Phone Registration
- `POST /api/v1/sms/register` - Register user account with verified phone

### Administrative
- `POST /api/v1/sms/cleanup-expired` - Cleanup expired codes (Admin only)

## Projects (`/api/v1/projects`)

### Project Management
- `POST /api/v1/projects/` - Create a new project
- `GET /api/v1/projects/{project_id}` - Get project details with users
- `PUT /api/v1/projects/{project_id}` - Update project details
- `DELETE /api/v1/projects/{project_id}` - Delete project (owner only)

### Project Users
- `POST /api/v1/projects/{project_id}/users` - Add user to project
- `DELETE /api/v1/projects/{project_id}/users/{user_id}` - Remove user from project

### Project Discovery
- `GET /api/v1/projects/users/{user_id}/projects` - Get user's projects
- `GET /api/v1/projects/search/` - Search projects with filters
- `GET /api/v1/projects/` - Get current user's projects

## Location (`/api/v1`)
- Location-based features and proximity matching

## Authentication Flow

### Email Registration
```json
POST /api/v1/auth/register/email
{
  "email": "user@example.com",
  "password": "securepass123",
  "name": "John Doe",
  "bio": "Optional bio"
}

Response:
{
  "access_token": "jwt_token",
  "refresh_token": "refresh_token",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": {
    "id": 1,
    "name": "John Doe",
    "bio": "Optional bio",
    "auth_methods": ["email"]
  }
}
```

### Email Login
```json
POST /api/v1/auth/login/email
{
  "email": "user@example.com",
  "password": "securepass123"
}

Response: Same as registration
```

### Email Verification
```json
POST /api/v1/auth/verify-email
{
  "email": "user@example.com",
  "code": "123456"
}
```

## SMS Verification Flow

### Send SMS Verification Code
```json
POST /api/v1/sms/send-code
{
  "phone_number": "13800138000",
  "country_code": "+86",
  "purpose": "REGISTRATION"
}

Response:
{
  "success": true,
  "message": "Verification code sent successfully",
  "verification_id": "sms_12345",
  "expires_in_minutes": 10,
  "rate_limit_seconds": null
}
```

### Verify SMS Code
```json
POST /api/v1/sms/verify-code
{
  "phone_number": "13800138000",
  "verification_code": "123456",
  "country_code": "+86",
  "purpose": "REGISTRATION"
}

Response:
{
  "success": true,
  "message": "Verification successful",
  "verified_at": "2025-08-06T12:00:00Z",
  "remaining_attempts": null
}
```

### Check SMS Status
```json
GET /api/v1/sms/status?phone_number=13800138000&country_code=%2B86&purpose=REGISTRATION

Response:
{
  "is_verified": false,
  "has_pending_code": true,
  "expires_in_seconds": 480,
  "attempts_used": 1,
  "max_attempts": 3,
  "can_request_new": false,
  "verified_at": null,
  "message": "Verification pending",
  "error": null
}
```

### Phone Registration
```json
POST /api/v1/sms/register
{
  "phone_number": "13800138000",
  "verification_code": "123456",
  "country_code": "+86",
  "password": "securepass123",
  "confirm_password": "securepass123",
  "full_name": "张三",
  "email": "optional@example.com",
  "gender": "prefer_not_to_say",
  "date_of_birth": "1990-01-01"
}

Response:
{
  "success": true,
  "message": "Registration successful",
  "user_id": 123,
  "access_token": "jwt_token_here",
  "refresh_token": "refresh_token_here",
  "expires_in": 3600
}
```

### SMS Verification Purposes
- `REGISTRATION` - New user registration
- `PASSWORD_RESET` - Password recovery
- `PHONE_CHANGE` - Changing phone number
- `LOGIN_VERIFICATION` - Two-factor authentication

## Project Management Flow

### Create Project
```json
POST /api/v1/projects/
{
  "short_description": "AI-powered dating app backend",
  "long_description": "Building a comprehensive dating app with AI matching, real-time chat, and smart recommendations",
  "start_time": "2025-08-06T12:00:00Z",
  "status": "ONGOING",
  "media_link_id": null
}

Response:
{
  "project_id": 1,
  "short_description": "AI-powered dating app backend",
  "long_description": "Building a comprehensive dating app with AI matching, real-time chat, and smart recommendations",
  "start_time": "2025-08-06T12:00:00Z",
  "status": "ongoing",
  "media_link_id": null,
  "created_at": "2025-08-06T12:00:00Z",
  "updated_at": "2025-08-06T12:00:00Z"
}
```

### Update Project Status
```json
PUT /api/v1/projects/1
{
  "status": "FINISHED",
  "long_description": "Successfully launched dating app with 1000+ users"
}

Response:
{
  "project_id": 1,
  "short_description": "AI-powered dating app backend",
  "long_description": "Successfully launched dating app with 1000+ users",
  "start_time": "2025-08-06T12:00:00Z",
  "status": "finished",
  "media_link_id": null,
  "created_at": "2025-08-06T12:00:00Z",
  "updated_at": "2025-08-06T15:30:00Z"
}
```

### Get Project with Users
```json
GET /api/v1/projects/1

Response:
{
  "project_id": 1,
  "short_description": "AI-powered dating app backend",
  "long_description": "Successfully launched dating app with 1000+ users",
  "start_time": "2025-08-06T12:00:00Z",
  "status": "finished",
  "media_link_id": null,
  "created_at": "2025-08-06T12:00:00Z",
  "updated_at": "2025-08-06T15:30:00Z",
  "users": [
    {
      "user_id": 123,
      "project_id": 1,
      "role": "Owner",
      "joined_at": "2025-08-06T12:00:00Z",
      "user_name": "John Doe",
      "project_short_description": "AI-powered dating app backend"
    }
  ]
}
```

### Delete Project
```json
DELETE /api/v1/projects/1

Response: 204 No Content
```

### Project Status Values
- `ONGOING` - Project is actively being worked on
- `ON_HOLD` - Project is temporarily paused
- `FINISHED` - Project has been completed

### Project User Roles
- `Owner` - Full project control (can delete, modify, add/remove users)
- `Collaborator` - Can contribute and modify project details
- `Contributor` - Can contribute but limited modification rights

## Security Features

### Authentication
- JWT tokens with refresh mechanism
- Email verification required
- Password strength validation (minimum 8 characters)
- Secure password hashing

### Content Moderation
- AI-powered content moderation middleware
- Text and image content filtering
- Inappropriate content blocking

### CORS & Security
- Environment-aware CORS configuration
- Trusted host middleware in production
- GZip compression
- Security event logging

### Monitoring
- Comprehensive logging system
- Security event tracking
- Health monitoring endpoints

## Environment Configuration
- Development, staging, and production configurations
- Environment-specific CORS settings
- Configurable feature flags
- Debug mode controls

## User Account Management Examples

### Get Deletion Preview
```json
GET /api/v1/users/account/deletion-preview

Response:
{
  "user_id": 123,
  "name": "John Doe",
  "data_to_delete": {
    "profile": "All profile information and photos",
    "matches": "5 matches and conversations",
    "messages": "127 messages sent",
    "projects": "3 projects created",
    "reports": "1 reports made",
    "authentication": "All login sessions and tokens",
    "preferences": "All app preferences and settings",
    "activity": "All swipe history and interactions"
  },
  "warning": "This action cannot be undone. All data will be permanently deleted."
}
```

### Deactivate Account (Soft Delete)
```json
POST /api/v1/users/account/deactivate

Response:
{
  "message": "Account deactivated successfully",
  "note": "Your account has been deactivated. Contact support to reactivate if needed."
}
```

### Permanently Delete Account
```json
DELETE /api/v1/users/account

Response: 204 No Content
```

## Project Idea Generation (`/api/v1/project-ideas`) ⭐ **NEW**

### Generate Project Ideas
- `POST /api/v1/project-ideas/generate` - Generate project ideas from user query
- `POST /api/v1/project-ideas/generate-stream` - Stream project idea generation with real-time progress

### Quota Management
- `GET /api/v1/project-ideas/quota` - Get current user quota status
- `GET /api/v1/project-ideas/history` - Get project idea generation history
- `POST /api/v1/project-ideas/quota/reset` - Admin: Reset user quota

### Subscription Management
- `POST /api/v1/project-ideas/subscription/upgrade` - Upgrade user subscription
- `GET /api/v1/project-ideas/subscription/status` - Get subscription details

### Request/Response Examples

#### Generate Project Ideas
```json
POST /api/v1/project-ideas/generate
{
  "query": "Build a mobile app for fitness tracking"
}

Response:
{
  "search_id": 1234,
  "original_query": "Build a mobile app for fitness tracking", 
  "generated_prompts": [
    {
      "prompt": "fitness tracking mobile app development 2025",
      "engine": "google",
      "results_count": 10
    }
  ],
  "total_sources_found": 15,
  "total_ideas_extracted": 3,
  "project_ideas": [
    {
      "title": "AI-Powered Fitness Coach App",
      "description": "Mobile application with computer vision for exercise form correction and personalized workout plans",
      "difficulty": "Intermediate",
      "technologies": ["React Native", "TensorFlow Lite", "Firebase"],
      "estimated_time": "3-4 months",
      "relevance_score": 0.95,
      "key_features": [
        "Real-time exercise form analysis",
        "Personalized workout recommendations",
        "Progress tracking and analytics"
      ]
    }
  ],
  "processing_time_seconds": 12.5,
  "created_at": "2025-08-14T04:30:00Z"
}
```

#### Stream Generation (Server-Sent Events)
```json
POST /api/v1/project-ideas/generate-stream
{
  "query": "Build a web app for recipe sharing"
}

Response Stream:
data: {"type": "progress", "step": "quota_check", "message": "Checking user quota..."}
data: {"type": "progress", "step": "query_refinement", "message": "Refining search queries..."}
data: {"type": "progress", "step": "web_search", "message": "Searching for relevant content..."}
data: {"type": "progress", "step": "content_scraping", "message": "Extracting content from sources..."}
data: {"type": "progress", "step": "idea_generation", "message": "Generating project ideas..."}
data: {"type": "result", "step": "completion", "data": {...}}
```

#### Quota Status
```json
GET /api/v1/project-ideas/quota

Response:
{
  "user_id": 123,
  "subscription_type": "free",
  "monthly_limit": 30,
  "current_usage": 5,
  "remaining_quota": 25,
  "quota_reset_date": "2025-09-01T00:00:00Z",
  "is_quota_exceeded": false,
  "period_start": "2025-08-01T00:00:00Z",
  "period_end": "2025-09-01T00:00:00Z"
}
```

#### Generation History
```json
GET /api/v1/project-ideas/history?days=30&limit=10

Response:
{
  "total_requests": 5,
  "successful_requests": 4,
  "failed_requests": 1,
  "success_rate": 80.0,
  "period_start": "2025-07-15T00:00:00Z",
  "period_end": "2025-08-14T00:00:00Z",
  "recent_requests": [
    {
      "id": 123,
      "query": "Build a mobile app for fitness tracking",
      "successful": true,
      "created_at": "2025-08-14T04:30:00Z",
      "processing_time": 12.5,
      "sources_found": 15,
      "ideas_extracted": 3
    }
  ]
}
```

#### Subscription Upgrade
```json
POST /api/v1/project-ideas/subscription/upgrade
{
  "subscription_type": "pro"
}

Response:
{
  "success": true,
  "message": "Subscription upgraded to pro",
  "new_quota_limit": 300,
  "upgrade_date": "2025-08-14T04:30:00Z"
}
```

### Error Responses

#### Quota Exceeded
```json
HTTP 429 Too Many Requests
{
  "error": "Monthly quota exceeded",
  "message": "You have used 30/30 requests this month",
  "subscription_type": "free",
  "quota_reset_date": "2025-09-01T00:00:00Z",
  "upgrade_message": "Upgrade to Pro for 300 requests per month"
}
```

#### Invalid Query
```json
HTTP 400 Bad Request
{
  "error": "Invalid query",
  "message": "Query must be between 5 and 500 characters"
}
```

## Database Models
- Users and authentication
- Messages and chats
- Matches and likes
- User reports
- Projects and location data
- **User subscriptions and quotas** ⭐ **NEW**
- **Project idea generation requests** ⭐ **NEW**
- Vector embeddings for AI features

## Error Handling
- Structured error responses
- Appropriate HTTP status codes
- Environment-aware error details (more in dev, less in production)

## Rate Limiting & Performance
- Request rate limiting
- Database connection pooling
- Response compression
- Optimized queries

This API supports a full-featured dating application with enterprise-grade authentication, AI-powered matching, real-time messaging, and comprehensive user management.
