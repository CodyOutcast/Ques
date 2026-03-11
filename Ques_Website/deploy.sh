#!/bin/bash

##############################################################################
# Ques Website Deployment Script
# Deploys the website to Nginx on a CVM server
##############################################################################

set -Ee -o pipefail

trap 'echo "[ERROR] Deployment failed at line ${LINENO}: ${BASH_COMMAND}" >&2' ERR

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
STAGING_NGINX_ROOT="${NGINX_ROOT}.staging"
BACKUP_NGINX_ROOT="${NGINX_ROOT}.backup"
NGINX_CONFIG="/etc/nginx/sites-available/ques"
NGINX_ENABLED="/etc/nginx/sites-enabled/ques"
DOMAIN="quesx.com"  # Change this to your domain
TARGET_NPM_VERSION="11.11.0"

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SUDO_KEEPALIVE_PID=""
SUDO_CMD=()

if [ "$EUID" -ne 0 ]; then
    if ! command -v sudo &> /dev/null; then
        echo "[ERROR] sudo is required for privileged deployment steps" >&2
        exit 1
    fi

    echo "[INFO] Verifying sudo access..."
    if ! sudo -n true 2>/dev/null; then
        echo "[INFO] Sudo password required. Please authenticate once to continue."
        sudo -v
    fi

    (
        while true; do
            sudo -n true >/dev/null 2>&1 || exit
            sleep 50
        done
    ) &
    SUDO_KEEPALIVE_PID=$!
    SUDO_CMD=(sudo)
fi

cleanup() {
    if [ -n "${SUDO_KEEPALIVE_PID:-}" ]; then
        kill "$SUDO_KEEPALIVE_PID" >/dev/null 2>&1 || true
    fi
}

trap cleanup EXIT

cd "$PROJECT_DIR"

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

run_project_command() {
    if [ "$EUID" -eq 0 ] && [ -n "${SUDO_USER:-}" ] && [ "$SUDO_USER" != "root" ]; then
        local owner_home
        if command -v getent &> /dev/null; then
            owner_home="$(getent passwd "$SUDO_USER" 2>/dev/null | cut -d: -f6)"
        fi
        if [ -z "$owner_home" ]; then
            owner_home="$(eval echo "~$SUDO_USER")"
        fi
        sudo -u "$SUDO_USER" env "PATH=$PATH" "HOME=$owner_home" "$@"
    else
        "$@"
    fi
}

version_lt() {
    [ "$1" != "$2" ] && [ "$(printf '%s\n%s\n' "$1" "$2" | sort -V | head -n1)" = "$1" ]
}

# Function to install Node.js
install_node() {
    print_info "Installing Node.js 20.x LTS..."
    
    # Install curl if not present
    if ! command -v curl &> /dev/null; then
        "${SUDO_CMD[@]}" apt-get update
        "${SUDO_CMD[@]}" apt-get install -y curl
    fi
    
    # Add NodeSource repository
    curl -fsSL https://deb.nodesource.com/setup_20.x | "${SUDO_CMD[@]}" bash -
    
    # Install Node.js
    "${SUDO_CMD[@]}" apt-get install -y nodejs
    
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
        "${SUDO_CMD[@]}" apt-get install -y npm
    fi

    CURRENT_NPM_VERSION=$(npm --version)
    if version_lt "$CURRENT_NPM_VERSION" "$TARGET_NPM_VERSION"; then
        print_info "Upgrading npm from $CURRENT_NPM_VERSION to $TARGET_NPM_VERSION..."
        "${SUDO_CMD[@]}" npm install -g "npm@$TARGET_NPM_VERSION"
        CURRENT_NPM_VERSION=$(npm --version)
    fi

    print_success "npm $CURRENT_NPM_VERSION detected"
}

# Function to check if Nginx is installed
check_nginx() {
    if ! command -v nginx &> /dev/null; then
        print_warning "Nginx is not installed. Installing Nginx..."
        "${SUDO_CMD[@]}" apt-get update
        "${SUDO_CMD[@]}" apt-get install -y nginx
        "${SUDO_CMD[@]}" systemctl enable nginx
        print_success "Nginx installed successfully"
    else
        print_success "Nginx $(nginx -v 2>&1 | cut -d'/' -f2) detected"
    fi
}

# Function to check if host command is available (for DNS lookups)
check_host_command() {
    if ! command -v host &> /dev/null; then
        print_info "Installing dnsutils for DNS lookups..."
        "${SUDO_CMD[@]}" apt-get update
        "${SUDO_CMD[@]}" apt-get install -y dnsutils
        print_success "dnsutils installed"
    fi
}

