# ✅ Ques Backend Deployment Checklist

Use this checklist to ensure a complete and successful deployment of your Ques dating app backend to Tencent Cloud CVM.

## 🚀 Pre-Deployment Preparation

### ☐ Cloud Services Setup
- [ ] **CVM Instance Created**
  - [ ] Ubuntu 20.04 LTS or later
  - [ ] Minimum 2GB RAM, 2 CPU cores
  - [ ] 50GB+ SSD storage
  - [ ] Public IP assigned
  - [ ] Security groups configured (ports 22, 80, 443, 8000)

- [ ] **PostgreSQL Database**
  - [ ] Tencent Cloud Database for PostgreSQL instance created
  - [ ] Database user and password configured
  - [ ] Network access allowed from CVM
  - [ ] Database name created (e.g., `ques_production`)

- [ ] **Vector Database**
  - [ ] Tencent Cloud VectorDB instance setup
  - [ ] API credentials obtained
  - [ ] Collection created for user vectors

- [ ] **Tencent Cloud Services**
  - [ ] SMS Service activated with SDK APP ID
  - [ ] SMS templates approved for verification codes
  - [ ] Simple Email Service (SES) configured
  - [ ] Email templates created and approved
  - [ ] Content Moderation Service (CMS/TMS) enabled
  - [ ] Cloud Object Storage (COS) bucket created
  - [ ] COS bucket permissions configured

- [ ] **API Keys and Credentials**
  - [ ] Tencent Cloud Secret ID and Secret Key
  - [ ] DeepSeek API key obtained
  - [ ] All service-specific credentials ready

### ☐ Domain and SSL (Optional but Recommended)
- [ ] **Domain Name**
  - [ ] Domain purchased and DNS configured
  - [ ] A record pointing to CVM public IP
  - [ ] Domain propagation verified

- [ ] **SSL Certificate**
  - [ ] Let's Encrypt or commercial SSL certificate ready
  - [ ] Certificate files accessible

## 🛠️ Deployment Process

### ☐ Initial Server Setup
- [ ] **SSH Access**
  - [ ] SSH connection to CVM established
  - [ ] Root or sudo access confirmed
  - [ ] SSH key authentication configured (recommended)

- [ ] **System Updates**
  - [ ] System packages updated (`apt update && apt upgrade`)
  - [ ] Essential tools installed (git, curl, htop)

### ☐ Automated Deployment
- [ ] **Repository Clone**
  - [ ] Repository cloned to `/opt/ques-backend`
  - [ ] Correct branch checkout (main/production)
  - [ ] File permissions verified

- [ ] **Deployment Script**
  - [ ] `deploy_to_cvm.sh` script made executable
  - [ ] Script executed successfully as root
  - [ ] All prompted configurations completed

### ☐ Manual Verification (If Automated Script Used)
- [ ] **Docker Installation**
  - [ ] Docker service running
  - [ ] Docker Compose installed and working
  - [ ] User added to docker group (if applicable)

- [ ] **Application Containers**
  - [ ] Application container built successfully
  - [ ] Nginx container running
  - [ ] All containers in "Up" status
  - [ ] No error messages in container logs

## ⚙️ Configuration Verification

### ☐ Environment Configuration
- [ ] **`.env.production` File**
  - [ ] File exists in correct location
  - [ ] All required variables set
  - [ ] Database connection string correct
  - [ ] Tencent Cloud credentials valid
  - [ ] API keys configured
  - [ ] Secret keys generated (strong, unique)

- [ ] **Critical Variables Verified:**
  ```bash
  # Database
  PG_HOST=correct_host
  PG_USER=correct_user  
  PG_PASSWORD=secure_password
  PG_DATABASE=correct_database
  
  # Tencent Cloud
  TENCENT_SECRET_ID=valid_secret_id
  TENCENT_SECRET_KEY=valid_secret_key
  TENCENT_REGION=correct_region
  
  # Security
  SECRET_KEY=strong_random_key
  JWT_SECRET_KEY=strong_random_key
  
  # Production Mode
  ENVIRONMENT=production
  ```

### ☐ Database Setup
- [ ] **Connection Test**
  - [ ] Database connection successful from application
  - [ ] Database user permissions verified
  - [ ] Connection pool settings optimized

- [ ] **Migrations**
  - [ ] Alembic migrations executed successfully
  - [ ] All tables created
  - [ ] Project status migration (007_project_status.py) applied
  - [ ] Database schema matches models

### ☐ External Services Testing
- [ ] **SMS Service**
  - [ ] SMS verification codes sending successfully
  - [ ] Template ID correct and approved
  - [ ] Rate limits configured properly

- [ ] **Email Service**
  - [ ] Email notifications working
  - [ ] Sender email verified
  - [ ] Email templates loading correctly

- [ ] **Content Moderation**
  - [ ] Text moderation API responding
  - [ ] Image moderation working (if applicable)
  - [ ] Moderation thresholds configured

- [ ] **Object Storage**
  - [ ] File upload/download working
  - [ ] Bucket permissions correct
  - [ ] CDN configuration (if applicable)

- [ ] **AI Services**
  - [ ] DeepSeek API responding
  - [ ] Vector database connections working
  - [ ] Recommendation engine functional

## 🔍 Application Testing

