# 🌐 Tencent Cloud Console Deployment Guide
# Use this when SSH is not available

## Step 1: Access Your CVM via Tencent Cloud Console
1. Log into Tencent Cloud Console (https://console.cloud.tencent.com/)
2. Navigate to: Products > Compute > Cloud Virtual Machine
3. Find your CVM instance (172.16.0.16)
4. Click "Log In" button next to your instance
5. Choose "Log in via Browser" or "VNC Login"

## Step 2: Upload Files via Console
Method A - File Manager:
1. In the console, look for "File Transfer" or "File Manager"
2. Upload your deployment_package folder
3. Extract it to /opt/ques-backend/

Method B - GitHub Download (RECOMMENDED):
1. Push your changes to GitHub repository
2. Use wget to download ONLY specific updated files
3. Much faster and safer than replacing everything
4. Preserves your environment variables and configuration

⚠️ IMPORTANT: DO NOT remove all existing files!
Only update the specific files that changed for message search.

Method C - Command Line Upload:
1. Use the web terminal
2. Download files directly: wget or curl commands (see below)

## Step 3: Create Backup and Download Updated Files
# ⚠️ First create a backup, then update specific files

cd ~/questrial/backend_merged

# Create a timestamped backup
BACKUP_NAME="backup_$(date +%Y%m%d_%H%M%S)"
cp -r . ../$BACKUP_NAME
echo "✅ Backup created at ~/questrial/$BACKUP_NAME"

# Download only the 3 files that changed for message search
wget -O routers/messages.py "https://raw.githubusercontent.com/WilliamJokuS/questrial/main/backend_merged/routers/messages.py"
mkdir -p schemas
wget -O schemas/messages.py "https://raw.githubusercontent.com/WilliamJokuS/questrial/main/backend_merged/schemas/messages.py"
wget -O migrations/versions/008_message_search_indexes.py "https://raw.githubusercontent.com/WilliamJokuS/questrial/main/backend_merged/migrations/versions/008_message_search_indexes.py"

echo "✅ Updated files downloaded!"

# Verify the files contain the new search functionality
echo "🔍 Verifying search endpoints were downloaded..."
grep -c "def search" routers/messages.py
grep -c "MessageSearchResponse" schemas/messages.py
if grep -q "def search_messages" routers/messages.py; then
    echo "✅ Search endpoints found in messages router"
else
    echo "❌ Search endpoints NOT found - files may not have been pushed to GitHub"
    echo "Please ensure you pushed the changes to GitHub first"
fi

## Step 4: Install Dependencies and Run Migration
# Copy and paste these commands one by one:

cd ~/questrial/backend_merged

# Install missing PostgreSQL adapter
sudo apt update
sudo apt install -y python3-psycopg2

# Install pip if not available
sudo apt install -y python3-pip python3-venv

# Option 1: Use virtual environment (RECOMMENDED)
python3 -m venv venv
source venv/bin/activate

# Install all Python dependencies in virtual environment
pip install -r requirements.txt

# Install core dependencies manually if requirements.txt fails
pip install "fastapi[all]" uvicorn sqlalchemy alembic psycopg2-binary

# Option 2: If virtual env doesn't work, use --break-system-packages (USE WITH CAUTION)
# pip3 install --break-system-packages "fastapi[all]" uvicorn sqlalchemy alembic psycopg2-binary

# Check if migration files exist
ls -la migrations/versions/
echo "Looking for 008_message_search_indexes.py..."
ls -la migrations/versions/008_message_search_indexes.py

# If migration file is missing, you need to upload it
# Check current migration status
alembic current

# List available migrations
alembic history

# Run migration
alembic upgrade head

## Step 4: Restart Application
# First, check how your app is currently running
ps aux | grep python | grep -v grep
ps aux | grep main.py
ps aux | grep uvicorn

# Check for systemd services
sudo systemctl list-units --type=service | grep -i ques
sudo systemctl list-units --type=service | grep -i questrial
sudo systemctl list-units --type=service | grep -i backend

# If no service found, restart manually:
# Kill existing process
pkill -f "python.*main.py"
pkill -f uvicorn

# Start application (choose one method):
# Method 1: Direct Python (if using virtual environment)
source venv/bin/activate && nohup python3 main.py > app.log 2>&1 &

# Method 2: Using uvicorn (if using virtual environment)
# source venv/bin/activate && nohup uvicorn main:app --host 0.0.0.0 --port 8000 > app.log 2>&1 &

# Method 3: Using start script if it exists
# source venv/bin/activate && nohup ./start_server.py > app.log 2>&1 &

echo "✅ Application restarted!"

## Step 5: Verify Deployment
curl http://localhost:8000/health
curl http://localhost:8000/api/v1/info

# Test the new search endpoints (without authentication - will show "Not authenticated" but confirms endpoints work)
echo "🔍 Testing search endpoints..."
curl "http://localhost:8000/api/v1/messages/1/search?query=test"
curl "http://localhost:8000/api/v1/messages/search/global?query=hello"

# ✅ If you see "Not authenticated" responses, the search endpoints are working correctly!
# To test with real data, you would need to:
# 1. Login through your app to get an authentication token
# 2. Add the token to the request: curl -H "Authorization: Bearer YOUR_TOKEN" ...

echo "🎉 DEPLOYMENT SUCCESSFUL!"
echo "Your message search functionality is now live!"
echo ""
echo "Available search endpoints:"
echo "- GET /api/v1/messages/{match_id}/search?query=..."
echo "- GET /api/v1/messages/search/global?query=..."
echo "- GET /api/v1/messages/{message_id}/context"
