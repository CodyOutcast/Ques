# Intelligent Agent API Documentation

## Overview

The Intelligent Agent API provides AI-powered interactions with **3 distinct paths**:

1. **🔍 Search** - Find matching users based on natural language criteria
2. **💬 Inquiry** - Answer questions about specific user profiles  
3. **🗨️ Chat** - General conversation and guidance

The system automatically detects user intent using GLM-4 LLM and routes to the appropriate handler.

---

## Base URL

```
http://localhost:8000/api/v1/intelligent
```

---

## Authentication

All endpoints (except `/health`) require authentication via Bearer token:

```
Authorization: Bearer <your_jwt_token>
```

---

## Endpoints

### 1. **POST `/conversation`** - Main Entry Point (Recommended)

Unified endpoint that automatically detects intent and routes to the appropriate handler.

#### Request Body

```json
{
  "user_input": "find me a student based in shenzhen who have interest in developing mobile apps",
  "referenced_ids": null,
  "viewed_user_ids": []
}
```

**Parameters:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `user_input` | string | ✅ Yes | User's natural language input |
| `referenced_ids` | array[string] | ❌ No | List of user IDs being referenced (for inquiry mode) |
| `viewed_user_ids` | array[string] | ❌ No | List of already viewed user IDs to exclude from search |

#### Response Examples

**Search Intent Response:**

```json
{
  "type": "search_results",
  "intent": "search",
  "query_understanding": "Looking for students in Shenzhen interested in mobile app development",
  "total_results": 50,
  "results": [
    {
      "user_id": "123",
      "name": "Zhang Wei",
      "avatar_url": "https://...",
      "location": "Shenzhen",
      "role": "student",
      "skills": ["React Native", "Flutter", "iOS"],
      "interests": ["mobile apps", "AI"],
      "bio": "CS student passionate about mobile development",
      "match_score": 0.92,
      "match_reason": "Strong match in location (Shenzhen) and interests (mobile app development)"
    }
    // ... 49 more results
  ],
  "search_strategy": "DBSF",
  "language": "en",
  "processing_time": 1.234,
  "intent_analysis": {
    "intent": "search",
    "confidence": 0.95,
    "reasoning": "User is clearly looking for people matching specific criteria"
  },
  "user_id": "456",
  "stats": {...}
}
```

**Inquiry Intent Response:**

```json
{
  "type": "inquiry_response",
  "intent": "inquiry",
  "user_input": "tell me more about their AI experience",
  "referenced_user": {
    "id": "123",
    "name": "Zhang Wei",
    "role": "student",
    "skills": ["Python", "TensorFlow", "PyTorch"],
    "bio": "AI enthusiast..."
  },
  "answer": "Based on Zhang Wei's profile...",
  "analysis": "Zhang Wei demonstrates strong AI capabilities with experience in...",
  "suggestions": [
    "Consider collaborating on a machine learning project",
    "Their PyTorch skills complement your TensorFlow expertise"
  ],
  "language": "en",
  "processing_time": 0.856
}
```

**Chat Intent Response:**

```json
{
  "type": "chat_response",
  "intent": "chat",
  "user_input": "how does this platform work?",
  "response": "Welcome! This platform helps you discover and connect with like-minded people...",
  "clarification_needed": false,
  "suggestions": [
    "Try searching for users with specific skills",
    "You can ask questions about any profile you're interested in"
  ],
  "language": "en",
  "processing_time": 0.523
}
```

---

### 2. **POST `/search`** - Direct Search (Bypass Intent Detection)

Use this when you know the user wants to search for people. Skips intent analysis.

#### Request Body

```json
{
  "user_input": "find students in Beijing interested in blockchain",
  "viewed_user_ids": ["123", "456"]
}
```

#### Response

Same format as search intent response from `/conversation`.

---

### 3. **POST `/analyze-intent`** - Intent Analysis Only

Analyze user input to determine intent **without executing** the action. Useful for UI/UX.

