# 🧪 Verification Commands for CVM
# Run these on your server to verify the message search functionality

echo "🔍 Testing Message Search Deployment"
echo "======================================"

# 1. Check if the application is running
echo "1. Checking application status..."
sudo systemctl status ques-backend --no-pager

# 2. Check database connection
echo "2. Testing database connection..."
cd /opt/ques-backend
python3 -c "
from dependencies.db import get_db
try:
    db = next(get_db())
    result = db.execute('SELECT 1').fetchone()
    print('✅ Database connection successful')
    db.close()
except Exception as e:
    print(f'❌ Database connection failed: {e}')
"

# 3. Check if new migration was applied
echo "3. Checking migration status..."
alembic current

# 4. Verify new indexes exist
echo "4. Checking if message search indexes exist..."
python3 -c "
from dependencies.db import get_db
try:
    db = next(get_db())
    result = db.execute(\"SELECT indexname FROM pg_indexes WHERE tablename = 'messages' AND indexname LIKE '%search%' OR indexname LIKE '%text%'\").fetchall()
    if result:
        print('✅ Message search indexes found:')
        for idx in result:
            print(f'  - {idx[0]}')
    else:
        print('⚠️  No message search indexes found')
    db.close()
except Exception as e:
    print(f'❌ Index check failed: {e}')
"

# 5. Test API endpoints
echo "5. Testing API endpoints..."
curl -s -o /dev/null -w "API Health Check: %{http_code}\n" http://localhost:8000/health
curl -s -o /dev/null -w "API Info: %{http_code}\n" http://localhost:8000/api/v1/info

echo ""
echo "🎉 Verification complete!"
echo "Your message search functionality should now be available at:"
echo "  - GET /api/v1/messages/{match_id}/search"
echo "  - GET /api/v1/messages/search/global" 
echo "  - GET /api/v1/messages/{match_id}/message/{message_id}/context"
