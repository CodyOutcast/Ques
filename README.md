# 🎯 Ques Backend - Merged Dating App API

A comprehensive dating application backend built with FastAPI, featuring intelligent matchmaking, messaging system, and AI-powered search capabilities.

## 🌟 Features

### 🔐 **Authentication & Security**
- Enterprise-grade email authentication
- WeChat OAuth integration
- JWT token-based session management
- Password hashing with bcrypt
- Rate limiting and security monitoring

### 🧠 **Smart Matchmaking System**
- **Vector Similarity Matching** using BGE Chinese embeddings
- **Progressive Search Strategy** with multiple fallback options
- **Tag-based Recommendations** for enhanced matching
- **Tencent Cloud VectorDB** integration for scalable similarity search
- **Production-ready recommendation engine** with retry logic

### 💬 **Messaging System with Greeting Flow**
- **Greeting/Acceptance Flow**: Users must like and send greetings before messaging
- **Chat Status Management**: pending → active → rejected/blocked
- **Real-time Messaging** capabilities
- **Message Read Status** tracking
- **PostgreSQL Storage** for chat history and messages

### 🔍 **AI-Powered Search (Page 2)**
- **DeepSeek API Integration** for intelligent tag extraction
- **Natural Language Processing** for search queries
- **Vector-based Similar User Discovery**
- **Contextual Recommendations** based on user preferences

### 📱 **User Management**
- Complete user profiles with bio, features, and links
- User verification system
- Activity tracking and history
- Profile customization options

## 🏗️ **Architecture**

```
backend_merged/
├── 🚀 main.py                 # FastAPI application entry point
├── 📋 requirements.txt        # Python dependencies
├── ⚙️ .env                    # Environment configuration
└── 🎮 run_server.py          # Server startup script

📁 API Layer
├── routers/
│   ├── auth.py               # Authentication endpoints
│   ├── users.py              # User management
│   ├── chats.py              # Messaging system ⭐ NEW
│   ├── recommendations.py    # Page 1 recommendations
│   ├── matches.py            # Page 2 AI search
│   ├── messages.py           # Legacy messaging
│   └── profile.py            # User profiles

📁 Business Logic
├── services/
│   ├── auth_service.py       # Authentication logic
│   ├── chat_service.py       # Messaging logic ⭐ NEW
│   ├── email_service.py      # Email notifications
│   └── security.py           # Security utilities

📁 Data Layer
├── models/
│   ├── users.py              # User database model
│   ├── chats.py              # Chat & messaging models ⭐ NEW
│   ├── matches.py            # Match relationships
│   ├── likes.py              # User interactions
│   └── user_auth.py          # Authentication models

📁 AI & Matching
├── production_recommendation_service.py  # Enterprise matchmaking ⭐
├── db_utils.py                           # VectorDB utilities ⭐
└── create_vectordb_collection.py         # VectorDB setup ⭐

📁 Database
├── migrations/               # Alembic database migrations
├── alembic.ini              # Migration configuration
└── setup_database.py        # Database initialization
```

## 🚀 **Quick Start**

### 1️⃣ **Prerequisites**
- Python 3.13+
- PostgreSQL database
- Tencent Cloud VectorDB account (optional for matchmaking)

### 2️⃣ **Installation**
```powershell
# Clone the repository
git clone <repository-url>
cd backend_merged

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
copy .env.example .env
# Edit .env with your configuration
```

### 3️⃣ **Configuration**
Update `.env` file with your settings:
```bash
# Database (Required)
PG_HOST=your-postgres-host
PG_PORT=5432
PG_USER=your-username
PG_PASSWORD=your-password
PG_DATABASE=your-database

# JWT Security (Required)
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret

# Vector Database (Optional - for matchmaking)
VECTORDB_ENDPOINT=your-vectordb-endpoint
VECTORDB_USERNAME=your-username
VECTORDB_KEY=your-api-key

# AI Search (Optional - for Page 2)
DEEPSEEK_API_KEY=your-deepseek-api-key

# Email Service (Optional)
TENCENT_SECRET_ID=your-tencent-id
TENCENT_SECRET_KEY=your-tencent-key
```

### 4️⃣ **Database Setup**
```powershell
# Initialize database and create tables
python setup_database.py

# Run database migrations
alembic upgrade head
```

### 5️⃣ **Start the Server**
```powershell
# Option 1: Use the custom starter (Recommended)
python run_server.py

# Option 2: Use uvicorn directly
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Option 3: Use Python directly
python main.py
```

### 6️⃣ **Access the API**
- **API Server**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 📚 **API Endpoints**

### 🔐 **Authentication**
```
POST /api/v1/auth/register    # User registration
POST /api/v1/auth/login       # User login
POST /api/v1/auth/refresh     # Token refresh
POST /api/v1/auth/logout      # User logout
```

### 👤 **User Management**
```
GET  /api/v1/users/me         # Get current user
PUT  /api/v1/users/me         # Update profile
GET  /api/v1/users/{id}       # Get user by ID
```

### 💝 **Matchmaking (Page 1)**
```
GET  /api/v1/recommendations/cards    # Get recommendation cards
POST /api/v1/recommendations/swipe    # Swipe action (like/pass)
```

### 🔍 **AI Search (Page 2)**
```
POST /api/v1/search/query     # AI-powered user search
GET  /api/v1/search/status    # Search service status
```

