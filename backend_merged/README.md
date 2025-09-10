# 🎯 Ques Backend - Merged Dating App API

A comprehensive dating application backend built with FastAPI, featuring intelligent matchmaking, messaging system, and AI-powered search capabilities.

## 🌟 Features

### 🔐 **Authentication & Security**
- Enterprise-grade email authentication
- WeChat OAuth integration
- JWT token-based session management
- Password hashing with bcrypt
- Rate limiting and security monitoring

### 🛡️ **Content Moderation & Safety** ⭐ **NEW**
- **Tencent Cloud CMS/TMS Integration** for comprehensive content filtering
- **Real-time Text Moderation** for all messages and profile content
- **Image Content Scanning** for inappropriate visual content
- **Automated Blocking** of policy-violating content
- **Graceful Fallbacks** with service resilience
- **Community Guidelines Enforcement** across all user interactions

### 🧠 **Smart Matchmaking System**
- **Vector Similarity Matching** using BGE Chinese embeddings
- **Progressive Search Strategy** with multiple fallback options
- **Tag-based Recommendations** for enhanced matching
- **Tencent Cloud VectorDB** integration for scalable similarity search
- **Production-ready recommendation engine** with retry logic

### 💬 **Messaging System with Greeting Flow**
- **Greeting/Acceptance Flow**: Users must like and send greetings before messaging
- **Chat Status Management**: pending → active → rejected/blocked
- **Real-time Messaging** capabilities with content moderation
- **Message Read Status** tracking
- **PostgreSQL Storage** for chat history and messages

### 🔍 **AI-Powered Search (Page 2)**
- **DeepSeek API Integration** for intelligent tag extraction
- **Natural Language Processing** for search queries
- **Vector-based Similar User Discovery**
- **Contextual Recommendations** based on user preferences

### 🤖 **Project Idea Generation System** ⭐ **NEW**
- **AI-Powered Project Idea Agent** using DeepSeek LLM for creative project suggestions
- **Web Research Integration** with SearchAPI for up-to-date project trends
- **Intelligent Content Scraping** using Crawl4AI for parallel web data extraction
- **Query Refinement Engine** that transforms user queries into optimized search prompts
- **Quota Management System** with subscription-based usage limits:
  - **Free Users**: 30 project idea generations per month
  - **Pro Users**: 300 project idea generations per month
  - **Enterprise Users**: 1000 project idea generations per month
- **Real-time Streaming API** for progressive project idea generation
- **Usage Analytics & Tracking** with detailed request history and success metrics
- **Content Filtering** optimized for Chinese firewall constraints
- **Multi-Engine Search Strategy** (Google, Baidu) with intelligent fallbacks

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
│   ├── project_ideas.py      # Project idea generation ⭐ NEW
│   ├── recommendations.py    # Page 1 recommendations
│   ├── matches.py            # Page 2 AI search
│   ├── messages.py           # Legacy messaging
│   └── profile.py            # User profiles

📁 Business Logic
├── services/
│   ├── auth_service.py       # Authentication logic
│   ├── chat_service.py       # Messaging logic ⭐ NEW
│   ├── project_idea_agent.py # AI project idea generation ⭐ NEW
│   ├── quota_service.py      # Subscription & quota management ⭐ NEW
│   ├── email_service.py      # Email notifications
│   └── security.py           # Security utilities

📁 Data Layer
├── models/
│   ├── users.py              # User database model
│   ├── chats.py              # Chat & messaging models ⭐ NEW
│   ├── subscriptions.py      # Subscription & quota models ⭐ NEW
│   ├── matches.py            # Match relationships
│   ├── likes.py              # User interactions
│   └── user_auth.py          # Authentication models

📁 AI & Matching
├── production_recommendation_service.py  # Enterprise matchmaking ⭐
├── project_idea_agent.py                # Standalone project agent ⭐ NEW
├── project_agent_test.py                # Agent testing utility ⭐ NEW
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

# Project Idea Generation (Required for project idea features) ⭐ NEW
SEARCHAPI_KEY=your-searchapi-key
DEEPSEEK_API_KEY_AGENT=your-deepseek-agent-api-key

# Email Service (Optional)
TENCENT_SECRET_ID=your-tencent-id
TENCENT_SECRET_KEY=your-tencent-key

