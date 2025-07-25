# Project Tinder Backend

**A "Tinder for Projects" mo# If port 8000 is in use, try another port
uvicorn main:app --reload --port 8001
```

### 6. Stop the Server

**Quick termination:**
- Press `Ctrl + C` in the terminal where the server is running

**Alternative method (if needed):**
1. **Find the process:**
   ```bash
   ps aux | grep uvicorn
   ```
   Look for the line with `uvicorn main:app --reload` and note the PID (second column).

2. **Graceful shutdown:**
   ```bash
   kill -SIGTERM <PID>
   # Example: kill -SIGTERM 12345
   ```

3. **Force kill (last resort):**
   ```bash
   kill -9 <PID>
   ```
   ⚠️ Use sparingly as it doesn't clean up properly.

🎉 **Server running at:** `http://127.0.0.1:8000` (or 8001/8002 if using alternate port)** - Connect people with projects they want to invest in, collaborate on, or fund. Built with FastAPI, PostgreSQL, and Tencent Cloud Vector Database.

This backend currently supports **Pages 1 & 2** of the mobile app:
- 📱 **Page 1**: Swipeable card recommendations 
- 🔍 **Page 2**: AI-powered project search

---

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.8+ (For Python 3.13, using psycopg3 instead of psycopg2)
- PostgreSQL database (Tencent Cloud)
- Tencent Cloud Vector Database access
- DeepSeek API key

### 2. Installation
```bash
# Clone and navigate to backend
git clone <your-repo-url>
cd backend

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Setup
```bash
# Copy environment template
cp .env.example .env

# Edit .env with your credentials
# (PostgreSQL, Vector DB, DeepSeek API key, JWT secret)
```

### 4. Database Setup
```bash
# Run database migrations
alembic upgrade head

# (Optional) Add test data with 6 sample users
python seed.py
```

### 5. Start the Server
```bash
# Using virtual environment (recommended)
.venv/bin/uvicorn main:app --reload

# Or if using system Python
uvicorn main:app --reload

# If port 8000 is in use, try another port
uvicorn main:app --reload --port 8001
```
To terminate:
Ctrl + C to terminate this in the terminal
or Find the Process ID (PID):
Open another terminal (or a new session on your CVM).
Run: ps aux | grep uvicorn to find the Uvicorn process.
Look for the line with uvicorn main:app --reload. Note the PID (a number in the second column of the output).
Kill the Process:
Run: kill -SIGTERM <PID> (replace <PID> with the actual number, e.g., kill -SIGTERM 12345).
This sends a termination signal, similar to Ctrl + C, allowing Uvicorn to shut down cleanly.
Force Kill (Last Resort):
If it still doesn’t stop, use: kill -9 <PID>. This forcefully terminates the process but might not clean up properly, so use it sparingly.

🎉 **Server running at:** `http://127.0.0.1:8000` (or 8001 if using alternate port)

📖 **API Documentation:** `http://127.0.0.1:8000/docs` (adjust port if needed)

---

## 📱 App Features

### Page 1: Home/Recommendations
**Tinder-style swiping for project discovery**

- User sees 20 most relevant cards (projects/people)
- Cards determined by vector similarity to user's profile tags
- Swipe right (like) or left (dislike)
- History tracking prevents showing same cards twice
- Each card shows feature tags like "AI enthusiast", "investor", "good at coding"

**API Endpoints:**
- `GET /recommendations/cards` - Get cards for swiping
- `POST /recommendations/swipe` - Record like/dislike action

### Page 2: AI Search
**Natural language search for projects and people**

- Simple search bar where users describe what they're looking for
- DeepSeek AI extracts 1-5 feature tags from the query
- Tags focus on transferable skills ("investor", "startup founder") vs specific tech
- Vector similarity search returns 20 most relevant results
- Filters out previously seen results

**API Endpoints:**
- `POST /search/query` - Natural language search

### Authentication
- `POST /auth/token` - Get JWT token for API access

---

## 🛠️ Tech Stack

