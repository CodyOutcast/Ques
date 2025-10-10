# ========================================
# Intelligent Search Agent Demo - Makefile
# ========================================

.PHONY: help install dev clean \
        setup-env init-db generate-data validate-data \
        run-api run-qdrant run-qdrant-bg stop-qdrant \
        generate-embeddings \
        test test-api test-db test-qdrant test-integration \
        format lint check \
        deploy deploy-basic deploy-full \
        status health logs \
        reset clean-all

# ----------------------------------------
# Help and Information
# ----------------------------------------

help: ## 📋 Show this help message with available commands
	@echo ""
	@echo "🤖 Intelligent Search Agent Demo - Available Commands"
	@echo "=================================================="
	@echo ""
	@echo "📦 Setup & Installation:"
	@grep -E '^[a-zA-Z_-]+:.*?## 📦.*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m  %-20s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "🗄️  Database Management:"
	@grep -E '^[a-zA-Z_-]+:.*?## 🗄️.*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m  %-20s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "🚀 Services:"
	@grep -E '^[a-zA-Z_-]+:.*?## 🚀.*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m  %-20s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "🧪 Testing:"
	@grep -E '^[a-zA-Z_-]+:.*?## 🧪.*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m  %-20s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "🔧 Development:"
	@grep -E '^[a-zA-Z_-]+:.*?## 🔧.*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m  %-20s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "🎯 Deployment:"
	@grep -E '^[a-zA-Z_-]+:.*?## 🎯.*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m  %-20s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "📊 Monitoring:"
	@grep -E '^[a-zA-Z_-]+:.*?## 📊.*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m  %-20s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "🧹 Cleanup:"
	@grep -E '^[a-zA-Z_-]+:.*?## 🧹.*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m  %-20s\033[0m %s\n", $$1, $$2}'
	@echo ""

# ----------------------------------------
# Setup & Installation
# ----------------------------------------

install: ## 📦 Install production dependencies
	@echo "📦 Installing production dependencies..."
	pip install -r requirements.txt
	@echo "✅ Dependencies installed successfully!"

dev: ## 📦 Install development dependencies (includes code quality tools)
	@echo "📦 Installing development dependencies..."
	pip install -r requirements.txt
	@echo "🔧 Installing development tools..."
	pip install black>=23.0.0 flake8>=6.0.0 mypy>=1.7.0 isort>=5.12.0
	@echo "✅ Development environment ready!"

setup-env: ## 📦 Setup environment variables (copy .env.example to .env)
	@if [ ! -f .env ]; then \
		echo "📝 Creating .env file from template..."; \
		cp .env.example .env; \
		echo "⚠️  Please edit .env and configure your GLM-4 API key!"; \
	else \
		echo "✅ .env file already exists"; \
	fi

# ----------------------------------------
# Database Management  
# ----------------------------------------

init-db: ## 🗄️ Initialize SQLite database with schema
	@echo "🗄️ Initializing SQLite database..."
	python src/database/init_database.py
	@echo "✅ Database initialized successfully!"

generate-data: ## 🗄️ Generate test data (1000 user records)
	@echo "🗄️ Generating test data..."
	python src/database/generate_test_data.py
	@echo "✅ Test data generated successfully!"

validate-data: ## 🗄️ Validate database data integrity
	@echo "🗄️ Validating database data..."
	python src/database/validate_data.py
	@echo "✅ Data validation completed!"

db-setup: init-db generate-data validate-data ## 🗄️ Complete database setup (init + data + validation)
	@echo "🎉 Database setup completed!"

# ----------------------------------------
# Services
# ----------------------------------------

run-api: ## 🚀 Start FastAPI server (localhost:8000)
	@echo "🚀 Starting FastAPI server..."
	@echo "📍 API will be available at: http://localhost:8000"
	@echo "📚 API docs at: http://localhost:8000/docs"
	uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload

run-api-prod: ## 🚀 Start FastAPI server in production mode
	@echo "🚀 Starting FastAPI server (production mode)..."
	uvicorn src.api.main:app --host 0.0.0.0 --port 8000

run-qdrant: ## 🚀 Start Qdrant vector database (localhost:6333) - foreground
	@echo "🚀 Starting Qdrant vector database..."
	@echo "📍 Qdrant will be available at: http://localhost:6333"
	@echo "🌐 Web UI at: http://localhost:6333/dashboard"
	docker run --name qdrant --rm \
		-p 6333:6333 \
		-v $$(pwd)/qdrant_storage:/qdrant/storage \
		qdrant/qdrant

run-qdrant-bg: ## 🚀 Start Qdrant vector database in background
	@echo "🚀 Starting Qdrant vector database in background..."
	docker run -d --name qdrant \
		-p 6333:6333 \
		-v $$(pwd)/qdrant_storage:/qdrant/storage \
		qdrant/qdrant
	@echo "✅ Qdrant started in background"
	@echo "📍 Available at: http://localhost:6333"

stop-qdrant: ## 🚀 Stop Qdrant vector database
	@echo "🛑 Stopping Qdrant vector database..."
	-docker stop qdrant
	-docker rm qdrant
	@echo "✅ Qdrant stopped"

generate-embeddings: ## 🚀 Generate and import vector embeddings (requires Qdrant)
	@echo "🚀 Generating vector embeddings..."
	@echo "⏳ This may take 10-30 minutes depending on your hardware..."
	python src/vector_search/generate_embeddings.py
	@echo "✅ Vector embeddings generated and imported!"

