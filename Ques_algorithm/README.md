# 🤖 Intelligent Search Agent Demo

An intelligent search agent testing project based on GLM-4 and hybrid vector search. This project aims to demonstrate and test the advanced intelligent search algorithm implemented in `intelligent_search_agent.py`.

## 📋 Project Overview

This is a complete intelligent search system that combines:

- **🧠 GLM-4 Large Language Model**: Intelligent intent recognition, quality assessment, natural language generation
- **🔍 Hybrid Vector Search**: Dense vectors (BGE-M3) + Sparse vectors (SPLADE) + Precise filtering
- **⚡ Intelligent Scheduling Strategy**: Three-level progressive search strategy, dynamic quality-driven
- **🎯 Multi-mode Interaction**: Three intelligent interaction modes: search, inquiry, and chat

## 🏗️ Project Architecture

```
quesai_backend_test/
├── 📁 src/                          # Core source code
│   ├── 🤖 vector_search/            # Intelligent search algorithm core
│   │   ├── intelligent_search_agent.py  # ⭐ Main algorithm implementation
│   │   ├── generate_embeddings.py       # Vector embedding generation
│   │   └── config.py                    # Search configuration
│   ├── 🌐 api/                      # RESTful API services
│   │   └── main.py                  # FastAPI application entry
│   ├── 🗄️ database/                 # Database management
│   │   ├── init_database.py         # Database initialization
│   │   ├── generate_test_data.py    # Test data generation
│   │   └── validate_data.py         # Data validation
│   └── 🧠 llm/                      # LLM client
│       └── glm4_client.py           # GLM-4 API client
├── 📚 docs/                         # Project documentation
│   └── search_agent_design.md   # ⭐ Algorithm design documentation
├── 🧪 tests/                        # Test suite
│   ├── test_integration.py          # Integration tests
│   ├── test_api.py                  # API tests
│   ├── test_database_integration.py # Database tests
│   └── test_qdrant_connection.py    # Vector database tests
├── 🐳 qdrant_storage/               # Vector database storage
├── 💾 quesai_test.db                # SQLite test database
└── 📋 requirements.txt              # Python dependencies
```

## 📖 Core Algorithm & Design Documentation

### 🔬 Algorithm Documentation Location⭐

This document does not show the actual algorithm design. If needed, please refer to the following files:

- **Main Algorithm Implementation**: `src/vector_search/intelligent_search_agent.py`
- **Design Documentation**: `docs/search_agent_design.md`

## 🚀 Local Deployment Guide

**This section is for local deployment testing. If you need actual deployment or cloud testing, directly modify 'generate_embeddings.py', 'intelligent_search_agent.py' and 'test_integration.py' to test and optimize the algorithm.**

### Step 1: Project Setup

```bash
# 1. Clone the project
git clone <your-repository-url>
cd quesai_backend_test

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
```

### Step 2: Environment Variable Configuration

```bash
# Copy environment variable template
cp .env.example .env

# Edit environment variables
nano .env  # or use your preferred editor
```

**Required environment variable configuration:**

```bash
# GLM-4 API key (required)
ZHIPUAI_API_KEY=your_glm4_api_key_here
GLM_API_KEY=your_glm4_api_key_here

# Qdrant vector database configuration
QDRANT_HOST=localhost
QDRANT_PORT=6333

# Search collection configuration
COLLECTION_NAME=users_rawjson
```

### Step 3: Database Creation and Initialization

```bash
# 1. Create SQLite database and table structure
python src/database/init_database.py

# 2. Generate test data (1000 user records)
python src/database/generate_test_data.py

# 3. Validate data integrity
python src/database/validate_data.py
```

### Step 4: API Service Startup

```bash
# Method 1: Direct execution
python src/api/main.py

# Method 2: Using uvicorn (recommended)
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload

# Verify API service
curl http://localhost:8000/health

# View API documentation
# Visit http://localhost:8000/docs
```

### Step 5: Vector Database Deployment (Docker)

```bash
# 1. Start Qdrant vector database
docker run -d --name qdrant \
    -p 6333:6333 \
    -v $(pwd)/qdrant_storage:/qdrant/storage \
    qdrant/qdrant

# 2. Verify Qdrant running status
curl http://localhost:6333/health

# 3. Check Qdrant version information
curl http://localhost:6333/

# Optional: View Qdrant Web UI
# Visit http://localhost:6333/dashboard
```

### Step 6: Vector Embedding Data Import

```bash
# Generate and import vector embeddings (takes a long time, about 10-30 minutes)
python src/vector_search/generate_embeddings.py

# This process includes:
# - Download BGE-M3 model (dense vectors)
# - Download SPLADE model (sparse vectors)  
# - Generate vector embeddings for 1000 users
# - Import to Qdrant vector database

# Verify vector data import
python tests/test_qdrant_connection.py
```

**🚀 Complete intelligent search functionality is now enabled!**
You can now use the complete intelligent search agent functionality, including hybrid vector search, intent recognition, and other advanced features.