# Function to install dependencies
install_dependencies() {
    print_info "Installing npm dependencies..."
    run_project_command npm install
    print_success "Dependencies installed"
}

# Function to build the project
build_project() {
    print_info "Building the project..."
    local live_build_dir="$BUILD_DIR"
    local staging_build_dir="${BUILD_DIR}.staging"
    local backup_build_dir="${BUILD_DIR}.old"

    rm -rf "$staging_build_dir" "$backup_build_dir"

    run_project_command env BUILD_DIR_OVERRIDE="$staging_build_dir" npm run build

    if [ ! -d "$staging_build_dir" ]; then
        print_error "Build failed. $staging_build_dir directory not found."
        exit 1
    fi

    if [ ! -f "$staging_build_dir/index.html" ]; then
        print_error "Build failed. index.html not found in $staging_build_dir."
        print_error "Build directory contents:"
        ls -la "$staging_build_dir"
        exit 1
    fi

    if grep -Eq '<div id="root">[[:space:]]*</div>' "$staging_build_dir/index.html"; then
        print_error "Prerender failed. index.html still contains an empty root container."
        exit 1
    fi

    if [ -d "$live_build_dir" ]; then
        mv "$live_build_dir" "$backup_build_dir"
    fi
    mv "$staging_build_dir" "$live_build_dir"
    rm -rf "$backup_build_dir"

    print_info "Build completed. Contents:"
    ls -lh "$live_build_dir" | head -10

    print_success "Project built and prerendered successfully"
}

# Function to create Nginx directory
create_nginx_directory() {
    print_info "Preparing staged Nginx web directory..."

    "${SUDO_CMD[@]}" rm -rf "$STAGING_NGINX_ROOT"
    "${SUDO_CMD[@]}" mkdir -p "$STAGING_NGINX_ROOT"
    print_success "Staging directory created"
}

# Function to copy build files
copy_build_files() {
    print_info "Copying build files to staged Nginx directory..."

    # Copy files, including dotfiles if present
    "${SUDO_CMD[@]}" cp -a "$BUILD_DIR"/. "$STAGING_NGINX_ROOT/"

    # Verify index.html was copied
    if [ ! -f "$STAGING_NGINX_ROOT/index.html" ]; then
        print_error "Failed to copy index.html to $STAGING_NGINX_ROOT"
        exit 1
    fi
    
    # Verify critical SEO files
    print_info "Verifying critical SEO files..."
    critical_files=("logo.png" "site.webmanifest" "robots.txt" "sitemap.xml")
    for file in "${critical_files[@]}"; do
        if [ ! -f "$STAGING_NGINX_ROOT/$file" ]; then
            print_warning "Critical SEO file missing: $file"
        else
            print_success "Found: $file"
        fi
    done
    
    # Set correct permissions
    "${SUDO_CMD[@]}" chown -R www-data:www-data "$STAGING_NGINX_ROOT"
    "${SUDO_CMD[@]}" chmod -R 755 "$STAGING_NGINX_ROOT"
    
    # Verify permissions
    print_info "Files in $STAGING_NGINX_ROOT:"
    "${SUDO_CMD[@]}" ls -lh "$STAGING_NGINX_ROOT" | head -10
    
    print_success "Build files copied with correct permissions"
}

activate_nginx_directory() {
    print_info "Activating staged Nginx web directory..."

    "${SUDO_CMD[@]}" rm -rf "$BACKUP_NGINX_ROOT"
    if [ -d "$NGINX_ROOT" ]; then
        "${SUDO_CMD[@]}" mv "$NGINX_ROOT" "$BACKUP_NGINX_ROOT"
    fi

    "${SUDO_CMD[@]}" mv "$STAGING_NGINX_ROOT" "$NGINX_ROOT"
    print_success "Staged web directory is now live"
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
                "${SUDO_CMD[@]}" rm "$enabled_site"
                print_success "Removed: $site_name from sites-enabled"
            elif [ -L "$enabled_site" ]; then
                # It's a symlink, check the target
                target=$(readlink "$enabled_site")
                if [ -f "$target" ] && grep -q "server_name.*$DOMAIN" "$target" 2>/dev/null; then
                    print_warning "Found conflicting enabled site: $site_name (symlink)"
                    "${SUDO_CMD[@]}" rm "$enabled_site"
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
                    "${SUDO_CMD[@]}" mv "$config" "${config}.backup.$(date +%Y%m%d%H%M%S)"
                    print_success "Backed up and removed: $config_name"
                fi
            fi
        done
    fi
    
    # Remove default site if it exists and is enabled
    if [ -L "/etc/nginx/sites-enabled/default" ]; then
        print_info "Disabling default Nginx site..."
        "${SUDO_CMD[@]}" rm "/etc/nginx/sites-enabled/default"
    fi
    
    print_success "Conflict check completed"
}

