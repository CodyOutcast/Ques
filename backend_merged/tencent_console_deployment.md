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
2. Use wget to download specific updated files
3. Much faster than uploading many files

Method C - Command Line Upload:
1. Use the web terminal
2. Download files directly: wget or curl commands (see below)

## Step 3: Install Dependencies and Run Migration
# Copy and paste these commands one by one:

cd /opt/ques-backend

# Install missing PostgreSQL adapter
sudo apt update
sudo apt install -y python3-psycopg2
# OR if using pip:
pip3 install psycopg2-binary

# Install all Python dependencies
pip3 install -r requirements.txt

# Check if migration files exist
ls -la migrations/versions/
echo "Looking for 008_message_search_indexes.py..."
ls -la migrations/versions/008_message_search_indexes.py

# If migration file is missing, you need to upload it
# Check current migration status
alembic current

# List available migrations
alembic history

# Now run migration (only if file exists)
alembic upgrade head
sudo systemctl restart ques-backend
sudo systemctl status ques-backend

## Step 4: Verify Deployment
curl http://localhost:8000/health
curl http://localhost:8000/api/v1/info
