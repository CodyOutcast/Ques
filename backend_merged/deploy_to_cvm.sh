#!/bin/bash
# deploy_to_cvm.sh - Deploy backend to Tencent CVM
# Run this script from Git Bash on Windows

set -e  # Exit on any error

# Configuration
LOCAL_PATH="/d/Ques/backend_merged/"
REMOTE_USER="ubuntu"
REMOTE_HOST="134.175.220.232"
REMOTE_PATH="/home/ubuntu/backend_merged/"
SSH_KEY="C:/Users/WilliamJonathan/.ssh/ques_cvm_key.pem"

echo "🚀 Deploying Ques Backend to CVM..."
echo "=================================="
echo "Local:  $LOCAL_PATH"
echo "Remote: $REMOTE_USER@$REMOTE_HOST:$REMOTE_PATH"
echo "SSH Key: $SSH_KEY"
echo ""

# Test SSH connection first
echo "🔐 Testing SSH connection..."
if ssh -i "$SSH_KEY" -o ConnectTimeout=10 "$REMOTE_USER@$REMOTE_HOST" "echo 'SSH connection successful'"; then
    echo "✅ SSH connection working"
else
    echo "❌ SSH connection failed"
    exit 1
fi

# Check if remote directory exists
echo "📁 Checking remote directory..."
ssh -i "$SSH_KEY" "$REMOTE_USER@$REMOTE_HOST" "mkdir -p $REMOTE_PATH && echo 'Remote directory ready'"

# Dry run first
echo "📋 Dry run - showing what will be updated:"
rsync -avz --dry-run --delete \
  --exclude '__pycache__' \
  --exclude '*.pyc' \
  --exclude '.git' \
  --exclude 'logs/' \
  --exclude '*.log' \
  --exclude '.env' \
  --exclude 'test_*.py' \
  --exclude '*.pem' \
  --exclude 'venv/' \
  --exclude '.vscode/' \
  -e "ssh -i $SSH_KEY" \
  "$LOCAL_PATH" \
  "$REMOTE_USER@$REMOTE_HOST:$REMOTE_PATH"

echo ""
read -p "🤔 Continue with actual sync? (y/n): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "✅ Syncing files..."
    
    rsync -avz --delete --progress \
      --exclude '__pycache__' \
      --exclude '*.pyc' \
      --exclude '.git' \
      --exclude 'logs/' \
      --exclude '*.log' \
      --exclude '.env' \
      --exclude 'test_*.py' \
      --exclude '*.pem' \
      --exclude 'venv/' \
      --exclude '.vscode/' \
      -e "ssh -i $SSH_KEY" \
      "$LOCAL_PATH" \
      "$REMOTE_USER@$REMOTE_HOST:$REMOTE_PATH"
    
    echo "🎉 Files synchronized successfully!"
    
    # Optional: Install dependencies
    echo ""
    read -p "📦 Install Python dependencies? (y/n): " -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "📦 Installing dependencies..."
        ssh -i "$SSH_KEY" "$REMOTE_USER@$REMOTE_HOST" "cd $REMOTE_PATH && pip3 install -r requirements.txt"
        echo "✅ Dependencies installed!"
    fi
    
    # Optional: Restart services
    echo ""
    read -p "🔄 Restart backend service? (y/n): " -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🔄 Restarting services..."
        ssh -i "$SSH_KEY" "$REMOTE_USER@$REMOTE_HOST" "cd $REMOTE_PATH && pkill -f 'uvicorn\|python.*main.py' || true && nohup python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 > app.log 2>&1 &"
        echo "✅ Service restarted!"
        
        # Check if service is running
        sleep 2
        ssh -i "$SSH_KEY" "$REMOTE_USER@$REMOTE_HOST" "ps aux | grep -v grep | grep -E 'uvicorn|main:app' || echo 'Service not found in process list'"
    fi
    
    echo ""
    echo "🎯 Deployment completed successfully!"
    echo "🌐 Your backend should be accessible at: http://134.175.220.232:8000"
    echo "📋 Check logs with: ssh -i \"$SSH_KEY\" $REMOTE_USER@$REMOTE_HOST \"tail -f $REMOTE_PATH/app.log\""
    
else
    echo "❌ Deployment cancelled"
fi