remove_legacy_redirect_config() {
    local legacy_available="/etc/nginx/sites-available/ques-redirects"
    local legacy_enabled="/etc/nginx/sites-enabled/ques-redirects"

    if [ -L "$legacy_enabled" ] || [ -f "$legacy_enabled" ]; then
        print_info "Removing legacy redirect-domain site from sites-enabled..."
        "${SUDO_CMD[@]}" rm -f "$legacy_enabled"
    fi

    if [ -f "$legacy_available" ]; then
        print_info "Removing legacy redirect-domain site from sites-available..."
        "${SUDO_CMD[@]}" rm -f "$legacy_available"
    fi
}

# Function to create Nginx configuration
create_nginx_config() {
    print_info "Creating Nginx configuration..."
    local temp_config
    temp_config="$(mktemp)"
    
    # Check if SSL certificates exist
    if [ -f "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" ]; then
        print_info "SSL certificates found - creating HTTPS configuration"
        
        cat > "$temp_config" << 'EOF'
# Redirect ALL HTTP traffic to canonical HTTPS URL (handles both www and non-www)
server {
    listen 80;
    listen [::]:80;
    server_name your-domain.com www.your-domain.com;
    
    # 301 permanent redirect to canonical HTTPS URL
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
    
    # Serve robots.txt and sitemap.xml with correct MIME types
    location = /robots.txt {
        add_header Content-Type text/plain;
        try_files $uri =404;
    }
    
    location = /sitemap.xml {
        add_header Content-Type application/xml;
        try_files $uri =404;
    }
    
    location = /site.webmanifest {
        add_header Content-Type application/manifest+json;
        try_files $uri =404;
    }

    error_page 404 /404.html;
    
    # Cache static assets
    location ~* \.(jpg|jpeg|png|gif|ico|css|js|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    location = / {
        add_header Cache-Control "no-cache, no-store, must-revalidate" always;
        add_header Pragma "no-cache" always;
        add_header Expires "0" always;

        try_files /index.html =404;
    }

    # Everything else should resolve to a real file or return 404.
    location / {
        add_header Cache-Control "no-cache, no-store, must-revalidate" always;
        add_header Pragma "no-cache" always;
        add_header Expires "0" always;

        try_files $uri $uri/ $uri.html =404;
    }

    location = /index.html {
        add_header Cache-Control "no-cache, no-store, must-revalidate" always;
        add_header Pragma "no-cache" always;
        add_header Expires "0" always;
    }

    location = /404.html {
        add_header Cache-Control "no-cache, no-store, must-revalidate" always;
        add_header Pragma "no-cache" always;
        add_header Expires "0" always;
    }
    
    # Deny access to hidden files
    location ~ /\. {
        deny all;
    }
}

# Redirect www HTTPS to non-www HTTPS (canonical URL)
# Uses the same certificate since Let's Encrypt issues one cert for both domains
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name www.your-domain.com;
    
    # SSL configuration - uses same cert as primary domain
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;
    
    # 301 permanent redirect to canonical URL
    return 301 https://your-domain.com$request_uri;
}
EOF
    else
        print_info "No SSL certificates found - creating HTTP-only configuration"
        print_info "SSL will be added by certbot in the next step"
        
    cat > "$temp_config" << 'EOF'
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
    
    # Serve robots.txt and sitemap.xml with correct MIME types
    location = /robots.txt {
        add_header Content-Type text/plain;
        try_files $uri =404;
    }
    
    location = /sitemap.xml {
        add_header Content-Type application/xml;
        try_files $uri =404;
    }
    
    location = /site.webmanifest {
        add_header Content-Type application/manifest+json;
        try_files $uri =404;
    }

    error_page 404 /404.html;
    
    # Cache static assets
    location ~* \.(jpg|jpeg|png|gif|ico|css|js|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    location = / {
        add_header Cache-Control "no-cache, no-store, must-revalidate" always;
        add_header Pragma "no-cache" always;
        add_header Expires "0" always;

        try_files /index.html =404;
    }

    # Everything else should resolve to a real file or return 404.
    location / {
        add_header Cache-Control "no-cache, no-store, must-revalidate" always;
        add_header Pragma "no-cache" always;
        add_header Expires "0" always;

        try_files $uri $uri/ $uri.html =404;
    }

    location = /index.html {
        add_header Cache-Control "no-cache, no-store, must-revalidate" always;
        add_header Pragma "no-cache" always;
        add_header Expires "0" always;
    }

    location = /404.html {
        add_header Cache-Control "no-cache, no-store, must-revalidate" always;
        add_header Pragma "no-cache" always;
        add_header Expires "0" always;
    }
    
    # Deny access to hidden files
    location ~ /\. {
        deny all;
    }
}
EOF
    fi

    # Replace domain placeholder with actual domain
    # Use -i '' for macOS compatibility, -i for Linux
    if [[ "$OSTYPE" == "darwin"* ]]; then
        sed -i '' "s/your-domain.com/$DOMAIN/g" "$temp_config"
    else
        sed -i "s/your-domain.com/$DOMAIN/g" "$temp_config"
    fi

    "${SUDO_CMD[@]}" cp "$temp_config" "$NGINX_CONFIG"
    rm -f "$temp_config"
    
    print_success "Nginx configuration created"
}

