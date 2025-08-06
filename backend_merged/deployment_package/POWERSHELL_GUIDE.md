## ✅ **FIXES COMPLETED** (All issues resolved!)

### ✅ SQLAlchemy Message Conflicts - FIXED
```powershell
# Issue: "Multiple classes found for path 'Message'" error
# ✅ RESOLVED: Removed duplicate Message import from models/__init__.py
# Server now starts without conflicts
python run_server.py
```

### ✅ Health Check SQL Errors - FIXED  
```powershell
# Issue: SQL text expression error on /health endpoint
# ✅ RESOLVED: Fixed "SELECT 1" to text("SELECT 1") with proper SQLAlchemy import
# Health endpoint now returns: {"status":"healthy","database":"connected"}
curl http://localhost:8000/health
```

## 🚀 **UPLOAD TO GITHUB** ✅ COMPLETED!

### ✅ Successfully Uploaded to GitHub!
```powershell
# ✅ COMPLETED: Repository successfully uploaded to GitHub
# Repository URL: https://github.com/WilliamJokuS/questrial
# Main branch now contains the clean, production-ready code
# 73 essential files, all secrets removed, ready for deployment
```

### Quick GitHub Upload Commands (for future updates)
```powershell
# 1. Add all changes
git add .

# 2. Commit with descriptive message
git commit -m "Update: describe your changes here"

# 3. Push to GitHub
git push origin main
```

### Manual Step-by-Step Upload
```powershell
# Check what files will be committed
git status

# Add specific files if needed
git add backend_merged/main.py
git add backend_merged/models/__init__.py  
git add backend_merged/POWERSHELL_GUIDE.md

# Commit changes
git commit -m "🐛 Fix critical server issues - all endpoints working"

# Push to your repository
git push origin main
```

### 🚨 Fix GitHub Upload Errors
```powershell
# If you get "rejected" error, pull remote changes first
git pull origin main --no-edit

# Then push your changes
git push origin main

# Alternative: Force push (CAREFUL - this overwrites remote)
# git push origin main --force
```

### Reset Database if Needed
```powershell
# Complete database reset (if models are corrupted)
python -c "from dependencies.db import engine; from models.base import Base; Base.metadata.drop_all(engine); Base.metadata.create_all(engine)"

# Recreate tables
alembic upgrade head
```

### Check for Remaining Issues
```powershell
# Test health endpoint
curl http://localhost:8000/health

# Test API documentation
# Open: http://localhost:8000/docs
```

---

# 🖥️ PowerShell Command Reference for Ques Backend

This guide provides PowerShell-optimized commands for Windows users.

## 🚀 Quick Setup (One-liners using `;`)

### Complete Installation
```powershell
# Clone, install, and setup in one command
git clone <repository-url>; cd backend_merged; pip install -r requirements.txt; copy .env.example .env

# After editing .env file:
python setup_database.py; alembic upgrade head; python run_server.py
```

### Development Workflow
```powershell
# Update code and restart server
git pull; pip install -r requirements.txt; python run_server.py

# Database operations
python setup_database.py; alembic upgrade head

# Run tests
python test_simple_upload.py; python test_complete_workflow.py
```

## 📋 PowerShell vs Bash Syntax

| Bash (Linux/Mac) | PowerShell (Windows) | Description |
|------------------|---------------------|-------------|
| `command1 && command2` | `command1; command2` | Run commands sequentially |
| `cp file1 file2` | `copy file1 file2` | Copy files |
| `mv file1 file2` | `move file1 file2` | Move/rename files |
| `rm file` | `del file` or `Remove-Item file` | Delete files |
| `ls` | `dir` or `Get-ChildItem` | List directory contents |

## 🔧 Common Development Commands

### Server Management
```powershell
# Start server with auto-reload
python run_server.py

# Start with specific port
uvicorn main:app --host 0.0.0.0 --port 8080 --reload

# Background process (if needed)
Start-Process -FilePath "python" -ArgumentList "run_server.py" -WindowStyle Hidden
```

### Database Operations
```powershell
# Reset database completely
python -c "from dependencies.db import engine; from models.base import Base; Base.metadata.drop_all(engine); Base.metadata.create_all(engine)"

# Check database connection
python -c "from dependencies.db import get_db; db = next(get_db()); print('✅ Database connected'); db.close()"

# View user count
python -c "from dependencies.db import get_db; from models.users import User; db = next(get_db()); print(f'Users: {db.query(User).count()}'); db.close()"
```

### File Upload Testing
```powershell
# Test COS upload and PostgreSQL storage
python test_simple_upload.py

# Comprehensive workflow test
python test_complete_workflow.py

# Test presigned URLs
python test_presigned_url.py
```

### Environment Management
```powershell
# Create virtual environment
python -m venv venv; .\venv\Scripts\Activate.ps1; pip install -r requirements.txt

# Activate existing environment
.\venv\Scripts\Activate.ps1

# Deactivate environment
deactivate
```

## 🐛 Troubleshooting Commands

### Check Dependencies
```powershell
# Verify Python packages
pip list | Select-String "fastapi|sqlalchemy|psycopg2"

# Check Python version
python --version

# Verify environment variables
python -c "import os; print('DB:', os.getenv('PG_HOST')); print('COS:', os.getenv('COS_BUCKET_NAME'))"
```

### Log Analysis
```powershell
# View recent logs
Get-Content logs\performance.log -Tail 20

# Monitor logs in real-time
Get-Content logs\performance.log -Wait -Tail 10

# Search for errors
Select-String "ERROR" logs\*.log
```

### Port Management
```powershell
# Check if port 8000 is in use
netstat -an | Select-String ":8000"

# Kill process on port 8000 (if needed)
$port = 8000; $proc = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue; if($proc) { Stop-Process -Id $proc.OwningProcess -Force }
```

## 💡 Pro Tips for PowerShell Users

1. **Use `;` instead of `&&`** for chaining commands
2. **Tab completion** works for most commands and file paths
3. **Use aliases**: `dir` = `Get-ChildItem`, `type` = `Get-Content`
4. **Background processes**: Use `Start-Process` for long-running tasks
5. **Environment variables**: Use `$env:VARIABLE_NAME` to access them

## 🎯 Quick Start Checklist

```powershell
# 1. Setup (run once)
git clone <repo>; cd backend_merged; pip install -r requirements.txt

# 2. Configure (edit .env file)
copy .env.example .env; notepad .env

# 3. Initialize database
python setup_database.py; alembic upgrade head

# 4. Test upload system
python test_simple_upload.py

# 5. Start server
python run_server.py

# 6. Test API
# Open: http://localhost:8000/docs
```

## 🔗 Useful Aliases for PowerShell Profile

Add these to your PowerShell profile (`$PROFILE`):
```powershell
# Quick navigation
function qcd { cd c:\Users\WilliamJonathan\Downloads\Ques\backend_merged }

# Development shortcuts
function qtest { python test_simple_upload.py; python test_complete_workflow.py }
function qstart { python run_server.py }
function qdb { python setup_database.py; alembic upgrade head }

# Git shortcuts
function qpush { git add .; git commit -m "Auto commit"; git push }
function qpull { git pull; pip install -r requirements.txt }
```

---
*This guide is optimized for Windows PowerShell users working with the Ques dating app backend.*
