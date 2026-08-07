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
BUILD_DIR="dist"
NGINX_ROOT="/var/www/ques"
STAGING_NGINX_ROOT="${NGINX_ROOT}.staging"
BACKUP_NGINX_ROOT="${NGINX_ROOT}.backup"
NGINX_CONFIG="/etc/nginx/sites-available/ques"
NGINX_ENABLED="/etc/nginx/sites-enabled/ques"
DOMAIN="quesx.com"  # Change this to your domain
TARGET_NPM_VERSION="11.11.0"

# Nginx http-context hardening snippet (written under /etc/nginx/conf.d/)
NGINX_HTTP_HARDENING_SNIPPET="/etc/nginx/conf.d/ques-origin-hardening.conf"

# Gentle origin guardrails (Cloudflare remains the primary DDoS layer)
NGINX_LIMIT_CONN_ZONE_SIZE="${NGINX_LIMIT_CONN_ZONE_SIZE:-10m}"
NGINX_LIMIT_CONN_PER_IP="${NGINX_LIMIT_CONN_PER_IP:-40}"
NGINX_LIMIT_REQ_ZONE_SIZE="${NGINX_LIMIT_REQ_ZONE_SIZE:-10m}"
NGINX_ROOT_RATE="${NGINX_ROOT_RATE:-10r/s}"
NGINX_ROOT_BURST="${NGINX_ROOT_BURST:-40}"
NGINX_LIMIT_STATUS="${NGINX_LIMIT_STATUS:-429}"

