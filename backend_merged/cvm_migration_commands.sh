# 🔧 CVM Server Migration Commands
# Run these commands on your CVM server (172.16.0.16)

# 1. Navigate to your application directory
cd /opt/ques-backend

# 2. Check current migration status
alembic current

# 3. Run the new migration (adds message search indexes)
alembic upgrade head

# 4. Verify migration was successful
alembic current

# 5. Restart your application
sudo systemctl restart ques-backend

# 6. Check if the application is running
sudo systemctl status ques-backend

# 7. Test the new message search endpoints
curl -X GET "http://localhost:8000/api/v1/info" | python3 -m json.tool

# Optional: Check application logs
tail -f /opt/ques-backend/logs/app.log

# Optional: Test message search (replace with real token)
# curl -X GET "http://localhost:8000/api/v1/messages/search/global?query=hello" \
#   -H "Authorization: Bearer YOUR_JWT_TOKEN"