- **Backend Framework**: FastAPI
- **Database**: PostgreSQL (Tencent Cloud)
- **Vector Database**: Tencent Cloud Vector DB  
- **AI/NLP**: DeepSeek API for tag extraction
- **Embeddings**: sentence-transformers (BAAI/bge-base-zh, 768 dimensions)
- **Authentication**: JWT tokens
- **Deployment**: Tencent Cloud CVM

---

## 📊 Database Schema

### Users Table
```sql
- id (Primary Key)
- name (User's display name)  
- bio (User description)
- feature_tags (JSON array of skills/interests)
- vector_id (Reference to vector database)
```

### Likes Table (Swipe History)
```sql
- id (Primary Key)
- liker_id (Who swiped)
- liked_item_id (Target user/project ID)
- liked_item_type ('profile' or 'project') 
- timestamp (When swipe occurred)
- granted_chat_access (True for likes, False for dislikes)
```

---

## 🧪 Testing & Development

### Test the API
```bash
# Run comprehensive API tests
python test_api.py
```

### Add Test Users
```bash
# Add a user with feature tags
python add_users.py "John Doe" "Experienced developer" "good at coding,startup founder,AI enthusiast"
```

### Interactive API Testing
Visit `http://127.0.0.1:8000/docs` for Swagger UI with:
- Live API testing
- Request/response examples  
- Parameter documentation
- Authentication testing

---

## 🚀 Deployment to Tencent Cloud

```bash
# Transfer files to CVM
scp -r ~/Desktop/backend ubuntu@YOUR_CVM_IP:/home/ubuntu/

# On CVM, install dependencies and run
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

---

## 📁 Project Structure

```
backend/
├── main.py                 # FastAPI app entry point
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
├── alembic.ini            # Database migration config
├── models/
│   ├── base.py            # Database connection & base model
│   ├── users.py           # User model 
│   └── likes.py           # Swipe history model
├── routers/
│   ├── auth.py            # JWT authentication
│   ├── recommendations.py # Page 1: Card swiping
│   └── match.py           # Page 2: AI search
├── dependencies/
│   └── auth.py            # JWT validation logic
├── migrations/            # Database migration files
├── db_utils.py            # Database & vector DB utilities
├── seed.py                # Test data creation
├── add_users.py           # Utility to add users
└── test_api.py            # API testing script
```

---

## 🔧 Development Notes

### Current Status
- ✅ **Page 1**: Card recommendations with vector similarity
- ✅ **Page 2**: AI search with tag extraction  
- ✅ **Authentication**: JWT-based API security
- ✅ **CORS**: Enabled for React Native frontend
- ❌ **Pages 3-4**: Chat & profile features (future)

### Adding New Users
Users need feature tags to appear in recommendations:
```python
# Example feature tags
["investor", "AI enthusiast", "good at coding", "startup founder", "marketing expert"]
```

### Vector Embedding Process
1. User's feature tags → joined text
2. Text → vector embedding (768 dimensions)  
3. Vector stored in Tencent Cloud Vector DB
4. Similarity search finds matching users

---

## 🆘 Troubleshooting

### Common Issues

**"psycopg2 compilation errors with Python 3.13"**
- Solution: Use psycopg3 instead (already configured in requirements.txt)
- Database URL should use: `postgresql+psycopg://user:pass@host:port/db`

**"pydantic compilation errors"**
- Solution: Use pydantic >= 2.9.0 (already configured)

**"Vector DB connection failed"**
- Check VECTORDB_ENDPOINT, VECTORDB_USERNAME, VECTORDB_KEY in .env

**"DeepSeek API error"**  
- Verify DEEPSEEK_API_KEY in .env
- Check API rate limits

**"No cards available"**
- Run `python seed.py` to add test users
- Check user has feature_tags and vector_id

**Database errors**
- Run `alembic upgrade head` to apply migrations
- Verify PostgreSQL connection in .env

**"Address already in use" error**
- Try a different port: `uvicorn main:app --reload --port 8001`

### Get Help
- Check server logs for detailed error messages
- Visit `/docs` for API documentation
- Test individual components with provided scripts

---

**Ready to swipe on some projects! 🚀**