# ----------------------------------------
# Testing
# ----------------------------------------

test: ## 🧪 Run all tests
	@echo "🧪 Running all tests..."
	pytest tests/ -v

test-api: ## 🧪 Test API endpoints (requires running API server)
	@echo "🧪 Testing API endpoints..."
	pytest tests/test_api.py -v

test-db: ## 🧪 Test database integration
	@echo "🧪 Testing database integration..."
	pytest tests/test_database_integration.py -v

test-qdrant: ## 🧪 Test Qdrant connection (requires running Qdrant)
	@echo "🧪 Testing Qdrant connection..."
	pytest tests/test_qdrant_connection.py -v

test-integration: ## 🧪 Test intelligent search agent (requires full setup)
	@echo "🧪 Testing intelligent search agent..."
	pytest tests/test_integration.py -v

test-basic: test-db test-api ## 🧪 Run basic tests (database + API)
	@echo "✅ Basic tests completed!"

test-full: test test-qdrant test-integration ## 🧪 Run full test suite (requires complete setup)
	@echo "✅ Full test suite completed!"

test-coverage: ## 🧪 Run tests with coverage report
	@echo "🧪 Running tests with coverage..."
	pytest tests/ --cov=src --cov-report=html --cov-report=term
	@echo "📊 Coverage report generated in htmlcov/"

# ----------------------------------------
# Development Tools
# ----------------------------------------

format: ## 🔧 Format code with black and isort
	@echo "🔧 Formatting code..."
	black src/ tests/
	isort src/ tests/
	@echo "✅ Code formatted!"

lint: ## 🔧 Run linting (flake8 + mypy)
	@echo "🔧 Running linters..."
	flake8 src/ tests/ --max-line-length=100
	mypy src/ --ignore-missing-imports
	@echo "✅ Linting completed!"

check: format lint ## 🔧 Format code and run linting
	@echo "✅ Code quality check completed!"

clean: ## 🔧 Clean up cache files and temporary files
	@echo "🧹 Cleaning up cache files..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
	find . -name "*.pyo" -delete 2>/dev/null || true
	find . -name "*.pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -name ".coverage" -delete 2>/dev/null || true
	rm -rf htmlcov/ 2>/dev/null || true
	@echo "✅ Cleanup completed!"

# ----------------------------------------
# Deployment Shortcuts
# ----------------------------------------

deploy-basic: setup-env install db-setup run-api ## 🎯 Deploy basic functionality (database + API)
	@echo "🎉 Basic deployment completed!"
	@echo "📍 API available at: http://localhost:8000"

deploy-full: setup-env install db-setup ## 🎯 Deploy full system (interactive setup)
	@echo "🎯 Starting full deployment..."
	@echo "1️⃣ Database and API setup completed"
	@echo "2️⃣ Next: Start Qdrant with 'make run-qdrant-bg'"
	@echo "3️⃣ Then: Generate embeddings with 'make generate-embeddings'"
	@echo "4️⃣ Finally: Test with 'make test-full'"

# ----------------------------------------
# Monitoring & Status
# ----------------------------------------

status: ## 📊 Check status of all services
	@echo "📊 Checking service status..."
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo "🗄️ Database:"
	@if [ -f quesai_test.db ]; then \
		echo "  ✅ SQLite database exists"; \
		sqlite3 quesai_test.db "SELECT COUNT(*) || ' users' FROM user_profiles;" 2>/dev/null || echo "  ❌ Database error"; \
	else \
		echo "  ❌ Database not found"; \
	fi
	@echo ""
	@echo "🌐 API Server:"
	@curl -s http://localhost:8000/health > /dev/null 2>&1 && echo "  ✅ API server running (http://localhost:8000)" || echo "  ❌ API server not running"
	@echo ""
	@echo "🔍 Qdrant Vector Database:"
	@curl -s http://localhost:6333/health > /dev/null 2>&1 && echo "  ✅ Qdrant running (http://localhost:6333)" || echo "  ❌ Qdrant not running"
	@echo ""
	@echo "🐳 Docker Containers:"
	@docker ps --format "table {{.Names}}\t{{.Status}}" --filter name=qdrant 2>/dev/null || echo "  ❌ Docker not available"

health: ## 📊 Quick health check of running services
	@echo "🔍 Quick health check..."
	@curl -s http://localhost:8000/health && echo "" || echo "❌ API not responding"
	@curl -s http://localhost:6333/health && echo "✅ Qdrant healthy" || echo "❌ Qdrant not responding"

logs: ## 📊 Show Qdrant container logs
	@echo "📋 Qdrant container logs:"
	docker logs qdrant --tail=50

# ----------------------------------------
# Cleanup & Reset
# ----------------------------------------

clean-all: clean stop-qdrant ## 🧹 Complete cleanup (stop services + clean cache)
	@echo "🧹 Performing complete cleanup..."
	@echo "✅ All cleanup completed!"

reset: clean-all ## 🧹 Reset everything (remove database, stop services, clean cache)
	@echo "🧹 Resetting project to clean state..."
	@read -p "⚠️  This will delete the database and vector data. Continue? (y/N) " confirm && [ $$confirm = y ]
	rm -f quesai_test.db
	rm -rf qdrant_storage/
	@echo "✅ Project reset completed!"

# ----------------------------------------
# Quick Start Aliases
# ----------------------------------------

start: setup-env install db-setup run-api ## 🎯 Quick start - basic functionality
start-full: deploy-full ## 🎯 Quick start - full setup guide