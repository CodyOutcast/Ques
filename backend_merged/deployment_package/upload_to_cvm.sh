#!/bin/bash
# Quick upload script for deployment package

read -p "Enter your CVM IP address: " CVM_IP
read -p "Enter your SSH user (default: root): " SSH_USER
SSH_USER=

echo "Uploading deployment package to @..."

# Create directory on remote server
ssh @ "mkdir -p /opt/ques-backend"

# Upload files
rsync -avz --progress ./ @:/opt/ques-backend/

echo "Upload complete! Now run the deployment script on your CVM:"
echo "ssh @"
echo "cd /opt/ques-backend"
echo "chmod +x deploy_to_cvm.sh"
echo "./deploy_to_cvm.sh"
