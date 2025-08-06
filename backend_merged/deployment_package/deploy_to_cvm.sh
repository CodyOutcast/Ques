#!/bin/bash

# Ques Backend Deployment Script for Tencent Cloud CVM
# This script automates the deployment of the FastAPI backend

set -e  # Exit on any error

# Configuration
APP_NAME="ques-backend"
REPO_URL="https://github.com/WilliamJokuS/questrial.git"
DEPLOY_DIR="/opt/ques-backend"
DOCKER_COMPOSE_FILE="docker-compose.production.yml"
BACKUP_DIR="/opt/backups/ques-$(date +%Y%m%d_%H%M%S)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
check_root() {
    if [ "$EUID" -ne 0 ]; then
        error "Please run this script as root or with sudo"
        exit 1
    fi
}

# Install required packages
install_dependencies() {
    log "Installing system dependencies..."
    
    # Update system
    apt-get update -y
    
    # Install Docker
    if ! command -v docker &> /dev/null; then
        log "Installing Docker..."
        curl -fsSL https://get.docker.com -o get-docker.sh
        sh get-docker.sh
        systemctl start docker
        systemctl enable docker
        success "Docker installed successfully"
    else
        success "Docker already installed"
    fi
    
    # Install Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        log "Installing Docker Compose..."
        curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
        chmod +x /usr/local/bin/docker-compose
        success "Docker Compose installed successfully"
    else
        success "Docker Compose already installed"
    fi
    
    # Install other utilities
    apt-get install -y git curl wget htop nginx certbot python3-certbot-nginx
}

# Setup SSL certificates
setup_ssl() {
    log "Setting up SSL certificates..."
    
    read -p "Enter your domain name (e.g., api.yourdomain.com): " DOMAIN
    
    if [ -z "$DOMAIN" ]; then
        warning "No domain provided, skipping SSL setup"
        warning "You'll need to manually configure SSL certificates"
        return
    fi
    
    # Stop nginx if running
    systemctl stop nginx 2>/dev/null || true
    
    # Get SSL certificate
    certbot certonly --standalone -d $DOMAIN --non-interactive --agree-tos --email admin@$DOMAIN
    
    if [ $? -eq 0 ]; then
        success "SSL certificate obtained for $DOMAIN"
        
        # Update nginx configuration with domain
        sed -i "s/server_name _;/server_name $DOMAIN;/g" $DEPLOY_DIR/nginx.conf
        
        # Update SSL paths
        sed -i "s|/etc/nginx/ssl/cert.pem|/etc/letsencrypt/live/$DOMAIN/fullchain.pem|g" $DEPLOY_DIR/nginx.conf
        sed -i "s|/etc/nginx/ssl/key.pem|/etc/letsencrypt/live/$DOMAIN/privkey.pem|g" $DEPLOY_DIR/nginx.conf
    else
        warning "Failed to obtain SSL certificate, using self-signed certificate"
        # Create self-signed certificate
        mkdir -p $DEPLOY_DIR/ssl
        openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
            -keyout $DEPLOY_DIR/ssl/key.pem \
            -out $DEPLOY_DIR/ssl/cert.pem \
            -subj "/C=US/ST=State/L=City/O=Organization/CN=$DOMAIN"
    fi
}

# Create backup of current deployment
create_backup() {
    if [ -d "$DEPLOY_DIR" ]; then
        log "Creating backup of current deployment..."
        mkdir -p "$BACKUP_DIR"
        cp -r "$DEPLOY_DIR" "$BACKUP_DIR/"
        success "Backup created at $BACKUP_DIR"
    fi
}

# Clone or update repository
setup_repository() {
    log "Setting up repository..."
    
    if [ -d "$DEPLOY_DIR" ]; then
        log "Updating existing repository..."
        cd "$DEPLOY_DIR"
        git pull origin main
    else
        log "Cloning repository..."
        git clone "$REPO_URL" "$DEPLOY_DIR"
        cd "$DEPLOY_DIR/backend_merged"
    fi
    
    success "Repository setup complete"
}

