#!/bin/bash

# Production Deployment Script for CVM
# This script deploys the clean, production-ready backend to Tencent CVM
# Usage: bash deploy_production_to_cvm.sh

set -e  # Exit on any error

# Configuration
CVM_HOST="134.175.220.232"
CVM_USER="root"
SSH_KEY="C:/Users/WilliamJonathan/.ssh/ques_cvm_key.pem"
LOCAL_DIR="."
REMOTE_DIR="/opt/questrial_backend"
REMOTE_BACKUP_DIR="/opt/questrial_backend_backup"
SERVICE_NAME="questrial_backend"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Production Deployment to CVM${NC}"
echo "=================================================="
echo "Host: $CVM_HOST"
echo "User: $CVM_USER"
echo "Remote Directory: $REMOTE_DIR"
echo

# Function to run remote commands
run_remote() {
    ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "$CVM_USER@$CVM_HOST" "$1"
}

# Function to copy files to remote
copy_to_remote() {
    rsync -avz --progress -e "ssh -i '$SSH_KEY' -o StrictHostKeyChecking=no" "$1" "$CVM_USER@$CVM_HOST:$2"
}

# Step 1: Pre-deployment validation
echo -e "${YELLOW}📋 Step 1: Pre-deployment Validation${NC}"

# Check if SSH key exists
if [ ! -f "$SSH_KEY" ]; then
    echo -e "${RED}❌ SSH key not found: $SSH_KEY${NC}"
    exit 1
fi

# Check if production summary exists (indicates clean codebase)
if [ ! -f "PRODUCTION_SUMMARY.md" ]; then
    echo -e "${RED}❌ PRODUCTION_SUMMARY.md not found. Please run cleanup first.${NC}"
    echo "Run: python cleanup_for_production.py --force"
    exit 1
fi

# Test SSH connection
echo "Testing SSH connection..."
if run_remote "echo 'SSH connection successful'"; then
    echo -e "${GREEN}✅ SSH connection verified${NC}"
else
    echo -e "${RED}❌ SSH connection failed${NC}"
    exit 1
fi

echo

# Step 2: Backup existing deployment
echo -e "${YELLOW}📦 Step 2: Backup Existing Deployment${NC}"

echo "Creating backup of existing deployment..."
run_remote "
    if [ -d '$REMOTE_DIR' ]; then
        sudo rm -rf '$REMOTE_BACKUP_DIR'
        sudo cp -r '$REMOTE_DIR' '$REMOTE_BACKUP_DIR'
        echo 'Backup created at $REMOTE_BACKUP_DIR'
    else
        echo 'No existing deployment found, skipping backup'
    fi
"

echo

# Step 3: Prepare remote environment
echo -e "${YELLOW}🛠️  Step 3: Prepare Remote Environment${NC}"

echo "Setting up remote directories and environment..."
run_remote "
    # Create application directory
    sudo mkdir -p '$REMOTE_DIR'
    sudo mkdir -p '$REMOTE_DIR/logs'
    
    # Update system packages
    sudo apt update
    
    # Install Python 3.9+ if not already installed
    if ! command -v python3.9 &> /dev/null; then
        sudo apt install -y python3.9 python3.9-venv python3.9-dev python3-pip
    fi
    
    # Install system dependencies
    sudo apt install -y build-essential libssl-dev libffi-dev python3-dev
    
    # Install nginx if not already installed
    if ! command -v nginx &> /dev/null; then
        sudo apt install -y nginx
    fi
    
    # Install supervisor for process management
    if ! command -v supervisorctl &> /dev/null; then
        sudo apt install -y supervisor
    fi
    
    echo 'Remote environment prepared'
"

echo

# Step 4: Deploy application files
echo -e "${YELLOW}📁 Step 4: Deploy Application Files${NC}"

echo "Copying application files to remote server..."

# Create a list of files to exclude from deployment
cat > .rsync_exclude << EOF
__pycache__/
*.pyc
*.pyo
*.pyd
.pytest_cache/
.vscode/
.idea/
*.swp
*~
.DS_Store
*.log
*.tmp
*.bak
*.backup
.git/
.gitignore
node_modules/
test_*
*_test.py
debug_*
temp_*
cleanup_for_production.py
validate_production_api.py
deploy_production_to_cvm.sh
.rsync_exclude
EOF

# Copy files using rsync with exclusions
copy_to_remote "--exclude-from=.rsync_exclude ." "$REMOTE_DIR/"

# Remove temporary exclude file
rm .rsync_exclude

echo -e "${GREEN}✅ Application files deployed${NC}"

echo

# Step 5: Set up Python environment
echo -e "${YELLOW}🐍 Step 5: Setup Python Environment${NC}"

echo "Creating Python virtual environment and installing dependencies..."
run_remote "
    cd '$REMOTE_DIR'
    
    # Remove old virtual environment if exists
    sudo rm -rf venv
    
    # Create new virtual environment
    python3.9 -m venv venv
    
    # Activate virtual environment and install dependencies
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    
    # Set proper ownership
    sudo chown -R www-data:www-data '$REMOTE_DIR'
    sudo chmod -R 755 '$REMOTE_DIR'
    
    echo 'Python environment setup complete'
"

echo

# Step 6: Configure Nginx
echo -e "${YELLOW}🌐 Step 6: Configure Nginx${NC}"