# Function to enable Nginx site
enable_nginx_site() {
    print_info "Enabling Nginx site..."
    
    # Remove old symlink if exists
    if [ -L "$NGINX_ENABLED" ]; then
        "${SUDO_CMD[@]}" rm "$NGINX_ENABLED"
    fi
    
    # Create new symlink
    "${SUDO_CMD[@]}" ln -sfn "$NGINX_CONFIG" "$NGINX_ENABLED"
    
    print_success "Nginx site enabled"
}

# Function to test Nginx configuration
test_nginx_config() {
    print_info "Testing Nginx configuration..."
    
    if "${SUDO_CMD[@]}" nginx -t; then
        print_success "Nginx configuration is valid"
    else
        print_error "Nginx configuration test failed"
        exit 1
    fi
}

# Function to restart Nginx
restart_nginx() {
    if "${SUDO_CMD[@]}" systemctl is-active --quiet nginx; then
        print_info "Reloading Nginx..."
        "${SUDO_CMD[@]}" systemctl reload nginx
    else
        print_info "Starting Nginx..."
        "${SUDO_CMD[@]}" systemctl start nginx
    fi

    # Wait a moment for Nginx to settle
    sleep 2

    # Verify Nginx is running
    if "${SUDO_CMD[@]}" systemctl is-active --quiet nginx; then
        print_success "Nginx is running"
    else
        print_error "Nginx failed to start properly"
        print_error "Checking Nginx error log:"
        "${SUDO_CMD[@]}" tail -20 /var/log/nginx/error.log
        exit 1
    fi
    
    # Show recent error log entries
    print_info "Recent Nginx error log entries:"
    "${SUDO_CMD[@]}" tail -5 /var/log/nginx/ques-error.log 2>/dev/null || echo "No errors logged yet"
}

