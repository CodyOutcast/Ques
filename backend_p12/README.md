# Project Tinder Backend

**A "Tinder for Projects" mobile app backend** - Connect people with projects they want to invest in, collaborate on, or fund. Built with FastAPI, PostgreSQL, and comprehensive authentication system.

This backend currently supports **Pages 1 & 2** of the mobile app:
- 📱 **Page 1**: Swipeable card recommendations 
- 🔍 **Page 2**: AI-powered project search

**✅ FULLY FUNCTIONAL - Ready for Frontend Integration!**

---

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.8+ (Tested with Python 3.12 & 3.13)
- PostgreSQL database
- Optional: Tencent Cloud Vector Database access
- Optional: DeepSeek API key for enhanced tag extraction

### 2. Installation
```bash
# Clone and navigate to backend
git clone <your-repo-url>
cd backend_p12

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Setup
```bash
# Copy environment template
cp .env.example .env

# Edit .env with your credentials
# (PostgreSQL required, Vector DB & API keys optional)
```

### 4. Database Setup
```bash
# Run database setup script (creates tables + sample data)
python setup_database.py

# Or manually with migrations
alembic upgrade head
python seed.py  # Optional: Add 6 sample users
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

### 6. Test the Backend
```bash
# Run core backend tests (recommended first test)
python test_backend.py

# Or run complete API tests
python test_api.py
```

🎉 **Server running at:** `http://127.0.0.1:8000`

📖 **API Documentation:** `http://127.0.0.1:8000/docs`

### To Stop the Server

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

---

## 🔐 Authentication System
```

### 3. Environment Setup
```bash
# Copy environment template
cp .env.example .env

# Edit .env with your credentials
# (PostgreSQL required, Vector DB & API keys optional)
```

### 4. Database Setup
```bash
# Run database setup script (creates tables + sample data)
python setup_database.py

# Or manually with migrations
alembic upgrade head
python seed.py  # Optional: Add 6 sample users
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

### 6. Test the Backend
```bash
# Run comprehensive API tests
python test_backend.py
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
If it still doesn't stop, use: kill -9 <PID>. This forcefully terminates the process but might not clean up properly, so use it sparingly.

🎉 **Server running at:** `http://127.0.0.1:8000` (or 8001 if using alternate port)

📖 **API Documentation:** `http://127.0.0.1:8000/docs` (adjust port if needed)
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

### ✅ Authentication System (FULLY IMPLEMENTED)
**Multi-method authentication with JWT tokens**

- **Email/Password**: Traditional registration with secure password hashing
- **WeChat OAuth**: Social login integration (configured for future use)
- **JWT Tokens**: Access tokens (30-minute expiry) + Refresh tokens (30-day expiry)
- **Security**: Token rotation, device tracking, rate limiting

**API Endpoints:**
- `POST /auth/register/email` - Register with email/password
- `POST /auth/login/email` - Login and get JWT tokens
- `POST /auth/refresh` - Refresh access token
- `POST /auth/logout` - Logout and revoke tokens
- `GET /auth/me` - Get current user profile

### ✅ Page 1: Home/Recommendations (IMPLEMENTED)
**Tinder-style swiping for project discovery**

- User sees 20 most relevant cards (projects/people)
- Cards determined by vector similarity to user's profile tags
- Swipe right (like) or left (dislike)
- History tracking prevents showing same cards twice
- Each card shows feature tags like "AI enthusiast", "investor", "good at coding"
- **Smart recommendation algorithm**: Progressive search strategy (50→150→300 similar profiles) with random fallback to ensure cards are always available

**API Endpoints:**
- `GET /recommendations/cards` - Get cards for swiping
- `POST /recommendations/swipe` - Record like/dislike action

### ✅ Page 2: AI Search (IMPLEMENTED)
**Natural language search for projects and people**

