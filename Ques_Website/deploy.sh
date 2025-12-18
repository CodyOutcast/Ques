#!/bin/bash

##############################################################################
# Ques Website Deployment Script
# Deploys the website to Nginx on a CVM server
##############################################################################

set -e  # Exit on any error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration variables
PROJECT_NAME="ques_website"
BUILD_DIR="dist"
NGINX_ROOT="/var/www/ques"
NGINX_CONFIG="/etc/nginx/sites-available/ques"
NGINX_ENABLED="/etc/nginx/sites-enabled/ques"
DOMAIN="quesx.com"  # Change this to your domain

# Function to print colored messages
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if running as root
check_root() {
    if [ "$EUID" -ne 0 ]; then
        print_error "This script must be run as root (use sudo)"
        exit 1
    fi
}

# Function to install Node.js
install_node() {
    print_info "Installing Node.js 20.x LTS..."
    
    # Install curl if not present
    if ! command -v curl &> /dev/null; then
        apt-get update
        apt-get install -y curl
    fi
    
    # Add NodeSource repository
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
    
    # Install Node.js
    apt-get install -y nodejs
    
    print_success "Node.js $(node --version) installed successfully"
}

# Function to check if Node.js is installed
check_node() {
    if ! command -v node &> /dev/null; then
        print_warning "Node.js is not installed. Installing Node.js 20.x LTS..."
        install_node
    else
        NODE_VERSION=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
        if [ "$NODE_VERSION" -lt 18 ]; then
            print_warning "Node.js version must be 18 or higher. Current version: $(node --version)"
            print_info "Upgrading Node.js..."
            install_node
        else
            print_success "Node.js $(node --version) detected"
        fi
    fi
}

# Function to check if npm is installed
check_npm() {
    if ! command -v npm &> /dev/null; then
        print_warning "npm is not installed. Installing npm..."
        apt-get install -y npm
    fi
    print_success "npm $(npm --version) detected"
}

# Function to check if Nginx is installed
check_nginx() {
    if ! command -v nginx &> /dev/null; then
        print_warning "Nginx is not installed. Installing Nginx..."
        apt-get update
        apt-get install -y nginx
        systemctl enable nginx
        print_success "Nginx installed successfully"
    else
        print_success "Nginx $(nginx -v 2>&1 | cut -d'/' -f2) detected"
    fi
}

# Function to install dependencies
install_dependencies() {
    print_info "Installing npm dependencies..."
    npm install
    print_success "Dependencies installed"
}

# Function to build the project
build_project() {
    print_info "Building the project..."
    
    # Clean old build
    if [ -d "$BUILD_DIR" ]; then
        print_info "Cleaning old build directory..."
        rm -rf "$BUILD_DIR"
    fi
    
    # Build the project
    npm run build
    
    # Verify build directory exists
    if [ ! -d "$BUILD_DIR" ]; then
        print_error "Build failed. $BUILD_DIR directory not found."
        exit 1
    fi
    
    # Verify index.html exists
    if [ ! -f "$BUILD_DIR/index.html" ]; then
        print_error "Build failed. index.html not found in $BUILD_DIR."
        print_error "Build directory contents:"
        ls -la "$BUILD_DIR"
        exit 1
    fi
    
    # Show build contents
    print_info "Build completed. Contents:"
    ls -lh "$BUILD_DIR" | head -10
    
    print_success "Project built successfully"
}

# Function to create Nginx directory
create_nginx_directory() {
    print_info "Creating Nginx web directory..."
    
    if [ -d "$NGINX_ROOT" ]; then
        print_warning "Directory $NGINX_ROOT already exists. Creating backup..."
        mv "$NGINX_ROOT" "${NGINX_ROOT}.backup.$(date +%Y%m%d%H%M%S)"
    fi
    
    mkdir -p "$NGINX_ROOT"
    print_success "Nginx directory created"
}

