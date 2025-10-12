# WeChat Mini App Backend - User Discovery & Whisper System

Complete FastAPI backend with PostgreSQL database, Qdrant vector database, and MCP (Model Context Protocol) integration for AI workflows.

## Features

### Database Architecture
- **PostgreSQL**: Main database with 10 core tables (users, profiles, projects, institutions, whispers, swipes, memberships, quotas, AI sessions, reports)
- **Qdrant Vector DB**: User profile embeddings for AI-powered matching
- **WeChat Local Storage**: UI preferences and temporary data

### AI Integration (MCP)
- **Chatbot Workflow**: General conversation handling
- **Vector Search Workflow**: User discovery based on natural language prompts
- **Profile Suggestions Workflow**: AI-powered profile improvement recommendations

### Authentication
- **WeChat Mini App Login**: Primary authentication method using WeChat OAuth
- **SMS OTP**: Alternative phone number authentication
- **JWT Tokens**: Secure session management

### Core Systems
- **Whisper System**: Anonymous/revealed messaging between users
- **Swipe Tracking**: User interaction analytics
- **Quota Management**: Basic (free) and Pro (10 RMB/month) plans
- **User Reports**: Content moderation with image proof

## Quick Start

### 1. Using Docker Compose (Recommended)

```bash
# Copy environment configuration
cp .env.example .env

# Edit .env with your WeChat App credentials
# WECHAT_APP_ID=your-wechat-mini-app-id
# WECHAT_APP_SECRET=your-wechat-mini-app-secret

# Start all services (PostgreSQL, Qdrant, Redis, Backend)
docker-compose up -d

# Check service health
docker-compose ps
```

### 2. Manual Installation

```bash
# Install Python dependencies
pip install -r requirements.txt

# Set up PostgreSQL database
createdb wechat_miniapp_db

# Start Qdrant vector database
docker run -p 6333:6333 qdrant/qdrant:latest

# Set environment variables
export DATABASE_URL="postgresql://username:password@localhost:5432/wechat_miniapp_db"
export QDRANT_HOST="localhost"
export QDRANT_PORT="6333"
export SECRET_KEY="your-secret-key"
export WECHAT_APP_ID="your-wechat-app-id"
export WECHAT_APP_SECRET="your-wechat-app-secret"

# Run the application
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

## API Endpoints

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/wechat/login` - WeChat Mini App login
- `POST /auth/sms/send-otp` - Send SMS OTP
- `POST /auth/sms/login` - SMS OTP login

### Profile Management
- `GET /profile` - Get user profile
- `POST /profile` - Create user profile
- `PUT /profile` - Update user profile

### Whisper System
- `POST /whispers` - Send whisper message
- `GET /whispers/received` - Get received whispers

### AI Workflows (MCP Integration)
- `POST /ai/chat` - General chatbot conversation
- `POST /ai/search` - Vector-based user search
- `POST /ai/profile-suggestions` - Get profile improvement suggestions

### User Interactions
- `POST /swipes` - Record user swipe action

### System
- `GET /health` - Health check endpoint

## Database Schema

The backend implements the corrected database design with 10 core tables:

1. **users** - Basic user authentication data
2. **user_profiles** - Detailed user profile information
3. **user_projects** - User project portfolios
4. **institutions** - Educational/professional institutions
5. **whispers** - Anonymous messaging system
6. **user_swipes** - User interaction tracking
7. **memberships** - Subscription plans (basic/pro)
8. **user_quotas** - Daily usage limits
9. **ai_sessions** - AI interaction history
10. **user_reports** - Content moderation reports

## Configuration

### Required Environment Variables

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
QDRANT_HOST=localhost
QDRANT_PORT=6333

# Security
SECRET_KEY=your-super-secure-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# WeChat Integration
WECHAT_APP_ID=your-wechat-mini-app-id
WECHAT_APP_SECRET=your-wechat-mini-app-secret

# SMS Provider (optional)
SMS_PROVIDER_API_KEY=your-sms-provider-key
```

## Development

### Running Tests
```bash
pytest
```

### Code Formatting
```bash
black app.py
isort app.py
```

### Database Migrations
```bash
# Initialize Alembic (if not done)
alembic init alembic

# Generate migration
alembic revision --autogenerate -m "Initial tables"

# Apply migration
alembic upgrade head
```

## Architecture Notes

### WeChat Mini App Constraints
- Frontend cannot directly access databases
- All data operations must go through HTTP APIs
- Local storage limited to small UI preferences
- WeChat authentication requires server-side code exchange

### Hybrid Storage Strategy
- **SQL Database**: All business data, user profiles, relationships
- **Vector Database**: User profile embeddings for AI matching
- **WeChat Local Storage**: UI preferences, theme settings only
- **AI Prompts**: Metadata-only storage (no sensitive content)

### MCP Integration
The Model Context Protocol (MCP) provides structured AI workflows:
- **Tools**: Predefined AI functions for specific tasks
- **Resources**: Data access patterns for AI context
- **Prompts**: Reusable AI interaction templates

## Production Deployment

### Environment Setup
1. Set up PostgreSQL database with proper user permissions
2. Deploy Qdrant vector database instance
3. Configure WeChat Mini App credentials
4. Set up SMS provider for OTP authentication
5. Configure proper SSL certificates for HTTPS

### Security Considerations
- Use strong SECRET_KEY for JWT signing
- Implement rate limiting for API endpoints
- Enable CORS only for your WeChat Mini App domain
- Regularly update dependencies for security patches
- Monitor and log user activities for audit trails

### Performance Optimization
- Use connection pooling for PostgreSQL
- Implement Redis caching for frequently accessed data
- Optimize vector search queries in Qdrant
- Use CDN for static assets and profile images

## Support

For questions or issues, please refer to:
- WeChat Mini App development documentation
- FastAPI documentation: https://fastapi.tiangolo.com/
- Qdrant documentation: https://qdrant.tech/documentation/
- PostgreSQL documentation: https://www.postgresql.org/docs/