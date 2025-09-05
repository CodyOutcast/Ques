#!/bin/bash

# Project Slots System Deployment Script
# Runs database migration and restarts services

echo "🚀 Deploying Project Slots System..."

# Check if we're in the right directory
if [ ! -f "main.py" ]; then
    echo "❌ Error: Please run this script from the backend_merged directory"
    exit 1
fi

# Backup database (optional but recommended)
echo "📦 Creating database backup..."
pg_dump -h $PG_HOST -p $PG_PORT -U $PG_USER -d $PG_DATABASE > "backup_before_slots_$(date +%Y%m%d_%H%M%S).sql"
echo "✅ Database backup created"

# Run database migration
echo "🗄️ Running database migration..."
alembic upgrade head

if [ $? -ne 0 ]; then
    echo "❌ Migration failed! Stopping deployment"
    exit 1
fi

echo "✅ Database migration completed"

# Install any new dependencies
echo "📋 Installing dependencies..."
pip install -r requirements.txt

# Restart services (adjust based on your deployment method)
if command -v systemctl &> /dev/null; then
    echo "🔄 Restarting systemd service..."
    sudo systemctl restart questrial-backend
elif command -v docker-compose &> /dev/null && [ -f "docker-compose.production.yml" ]; then
    echo "🐳 Restarting Docker containers..."
    docker-compose -f docker-compose.production.yml down
    docker-compose -f docker-compose.production.yml up -d
elif command -v supervisorctl &> /dev/null; then
    echo "🔄 Restarting supervisor service..."
    supervisorctl restart questrial-backend
else
    echo "⚠️  Please manually restart your application server"
fi

# Verify deployment
echo "🔍 Verifying deployment..."
sleep 5

# Check if the service is responding
if command -v curl &> /dev/null; then
    response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/v1/slots/statistics 2>/dev/null)
    if [ "$response" = "200" ]; then
        echo "✅ Slot system API is responding"
    else
        echo "⚠️  API check returned: $response (may need authentication)"
    fi
else
    echo "⚠️  curl not available, skipping API check"
fi

echo "🎉 Project Slots System deployment completed!"
echo ""
echo "📚 Next steps:"
echo "1. Test the slot system endpoints"
echo "2. Configure membership webhook URLs"  
echo "3. Set up monitoring for background tasks"
echo "4. Update client applications to use new slot API"
echo ""
echo "📖 Documentation: See PROJECT_SLOTS_README.md for usage details"