# Content Moderation (Recommended for production)
ENABLE_CONTENT_MODERATION=true
TENCENT_MODERATION_BIZ_TYPE=default
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
POST /api/v1/auth/register      # User registration
POST /api/v1/auth/login         # User login
POST /api/v1/auth/refresh       # Token refresh
POST /api/v1/auth/logout        # User logout
POST /api/v1/auth/forgot-password  # Send password reset email ⭐ NEW
POST /api/v1/auth/reset-password   # Reset password with code ⭐ NEW
```

### 👤 **User Management**
```
GET  /api/v1/users/profile     # Get current user profile
PUT  /api/v1/users/profile     # Update profile
GET  /api/v1/users/search      # Search users
GET  /api/v1/users/liked       # Get profiles you liked ⭐ NEW
GET  /api/v1/users/liked/mutual # Get mutual likes (matches) ⭐ NEW
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
POST /api/v1/chats/search             # Search chats and messages ⭐ **NEW**
```

### 🤖 **Project Idea Generation APIs** ⭐ **NEW**
```bash
POST /api/v1/project-ideas/generate        # Generate project ideas
POST /api/v1/project-ideas/generate-stream # Real-time streaming generation
GET  /api/v1/project-ideas/quota           # Check user quota status
GET  /api/v1/project-ideas/history         # Get generation history
POST /api/v1/project-ideas/quota/reset     # Admin: Reset user quota
POST /api/v1/project-ideas/subscription/upgrade # Upgrade subscription
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

## 🛡️ **Content Moderation & Safety** ⭐ **NEW**

### **Comprehensive Content Filtering**
All user-generated content is automatically filtered through Tencent Cloud's industry-leading content moderation services for maximum safety and compliance.

### **What Gets Moderated:**
- **💬 Chat Messages** - All messages are scanned before delivery
- **👤 User Profiles** - Bio, display name, location, interests, and other profile fields
- **🖼️ Profile Images** - Avatar and cover photos scanned for inappropriate content
- **📝 User Registration** - Username and initial profile information
- **🎯 All Text Content** - Any user-submitted text across the platform

### **Moderation Technology:**
- **Tencent Cloud TMS (Text Moderation Service)** - Advanced AI text filtering
- **Tencent Cloud CMS (Content Moderation Service)** - Comprehensive image analysis
- **Real-time Processing** - Content is moderated instantly as it's submitted
- **Multi-language Support** - Handles Chinese, English, and other languages
- **High Accuracy** - Industry-leading detection of policy violations

### **Safety Features:**
- **Automatic Blocking** - Inappropriate content is blocked immediately
- **Graceful Degradation** - Service continues if moderation API is unavailable
- **Detailed Logging** - All moderation decisions are logged for audit
- **Violation Reporting** - Clear feedback on why content was blocked
- **Appeal Process** - Users receive clear guidance on content policies

### **Content Policies Enforced:**
- **Hate Speech & Harassment** - Zero tolerance for abusive content
- **Adult Content** - Inappropriate sexual content blocked
- **Violence & Threats** - Threatening or violent content removed
- **Spam & Scams** - Commercial spam and fraudulent content filtered
- **Personal Information** - Protection against doxxing and privacy violations
- **Illegal Activities** - Content promoting illegal activities blocked

### **API Integration:**
```python
# Example: Manual content moderation
from services.content_moderation import moderate_text_content

result = await moderate_text_content("User message here", user_id=123)
if result.result == "rejected":
    # Handle blocked content
    print(f"Content blocked: {result.violations}")
```

### **Configuration:**
```bash
# Enable content moderation (recommended for production)
ENABLE_CONTENT_MODERATION=true

# Tencent Cloud credentials (required)
TENCENT_SECRET_ID=your_secret_id
TENCENT_SECRET_KEY=your_secret_key
TENCENT_REGION=ap-guangzhou

# Moderation settings (optional)
TENCENT_MODERATION_BIZ_TYPE=default
MODERATION_AUTO_APPROVE_THRESHOLD=0.8
MODERATION_AUTO_REJECT_THRESHOLD=0.9
```

### **Testing Content Moderation:**
```powershell
# Test the moderation system
python test_content_moderation.py
```

### **Moderation Flow:**
1. **🔍 Content Submitted** - User sends message/updates profile
2. **🛡️ Automatic Scanning** - Content sent to Tencent Cloud APIs
3. **⚡ Instant Results** - Moderation decision made in milliseconds
4. **✅ Approved Content** - Clean content delivered normally
5. **❌ Blocked Content** - User receives clear error message
6. **📊 Audit Logging** - All decisions logged for compliance

