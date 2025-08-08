# 📁 GitHub Selective Update Commands
# Run these on your CVM server to update only the changed files

# Replace YOUR_GITHUB_USERNAME and YOUR_REPO_NAME with your actual GitHub info
GITHUB_USER="YOUR_GITHUB_USERNAME"
REPO_NAME="YOUR_REPO_NAME"
BASE_URL="https://raw.githubusercontent.com/$GITHUB_USER/$REPO_NAME/main"

cd /opt/ques-backend

echo "📥 Downloading updated files for message search feature..."

# 1. Download updated messages router
wget -O routers/messages.py "$BASE_URL/routers/messages.py"

# 2. Download new message schemas
wget -O schemas/messages.py "$BASE_URL/schemas/messages.py"

# 3. Download the new migration file
wget -O migrations/versions/008_message_search_indexes.py "$BASE_URL/migrations/versions/008_message_search_indexes.py"

# 4. Update main.py if it changed
wget -O main.py "$BASE_URL/main.py"

# 5. Update requirements.txt if needed
wget -O requirements.txt "$BASE_URL/requirements.txt"

echo "✅ Updated files downloaded!"
echo "Now installing dependencies and running migration..."

# Install dependencies and run migration
pip3 install -r requirements.txt
alembic upgrade head
sudo systemctl restart ques-backend

echo "🎉 Message search feature deployed!"