### ☐ Health Checks
- [ ] **Basic Health**
  - [ ] `/health` endpoint responding (200 OK)
  - [ ] Application startup logs clean
  - [ ] No critical errors in logs

- [ ] **API Documentation**
  - [ ] `/docs` (Swagger UI) accessible
  - [ ] `/redoc` (ReDoc) accessible
  - [ ] All endpoints visible in documentation

### ☐ Core Functionality
- [ ] **Authentication**
  - [ ] User registration working
  - [ ] User login successful
  - [ ] JWT token generation/validation
  - [ ] Password hashing working

- [ ] **User Management**
  - [ ] Profile creation/updates
  - [ ] User search functionality
  - [ ] Location-based features

- [ ] **Messaging System**
  - [ ] Chat creation
  - [ ] Message sending/receiving
  - [ ] Real-time features (if applicable)

- [ ] **Project Management**
  - [ ] Project CRUD operations
  - [ ] Project status updates
  - [ ] User-project relationships

- [ ] **Phone Verification**
  - [ ] SMS code sending
  - [ ] Code verification
  - [ ] Phone number validation

## 🛡️ Security Configuration

### ☐ Network Security
- [ ] **Firewall**
  - [ ] UFW or iptables configured
  - [ ] Only necessary ports open (22, 80, 443)
  - [ ] SSH access restricted (if applicable)

- [ ] **SSL/HTTPS**
  - [ ] SSL certificate installed
  - [ ] HTTPS redirection working
  - [ ] SSL grade A rating (use SSL Labs test)
  - [ ] Security headers present

### ☐ Application Security
- [ ] **Rate Limiting**
  - [ ] API rate limits active
  - [ ] Login attempt limiting
  - [ ] Abuse prevention measures

- [ ] **Content Security**
  - [ ] Content moderation active
  - [ ] File upload restrictions
  - [ ] Input validation working

## 📊 Monitoring and Logging

### ☐ Logging Setup
- [ ] **Application Logs**
  - [ ] Logs writing to correct location
  - [ ] Log rotation configured
  - [ ] Log levels appropriate for production

- [ ] **System Monitoring**
  - [ ] System resource monitoring
  - [ ] Container health monitoring
  - [ ] Auto-restart on failure configured

### ☐ Backup Configuration
- [ ] **Database Backup**
  - [ ] Automated backup script created
  - [ ] Backup schedule configured (cron)
  - [ ] Backup restoration tested

- [ ] **Application Backup**
  - [ ] Code backup strategy
  - [ ] Configuration files backed up
  - [ ] Media files backup (if applicable)

## 🔧 Performance Optimization

### ☐ Resource Optimization
- [ ] **Database Performance**
  - [ ] Connection pooling configured
  - [ ] Query optimization
  - [ ] Database indexes present

- [ ] **Application Performance**
  - [ ] Gunicorn worker count optimized
  - [ ] Memory usage within limits
  - [ ] Response times acceptable

### ☐ Caching and CDN
- [ ] **Static Content**
  - [ ] Static files served efficiently
  - [ ] Compression enabled (gzip)
  - [ ] Cache headers configured

## 🚀 Go-Live Checklist

### ☐ Final Verification
- [ ] **Load Testing**
  - [ ] Application handles expected load
  - [ ] Database performance under load
  - [ ] No memory leaks detected

- [ ] **User Acceptance**
  - [ ] Frontend can connect successfully
  - [ ] All user flows working end-to-end
  - [ ] Mobile app integration tested

### ☐ DNS and Domain
- [ ] **Production DNS**
  - [ ] Production domain pointing to CVM
  - [ ] DNS propagation complete
  - [ ] Domain accessibility verified

### ☐ Post-Deployment
- [ ] **Documentation**
  - [ ] Deployment notes documented
  - [ ] Access credentials secured
  - [ ] Emergency contacts updated

- [ ] **Team Notification**
  - [ ] Deployment team notified
  - [ ] Frontend team provided API endpoints
  - [ ] Stakeholders informed of go-live

## 🆘 Emergency Procedures

### ☐ Rollback Plan
- [ ] **Backup Verification**
  - [ ] Recent backup confirmed working
  - [ ] Rollback procedure documented
  - [ ] Emergency contacts list ready

### ☐ Monitoring Alerts
- [ ] **Alert Setup**
  - [ ] Health check monitoring
  - [ ] Error rate alerts
  - [ ] Resource usage alerts

## 📈 Post-Deployment Tasks

### ☐ Optimization (Week 1-2)
- [ ] Performance monitoring
- [ ] Error rate analysis
- [ ] User feedback collection
- [ ] Security audit scheduling

### ☐ Maintenance Schedule
- [ ] Regular update schedule
- [ ] Security patch management
- [ ] Backup verification schedule
- [ ] Performance review meetings

---

## ✅ Deployment Sign-off

**Deployed by:** ___________________ **Date:** ___________

**Technical Lead Approval:** ___________________ **Date:** ___________

**QA Sign-off:** ___________________ **Date:** ___________

**Production Ready:** ☐ **Go-Live Approved:** ☐

---

## 📞 Emergency Contacts

- **Technical Lead:** ___________________
- **DevOps Engineer:** ___________________  
- **Database Admin:** ___________________
- **Cloud Provider Support:** ___________________

**Deployment Status: ☐ COMPLETED SUCCESSFULLY**

*Save this checklist and refer back to it for future deployments and maintenance.*