echo "Configuring Nginx..."
run_remote "
    # Copy nginx configuration
    sudo cp '$REMOTE_DIR/nginx.conf' /etc/nginx/sites-available/questrial_backend
    
    # Enable the site
    sudo ln -sf /etc/nginx/sites-available/questrial_backend /etc/nginx/sites-enabled/
    
    # Remove default nginx site
    sudo rm -f /etc/nginx/sites-enabled/default
    
    # Test nginx configuration
    sudo nginx -t
    
    echo 'Nginx configured'
"

echo

# Step 7: Configure Supervisor (Process Manager)
echo -e "${YELLOW}⚙️  Step 7: Configure Process Management${NC}"

echo "Configuring Supervisor..."
run_remote "
    # Create supervisor configuration
    sudo tee /etc/supervisor/conf.d/questrial_backend.conf > /dev/null << 'EOL'
[program:questrial_backend]
command=$REMOTE_DIR/venv/bin/python -m uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
directory=$REMOTE_DIR
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=$REMOTE_DIR/logs/supervisor.log
environment=PATH=\"$REMOTE_DIR/venv/bin\"
EOL

    echo 'Supervisor configured'
"

echo

# Step 8: Set up environment variables
echo -e "${YELLOW}🔐 Step 8: Configure Environment Variables${NC}"

echo "Setting up environment variables..."
run_remote "
    # Create production environment file
    sudo tee '$REMOTE_DIR/.env' > /dev/null << 'EOL'
# Production Environment Configuration
ENVIRONMENT=production
DEBUG=false
SECRET_KEY=your_production_secret_key_here
DATABASE_URL=sqlite:///./questrial_production.db
CORS_ORIGINS=[\"http://134.175.220.232\", \"https://your-domain.com\"]

# API Configuration
API_VERSION=1.0.0
MAX_CONNECTIONS_COUNT=10
MIN_CONNECTIONS_COUNT=10

# Security
JWT_SECRET_KEY=your_jwt_secret_here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Feature Flags
ENABLE_VECTOR_RECOMMENDATIONS=true
ENABLE_AI_MATCHING=true
ENABLE_PAYMENTS=true

# Logging
LOG_LEVEL=INFO
EOL

    # Set proper permissions
    sudo chown www-data:www-data '$REMOTE_DIR/.env'
    sudo chmod 600 '$REMOTE_DIR/.env'
    
    echo 'Environment variables configured'
    echo 'IMPORTANT: Update .env file with your actual production values!'
"

echo

# Step 9: Database setup
echo -e "${YELLOW}🗄️  Step 9: Database Setup${NC}"

echo "Setting up database..."
run_remote "
    cd '$REMOTE_DIR'
    source venv/bin/activate
    
    # Run database migrations
    if [ -f 'alembic.ini' ]; then
        alembic upgrade head
        echo 'Database migrations applied'
    else
        echo 'No alembic.ini found, skipping migrations'
    fi
"

echo

# Step 10: Start services
echo -e "${YELLOW}🚀 Step 10: Start Services${NC}"

echo "Starting services..."
run_remote "
    # Reload supervisor configuration
    sudo supervisorctl reread
    sudo supervisorctl update
    
    # Start the application
    sudo supervisorctl start questrial_backend
    
    # Restart nginx
    sudo systemctl restart nginx
    sudo systemctl enable nginx
    
    # Enable supervisor to start on boot
    sudo systemctl enable supervisor
    
    echo 'Services started'
"

echo

# Step 11: Deployment verification
echo -e "${YELLOW}✅ Step 11: Deployment Verification${NC}"

echo "Verifying deployment..."

# Check if application is running
run_remote "
    # Check supervisor status
    sudo supervisorctl status questrial_backend
    
    # Check nginx status
    sudo systemctl status nginx --no-pager -l
    
    # Test API endpoint
    sleep 5  # Wait for app to start
    curl -f http://localhost:8000/health || echo 'Health check failed'
"

echo

# Step 12: Deployment summary
echo -e "${GREEN}🎉 Deployment Complete!${NC}"
echo "=================================================="
echo "Server: http://$CVM_HOST"
echo "Health Check: http://$CVM_HOST/health"
echo "API Documentation: http://$CVM_HOST/docs"
echo
echo -e "${YELLOW}📝 Post-Deployment Tasks:${NC}"
echo "1. Update .env file with production values:"
echo "   ssh -i '$SSH_KEY' $CVM_USER@$CVM_HOST"
echo "   sudo nano $REMOTE_DIR/.env"
echo
echo "2. Configure domain name (optional):"
echo "   - Point your domain to $CVM_HOST"
echo "   - Update CORS_ORIGINS in .env"
echo "   - Configure SSL certificate"
echo
echo "3. Monitor logs:"
echo "   sudo supervisorctl tail -f questrial_backend"
echo
echo "4. Manage services:"
echo "   sudo supervisorctl restart questrial_backend"
echo "   sudo systemctl restart nginx"
echo
echo -e "${GREEN}✅ Production deployment successful!${NC}"

# Final health check
echo
echo -e "${BLUE}🔍 Final Health Check${NC}"
echo "Testing deployed API..."

if curl -f -s http://$CVM_HOST/health > /dev/null; then
    echo -e "${GREEN}✅ API is responding successfully!${NC}"
    echo "🌐 Access your API at: http://$CVM_HOST"
else
    echo -e "${YELLOW}⚠️  API health check failed. Check logs:${NC}"
    echo "ssh -i '$SSH_KEY' $CVM_USER@$CVM_HOST 'sudo supervisorctl tail questrial_backend'"
fi
