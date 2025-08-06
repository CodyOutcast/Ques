# 🚀 Quick Start Deployment Guide

Get your Ques Backend running on Tencent Cloud CVM in minutes!

## 🎯 What You Need

Before starting, ensure you have:

✅ **Tencent Cloud CVM** (Ubuntu 20.04+, 2GB+ RAM)  
✅ **PostgreSQL Database** (Tencent Cloud Database)  
✅ **Domain Name** (optional but recommended)  
✅ **Tencent Cloud Services** configured:
- SMS Service (phone verification)
- Email Service (notifications) 
- Object Storage COS (media files)
- Content Moderation (safety)
- Vector Database (AI matching)

## 🚀 One-Command Deployment

### Step 1: Connect to Your CVM
```bash
ssh root@YOUR_CVM_IP
```

### Step 2: Run Auto-Deployment
```bash
# Download and run deployment script
curl -sSL https://raw.githubusercontent.com/WilliamJokuS/questrial/main/backend_merged/deploy_to_cvm.sh | bash
```

**That's it!** 🎉 The script will:
- Install Docker and all dependencies
- Setup SSL certificates
- Configure the application
- Start all services
- Configure monitoring and backups

## 🛠️ Manual Deployment (Alternative)

If you prefer step-by-step control:

### 1. Prepare Files on Windows
```powershell
# Run from backend_merged directory
.\deploy_windows.ps1 -PrepareUpload
```

### 2. Upload to CVM
```bash
scp -r deployment_package/ root@YOUR_CVM_IP:/opt/ques-backend/
```

### 3. Deploy on CVM
```bash
ssh root@YOUR_CVM_IP
cd /opt/ques-backend
chmod +x deploy_to_cvm.sh
./deploy_to_cvm.sh
```

## ⚙️ Configuration

During deployment, you'll configure:

```env
# Database
PG_HOST=your_postgres_host.tencentcdb.com
PG_USER=your_user
PG_PASSWORD=your_password

# Tencent Cloud
TENCENT_SECRET_ID=your_secret_id
TENCENT_SECRET_KEY=your_secret_key

# Services
TENCENT_SMS_SDK_APP_ID=your_sms_app_id
DEEPSEEK_API_KEY=your_ai_api_key
```

## 🔍 Verification

After deployment:

```bash
# Check health
curl http://localhost:8000/health

# View API docs  
curl http://localhost:8000/docs

# Check logs
docker-compose logs -f app
```

## 📞 Need Help?

- 📖 **Complete Guide**: `CVM_DEPLOYMENT_GUIDE.md`
- ✅ **Checklist**: `DEPLOYMENT_CHECKLIST.md`
- 🔧 **Troubleshooting**: Check application logs
- 📧 **Support**: Review configuration and service connections

## 🎯 Success Indicators

Your deployment is successful when:
- ✅ Health endpoint returns 200 OK
- ✅ API documentation is accessible
- ✅ Database migrations completed
- ✅ SMS/Email services responding
- ✅ HTTPS certificate installed
- ✅ No errors in application logs

**Your Ques Backend is now running 24/7!** 🌟

---

*For detailed instructions, see `CVM_DEPLOYMENT_GUIDE.md`*
