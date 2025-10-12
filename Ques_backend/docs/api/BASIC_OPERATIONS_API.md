# Basic Operations API Documentation

## Overview

The Basic Operations API provides essential functionality for user management and interactions:

1. **👤 User Creation** - Register new users with profiles
2. **💬 Whispers** - Send greeting messages between users
3. **👍 Swiping** - Like/dislike user profiles with match detection
4. **🔝 Top Profiles** - Get recommended profiles to explore

---

## Base URL

```
http://localhost:8000/api/v1/basic
```

---

## Authentication

Most endpoints require authentication via Bearer token:

```
Authorization: Bearer <your_jwt_token>
```

**Exception:** User creation endpoint does not require authentication.

---

## Endpoints

### 1. **POST `/users`** - Create New User ⭐ (No Auth Required)

Register a new user account with profile information.

#### Request Body

```json
{
  "email": "zhang.wei@example.com",
  "password": "SecurePass123",
  "name": "Zhang Wei",
  "phone_number": "+86 138 0000 0000",
  "wechat_id": "zhangwei2024",
  "role": "student",
  "location": "Shenzhen",
  "bio": "CS student interested in mobile development",
  "skills": ["Python", "React Native", "Flutter"],
  "interests": ["AI", "mobile apps", "startups"]
}
```

**Required Fields:**
- `email` - Valid email address
- `password` - Min 8 characters, must include uppercase, lowercase, and digit
- `name` - User's full name (2-100 characters)

**Optional Fields:**
- `phone_number` - Phone number
- `wechat_id` - WeChat ID
- `role` - Role: student, professional, entrepreneur
- `location` - City/location
- `bio` - Short bio (max 500 characters)
- `skills` - Array of skills
- `interests` - Array of interests

#### Response

```json
{
  "user_id": 151,
  "email": "zhang.wei@example.com",
  "name": "Zhang Wei",
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "message": "User created successfully. Welcome!"
}
```

**Status Codes:**
- `201 Created` - User created successfully
- `400 Bad Request` - Validation error or user already exists
- `500 Internal Server Error` - Server error

---

### 2. **POST `/whispers`** - Send Whisper Message 💬

Send a greeting message (whisper) to another user.

#### Request Body

```json
{
  "recipient_id": 123,
  "greeting_message": "Hi! I saw your profile and I'm also interested in mobile app development. Would love to connect!",
  "sender_wechat_id": null,
  "swipe_id": null,
  "from_template": false
}
```

**Required Fields:**
- `recipient_id` - User ID of the recipient
- `greeting_message` - Message content (1-500 characters)

**Optional Fields:**
- `sender_wechat_id` - Your WeChat ID to share with recipient
- `swipe_id` - Related swipe ID if this is a follow-up
- `from_template` - Whether message is from a template

#### Response

```json
{
  "id": 456,
  "sender_id": 151,
  "recipient_id": 123,
  "greeting_message": "Hi! I saw your profile and I'm also interested in mobile app development. Would love to connect!",
  "is_read": false,
  "created_at": "2025-10-06T12:00:00Z",
  "sender_name": "Zhang Wei",
  "recipient_name": "Li Ming"
}
```

**Status Codes:**
- `201 Created` - Whisper sent successfully
- `400 Bad Request` - Invalid recipient or trying to message yourself
- `404 Not Found` - Recipient not found
- `500 Internal Server Error` - Server error

**Notes:**
- Free users: Limited whispers per day
- Premium users: Unlimited whispers
- Whispers can be anonymous or revealed

---

### 3. **POST `/swipe`** - Swipe on User 👍

Swipe on a user profile to show interest (or lack thereof).

#### Request Body

```json
{
  "target_user_id": 123,
  "direction": "like"
}
```

**Required Fields:**
- `target_user_id` - User ID to swipe on
- `direction` - Swipe direction: `"like"`, `"dislike"`, or `"superlike"`

**Swipe Directions:**
- `like` - Show interest in the user
- `dislike` - Pass on the user
- `superlike` - Strong interest (may require premium)

#### Response

```json
{
  "swipe_id": 789,
  "user_id": 151,
  "target_user_id": 123,
  "direction": "like",
  "is_match": true,
  "match_id": 42,
  "created_at": "2025-10-06T12:00:00Z",
  "message": "🎉 It's a match! You can now send messages."
}
```

**Match Detection:**
- If both users liked each other, `is_match` will be `true`
- A match enables messaging between users
- `match_id` is provided when a match occurs

**Status Codes:**
- `200 OK` - Swipe recorded successfully
- `400 Bad Request` - Already swiped on this user or invalid request
- `404 Not Found` - Target user not found
- `500 Internal Server Error` - Server error

---

### 4. **GET `/top-profiles`** - Get Top Recommended Profiles 🔝

Get recommended user profiles to explore and swipe on.

#### Query Parameters