### **Performance & Reliability:**
- **⚡ Sub-second Response** - Moderation adds minimal latency
- **🔄 Automatic Retries** - Handles temporary service outages
- **📈 Scalable Architecture** - Handles high message volumes
- **🛡️ Failsafe Mode** - Defaults to approval if service fails
- **📊 Monitoring Integration** - Tracks moderation performance

## � **Chat Search Feature** ⭐ **NEW**

### **Intelligent Chat & Message Search**
Find conversations and messages quickly with comprehensive search capabilities.

### **Search Capabilities**
- **💬 Message Content Search** - Search through all your messages
- **👤 User Name Search** - Find chats by username or display name
- **📝 Bio Search** - Search user bios for keywords
- **🎯 Highlighted Results** - Search terms highlighted in results
- **📄 Contextual Results** - Recent messages shown for context

### **API Usage**
```bash
POST /api/v1/chats/search
{
  "query": "hello world",
  "search_messages": true,
  "search_users": true,
  "limit": 20
}
```

### **Response Format**
```json
{
  "query": "hello world",
  "total_chats": 3,
  "total_messages": 15,
  "chats": [
    {
      "chat_id": 123,
      "other_user_name": "John Doe",
      "match_reason": "Username match",
      "recent_messages": [...],
      "status": "active"
    }
  ],
  "messages": [
    {
      "message_id": 456,
      "content": "Hello world! How are you?",
      "highlighted_content": "**Hello world**! How are you?",
      "sender_name": "Jane Smith",
      "created_at": "2025-01-15T10:30:00Z"
    }
  ]
}
```

### **Search Features**
- **🚀 Fast Performance** - Optimized database queries
- **🔤 Case Insensitive** - Finds matches regardless of case
- **📱 Pagination Support** - Configurable result limits
- **🛡️ Security** - Only searches your own chats
- **✨ Smart Highlighting** - Shows search terms in context

## 🔐 **Password Reset Flow**

### **Secure Password Reset System**
1. **📧 User requests password reset** → Email sent with 6-digit code
2. **🔑 User receives reset code** → Code expires in 15 minutes
3. **✍️ User enters code + new password** → Password updated securely
4. **🚫 All sessions invalidated** → User must log in again
5. **🔒 Old password becomes invalid** → Enhanced security

### **Security Features**
- **Time-based expiration** (15 minutes for security)
- **One-time use codes** (invalidated after successful reset)
- **Email enumeration protection** (same response for valid/invalid emails)
- **Session invalidation** (all refresh tokens revoked)
- **Audit logging** (all attempts logged for security monitoring)
- **Rate limiting** (prevents abuse and brute force attacks)

### **API Usage**
```bash
# Step 1: Request password reset
POST /api/v1/auth/forgot-password
{
  "email": "user@example.com"
}

# Step 2: Reset password with code
POST /api/v1/auth/reset-password
{
  "email": "user@example.com",
  "reset_code": "123456",
  "new_password": "newSecurePassword123"
}
```

## 👀 **Liked Profiles Feature** ⭐ **NEW**

### **View Your Liked Users**
Browse through profiles of users you've previously liked, with enhanced information about mutual connections.

### **Key Features**
- **📱 Paginated Browsing** - Smooth pagination through your liked users
- **💕 Mutual Like Detection** - See which users liked you back
- **🔍 Detailed Profiles** - Full profile information for each liked user
- **⏰ Like Timestamps** - See when you liked each user
- **🚀 Fast Queries** - Optimized database queries for quick loading

### **API Endpoints**
```bash
# Get all users you've liked (paginated)
GET /api/v1/users/liked?page=1&per_page=20

# Get only mutual likes (matches)
GET /api/v1/users/liked/mutual?page=1&per_page=20
```

### **Response Format**
```json
{
  "page": 1,
  "per_page": 20,
  "total": 45,
  "total_pages": 3,
  "has_next": true,
  "has_prev": false,
  "users": [
    {
      "id": 123,
      "username": "johndoe",
      "display_name": "John Doe",
      "bio": "Love hiking and photography",
      "age": 28,
      "location": "San Francisco",
      "avatar_url": "https://...",
      "is_verified": true,
      "liked_at": "2025-01-15T10:30:00Z",
      "is_mutual_like": true
    }
  ]
}
```

### **Use Cases**
- **Review Past Likes** - Browse users you've shown interest in
- **Find Matches** - Quickly see who liked you back
- **Re-engage** - Message users you've already connected with
- **Analytics** - Track your dating activity and preferences

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

## � **Project Idea Generation System** ⭐ **NEW**

### **AI-Powered Project Ideation**
Transform user queries into creative, actionable project ideas using advanced AI and web research.

