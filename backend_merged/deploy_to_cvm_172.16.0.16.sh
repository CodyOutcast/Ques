#!/bin/bash
# Deployment script for CVM 172.16.0.16

CVM_IP="172.16.0.16"
SSH_USER="root"

echo "🚀 Uploading to $SSH_USER@$CVM_IP..."

# Upload files using rsync
rsync -avz --progress deployment_package/ $SSH_USER@$CVM_IP:/opt/ques-backend/

echo "✅ Upload complete!"
echo ""
echo "📋 Next, run these commands on your CVM server:"
echo "ssh $SSH_USER@$CVM_IP"
echo "cd /opt/ques-backend"
echo "alembic upgrade head"
echo "sudo systemctl restart ques-backend"