```
GET /api/v1/basic/top-profiles?limit=10&exclude_seen=true
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `limit` | integer | 10 | Number of profiles (1-50) |
| `exclude_seen` | boolean | true | Exclude already swiped users |

#### Response

```json
{
  "total_count": 10,
  "profiles": [
    {
      "user_id": 123,
      "name": "Li Ming",
      "role": "student",
      "location": "Shenzhen",
      "bio": "AI enthusiast and mobile developer",
      "skills": ["Python", "TensorFlow", "Flutter"],
      "interests": ["AI", "machine learning", "mobile apps"],
      "avatar_url": "https://...",
      "match_score": null
    }
    // ... 9 more profiles
  ],
  "timestamp": "2025-10-06T12:00:00Z"
}
```

**Algorithm:**
- Filters out already swiped users (if `exclude_seen=true`)
- Returns active users with complete profiles
- Ordered by relevance
- Can be enhanced with ML-based ranking

**Status Codes:**
- `200 OK` - Profiles retrieved successfully
- `500 Internal Server Error` - Server error

---

### 5. **GET `/my-whispers`** - Get My Whispers 📬

Get whispers sent and received by the current user.

#### Query Parameters

```
GET /api/v1/basic/my-whispers?type=all&limit=50
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `type` | string | all | Filter: `"sent"`, `"received"`, or `"all"` |
| `limit` | integer | 50 | Max whispers per category |

#### Response

```json
{
  "sent": [
    {
      "id": 456,
      "sender_id": 151,
      "recipient_id": 123,
      "greeting_message": "Hi! Would love to connect...",
      "is_read": true,
      "created_at": "2025-10-06T11:00:00Z",
      "sender_name": null,
      "recipient_name": "Li Ming"
    }
  ],
  "received": [
    {
      "id": 457,
      "sender_id": 124,
      "recipient_id": 151,
      "greeting_message": "Hey! I saw your profile...",
      "is_read": false,
      "created_at": "2025-10-06T12:00:00Z",
      "sender_name": "Wang Fang",
      "recipient_name": null
    }
  ],
  "total_sent": 1,
  "total_received": 1,
  "unread_count": 1
}
```

**Status Codes:**
- `200 OK` - Whispers retrieved successfully
- `500 Internal Server Error` - Server error

---

### 6. **PATCH `/whispers/{whisper_id}/read`** - Mark Whisper as Read ✅

Mark a received whisper as read.

#### Request

```
PATCH /api/v1/basic/whispers/457/read
```

No request body required.

#### Response

```json
{
  "message": "Whisper marked as read",
  "whisper_id": 457
}
```

**Status Codes:**
- `200 OK` - Whisper marked as read
- `403 Forbidden` - Not your whisper to mark
- `404 Not Found` - Whisper not found
- `500 Internal Server Error` - Server error

**Notes:**
- Only the recipient can mark a whisper as read
- Sets `is_read=true` and `read_at` timestamp

---

### 7. **GET `/health`** - Health Check (No Auth Required)

Check if the basic operations service is running.

#### Response

```json
{
  "status": "healthy",
  "service": "basic_operations",
  "timestamp": "2025-10-06T12:00:00Z"
}
```

---

## Complete Workflow Example

### Step 1: Create a New User

```bash
curl -X POST "http://localhost:8000/api/v1/basic/users" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "zhang.wei@example.com",
    "password": "SecurePass123",
    "name": "Zhang Wei",
    "role": "student",
    "location": "Shenzhen",
    "skills": ["Python", "React Native"],
    "interests": ["AI", "mobile apps"]
  }'
```

**Response:** Receive `access_token` for subsequent requests.

---

### Step 2: Get Top Profiles

```bash
curl -X GET "http://localhost:8000/api/v1/basic/top-profiles?limit=10" \
  -H "Authorization: Bearer <access_token>"
```

**Response:** List of 10 recommended profiles.

---

### Step 3: Swipe on a User

```bash
curl -X POST "http://localhost:8000/api/v1/basic/swipe" \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "target_user_id": 123,
    "direction": "like"
  }'
```

**Response:** Swipe recorded, match status indicated.

---

### Step 4: Send a Whisper

```bash
curl -X POST "http://localhost:8000/api/v1/basic/whispers" \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "recipient_id": 123,
    "greeting_message": "Hi! I saw your profile and would love to connect!"
  }'
```

**Response:** Whisper sent confirmation.

---

### Step 5: Check Your Whispers

```bash
curl -X GET "http://localhost:8000/api/v1/basic/my-whispers?type=all" \
  -H "Authorization: Bearer <access_token>"
```

**Response:** All sent and received whispers with unread count.

---

## Python Client Example