# Setup environment configuration
setup_environment() {
    log "Setting up environment configuration..."
    
    if [ ! -f "$DEPLOY_DIR/backend_merged/.env.production" ]; then
        cp "$DEPLOY_DIR/backend_merged/.env.production.example" "$DEPLOY_DIR/backend_merged/.env.production"
        
        warning "Please edit .env.production with your actual configuration:"
        echo "  sudo nano $DEPLOY_DIR/backend_merged/.env.production"
        echo ""
        echo "Required configurations:"
        echo "  - Database connection (PostgreSQL)"
        echo "  - Tencent Cloud credentials"
        echo "  - Secret keys"
        echo "  - API keys (DeepSeek, etc.)"
        echo ""
        read -p "Press Enter after configuring .env.production..."
    fi
}

# Deploy with Docker Compose
deploy_application() {
    log "Deploying application with Docker Compose..."
    
    cd "$DEPLOY_DIR/backend_merged"
    
    # Stop existing containers
    docker-compose -f $DOCKER_COMPOSE_FILE down 2>/dev/null || true
    
    # Build and start containers
    docker-compose -f $DOCKER_COMPOSE_FILE build --no-cache
    docker-compose -f $DOCKER_COMPOSE_FILE up -d
    
    # Wait for application to start
    log "Waiting for application to start..."
    sleep 30
    
    # Check if application is running
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        success "Application deployed successfully!"
    else
        error "Application failed to start. Check logs:"
        echo "  docker-compose -f $DOCKER_COMPOSE_FILE logs"
        exit 1
    fi
}

# Setup monitoring and logging
setup_monitoring() {
    log "Setting up monitoring and log rotation..."
    
    # Create log rotation configuration
    cat > /etc/logrotate.d/ques-backend << EOF
$DEPLOY_DIR/backend_merged/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    sharedscripts
    postrotate
        docker-compose -f $DEPLOY_DIR/backend_merged/$DOCKER_COMPOSE_FILE restart app
    endscript
}
EOF
    
    # Setup systemd service for auto-restart
    cat > /etc/systemd/system/ques-backend.service << EOF
[Unit]
Description=Ques Backend Service
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=$DEPLOY_DIR/backend_merged
ExecStart=/usr/local/bin/docker-compose -f $DOCKER_COMPOSE_FILE up -d
ExecStop=/usr/local/bin/docker-compose -f $DOCKER_COMPOSE_FILE down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
EOF
    
    systemctl daemon-reload
    systemctl enable ques-backend.service
    
    success "Monitoring and auto-restart configured"
}

# Setup firewall
setup_firewall() {
    log "Configuring firewall..."
    
    # Install ufw if not present
    apt-get install -y ufw
    
    # Reset to defaults
    ufw --force reset
    
    # Default policies
    ufw default deny incoming
    ufw default allow outgoing
    
    # Allow SSH
    ufw allow ssh
    
    # Allow HTTP and HTTPS
    ufw allow 80/tcp
    ufw allow 443/tcp
    
    # Enable firewall
    ufw --force enable
    
    success "Firewall configured"
}

# Main deployment function
main() {
    log "Starting Ques Backend deployment to Tencent Cloud CVM..."
    
    check_root
    install_dependencies
    create_backup
    setup_repository
    setup_environment
    setup_ssl
    deploy_application
    setup_monitoring
    setup_firewall
    
    success "🎉 Deployment completed successfully!"
    echo ""
    echo "Your Ques Backend is now running at:"
    echo "  Health Check: http://your-domain/health"
    echo "  API Documentation: http://your-domain/docs"
    echo ""
    echo "Useful commands:"
    echo "  View logs: docker-compose -f $DEPLOY_DIR/backend_merged/$DOCKER_COMPOSE_FILE logs -f"
    echo "  Restart: systemctl restart ques-backend"
    echo "  Update: cd $DEPLOY_DIR && git pull && systemctl restart ques-backend"
    echo ""
    warning "Don't forget to:"
    echo "  1. Configure your database connection in .env.production"
    echo "  2. Set up your domain DNS to point to this server"
    echo "  3. Configure Tencent Cloud services (SMS, Email, COS, etc.)"
}

# Run main function
main "$@"