- Simple search bar where users describe what they're looking for
- DeepSeek AI extracts 1-5 feature tags from the query
- Tags focus on transferable skills ("investor", "startup founder") vs specific tech
- Vector similarity search returns 20 most relevant results
- Filters out previously seen results
- **Smart search algorithm**: Progressive search strategy (50→150→300 similar profiles) with random fallback to ensure results are always available

**API Endpoints:**
- `POST /search/query` - Natural language search

---

## 🛠️ Tech Stack

- **Backend Framework**: FastAPI
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Authentication**: JWT tokens with bcrypt password hashing
- **Vector Database**: Tencent Cloud Vector DB (optional)
- **AI/NLP**: DeepSeek API for tag extraction (optional)
- **Embeddings**: sentence-transformers (BAAI/bge-base-zh, 768 dimensions) (optional)
- **Email Service**: Tencent Cloud SES for verification emails
- **Database Migrations**: Alembic
- **Deployment**: Ready for Tencent Cloud CVM

---

## 📊 Database Schema

### Users Table
```sql
- user_id (Primary Key)
- name (User's display name)  
- bio (User description)
- verification_status (Email verification status)
- is_active (Boolean, user account status)
```

### User Authentication Table
```sql
- id (Primary Key)
- user_id (Foreign Key to users)
- provider_type (EMAIL, WECHAT)
- provider_id (email address or WeChat openid)
- password_hash (bcrypt hashed password)
- is_verified (Boolean)
- is_primary (Boolean, primary auth method)
- created_at, verified_at, last_login (Timestamps)
```

### Refresh Tokens Table
```sql
- id (Primary Key)
- user_id (Foreign Key to users)
- token_hash (SHA256 hashed refresh token)
- expires_at (Token expiration)
- is_revoked (Boolean)
- device_info, ip_address (Optional tracking)
```

### Verification Codes Table
```sql
- id (Primary Key)
- user_id (Foreign Key to users)
- code (6-digit verification code)
- code_type (EMAIL_VERIFICATION, PASSWORD_RESET)
- expires_at (Code expiration - 10 minutes)
- is_used (Boolean)
```

### Likes Table (Swipe History)
```sql
- id (Primary Key)
- liker_id (Who swiped, Foreign Key to users.user_id)
- liked_item_id (Target user/project ID)
- liked_item_type ('profile' or 'project') 
- timestamp (When swipe occurred)
- granted_chat_access (True for likes, False for dislikes)
```

---

## 🧪 Testing & Development

### Available Test Suites
The backend includes multiple test files for different scenarios:

```bash
# Core backend functionality (recommended first test)
python test_backend.py

# Complete API endpoint testing
python test_api.py

# Authentication system testing
python test_authentication.py

# Algorithm testing for Pages 1 & 2
python test_recommendation_algorithm.py
```

**📝 Note:** Tests may show "Expected 500 error" messages when the database lacks sample data - this is normal behavior. The tests verify that authentication works and endpoints are accessible.

### Add Test Users
```bash
# Add a user with feature tags
python add_users.py "John Doe" "Experienced developer" "good at coding,startup founder,AI enthusiast"

# Or add sample data through the database setup
python setup_database.py
```

### Interactive API Testing
Visit `http://127.0.0.1:8000/docs` for Swagger UI with:
- Live API testing
- Request/response examples  
- Parameter documentation
- Authentication testing