# Function to configure firewall
configure_firewall() {
    print_info "Configuring firewall..."
    
    if command -v ufw &> /dev/null; then
        "${SUDO_CMD[@]}" ufw allow 'Nginx Full'
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

wait_for_certbot() {
    local certbot_lock="/var/lib/letsencrypt/.certbot.lock"
    local certbot_wait_timeout_sec="${CERTBOT_WAIT_TIMEOUT_SEC:-300}"
    local wait_start

    if [ -f "$certbot_lock" ]; then
        if pgrep -x certbot > /dev/null; then
            print_info "Another certbot process is running. Waiting for it to complete..."
            wait_start=$(date +%s)
            while pgrep -x certbot > /dev/null; do
                if [ $(( $(date +%s) - wait_start )) -ge "$certbot_wait_timeout_sec" ]; then
                    print_error "Timed out waiting for certbot after ${certbot_wait_timeout_sec}s"
                    return 1
                fi
                sleep 2
            done
            print_success "Previous certbot process completed"
        else
            print_info "Removing stale certbot lock file..."
            "${SUDO_CMD[@]}" rm -f "$certbot_lock"
            print_success "Stale certbot lock file removed"
        fi
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
        "${SUDO_CMD[@]}" apt-get update
        "${SUDO_CMD[@]}" apt-get install -y certbot python3-certbot-nginx
        print_success "Certbot installed"
    fi

    if ! wait_for_certbot; then
        return 1
    fi
    
    # Get SSL certificate
    print_info "Obtaining SSL certificate from Let's Encrypt..."
    
    # Run certbot - it will modify the Nginx config automatically
    if "${SUDO_CMD[@]}" certbot --nginx -d "$DOMAIN" -d "www.$DOMAIN" --non-interactive --agree-tos --redirect --email "admin@$DOMAIN"; then
        print_success "SSL certificate installed successfully"
        
        # Now recreate our custom configuration with proper redirects and headers
        print_info "Updating Nginx configuration with SEO optimizations..."
        create_nginx_config_with_ssl
        
        # Test the new configuration
        if "${SUDO_CMD[@]}" nginx -t; then
            "${SUDO_CMD[@]}" systemctl reload nginx
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
    local temp_config
    temp_config="$(mktemp)"

    cat > "$temp_config" << 'EOF'
# Redirect ALL HTTP traffic to canonical HTTPS URL (handles both www and non-www)
server {
    listen 80;
    listen [::]:80;
    server_name your-domain.com www.your-domain.com;
    
    # 301 permanent redirect to canonical HTTPS URL
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
    
    # Serve robots.txt and sitemap.xml with correct MIME types
    location = /robots.txt {
        add_header Content-Type text/plain;
        try_files $uri =404;
    }
    
    location = /sitemap.xml {
        add_header Content-Type application/xml;
        try_files $uri =404;
    }
    
    location = /site.webmanifest {
        add_header Content-Type application/manifest+json;
        try_files $uri =404;
    }

    error_page 404 /404.html;
    
    # Cache static assets
    location ~* \.(jpg|jpeg|png|gif|ico|css|js|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    location = / {
        add_header Cache-Control "no-cache, no-store, must-revalidate" always;
        add_header Pragma "no-cache" always;
        add_header Expires "0" always;

        try_files /index.html =404;
    }

    # Everything else should resolve to a real file or return 404.
    location / {
        add_header Cache-Control "no-cache, no-store, must-revalidate" always;
        add_header Pragma "no-cache" always;
        add_header Expires "0" always;

        try_files $uri $uri/ $uri.html =404;
    }

    location = /index.html {
        add_header Cache-Control "no-cache, no-store, must-revalidate" always;
        add_header Pragma "no-cache" always;
        add_header Expires "0" always;
    }

    location = /404.html {
        add_header Cache-Control "no-cache, no-store, must-revalidate" always;
        add_header Pragma "no-cache" always;
        add_header Expires "0" always;
    }
    
    # Deny access to hidden files
    location ~ /\. {
        deny all;
    }
}

# Redirect www HTTPS to non-www HTTPS (canonical URL)
# Uses the same certificate since Let's Encrypt issues one cert for both domains
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name www.your-domain.com;
    
    # SSL configuration - uses same cert as primary domain
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;
    
    # 301 permanent redirect to canonical URL
    return 301 https://your-domain.com$request_uri;
}
EOF

    # Replace domain placeholder with actual domain
    # Use -i '' for macOS compatibility, -i for Linux
    if [[ "$OSTYPE" == "darwin"* ]]; then
        sed -i '' "s/your-domain.com/$DOMAIN/g" "$temp_config"
    else
        sed -i "s/your-domain.com/$DOMAIN/g" "$temp_config"
    fi

    "${SUDO_CMD[@]}" cp "$temp_config" "$NGINX_CONFIG"
    rm -f "$temp_config"
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
    echo "  - Reload Nginx: sudo systemctl reload nginx"
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

    print_info "Working directory: $PROJECT_DIR"
    
    # Check prerequisites
    check_node
    check_npm
    check_nginx
    check_host_command
    
    echo ""
    print_info "Building application..."

    install_dependencies
    build_project
    
    echo ""
    print_info "Deploying to Nginx..."
    
    # Deploy to Nginx
    create_nginx_directory
    copy_build_files
    remove_conflicting_configs
    remove_legacy_redirect_config
    create_nginx_config
    enable_nginx_site
    test_nginx_config
    activate_nginx_directory
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
    
    # Test and reload Nginx with all configurations
    test_nginx_config
    restart_nginx
    
    # Display final instructions
    display_final_instructions "$ssl_status"
}

# Run main function
main
