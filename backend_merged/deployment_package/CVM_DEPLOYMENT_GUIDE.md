# 🚀 Ques Backend - Tencent Cloud CVM Deployment Guide

This guide provides step-by-step instructions for deploying the Ques dating app backend to Tencent Cloud Virtual Machine (CVM) for 24/7 operation.

## 📋 Prerequisites

### Tencent Cloud Services Required:
- **CVM Instance** (Ubuntu 20.04 LTS or later, minimum 2GB RAM, 2 CPU cores)
- **PostgreSQL Database** (Cloud Database for PostgreSQL)
- **Vector Database** (for AI matching)
- **SMS Service** (for phone verification)
- **Simple Email Service (SES)** (for email notifications)
- **Content Moderation Service (CMS/TMS)** (for content filtering)
- **Cloud Object Storage (COS)** (for media files)
- **Domain Name** (optional, for HTTPS)

### Local Requirements:
- Git installed
- SSH access to your CVM instance
- Domain name (recommended for production)

## 🖥️ Step 1: CVM Instance Setup

### 1.1 Create CVM Instance
```bash
# Login to Tencent Cloud Console
# Navigate to: Cloud Virtual Machine > Instances
# Create Instance with:
# - OS: Ubuntu 20.04 LTS
# - Instance Type: S5.MEDIUM4 (2 cores, 4GB RAM) or higher
# - System Disk: 50GB SSD
# - Network: VPC with public IP
# - Security Group: Allow ports 22, 80, 443, 8000
```

### 1.2 Connect to Your CVM
```bash
# Replace YOUR_PUBLIC_IP with your CVM's public IP
ssh root@YOUR_PUBLIC_IP

# Or use Tencent Cloud Console web terminal
```

## 🛠️ Step 2: Automated Deployment

### 2.1 Download and Run Deployment Script
```bash
# Download the repository
git clone https://github.com/WilliamJokuS/questrial.git
cd questrial/backend_merged

# Make deployment script executable
chmod +x deploy_to_cvm.sh

# Run automated deployment (as root)
sudo ./deploy_to_cvm.sh
```

The script will automatically:
- Install Docker and Docker Compose
- Setup SSL certificates (if domain provided)
- Clone/update the repository
- Configure environment files
- Deploy with Docker Compose
- Setup monitoring and auto-restart
- Configure firewall

### 2.2 Manual Configuration During Deployment

When prompted, configure your `.env.production` file:

```bash
sudo nano /opt/ques-backend/backend_merged/.env.production
```

**Critical configurations:**
```env
# Production Environment
ENVIRONMENT=production

# Database (Update with your Tencent Cloud PostgreSQL)
PG_HOST=your_postgres_host.tencentcdb.com
PG_PORT=5432
PG_USER=your_postgres_user
PG_PASSWORD=your_secure_password
PG_DATABASE=ques_production

# Tencent Cloud Credentials
TENCENT_SECRET_ID=your_secret_id
TENCENT_SECRET_KEY=your_secret_key
TENCENT_REGION=ap-guangzhou

# SMS Service
TENCENT_SMS_SDK_APP_ID=your_sms_app_id
TENCENT_SMS_SIGNATURE=YourAppName
TENCENT_SMS_VERIFICATION_TEMPLATE_ID=your_template_id

# Email Service
TENCENT_SENDER_EMAIL=noreply@yourdomain.com
TENCENT_EMAIL_TEMPLATE_ID=your_email_template_id

# Object Storage
COS_REGION=ap-guangzhou
COS_BUCKET_NAME=your-bucket-name
COS_DOMAIN=your-bucket-domain.cos.ap-guangzhou.myqcloud.com

# Vector Database
VECTORDB_ENDPOINT=your-vectordb-endpoint
VECTORDB_USERNAME=your-vectordb-username
VECTORDB_KEY=your-vectordb-api-key

# AI Services
DEEPSEEK_API_KEY=your-deepseek-api-key

# Security Keys (Generate strong random keys)
SECRET_KEY=your-super-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here
```

## 🔧 Step 3: Manual Deployment (Alternative)

If you prefer manual deployment:

### 3.1 Install Dependencies
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo systemctl start docker
sudo systemctl enable docker

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Install additional tools
sudo apt install -y git nginx certbot python3-certbot-nginx
```

### 3.2 Clone Repository
```bash
sudo mkdir -p /opt/ques-backend
sudo git clone https://github.com/WilliamJokuS/questrial.git /opt/ques-backend
cd /opt/ques-backend/backend_merged
```

### 3.3 Configure Environment
```bash
# Copy environment template
sudo cp .env.production.example .env.production

# Edit with your configurations
sudo nano .env.production
```

### 3.4 Deploy with Docker
```bash
# Build and start containers
sudo docker-compose -f docker-compose.production.yml up -d --build

# Check status
sudo docker-compose -f docker-compose.production.yml ps
```

## 🌐 Step 4: Domain and SSL Setup

### 4.1 Configure DNS
```bash
# Point your domain to your CVM public IP
# Create A record: api.yourdomain.com -> YOUR_CVM_IP
```

### 4.2 Setup SSL Certificate
```bash
# Stop nginx if running
sudo systemctl stop nginx

# Get SSL certificate (replace with your domain)
sudo certbot certonly --standalone -d api.yourdomain.com