### 💬 **Messaging System** ⭐ **NEW**
```
POST /api/v1/chats/greeting           # Send initial greeting
POST /api/v1/chats/greeting/respond   # Accept/reject greeting
POST /api/v1/chats/message            # Send message
GET  /api/v1/chats/                   # Get all chats
GET  /api/v1/chats/pending            # Get pending greetings
GET  /api/v1/chats/{chat_id}          # Get chat with messages
POST /api/v1/chats/messages/read      # Mark messages as read
```

## 🎯 **Messaging Flow**

### **Greeting/Acceptance System**
1. **👍 User A likes User B** (prerequisite)
2. **📨 User A sends greeting** → Chat status: `pending`
3. **📥 User B sees pending greeting**
4. **🤝 User B accepts/rejects** → Chat status: `active` or `rejected`
5. **💬 If accepted: Both users can message normally**
6. **🚫 If rejected: No further messaging allowed**

### **Chat States**
- `pending` - Greeting sent, waiting for response
- `active` - Greeting accepted, messaging enabled
- `rejected` - Greeting rejected, messaging blocked
- `blocked` - Chat blocked by user

## 🧠 **Matchmaking Algorithm**

### **Progressive Search Strategy**
1. **Vector Similarity** - BGE embeddings with cosine similarity
2. **Tag-based Matching** - Feature tag intersection scoring
3. **Fallback Recommendations** - Random unseen users
4. **Hybrid Scoring** - Combined similarity + tag + activity metrics

### **Vector Database Features**
- **768-dimensional BGE embeddings** for Chinese text
- **Tencent Cloud VectorDB** integration
- **Real-time similarity search** with configurable thresholds
- **Scalable architecture** supporting millions of users

## 🗄️ **Database Schema**

### **Core Tables**
- `users` - User profiles and information
- `user_auth` - Authentication credentials
- `user_swipes` - Like/dislike history
- `matches` - Mutual likes and connections

### **Messaging Tables** ⭐ **NEW**
- `chats` - Chat sessions with greeting/acceptance flow
- `chat_messages` - Individual messages within chats

### **System Tables**
- `user_sessions` - Active user sessions
- `security_logs` - Security audit trail
- `alembic_version` - Database migration tracking

## 🧪 **Testing**

### **Run Tests**
```powershell
# Test database setup
python setup_database.py

# Test matchmaking integration
python test_matchmaking_integration.py

# Test API endpoints
python test_api_endpoints.py
```

### **Manual Testing**
```powershell
# Test server health
curl http://localhost:8000/health

# Test API documentation
# Visit: http://localhost:8000/docs
```

## 🔧 **Development**

### **Project Structure**
- **FastAPI** - Modern Python web framework
- **SQLAlchemy** - Database ORM with Alembic migrations
- **Pydantic** - Data validation and serialization
- **PostgreSQL** - Primary database
- **Tencent Cloud VectorDB** - Vector similarity search
- **JWT** - Secure token-based authentication

### **Code Quality**
- **Type hints** throughout the codebase
- **Pydantic models** for request/response validation
- **Structured logging** for debugging and monitoring
- **Error handling** with proper HTTP status codes

### **Scalability Features**
- **Connection pooling** for database efficiency
- **Rate limiting** to prevent abuse
- **Background tasks** for non-blocking operations
- **Configurable environment** settings

## 🚀 **Deployment**

### **Production Checklist**
- [ ] Update `.env` with production credentials
- [ ] Set up SSL/TLS certificates
- [ ] Configure reverse proxy (nginx)
- [ ] Set up database backups
- [ ] Configure monitoring and logging
- [ ] Test all API endpoints
- [ ] Verify messaging system functionality

### **Environment Variables**
- Set `SECRET_KEY` to a secure random string
- Configure production database credentials
- Set up email service for notifications
- Configure VectorDB for matchmaking (optional)

## 📈 **Performance Features**

- **Vector similarity search** with sub-second response times
- **Database indexing** for optimized queries
- **Connection pooling** for efficient database usage
- **Async/await** support for concurrent operations
- **Progressive search** ensuring results are always available

## 🆘 **Troubleshooting**

### **Common Issues**
1. **Import Errors**: Use `python run_server.py` instead of uvicorn directly
2. **Database Connection**: Check `.env` file and database credentials
3. **Missing Dependencies**: Run `pip install -r requirements.txt`
4. **Port Conflicts**: Change port in `run_server.py` or stop other services

### **Debug Mode**
```powershell
# Run with debug logging
python run_server.py --debug

# Check database connection
python setup_database.py
```

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 **License**

This project is licensed under the MIT License.

---

## 🎉 **What's New in This Version**

### ⭐ **Major Features Added**
- **Complete Messaging System** with greeting/acceptance flow
- **Enterprise Matchmaking Algorithm** with vector similarity
- **AI-Powered Search** using DeepSeek API
- **Production-Ready Database** with PostgreSQL + VectorDB
- **Comprehensive Authentication** with JWT and security monitoring

### 🔧 **Technical Improvements**
- **Clean Architecture** with proper separation of concerns
- **Type Safety** with comprehensive Pydantic models
- **Error Handling** with graceful fallbacks
- **Performance Optimization** with connection pooling and indexing
- **Scalable Design** supporting high concurrent usage

### 📱 **User Experience**
- **Intuitive Messaging Flow** requiring likes before messaging
- **Smart Recommendations** with multiple fallback strategies
- **Real-time Features** for instant messaging and notifications
- **Secure Authentication** with enterprise-grade security

**Ready to launch your dating app! 🚀❤️**