#### Request Body

```json
{
  "user_input": "tell me about this person's background",
  "referenced_ids": ["123"]
}
```

#### Response

```json
{
  "intent": "inquiry",
  "confidence": 0.88,
  "reasoning": "User is asking for detailed information about a specific person, indicating inquiry intent",
  "clarification_needed": false,
  "uncertainty_reason": null
}
```

**Intent Types:**

| Intent | Description | Example Inputs |
|--------|-------------|----------------|
| `search` | User wants to find people | "find students in Shanghai", "looking for AI developers" |
| `inquiry` | User asks about specific profile(s) | "tell me about their experience", "what are their skills?" |
| `chat` | General conversation | "how does this work?", "what can you help me with?" |

---

### 4. **GET `/stats`** - Agent Statistics

Get performance metrics and usage statistics.

#### Response

```json
{
  "stats": {
    "search_count": 1234,
    "total_candidates_found": 56789,
    "avg_search_time": 1.234,
    "cache_hit_rate": 0.67
  },
  "timestamp": "2025-10-06T12:00:00Z"
}
```

---

### 5. **GET `/health`** - Health Check (No Auth Required)

Check if the intelligent agent service is operational.

#### Response

```json
{
  "status": "healthy",
  "service": "intelligent_agent",
  "vector_db": "connected",
  "llm": "connected",
  "timestamp": "2025-10-06T12:00:00Z"
}
```

---

## Intent Detection Logic

The system uses **GLM-4 LLM** to analyze user input and classify into 3 intents:

### Search Intent
**Triggers when:**
- User wants to find people matching criteria
- Contains search keywords: "find", "looking for", "search for", "discover"
- Describes desired characteristics: skills, location, interests, role

**Examples:**
- ✅ "find me a student based in shenzhen who have interest in developing mobile apps"
- ✅ "looking for AI engineers in Beijing"
- ✅ "search for designers interested in UX"

### Inquiry Intent
**Triggers when:**
- User asks questions about specific referenced users
- Contains inquiry keywords: "tell me about", "what is their", "how experienced"
- `referenced_ids` parameter is provided

**Examples:**
- ✅ "tell me more about their AI experience" (with referenced_ids)
- ✅ "what are their main skills?" (with referenced_ids)
- ✅ "how compatible are we?" (with referenced_ids)

### Chat Intent
**Triggers when:**
- General conversation or help request
- Unclear intent requiring clarification
- Questions about the platform itself

**Examples:**
- ✅ "how does this platform work?"
- ✅ "what can you help me with?"
- ✅ "hello"

---

## Search Features

### Vector Search Technology
- **BGE-M3**: 1024-dimensional dense embeddings for semantic search
- **SPLADE** (optional): Sparse embeddings for keyword matching
- **Tencent VectorDB**: High-performance vector database with 150 users

### Search Strategies
1. **DBSF (Default)**: Dense + BM25 + Sparse Fusion
2. **RRF (Fallback)**: Reciprocal Rank Fusion for expanded results
3. **Custom**: Adaptive strategy based on query characteristics

### Result Limit
Returns **up to 50 candidates** per search, ranked by relevance.

---

## Error Responses

All errors follow this format:

```json
{
  "detail": "Error message describing what went wrong",
  "status_code": 500
}
```

**Common Error Codes:**

| Code | Description |
|------|-------------|
| 401 | Unauthorized - Missing or invalid token |
| 500 | Internal Server Error - Service failure |

---

## Example Usage (Python)