# Update nginx configuration
sudo sed -i 's/server_name _;/server_name api.yourdomain.com;/g' /opt/ques-backend/backend_merged/nginx.conf
```

## 🗄️ Step 5: Database Setup

### 5.1 Run Database Migrations
```bash
cd /opt/ques-backend/backend_merged

# Run migrations inside the app container
sudo docker-compose -f docker-compose.production.yml exec app alembic upgrade head
```

### 5.2 Verify Database Connection
```bash
# Test database connection
sudo docker-compose -f docker-compose.production.yml exec app python -c "
from config.database import engine
from sqlalchemy import text
with engine.connect() as conn:
    result = conn.execute(text('SELECT version()'))
    print('Database connected:', result.fetchone()[0])
"
```

## 🔍 Step 6: Verification and Testing

### 6.1 Health Check
```bash
# Check application health
curl http://localhost:8000/health

# Or with domain
curl https://api.yourdomain.com/health
```

### 6.2 API Documentation
```bash
# Access FastAPI docs
# Visit: https://api.yourdomain.com/docs
# Or: https://api.yourdomain.com/redoc
```

### 6.3 Test Key Endpoints
```bash
# Test user registration
curl -X POST "https://api.yourdomain.com/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpass123"}'

# Test SMS verification (requires valid phone)
curl -X POST "https://api.yourdomain.com/api/sms/send-verification" \
  -H "Content-Type: application/json" \
  -d '{"phone_number":"+86XXXXXXXXXX"}'
```

## 📊 Step 7: Monitoring and Maintenance

### 7.1 View Logs
```bash
# Application logs
sudo docker-compose -f docker-compose.production.yml logs -f app

# Nginx logs
sudo docker-compose -f docker-compose.production.yml logs -f nginx

# System logs
sudo journalctl -u ques-backend -f
```

### 7.2 Restart Services
```bash
# Restart application
sudo systemctl restart ques-backend

# Or manually
sudo docker-compose -f docker-compose.production.yml restart

# Update application
cd /opt/ques-backend
sudo git pull origin main
sudo systemctl restart ques-backend
```

### 7.3 Monitor Resources
```bash
# Check system resources
htop

# Check disk usage
df -h

# Check Docker container stats
sudo docker stats
```

## 🛡️ Step 8: Security Configuration

### 8.1 Firewall Setup
```bash
# Configure UFW firewall
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### 8.2 Security Headers
The nginx configuration includes security headers:
- X-Frame-Options
- X-Content-Type-Options
- X-XSS-Protection
- Strict-Transport-Security

### 8.3 Rate Limiting
- API endpoints: 10 requests/second
- Login endpoints: 5 requests/minute

## 📋 Step 9: Backup and Recovery

### 9.1 Database Backup
```bash
# Create backup script
sudo tee /opt/backup_db.sh > /dev/null << 'EOF'
#!/bin/bash
BACKUP_DIR="/opt/backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p $BACKUP_DIR
docker-compose -f /opt/ques-backend/backend_merged/docker-compose.production.yml exec -T app pg_dump $DATABASE_URL > $BACKUP_DIR/database.sql
tar -czf $BACKUP_DIR/app_files.tar.gz /opt/ques-backend
echo "Backup completed: $BACKUP_DIR"
EOF

sudo chmod +x /opt/backup_db.sh

# Schedule daily backups
echo "0 2 * * * /opt/backup_db.sh" | sudo crontab -
```

### 9.2 Application Backup
```bash
# Manual backup
sudo cp -r /opt/ques-backend /opt/backups/ques-backup-$(date +%Y%m%d)
```

## 🚀 Step 10: Production Optimizations

### 10.1 Performance Tuning
```bash
# Increase file limits
echo "* soft nofile 65536" | sudo tee -a /etc/security/limits.conf
echo "* hard nofile 65536" | sudo tee -a /etc/security/limits.conf

# Optimize PostgreSQL connection pool in .env.production
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=30
```

### 10.2 Auto-scaling (Optional)
Consider Tencent Cloud Auto Scaling Groups for high-traffic scenarios.

## 🆘 Troubleshooting

### Common Issues:

**Application won't start:**
```bash
# Check logs
sudo docker-compose -f docker-compose.production.yml logs app

# Check environment variables
sudo docker-compose -f docker-compose.production.yml exec app env | grep -E "(PG_|TENCENT_)"
```

**Database connection fails:**
```bash
# Test database connection
sudo docker-compose -f docker-compose.production.yml exec app python -c "
from sqlalchemy import create_engine
from config.settings import settings
engine = create_engine(settings.database_url)
print('Database URL:', settings.database_url)
with engine.connect() as conn:
    print('Connection successful!')
"
```

**SSL certificate issues:**
```bash
# Renew certificate
sudo certbot renew --dry-run

# Check certificate status
sudo certbot certificates
```

## 📞 Support

For deployment issues:
1. Check application logs
2. Verify environment configuration
3. Test external service connections (database, Tencent Cloud services)
4. Review firewall and security group settings

## 🎯 Next Steps

After successful deployment:
1. **Configure monitoring** (CloudWatch, Prometheus)
2. **Setup CI/CD pipeline** for automated deployments
3. **Performance testing** with expected load
4. **Backup verification** and disaster recovery testing
5. **Security audit** and penetration testing

Your Ques Backend is now running 24/7 on Tencent Cloud! 🎉