escape_sed_replacement() {
    local value="$1"

    value=${value//\\/\\\\}
    value=${value//&/\\&}
    value=${value//#/\\#}

    printf '%s' "$value"
}

nginx_conf_includes_conf_d() {
    local nginx_conf="/etc/nginx/nginx.conf"

    if [ ! -f "$nginx_conf" ]; then
        return 1
    fi

    grep -Eq '^[[:space:]]*include[[:space:]]+/etc/nginx/conf\.d/\*\.conf;[[:space:]]*(#.*)?$' "$nginx_conf"
}

nginx_site_should_include_hardening_snippet() {
    # Most Debian/Ubuntu configs include /etc/nginx/conf.d/*.conf in http {}.
    # If they don't, we explicitly include the snippet from the vhost file (still in http context).
    if nginx_conf_includes_conf_d; then
        return 1
    fi

    return 0
}

nginx_conf_includes_sites_enabled() {
    local nginx_conf="/etc/nginx/nginx.conf"

    if [ ! -f "$nginx_conf" ]; then
        return 1
    fi

    # Debian/Ubuntu typical: include /etc/nginx/sites-enabled/*;
    grep -Eq '^[[:space:]]*include[[:space:]]+/etc/nginx/sites-enabled/\*[^;]*;[[:space:]]*(#.*)?$' "$nginx_conf" \
        || grep -Eq 'include[[:space:]]+/etc/nginx/sites-enabled/\*' "$nginx_conf"
}

verify_nginx_layout() {
    # We deploy to /etc/nginx/sites-available + sites-enabled, so nginx.conf must include sites-enabled.
    if ! nginx_conf_includes_sites_enabled; then
        print_error "Nginx is not configured to load /etc/nginx/sites-enabled/*."
        print_error "Your deployment would succeed but Nginx would ignore the site config at: $NGINX_ENABLED"
        echo ""
        print_info "Fix (typical Debian/Ubuntu): ensure this line exists inside the http { } block in /etc/nginx/nginx.conf:"
        echo "  include /etc/nginx/sites-enabled/*;"
        echo ""
        print_info "Then run: sudo nginx -t && sudo systemctl reload nginx"
        exit 1
    fi
}

ensure_certbot_auto_renewal() {
    # Best effort: on many Debian/Ubuntu installs, certbot ships a systemd timer.
    # If no timer/cron is found, we warn so renewal doesn't silently fail.
    if ! command -v certbot &> /dev/null; then
        return 0
    fi

    if command -v systemctl &> /dev/null; then
        if systemctl list-unit-files 2>/dev/null | awk '{print $1}' | grep -qx 'certbot.timer'; then
            print_info "Ensuring certbot auto-renew timer is enabled..."
            "${SUDO_CMD[@]}" systemctl enable --now certbot.timer >/dev/null 2>&1 || true

            if systemctl is-enabled --quiet certbot.timer 2>/dev/null && systemctl is-active --quiet certbot.timer 2>/dev/null; then
                print_success "certbot.timer is enabled and active"
                return 0
            fi

            print_warning "certbot.timer exists but is not enabled/active. Check with: sudo systemctl status certbot.timer"
            return 0
        fi
    fi

    # Cron-based renewal is also common.
    if [ -f /etc/cron.d/certbot ] || [ -f /etc/cron.daily/certbot ]; then
        print_success "Certbot renewal appears to be scheduled via cron"
        return 0
    fi

    print_warning "Could not detect automatic certbot renewal scheduling (no certbot.timer and no certbot cron job found)."
    print_warning "Recommended: run 'sudo certbot renew --dry-run' and ensure a scheduled renewal mechanism exists on this host."
}

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
        local required_node_version="20.17.0"
        local current_node_version
        current_node_version="$(node --version | cut -d'v' -f2)"

        if version_lt "$current_node_version" "$required_node_version"; then
            print_warning "Node.js must be >= $required_node_version for npm@$TARGET_NPM_VERSION. Current version: v$current_node_version"
            print_info "Upgrading Node.js..."
            install_node
        else
            print_success "Node.js v$current_node_version detected"
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

write_nginx_http_hardening_snippet() {
    print_info "Writing Nginx origin-hardening snippet (http context)..."

    "${SUDO_CMD[@]}" mkdir -p "$(dirname "$NGINX_HTTP_HARDENING_SNIPPET")"

    # NOTE: This is a snapshot of Cloudflare IP ranges.
    # If Cloudflare updates ranges, refresh these and redeploy.
    "${SUDO_CMD[@]}" tee "$NGINX_HTTP_HARDENING_SNIPPET" > /dev/null <<EOF
# Ques origin hardening
# Generated by deploy.sh on $(date)

server_tokens off;

map \$request_method \$ques_block_invalid_method {
    default 0;
    CONNECT 1;
    PRI 1;
    TRACE 1;
    TRACK 1;
}

limit_conn_zone \$binary_remote_addr zone=ques_conn_per_ip:${NGINX_LIMIT_CONN_ZONE_SIZE};
limit_req_zone \$binary_remote_addr zone=ques_root:${NGINX_LIMIT_REQ_ZONE_SIZE} rate=${NGINX_ROOT_RATE};

# Cloudflare real client IP (only trusted when the immediate peer is Cloudflare)
real_ip_header CF-Connecting-IP;
real_ip_recursive on;
set_real_ip_from 127.0.0.1;
set_real_ip_from ::1;

set_real_ip_from 173.245.48.0/20;
set_real_ip_from 103.21.244.0/22;
set_real_ip_from 103.22.200.0/22;
set_real_ip_from 103.31.4.0/22;
set_real_ip_from 141.101.64.0/18;
set_real_ip_from 108.162.192.0/18;
set_real_ip_from 190.93.240.0/20;
set_real_ip_from 188.114.96.0/20;
set_real_ip_from 197.234.240.0/22;
set_real_ip_from 198.41.128.0/17;
set_real_ip_from 162.158.0.0/15;
set_real_ip_from 104.16.0.0/13;
set_real_ip_from 104.24.0.0/14;
set_real_ip_from 172.64.0.0/13;
set_real_ip_from 131.0.72.0/22;

set_real_ip_from 2400:cb00::/32;
set_real_ip_from 2606:4700::/32;
set_real_ip_from 2803:f800::/32;
set_real_ip_from 2405:b500::/32;
set_real_ip_from 2405:8100::/32;
set_real_ip_from 2a06:98c0::/29;
set_real_ip_from 2c0f:f248::/32;
EOF

    print_success "Origin-hardening snippet updated: $NGINX_HTTP_HARDENING_SNIPPET"
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

    if [ -f "package-lock.json" ]; then
        run_project_command npm ci
    else
        run_project_command npm install
    fi

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
    
    # Verify critical public files
    print_info "Verifying critical SEO files..."
    critical_files=("404.html" "site.webmanifest" "robots.txt" "sitemap.xml")
    for file in "${critical_files[@]}"; do
        if [ ! -f "$STAGING_NGINX_ROOT/$file" ]; then
            print_warning "Critical SEO file missing: $file"
        else
            print_success "Found: $file"
        fi
    done

    print_info "Verifying required public assets..."
    required_assets=(
        "brand/favicon.ico"
        "brand/mark.ico"
        "brand/icons/icon-32.png"
        "brand/icons/icon-192.png"
        "products/geoseer/demo.mp4"
        "products/geoseer/logo.png"
        "products/geoseer/screenshots/input.png"
        "products/geoseer/screenshots/analysis.png"
        "products/geoseer/screenshots/result.png"
        "legal/police-badge.png"
    )
    for asset in "${required_assets[@]}"; do
        if [ ! -f "$STAGING_NGINX_ROOT/$asset" ]; then
            print_error "Required deployment asset missing: $asset"
            exit 1
        fi

        print_success "Found asset: $asset"
    done
    
    # Set correct permissions
    "${SUDO_CMD[@]}" chown -R www-data:www-data "$STAGING_NGINX_ROOT"

    # Directories: 755, Files: 644 (avoid making every file executable)
    "${SUDO_CMD[@]}" find "$STAGING_NGINX_ROOT" -type d -exec chmod 755 {} +
    "${SUDO_CMD[@]}" find "$STAGING_NGINX_ROOT" -type f -exec chmod 644 {} +
    
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
                if [[ "$target" != /* ]]; then
                    target="$(dirname "$enabled_site")/$target"
                fi
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

    local hardening_include
    hardening_include="# (origin hardening snippet is loaded via /etc/nginx/conf.d/*.conf)"
    if nginx_site_should_include_hardening_snippet; then
        hardening_include="include $NGINX_HTTP_HARDENING_SNIPPET;"
    fi

    write_nginx_http_hardening_snippet
    
    # Check if SSL certificates exist
    if [ -f "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" ]; then
        print_info "SSL certificates found - creating HTTPS configuration"
        
        cat > "$temp_config" << 'EOF'
    __QUES_HARDENING_INCLUDE__

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

    # Origin guardrails
    limit_conn ques_conn_per_ip __NGINX_LIMIT_CONN_PER_IP__;
    limit_req_status __NGINX_LIMIT_STATUS__;
    limit_conn_status __NGINX_LIMIT_STATUS__;

    if ($ques_block_invalid_method) {
        return 405;
    }
    
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
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Permissions-Policy "geolocation=(), microphone=(), camera=(), payment=()" always;
    add_header X-Permitted-Cross-Domain-Policies "none" always;
    add_header Content-Security-Policy "base-uri 'self'; frame-ancestors 'self'" always;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    
    # Add canonical Link header
    add_header Link '<https://your-domain.com/>; rel="canonical"' always;
    
    # Serve robots.txt and sitemap.xml with correct MIME types
    location = /robots.txt {
        add_header Content-Type text/plain;
        add_header Cache-Control "public, max-age=3600, must-revalidate";
        expires 1h;
        try_files $uri =404;
    }
    
    location = /sitemap.xml {
        add_header Content-Type application/xml;
        add_header Cache-Control "public, max-age=3600, must-revalidate";
        expires 1h;
        try_files $uri =404;
    }
    
    location = /site.webmanifest {
        add_header Content-Type application/manifest+json;
        add_header Cache-Control "public, no-cache, must-revalidate";
        expires 0;
        try_files $uri =404;
    }

    error_page 404 /404.html;
    
    # Cache static assets
    location ~* \.(jpg|jpeg|png|gif|ico|css|js|svg|woff|woff2|ttf|eot|mp4|webm|ogg|m4v)$ {
        expires 1y;
        add_header Cache-Control "public, max-age=31536000, immutable";
        access_log off;
        try_files $uri =404;
    }

    # Prevent third-party hotlinking of the large demo video.
    location = /products/geoseer/demo.mp4 {
        valid_referers none blocked server_names;
        if ($invalid_referer) {
            return 403;
        }

        expires 30d;
        add_header Cache-Control "public, max-age=2592000";
        try_files $uri =404;
    }
    
    location = / {
        limit_req zone=ques_root burst=__NGINX_ROOT_BURST__ nodelay;

        add_header Cache-Control "public, no-cache, must-revalidate" always;
        add_header Pragma "no-cache" always;
        add_header Expires "0" always;

        try_files /index.html =404;
    }

    # Everything else should resolve to a real file or return 404.
    location / {
        limit_req zone=ques_root burst=__NGINX_ROOT_BURST__ nodelay;

        add_header Cache-Control "public, no-cache, must-revalidate" always;
        add_header Pragma "no-cache" always;
        add_header Expires "0" always;

        try_files $uri $uri/ $uri.html =404;
    }

    location = /index.html {
        add_header Cache-Control "public, no-cache, must-revalidate" always;
        add_header Pragma "no-cache" always;
        add_header Expires "0" always;
    }

    location = /404.html {
        add_header Cache-Control "public, no-cache, must-revalidate" always;
        add_header Pragma "no-cache" always;
        add_header Expires "0" always;
    }
    
    # Hide dotfiles, but allow /.well-known/ for ACME/certbot
    location ~ /\.(?!well-known) {
        return 404;
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
__QUES_HARDENING_INCLUDE__

# HTTP server - will be modified by certbot to add HTTPS
server {
    listen 80;
    listen [::]:80;
    
    server_name your-domain.com www.your-domain.com;
    
    root /var/www/ques;
    index index.html index.htm;

    # Origin guardrails
    limit_conn ques_conn_per_ip __NGINX_LIMIT_CONN_PER_IP__;
    limit_req_status __NGINX_LIMIT_STATUS__;
    limit_conn_status __NGINX_LIMIT_STATUS__;

    if ($ques_block_invalid_method) {
        return 405;
    }
    
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
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Permissions-Policy "geolocation=(), microphone=(), camera=(), payment=()" always;
    add_header X-Permitted-Cross-Domain-Policies "none" always;
    add_header Content-Security-Policy "base-uri 'self'; frame-ancestors 'self'" always;
    
    # Add canonical Link header
    add_header Link '<https://your-domain.com/>; rel="canonical"' always;
    
    # Serve robots.txt and sitemap.xml with correct MIME types
    location = /robots.txt {
        add_header Content-Type text/plain;
        add_header Cache-Control "public, max-age=3600, must-revalidate";
        expires 1h;
        try_files $uri =404;
    }
    
    location = /sitemap.xml {
        add_header Content-Type application/xml;
        add_header Cache-Control "public, max-age=3600, must-revalidate";
        expires 1h;
        try_files $uri =404;
    }
    
    location = /site.webmanifest {
        add_header Content-Type application/manifest+json;
        add_header Cache-Control "public, no-cache, must-revalidate";
        expires 0;
        try_files $uri =404;
    }

    error_page 404 /404.html;
    
    # Cache static assets
    location ~* \.(jpg|jpeg|png|gif|ico|css|js|svg|woff|woff2|ttf|eot|mp4|webm|ogg|m4v)$ {
        expires 1y;
        add_header Cache-Control "public, max-age=31536000, immutable";
        access_log off;
        try_files $uri =404;
    }

    # Prevent third-party hotlinking of the large demo video.
    location = /products/geoseer/demo.mp4 {
        valid_referers none blocked server_names;
        if ($invalid_referer) {
            return 403;
        }

        expires 30d;
        add_header Cache-Control "public, max-age=2592000";
        try_files $uri =404;
    }
    
    location = / {
        limit_req zone=ques_root burst=__NGINX_ROOT_BURST__ nodelay;

        add_header Cache-Control "public, no-cache, must-revalidate" always;
        add_header Pragma "no-cache" always;
        add_header Expires "0" always;

        try_files /index.html =404;
    }

    # Everything else should resolve to a real file or return 404.
    location / {
        limit_req zone=ques_root burst=__NGINX_ROOT_BURST__ nodelay;

        add_header Cache-Control "public, no-cache, must-revalidate" always;
        add_header Pragma "no-cache" always;
        add_header Expires "0" always;

        try_files $uri $uri/ $uri.html =404;
    }

    location = /index.html {
        add_header Cache-Control "public, no-cache, must-revalidate" always;
        add_header Pragma "no-cache" always;
        add_header Expires "0" always;
    }

    location = /404.html {
        add_header Cache-Control "public, no-cache, must-revalidate" always;
        add_header Pragma "no-cache" always;
        add_header Expires "0" always;
    }
    
    # Hide dotfiles, but allow /.well-known/ for ACME/certbot
    location ~ /\.(?!well-known) {
        return 404;
    }
}
EOF
    fi

    # Replace placeholders with actual values
    # Use -i '' for macOS compatibility, -i for Linux
    local escaped_hardening_include
    local escaped_domain
    local escaped_limit_conn_per_ip
    local escaped_limit_status
    local escaped_root_burst

    escaped_hardening_include="$(escape_sed_replacement "$hardening_include")"
    escaped_domain="$(escape_sed_replacement "$DOMAIN")"
    escaped_limit_conn_per_ip="$(escape_sed_replacement "$NGINX_LIMIT_CONN_PER_IP")"
    escaped_limit_status="$(escape_sed_replacement "$NGINX_LIMIT_STATUS")"
    escaped_root_burst="$(escape_sed_replacement "$NGINX_ROOT_BURST")"

    if [[ "$OSTYPE" == "darwin"* ]]; then
        sed -i '' \
            -e "s#__QUES_HARDENING_INCLUDE__#$escaped_hardening_include#g" \
            -e "s#your-domain.com#$escaped_domain#g" \
            -e "s#__NGINX_LIMIT_CONN_PER_IP__#$escaped_limit_conn_per_ip#g" \
            -e "s#__NGINX_LIMIT_STATUS__#$escaped_limit_status#g" \
            -e "s#__NGINX_ROOT_BURST__#$escaped_root_burst#g" \
            "$temp_config"
    else
        sed -i \
            -e "s#__QUES_HARDENING_INCLUDE__#$escaped_hardening_include#g" \
            -e "s#your-domain.com#$escaped_domain#g" \
            -e "s#__NGINX_LIMIT_CONN_PER_IP__#$escaped_limit_conn_per_ip#g" \
            -e "s#__NGINX_LIMIT_STATUS__#$escaped_limit_status#g" \
            -e "s#__NGINX_ROOT_BURST__#$escaped_root_burst#g" \
            "$temp_config"
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

    local hardening_include
    hardening_include="# (origin hardening snippet is loaded via /etc/nginx/conf.d/*.conf)"
    if nginx_site_should_include_hardening_snippet; then
        hardening_include="include $NGINX_HTTP_HARDENING_SNIPPET;"
    fi

    write_nginx_http_hardening_snippet

    cat > "$temp_config" << 'EOF'
__QUES_HARDENING_INCLUDE__

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

    # Origin guardrails
    limit_conn ques_conn_per_ip __NGINX_LIMIT_CONN_PER_IP__;
    limit_req_status __NGINX_LIMIT_STATUS__;
    limit_conn_status __NGINX_LIMIT_STATUS__;

    if ($ques_block_invalid_method) {
        return 405;
    }
    
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
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Permissions-Policy "geolocation=(), microphone=(), camera=(), payment=()" always;
    add_header X-Permitted-Cross-Domain-Policies "none" always;
    add_header Content-Security-Policy "base-uri 'self'; frame-ancestors 'self'" always;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    
    # Add canonical Link header
    add_header Link '<https://your-domain.com/>; rel="canonical"' always;
    
    # Serve robots.txt and sitemap.xml with correct MIME types
    location = /robots.txt {
        add_header Content-Type text/plain;
        add_header Cache-Control "public, max-age=3600, must-revalidate";
        expires 1h;
        try_files $uri =404;
    }
    
    location = /sitemap.xml {
        add_header Content-Type application/xml;
        add_header Cache-Control "public, max-age=3600, must-revalidate";
        expires 1h;
        try_files $uri =404;
    }
    
    location = /site.webmanifest {
        add_header Content-Type application/manifest+json;
        add_header Cache-Control "public, no-cache, must-revalidate";
        expires 0;
        try_files $uri =404;
    }

    error_page 404 /404.html;
    
    # Cache static assets
    location ~* \.(jpg|jpeg|png|gif|ico|css|js|svg|woff|woff2|ttf|eot|mp4|webm|ogg|m4v)$ {
        expires 1y;
        add_header Cache-Control "public, max-age=31536000, immutable";
        access_log off;
        try_files $uri =404;
    }

    # Prevent third-party hotlinking of the large demo video.
    location = /products/geoseer/demo.mp4 {
        valid_referers none blocked server_names;
        if ($invalid_referer) {
            return 403;
        }

        expires 30d;
        add_header Cache-Control "public, max-age=2592000";
        try_files $uri =404;
    }
    
    location = / {
        limit_req zone=ques_root burst=__NGINX_ROOT_BURST__ nodelay;

        add_header Cache-Control "public, no-cache, must-revalidate" always;
        add_header Pragma "no-cache" always;
        add_header Expires "0" always;

        try_files /index.html =404;
    }

    # Everything else should resolve to a real file or return 404.
    location / {
        limit_req zone=ques_root burst=__NGINX_ROOT_BURST__ nodelay;

        add_header Cache-Control "public, no-cache, must-revalidate" always;
        add_header Pragma "no-cache" always;
        add_header Expires "0" always;

        try_files $uri $uri/ $uri.html =404;
    }

    location = /index.html {
        add_header Cache-Control "public, no-cache, must-revalidate" always;
        add_header Pragma "no-cache" always;
        add_header Expires "0" always;
    }

    location = /404.html {
        add_header Cache-Control "public, no-cache, must-revalidate" always;
        add_header Pragma "no-cache" always;
        add_header Expires "0" always;
    }
    
    # Hide dotfiles, but allow /.well-known/ for ACME/certbot
    location ~ /\.(?!well-known) {
        return 404;
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

    # Replace placeholders with actual values
    # Use -i '' for macOS compatibility, -i for Linux
    local escaped_hardening_include
    local escaped_domain
    local escaped_limit_conn_per_ip
    local escaped_limit_status
    local escaped_root_burst

    escaped_hardening_include="$(escape_sed_replacement "$hardening_include")"
    escaped_domain="$(escape_sed_replacement "$DOMAIN")"
    escaped_limit_conn_per_ip="$(escape_sed_replacement "$NGINX_LIMIT_CONN_PER_IP")"
    escaped_limit_status="$(escape_sed_replacement "$NGINX_LIMIT_STATUS")"
    escaped_root_burst="$(escape_sed_replacement "$NGINX_ROOT_BURST")"

    if [[ "$OSTYPE" == "darwin"* ]]; then
        sed -i '' \
            -e "s#__QUES_HARDENING_INCLUDE__#$escaped_hardening_include#g" \
            -e "s#your-domain.com#$escaped_domain#g" \
            -e "s#__NGINX_LIMIT_CONN_PER_IP__#$escaped_limit_conn_per_ip#g" \
            -e "s#__NGINX_LIMIT_STATUS__#$escaped_limit_status#g" \
            -e "s#__NGINX_ROOT_BURST__#$escaped_root_burst#g" \
            "$temp_config"
    else
        sed -i \
            -e "s#__QUES_HARDENING_INCLUDE__#$escaped_hardening_include#g" \
            -e "s#your-domain.com#$escaped_domain#g" \
            -e "s#__NGINX_LIMIT_CONN_PER_IP__#$escaped_limit_conn_per_ip#g" \
            -e "s#__NGINX_LIMIT_STATUS__#$escaped_limit_status#g" \
            -e "s#__NGINX_ROOT_BURST__#$escaped_root_burst#g" \
            "$temp_config"
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

    verify_nginx_layout
    
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

    ensure_certbot_auto_renewal
    
    # Test and reload Nginx with all configurations
    test_nginx_config
    restart_nginx
    
    # Display final instructions
    display_final_instructions "$ssl_status"
}

# Run main function
main