## 🧪 Phased Testing Guide

### 📋 After Step 4 - Basic API Testing

After completing database creation and API startup, you can perform basic functionality tests:

```bash
# 1. API interface testing
pytest tests/test_api.py -v

# 2. Database integration testing  
pytest tests/test_database_integration.py -v

# 3. Manual API interface testing
curl "http://localhost:8000/users?page=1&page_size=5"
curl "http://localhost:8000/users/1"
curl "http://localhost:8000/stats"
```

### 🤖 After Step 6 - Complete Functionality Testing

After completing vector database and embedding data import, you can perform complete testing:

```bash
# 1. Vector database connection testing
pytest tests/test_qdrant_connection.py -v

# 2. Intelligent search agent integration testing (core testing)
pytest tests/test_integration.py -v

# 3. Complete test suite
pytest tests/ -v

# 4. Display test coverage
pytest tests/ --cov=src --cov-report=html
```

### 🔄 Run All Tests

```bash
# Complete test suite (requires completion of all deployment steps)
pytest tests/ -v

# Display test coverage
pytest tests/ --cov=src --cov-report=html
```

### 🎯 Functionality Verification Testing

```bash
# Basic data API testing (available after Step 4)
pytest tests/test_api.py -v
pytest tests/test_database_integration.py -v

# Vector search functionality testing (available after Step 6)
pytest tests/test_qdrant_connection.py -v
pytest tests/test_integration.py -v
```

### 🤖 Intelligent Search Agent Manual Testing

```bash
# Run intelligent search agent interactive testing
python tests/test_integration.py

# Test content includes:
# - Intent recognition testing (search/inquiry/chat)
# - Quality assessment logic testing
# - Hybrid vector search testing
# - Intelligent scheduling strategy testing
```

## 🔧 Core Functionality Usage Examples

### 🤖 Intelligent Search Agent

```python
from src.vector_search.intelligent_search_agent import create_search_agent

# Create search agent
agent = await create_search_agent()

# Intelligent search
result = await agent.intelligent_search(
    user_query="Find backend engineers with Python experience",
    user_id=1,
    user_preferences={"location": "Beijing"}
)

# Inquire about specific user
result = await agent.intelligent_search(
    user_query="Analyze the skill matching degree of user 123 in detail",
    user_id=1,
    referenced_users=[{"user_id": 123}]
)

# Natural chat
result = await agent.intelligent_search(
    user_query="Hello, please introduce your functions",
    user_id=1
)
```

### 🌐 API Interface Usage

```bash
# Get user list
curl "http://localhost:8000/users?page=1&page_size=10"

# Search users
curl "http://localhost:8000/users?search=Python&page=1"

# Get user details
curl "http://localhost:8000/users/1"

# View system statistics
curl "http://localhost:8000/stats"
```

## 🐛 Troubleshooting

### Common Problem Solutions

**1. GLM-4 API Connection Failure**

```bash
# Check API key configuration
echo $ZHIPUAI_API_KEY

# Test API connection
python -c "from src.llm.glm4_client import GLM4Client; print(GLM4Client().test_connection())"
```

**2. Qdrant Connection Failure**

```bash
# Check Docker container status
docker ps | grep qdrant

# Restart Qdrant container
docker restart qdrant

# Check port usage
lsof -i :6333
```

**3. Vector Embedding Generation Failure**

```bash
# Check model download
ls ~/.cache/huggingface/transformers/

# Check GPU/memory usage
nvidia-smi  # GPU
free -h     # Memory
```

## 📚 API Documentation

After starting the service, visit:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## 🤝 Development Guide

### Code Structure Description

- **`intelligent_search_agent.py`**: Core search algorithm, including intent recognition, hybrid search, quality assessment
- **`generate_embeddings.py`**: Vector embedding generation, supporting BGE-M3 and SPLADE models
- **`glm4_client.py`**: GLM-4 API client, supporting all models and features

### Extension Development

1. **Add new search strategies**: Modify `SearchAgent.search_with_strategy()`
2. **Custom quality assessment**: Adjust evaluation logic in `analyze_candidates_quality()`
3. **Add new interaction modes**: Add new processors in the intent recognizer

## 📄 License

MIT License - See [LICENSE](LICENSE) file for details

## 🆘 Technical Support

When encountering problems:

1. 📖 Check `docs/search_agent_design.md` for detailed design documentation
2. 🧪 Run relevant tests to confirm environment configuration
3. 📝 When submitting Issues, please include error logs and environment information

## 🔗 Related Resources

- [GLM-4 API Documentation](https://open.bigmodel.cn/dev/api)
- [Qdrant Vector Database](https://qdrant.tech/documentation/)
- [BGE-M3 Model](https://huggingface.co/BAAI/bge-m3)
- [SPLADE Model](https://huggingface.co/naver/splade-cocondenser-ensembledistil)