### Manual Testing Examples
```bash
# Register a new user
curl -X POST http://localhost:8000/auth/register/email \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "TestPassword123!", "name": "Test User"}'

# Login to get access token
curl -X POST http://localhost:8000/auth/login/email \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "TestPassword123!"}'

# Use access token to get recommendations
curl -X GET http://localhost:8000/recommendations/cards \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

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
backend_p12/
├── main.py                 # FastAPI app entry point
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
├── alembic.ini            # Database migration config
├── setup_database.py      # Database setup script
├── seed.py                # Test data creation
├── add_users.py           # Utility to add users
├── test_backend.py        # Core API functionality tests
├── test_api.py            # Complete API endpoint tests
├── test_authentication.py # Authentication system tests
├── test_recommendation_algorithm.py # Algorithm testing for Pages 1 & 2
├── models/
│   ├── base.py            # Database connection & base model
│   ├── users.py           # User model 
│   ├── auth.py            # Authentication models
│   └── likes.py           # Swipe history model
├── routers/
│   ├── auth.py            # JWT authentication endpoints
│   ├── recommendations.py # Page 1: Card swiping
│   └── match.py           # Page 2: AI search
├── dependencies/
│   ├── auth.py            # JWT validation & utilities
│   └── db.py              # Database dependency
├── schemas/
│   └── auth.py            # Pydantic request/response models
├── services/
│   ├── auth_service.py    # Authentication business logic
│   └── email_service.py   # Email verification service
├── migrations/            # Database migration files
└── db_utils.py            # Database & vector DB utilities
```

---

## 🔧 Development Notes

### Current Status
- ✅ **Authentication**: Multi-method auth (Email/Password, WeChat OAuth configured)
- ✅ **Page 1**: Card recommendations with vector similarity
- ✅ **Page 2**: AI search with tag extraction  
- ✅ **Database**: PostgreSQL with comprehensive schema
- ✅ **Security**: JWT tokens, password hashing, rate limiting
- ✅ **CORS**: Enabled for React Native frontend
- ✅ **Testing**: Comprehensive test suite
- ✅ **Documentation**: Interactive API docs at /docs
- ❌ **Pages 3-4**: Chat & profile features (future)

### Recent Updates (Latest Session)
- ✅ **Fixed SQLAlchemy relationship issues**: Resolved circular import problems
- ✅ **Database schema corrections**: Fixed User model field types (Boolean vs String)
- ✅ **Authentication system completion**: JWT token validation now working
- ✅ **Enhanced error handling**: Global exception handler with structured responses
- ✅ **Testing infrastructure**: Comprehensive test suite with 4 test files covering API, authentication, and algorithms
- ✅ **Email service integration**: Tencent Cloud SES for verification emails

### Multi-Method Authentication System
**Three Authentication Methods Supported**:

1. **Email/Password** ✅ FULLY IMPLEMENTED
   - Registration with email verification
   - Secure password hashing with bcrypt
   - JWT access & refresh tokens
   - Password reset functionality (infrastructure ready)

2. **WeChat OAuth** ⚙️ CONFIGURED FOR FUTURE USE
   - Social login integration prepared
   - Automatic user registration for new WeChat users
   - Seamless mobile app integration

**Security Features**:
- JWT access tokens (30-minute expiry)
- Refresh tokens (30-day expiry) with rotation
- Token revocation on logout
- Verification code expiry (10 minutes)
- Rate limiting and attempt tracking
- Secure password hashing with bcrypt
- Device tracking and IP logging

**Database Tables**:
- `user_auth`: Multiple auth methods per user
- `verification_codes`: Email verification codes  
- `refresh_tokens`: Token management and device tracking
### Smart Algorithm Improvements
**Problem Solved**: Active users could exhaust similar profiles, leaving no cards/search results.

**Solution**: Progressive search strategy with fallback (applied to both Page 1 & Page 2)

#### Recommendation Cards (Page 1) & AI Search (Page 2)
1. **First attempt**: Search top 50 most similar profiles
2. **Second attempt**: If insufficient results, expand to top 150
3. **Third attempt**: Expand to top 300 similar profiles  
4. **Fallback**: If still insufficient, add random unseen users to maintain 20-result target

**Benefits**:
- Guarantees content is always available for active users
- Maintains relevance by prioritizing similar profiles first
- Prevents user frustration from empty results
- Logs attempt details for monitoring user engagement patterns
- Works for both swiping (Page 1) and searching (Page 2)

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
- ~~This should now be rare due to the improved algorithm~~
- If it persists, run `python seed.py` to add more test users
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