```python
import requests

BASE_URL = "http://localhost:8000/api/v1/basic"

# Step 1: Create user (no auth required)
create_response = requests.post(
    f"{BASE_URL}/users",
    json={
        "email": "zhang.wei@example.com",
        "password": "SecurePass123",
        "name": "Zhang Wei",
        "role": "student",
        "location": "Shenzhen",
        "skills": ["Python", "React Native"],
        "interests": ["AI", "mobile apps"]
    }
)

user_data = create_response.json()
access_token = user_data["access_token"]
print(f"✅ User created: {user_data['user_id']}")

# Setup headers for authenticated requests
headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json"
}

# Step 2: Get top profiles
profiles_response = requests.get(
    f"{BASE_URL}/top-profiles?limit=10",
    headers=headers
)
profiles = profiles_response.json()
print(f"📋 Found {profiles['total_count']} profiles")

# Step 3: Swipe on first profile
if profiles['profiles']:
    target_user = profiles['profiles'][0]
    swipe_response = requests.post(
        f"{BASE_URL}/swipe",
        headers=headers,
        json={
            "target_user_id": target_user['user_id'],
            "direction": "like"
        }
    )
    swipe_data = swipe_response.json()
    print(f"👍 Swiped on {target_user['name']}")
    if swipe_data['is_match']:
        print("🎉 It's a match!")
    
    # Step 4: Send whisper
    whisper_response = requests.post(
        f"{BASE_URL}/whispers",
        headers=headers,
        json={
            "recipient_id": target_user['user_id'],
            "greeting_message": "Hi! Would love to connect!"
        }
    )
    whisper_data = whisper_response.json()
    print(f"💬 Whisper sent: {whisper_data['id']}")

# Step 5: Check whispers
whispers_response = requests.get(
    f"{BASE_URL}/my-whispers",
    headers=headers
)
whispers = whispers_response.json()
print(f"📬 Whispers - Sent: {whispers['total_sent']}, Received: {whispers['total_received']}, Unread: {whispers['unread_count']}")
```

---

## Error Handling

All endpoints return errors in this format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

**Common HTTP Status Codes:**

| Code | Meaning | Common Causes |
|------|---------|---------------|
| 400 | Bad Request | Validation error, duplicate action, invalid input |
| 401 | Unauthorized | Missing or invalid authentication token |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource doesn't exist |
| 500 | Internal Server Error | Server-side error |

---

## Rate Limits & Quotas

### Free Users
- **Whispers**: 5 per day
- **Swipes**: Unlimited
- **Profile Views**: Unlimited

### Premium Users
- **Whispers**: Unlimited
- **Swipes**: Unlimited
- **Profile Views**: Unlimited
- **Superlikes**: 5 per day

---

## Data Models

### UserProfile
```typescript
{
  user_id: number
  name: string
  role?: "student" | "professional" | "entrepreneur"
  location?: string
  bio?: string
  skills?: string[]
  interests?: string[]
  avatar_url?: string
}
```

### Whisper
```typescript
{
  id: number
  sender_id: number
  recipient_id: number
  greeting_message: string
  is_read: boolean
  created_at: datetime
  sender_name?: string
  recipient_name?: string
}
```

### Swipe
```typescript
{
  swipe_id: number
  user_id: number
  target_user_id: number
  direction: "like" | "dislike" | "superlike"
  is_match: boolean
  match_id?: number
  created_at: datetime
}
```

---

## Interactive Documentation

Visit the Swagger UI for interactive API testing:

```
http://localhost:8000/docs#/Basic%20Operations
```

Or ReDoc:

```
http://localhost:8000/redoc
```

---

## Best Practices

### User Creation
- ✅ Use strong passwords (8+ chars, mixed case, numbers)
- ✅ Provide complete profile information for better matching
- ✅ Store access token securely

### Whispers
- ✅ Personalize messages (avoid generic templates)
- ✅ Keep messages concise and friendly
- ✅ Respect daily limits

### Swiping
- ✅ Swipe thoughtfully on profiles you're genuinely interested in
- ✅ Use `exclude_seen=true` to avoid duplicate swipes
- ✅ Check for matches regularly

### Profile Discovery
- ✅ Use `top-profiles` to get curated recommendations
- ✅ Adjust `limit` based on your browsing pattern
- ✅ Refresh regularly for new users

---

## FAQ

**Q: How do I register a new user?**  
A: Use `POST /users` with email, password, and name. No authentication required.

**Q: What happens when I like someone who already liked me?**  
A: You get an instant match! The response will have `is_match: true` and a `match_id`.

**Q: Can I send multiple whispers to the same person?**  
A: Yes, but be mindful of rate limits and don't spam.

**Q: How do I know if someone read my whisper?**  
A: Check the `is_read` field in the whisper object.

**Q: Can I undo a swipe?**  
A: Currently, swipes are final. Choose carefully!

**Q: How are top profiles selected?**  
A: Currently based on recent activity and completeness. ML-based matching coming soon!

---

## Support & Resources

**Files:**
- Router: `routers/basic_operations.py`
- Documentation: `BASIC_OPERATIONS_API.md`
- Models: `models/users.py`, `models/whispers.py`, `models/likes.py`

**Related Endpoints:**
- Authentication: `/api/v1/auth/*`
- Intelligent Search: `/api/v1/intelligent/*`
- Messaging: `/api/v1/messages/*`

**Need Help?**
- Check Swagger docs: `http://localhost:8000/docs`
- Review error responses for details
- Verify authentication token is valid