```python
import requests

# Authentication token
headers = {
    "Authorization": "Bearer <your_jwt_token>",
    "Content-Type": "application/json"
}

base_url = "http://localhost:8000/api/v1/intelligent"

# 1. Main conversation endpoint (recommended)
response = requests.post(
    f"{base_url}/conversation",
    json={
        "user_input": "find me a student based in shenzhen who have interest in developing mobile apps",
        "viewed_user_ids": []
    },
    headers=headers
)
result = response.json()
print(f"Intent: {result['intent']}")
print(f"Results: {result['total_results']}")

# 2. Analyze intent first
intent_response = requests.post(
    f"{base_url}/analyze-intent",
    json={
        "user_input": "tell me about their experience"
    },
    headers=headers
)
intent = intent_response.json()
print(f"Detected intent: {intent['intent']} (confidence: {intent['confidence']})")

# 3. Direct search
search_response = requests.post(
    f"{base_url}/search",
    json={
        "user_input": "find AI engineers in Beijing",
        "viewed_user_ids": ["123", "456"]
    },
    headers=headers
)
search_results = search_response.json()

# 4. Check health
health = requests.get(f"{base_url}/health").json()
print(f"Service status: {health['status']}")
```

---

## Example Usage (cURL)

```bash
# Main conversation endpoint
curl -X POST "http://localhost:8000/api/v1/intelligent/conversation" \
  -H "Authorization: Bearer <your_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "user_input": "find me a student based in shenzhen who have interest in developing mobile apps",
    "viewed_user_ids": []
  }'

# Analyze intent
curl -X POST "http://localhost:8000/api/v1/intelligent/analyze-intent" \
  -H "Authorization: Bearer <your_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "user_input": "tell me about their background"
  }'

# Health check (no auth)
curl "http://localhost:8000/api/v1/intelligent/health"
```

---

## Environment Variables Required

```bash
# GLM-4 API Configuration
GLM_API_KEY=your_glm_api_key

# Tencent VectorDB Configuration
TENCENT_VECTORDB_URL=http://lb-beofq7pb-lf9vj28fmr5hnf4m.clb.ap-guangzhou.tencentclb.com:20000
TENCENT_VECTORDB_USERNAME=root
TENCENT_VECTORDB_KEY=CiNRD4rMCEJVSjUYqr9w3hYvdOVFMUF8p60R2xr2

# Backend API
API_BASE_URL=http://localhost:8000
```

---

## Performance Metrics

- **Intent Analysis**: ~0.3-0.5s
- **Vector Search**: ~0.8-1.5s
- **Inquiry Response**: ~0.5-1.0s
- **Chat Response**: ~0.3-0.6s

**Total Processing Time**: 0.5s - 2.0s depending on complexity

---

## Interactive API Documentation

Visit the auto-generated Swagger UI:

```
http://localhost:8000/docs#/Intelligent%20Agent
```

Or ReDoc:

```
http://localhost:8000/redoc
```

---

## Architecture Diagram

```
User Input
    ↓
POST /api/v1/intelligent/conversation
    ↓
Detect Language (zh/en)
    ↓
Fetch User Context (PostgreSQL)
    ↓
Analyze Intent (GLM-4)
    ↓
    ├─→ intent="search" → Vector Search (Tencent VectorDB + BGE-M3)
    ├─→ intent="inquiry" → Profile Analysis (GLM-4)
    └─→ intent="chat" → Conversation (GLM-4)
    ↓
Format Response
    ↓
Return JSON
```

---

## FAQ

**Q: Which endpoint should I use?**  
A: Use **`POST /conversation`** - it automatically detects intent and routes appropriately.

**Q: How do I search for users?**  
A: Just send natural language like "find students in Shanghai interested in AI" to `/conversation`.

**Q: How do I ask about a specific user?**  
A: Send your question with `referenced_ids`: `{"user_input": "tell me about their skills", "referenced_ids": ["123"]}`.

**Q: Can I exclude certain users from search?**  
A: Yes, use `viewed_user_ids` to exclude already seen users.

**Q: How many search results do I get?**  
A: Up to **50 candidates** ranked by relevance.

**Q: What if the agent doesn't understand my input?**  
A: It will respond in chat mode asking for clarification.

---

## Support

For issues or questions:
- Check `/health` endpoint status
- Review logs for error details
- Verify environment variables are set correctly
- Ensure PostgreSQL and Tencent VectorDB are accessible