### **System Architecture**
1. **🧠 Query Intelligence** - DeepSeek LLM refines user queries into optimized search prompts
2. **🌐 Web Research** - SearchAPI gathers up-to-date information from multiple search engines
3. **🕷️ Content Extraction** - Crawl4AI performs parallel web scraping with intelligent filtering
4. **💡 Idea Generation** - AI synthesizes research into creative project suggestions
5. **📊 Usage Tracking** - Comprehensive quota and analytics system

### **Core Features**
- **🎯 Smart Query Processing**: Transforms vague ideas into specific search strategies
- **⚡ Real-time Streaming**: Progressive updates during generation process
- **🔄 Multi-Engine Search**: Google + Baidu with intelligent fallbacks
- **🚫 Content Filtering**: Optimized for Chinese firewall constraints
- **📈 Subscription Management**: Tiered quota system with usage analytics
- **🎨 Creative Synthesis**: AI combines multiple sources into unique project ideas

### **Subscription Tiers & Quotas**
| Tier | Monthly Quota | Features |
|------|---------------|----------|
| **Free** | 30 generations | Basic project ideas |
| **Pro** | 300 generations | Priority processing + history |
| **Enterprise** | 1000 generations | Advanced analytics + support |

### **API Endpoints**
```bash
# Generate project ideas
POST /api/v1/project-ideas/generate
{
  "query": "Build a mobile app for fitness tracking"
}

# Stream generation process
POST /api/v1/project-ideas/generate-stream
# Returns Server-Sent Events with real-time progress

# Check quota status
GET /api/v1/project-ideas/quota

# View generation history
GET /api/v1/project-ideas/history?days=30

# Upgrade subscription
POST /api/v1/project-ideas/subscription/upgrade
{
  "subscription_type": "pro"
}
```

### **Example Response**
```json
{
  "search_id": 1234,
  "original_query": "Build a mobile app for fitness tracking",
  "total_sources_found": 15,
  "total_ideas_extracted": 3,
  "processing_time_seconds": 12.5,
  "project_ideas": [
    {
      "title": "AI-Powered Fitness Coach App",
      "description": "Mobile app with computer vision for exercise form correction and personalized workout plans",
      "difficulty": "Intermediate",
      "technologies": ["React Native", "TensorFlow Lite", "Firebase"],
      "estimated_time": "3-4 months",
      "relevance_score": 0.95
    }
  ]
}
```

### **Environment Configuration**
```bash
# Required for project idea generation
SEARCHAPI_KEY=your-searchapi-key          # Web search capabilities
DEEPSEEK_API_KEY_AGENT=your-deepseek-key  # AI query processing & idea generation
```

### **Database Models**
- **UserSubscription** - Tracks user subscription status and quota limits
- **ProjectIdeaRequest** - Logs all generation requests with metadata
- **Usage Analytics** - Detailed tracking of success rates and performance

### **Testing & Development**
```bash
# Test project idea agent
python project_agent_test.py

# Test quota system
python test_quota_system.py

# Interactive agent testing
python -c "from services.project_idea_agent import generate_project_ideas; print(generate_project_ideas('build a chatbot', 123))"
```

## �🧪 **Testing**

### **Run Tests**
```powershell
# Test database setup
python setup_database.py

# Test content moderation system ⭐ NEW
python test_content_moderation.py

# Test project idea generation system ⭐ NEW
python project_agent_test.py
python test_quota_system.py

# Test matchmaking integration
python test_matchmaking_integration.py

# Test API endpoints
python test_api_endpoints.py

# Test password reset functionality
python test_password_reset.py

# Test liked profiles functionality
python test_liked_profiles.py

# Test messaging system
python test_messaging_system.py

# Test chat search functionality ⭐ NEW
python test_chat_search.py
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
- **Tencent Cloud Content Moderation** with CMS/TMS integration ⭐ **NEW**
- **Enterprise Matchmaking Algorithm** with vector similarity
- **AI-Powered Search** using DeepSeek API
- **Production-Ready Database** with PostgreSQL + VectorDB
- **Comprehensive Authentication** with JWT and security monitoring
- **Password Reset System** with secure email-based recovery
- **Liked Profiles Management** with mutual like detection
- **Chat Search Functionality** with intelligent message & user search ⭐ **NEW**

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
- **Password Recovery** with secure email-based reset flow
- **Liked User Management** with easy browsing and mutual detection
- **Intelligent Search** with message content and user search ⭐ **NEW**

**Ready to launch your dating app! 🚀❤️**
