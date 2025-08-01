#!/bin/bash
# Production deployment script for Ques backend

set -e  # Exit on any error

echo "🚀 Starting production deployment..."

# Environment setup
export ENVIRONMENT=production
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Check if .env.production exists
if [ ! -f ".env.production" ]; then
    echo "❌ Error: .env.production file not found!"
    echo "Please copy .env.production.example and configure it."
    exit 1
fi

# Copy production environment
cp .env.production .env

# Install dependencies
echo "📦 Installing production dependencies..."
pip install -r requirements.txt

# Run database migrations
echo "🗄️ Running database migrations..."
alembic upgrade head

# Create log directory
mkdir -p logs

# Validate configuration
echo "🔍 Validating configuration..."
python -c "from config.settings import settings; print(f'✅ Configuration loaded for {settings.environment.value} environment')"

# Start the application with Gunicorn for production
echo "🌐 Starting production server..."
exec gunicorn main:app \
    --bind 0.0.0.0:8000 \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --access-logfile logs/access.log \
    --error-logfile logs/error.log \
    --log-level warning \
    --timeout 120 \
    --keep-alive 2 \
    --max-requests 1000 \
    --max-requests-jitter 100 \
    --preload
