# 🎯 Targeted Update Commands for Your CVM Server
# Copy and paste these commands into your Tencent Console web terminal

# Navigate to your application directory
cd /opt/ques-backend

# Update the key files for message search functionality
echo "📥 Downloading updated message search files..."

# 1. Update messages router (main changes)
wget -O routers/messages.py "https://raw.githubusercontent.com/WilliamJokuS/questrial/main/backend_merged/routers/messages.py"

# 2. Download new message schemas
mkdir -p schemas
wget -O schemas/messages.py "https://raw.githubusercontent.com/WilliamJokuS/questrial/main/backend_merged/schemas/messages.py"

# 3. Download the migration file
wget -O migrations/versions/008_message_search_indexes.py "https://raw.githubusercontent.com/WilliamJokuS/questrial/main/backend_merged/migrations/versions/008_message_search_indexes.py"

# 4. Install any missing dependencies
pip3 install -r requirements.txt

# 5. Run the migration
echo "🔄 Running database migration..."
alembic upgrade head

# 6. Restart the application
echo "🔄 Restarting application..."
sudo systemctl restart ques-backend

# 7. Check status
sudo systemctl status ques-backend

echo "✅ Message search feature deployed!"
echo "🔍 New endpoints available:"
echo "  - GET /api/v1/messages/{match_id}/search"
echo "  - GET /api/v1/messages/search/global"
echo "  - GET /api/v1/messages/{match_id}/message/{message_id}/context"