# Function to copy build files
copy_build_files() {
    print_info "Copying build files to Nginx directory..."
    
    # Copy files
    cp -r "$BUILD_DIR"/* "$NGINX_ROOT/"
    
    # Verify index.html was copied
    if [ ! -f "$NGINX_ROOT/index.html" ]; then
        print_error "Failed to copy index.html to $NGINX_ROOT"
        exit 1
    fi
    
    # Set correct permissions
    chown -R www-data:www-data "$NGINX_ROOT"
    chmod -R 755 "$NGINX_ROOT"
    
    # Verify permissions
    print_info "Files in $NGINX_ROOT:"
    ls -lh "$NGINX_ROOT" | head -10
    
    print_success "Build files copied with correct permissions"
}

# Function to remove conflicting configurations
remove_conflicting_configs() {
    print_info "Checking for conflicting Nginx configurations..."
    
    # First, check all enabled sites that might have our domain
    print_info "Checking /etc/nginx/sites-enabled/ for conflicts..."
    for enabled_site in /etc/nginx/sites-enabled/*; do
        if [ -f "$enabled_site" ] || [ -L "$enabled_site" ]; then
            site_name=$(basename "$enabled_site")
            
            # Skip our own config
            if [ "$site_name" = "ques" ]; then
                continue
            fi
            
            # Check if this site uses our domain
            if [ -f "$enabled_site" ] && grep -q "server_name.*$DOMAIN" "$enabled_site" 2>/dev/null; then
                print_warning "Found conflicting enabled site: $site_name"
                rm "$enabled_site"
                print_success "Removed: $site_name from sites-enabled"
            elif [ -L "$enabled_site" ]; then
                # It's a symlink, check the target
                target=$(readlink "$enabled_site")
                if [ -f "$target" ] && grep -q "server_name.*$DOMAIN" "$target" 2>/dev/null; then
                    print_warning "Found conflicting enabled site: $site_name (symlink)"
                    rm "$enabled_site"
                    print_success "Removed symlink: $site_name from sites-enabled"
                fi
            fi
        fi
    done
    
    # Check sites-available for domain conflicts (except our config)
    print_info "Checking /etc/nginx/sites-available/ for conflicts..."
    if [ -d "/etc/nginx/sites-available" ]; then
        for config in /etc/nginx/sites-available/*; do
            if [ -f "$config" ]; then
                config_name=$(basename "$config")
                
                # Skip our own config and backup files
                if [ "$config_name" = "ques" ] || [[ "$config_name" == *.backup.* ]]; then
                    continue
                fi
                
                # Check if uses our domain
                if grep -q "server_name.*$DOMAIN" "$config" 2>/dev/null; then
                    print_warning "Found conflicting config in sites-available: $config_name"
                    mv "$config" "${config}.backup.$(date +%Y%m%d%H%M%S)"
                    print_success "Backed up and removed: $config_name"
                fi
            fi
        done
    fi
    
    # Remove default site if it exists and is enabled
    if [ -L "/etc/nginx/sites-enabled/default" ]; then
        print_info "Disabling default Nginx site..."
        rm "/etc/nginx/sites-enabled/default"
    fi
    
    print_success "Conflict check completed"
}

# Function to create Nginx configuration
create_nginx_config() {
    print_info "Creating Nginx configuration..."
    
    # Check if SSL certificates exist
    if [ -f "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" ]; then
        print_info "SSL certificates found - creating HTTPS configuration"
        
        cat > "$NGINX_CONFIG" << 'EOF'
# Redirect www to non-www (HTTP)
server {
    listen 80;
    listen [::]:80;
    server_name www.your-domain.com;
    
    add_header X-Robots-Tag "noindex, nofollow" always;
    return 301 https://your-domain.com$request_uri;
}

# Redirect HTTP to HTTPS for non-www
server {
    listen 80;
    listen [::]:80;
    server_name your-domain.com;
    
    add_header X-Robots-Tag "noindex, nofollow" always;
    return 301 https://your-domain.com$request_uri;
}

# Main HTTPS server block
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    
    server_name your-domain.com;
    
    root /var/www/ques;
    index index.html index.htm;
    
    # SSL configuration
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;
    
    # Logging
    access_log /var/log/nginx/ques-access.log;
    error_log /var/log/nginx/ques-error.log warn;
    
    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json image/svg+xml;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    
    # Add canonical Link header
    add_header Link '<https://your-domain.com/>; rel="canonical"' always;
    
    # Redirect specific problematic paths
    location = /security-tips {
        return 301 https://your-domain.com/;
    }
    
    location ^~ /weixin/openWx/event/authorize {
        return 301 https://your-domain.com/;
    }
    
    # Cache static assets
    location ~* \.(jpg|jpeg|png|gif|ico|css|js|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # Main location - SPA fallback
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    # Deny access to hidden files
    location ~ /\. {
        deny all;
    }
}

# Redirect www to non-www for HTTPS
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name www.your-domain.com;
    
    # SSL configuration
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;
    
    add_header X-Robots-Tag "noindex, nofollow" always;
    return 301 https://your-domain.com$request_uri;
}
EOF
    else
        print_info "No SSL certificates found - creating HTTP-only configuration"
        print_info "SSL will be added by certbot in the next step"
        
        cat > "$NGINX_CONFIG" << 'EOF'
# HTTP server - will be modified by certbot to add HTTPS
server {
    listen 80;
    listen [::]:80;
    
    server_name your-domain.com www.your-domain.com;
    
    root /var/www/ques;
    index index.html index.htm;
    
    # Logging
    access_log /var/log/nginx/ques-access.log;
    error_log /var/log/nginx/ques-error.log warn;
    
    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json image/svg+xml;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    # Add canonical Link header
    add_header Link '<https://your-domain.com/>; rel="canonical"' always;
    
    # Redirect specific problematic paths
    location = /security-tips {
        return 301 https://your-domain.com/;
    }
    
    location ^~ /weixin/openWx/event/authorize {
        return 301 https://your-domain.com/;
    }
    
    # Cache static assets
    location ~* \.(jpg|jpeg|png|gif|ico|css|js|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # Main location - SPA fallback
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    # Deny access to hidden files
    location ~ /\. {
        deny all;
    }
}
EOF
    fi

    # Replace domain placeholder with actual domain
    sed -i "s/your-domain.com/$DOMAIN/g" "$NGINX_CONFIG"
    
    print_success "Nginx configuration created"
}

# Function to enable Nginx site
enable_nginx_site() {
    print_info "Enabling Nginx site..."
    
    # Remove old symlink if exists
    if [ -L "$NGINX_ENABLED" ]; then
        rm "$NGINX_ENABLED"
    fi
    
    # Create new symlink
    ln -s "$NGINX_CONFIG" "$NGINX_ENABLED"
    
    print_success "Nginx site enabled"
}

# Function to test Nginx configuration
test_nginx_config() {
    print_info "Testing Nginx configuration..."
    
    if nginx -t; then
        print_success "Nginx configuration is valid"
    else
        print_error "Nginx configuration test failed"
        exit 1
    fi
}

# Function to restart Nginx
restart_nginx() {
    print_info "Restarting Nginx..."
    systemctl restart nginx
    
    # Wait a moment for Nginx to start
    sleep 2
    
    # Verify Nginx is running
    if systemctl is-active --quiet nginx; then
        print_success "Nginx restarted and is running"
    else
        print_error "Nginx failed to start properly"
        print_error "Checking Nginx error log:"
        tail -20 /var/log/nginx/error.log
        exit 1
    fi
    
    # Show recent error log entries
    print_info "Recent Nginx error log entries:"
    tail -5 /var/log/nginx/ques-error.log 2>/dev/null || echo "No errors logged yet"
}

# Function to configure firewall
configure_firewall() {
    print_info "Configuring firewall..."
    
    if command -v ufw &> /dev/null; then
        ufw allow 'Nginx Full'
        print_success "Firewall configured for Nginx"
    else
        print_warning "ufw not found. Please configure firewall manually:"
        print_warning "  - Allow port 80 (HTTP)"
        print_warning "  - Allow port 443 (HTTPS)"
    fi
}

# Function to check DNS resolution
check_dns() {
    print_info "Checking DNS resolution for $DOMAIN..."
    
    if host "$DOMAIN" &> /dev/null; then
        print_success "DNS is configured for $DOMAIN"
        return 0
    else
        print_warning "DNS does not resolve for $DOMAIN"
        return 1
    fi
}

# Function to install SSL certificate
install_ssl() {
    print_info "Installing SSL certificate..."
    
    # Check if DNS is configured
    if ! check_dns; then
        print_warning "Skipping SSL installation. Please configure DNS first, then run:"
        print_warning "  sudo certbot --nginx -d $DOMAIN -d www.$DOMAIN"
        return 1
    fi
    
    # Install certbot if not present
    if ! command -v certbot &> /dev/null; then
        print_info "Installing certbot..."
        apt-get update
        apt-get install -y certbot python3-certbot-nginx
        print_success "Certbot installed"
    fi
    
    # Get SSL certificate
    print_info "Obtaining SSL certificate from Let's Encrypt..."
    
    # Run certbot - it will modify the Nginx config automatically
    if certbot --nginx -d "$DOMAIN" -d "www.$DOMAIN" --non-interactive --agree-tos --redirect --email "admin@$DOMAIN"; then
        print_success "SSL certificate installed successfully"
        
        # Now recreate our custom configuration with proper redirects and headers
        print_info "Updating Nginx configuration with SEO optimizations..."
        create_nginx_config_with_ssl
        
        # Test the new configuration
        if nginx -t; then
            systemctl reload nginx
            print_success "Nginx configuration updated with SEO optimizations"
        else
            print_warning "Custom configuration failed, keeping certbot defaults"
        fi
        
        print_success "HTTPS is now enabled with automatic HTTP to HTTPS redirect"
        return 0
    else
        print_warning "SSL certificate installation failed"
        print_warning "You can try manually later with:"
        print_warning "  sudo certbot --nginx -d $DOMAIN -d www.$DOMAIN"
        return 1
    fi
}

# Function to create SEO-optimized Nginx configuration after SSL is installed
create_nginx_config_with_ssl() {
    cat > "$NGINX_CONFIG" << 'EOF'
# Redirect www to non-www (HTTP)
server {
    listen 80;
    listen [::]:80;
    server_name www.your-domain.com;
    
    add_header X-Robots-Tag "noindex, nofollow" always;
    return 301 https://your-domain.com$request_uri;
}

# Redirect HTTP to HTTPS for non-www
server {
    listen 80;
    listen [::]:80;
    server_name your-domain.com;
    
    add_header X-Robots-Tag "noindex, nofollow" always;
    return 301 https://your-domain.com$request_uri;
}

# Main HTTPS server block
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    
    server_name your-domain.com;
    
    root /var/www/ques;
    index index.html index.htm;
    
    # SSL configuration
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;
    
    # Logging
    access_log /var/log/nginx/ques-access.log;
    error_log /var/log/nginx/ques-error.log warn;
    
    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json image/svg+xml;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    
    # Add canonical Link header
    add_header Link '<https://your-domain.com/>; rel="canonical"' always;
    
    # Redirect specific problematic paths
    location = /security-tips {
        return 301 https://your-domain.com/;
    }
    
    location ^~ /weixin/openWx/event/authorize {
        return 301 https://your-domain.com/;
    }
    
    # Cache static assets
    location ~* \.(jpg|jpeg|png|gif|ico|css|js|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # Main location - SPA fallback
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    # Deny access to hidden files
    location ~ /\. {
        deny all;
    }
}

# Redirect www to non-www for HTTPS
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name www.your-domain.com;
    
    # SSL configuration
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;
    
    add_header X-Robots-Tag "noindex, nofollow" always;
    return 301 https://your-domain.com$request_uri;
}
EOF

    # Replace domain placeholder with actual domain
    sed -i "s/your-domain.com/$DOMAIN/g" "$NGINX_CONFIG"
}

# Function to display final instructions
display_final_instructions() {
    local ssl_status=$1
    
    echo ""
    echo "======================================================================"
    print_success "Deployment completed successfully!"
    echo "======================================================================"
    echo ""
    
    if [ "$ssl_status" = "installed" ]; then
        echo -e "${BLUE}Website URL:${NC} https://$DOMAIN"
        echo -e "${GREEN}✓${NC} SSL certificate installed - HTTPS enabled"
    else
        echo -e "${BLUE}Website URL:${NC} http://$DOMAIN"
        echo ""
        echo -e "${YELLOW}Next Steps:${NC}"
        if [ "$ssl_status" = "no-dns" ]; then
            echo "  1. Update DNS records to point $DOMAIN to this server's IP: $(curl -s ifconfig.me)"
            echo "  2. Wait for DNS propagation (may take a few minutes to hours)"
            echo "  3. Install SSL certificate:"
        else
            echo "  1. Install SSL certificate:"
        fi
        echo "     sudo certbot --nginx -d $DOMAIN -d www.$DOMAIN"
    fi
    
    echo ""
    echo -e "${BLUE}Useful Commands:${NC}"
    echo "  - Check Nginx status: sudo systemctl status nginx"
    echo "  - View error logs: sudo tail -f /var/log/nginx/ques-error.log"
    echo "  - View access logs: sudo tail -f /var/log/nginx/ques-access.log"
    echo "  - Restart Nginx: sudo systemctl restart nginx"
    echo "  - Test Nginx config: sudo nginx -t"
    echo "  - List web files: ls -la /var/www/ques/"
    if [ "$ssl_status" = "installed" ]; then
        echo "  - Renew SSL certificate: sudo certbot renew"
        echo "  - Check SSL certificate: sudo certbot certificates"
    fi
    echo ""
    echo -e "${YELLOW}Troubleshooting:${NC}"
    echo "  If you see 500 error:"
    echo "    1. Check error log: sudo tail -50 /var/log/nginx/ques-error.log"
    echo "    2. Verify files exist: ls -la /var/www/ques/"
    echo "    3. Check permissions: sudo namei -l /var/www/ques/index.html"
    echo "    4. Test config: sudo nginx -t"
    echo ""
    echo "======================================================================"
}

# Main deployment function
main() {
    echo ""
    echo "======================================================================"
    echo "         Ques Website Deployment Script"
    echo "======================================================================"
    echo ""
    
    print_info "Starting deployment process..."
    echo ""
    
    # Check if running as root
    check_root
    
    # Check prerequisites
    check_node
    check_npm
    check_nginx
    
    echo ""
    print_info "Building application..."
    
    # Build the project (run as the user who owns the files, not root)
    if [ -n "$SUDO_USER" ]; then
        sudo -u "$SUDO_USER" bash << 'USERSCRIPT'
            npm install
            npm run build
USERSCRIPT
    else
        install_dependencies
        build_project
    fi
    
    echo ""
    print_info "Deploying to Nginx..."
    
    # Deploy to Nginx
    create_nginx_directory
    copy_build_files
    remove_conflicting_configs
    create_nginx_config
    enable_nginx_site
    test_nginx_config
    restart_nginx
    configure_firewall
    
    # Install SSL certificate
    echo ""
    print_info "Setting up SSL certificate..."
    ssl_status="no-dns"
    if install_ssl; then
        ssl_status="installed"
    elif check_dns; then
        ssl_status="failed"
    fi
    
    # Display final instructions
    display_final_instructions "$ssl_status"
}

# Run main function
main
