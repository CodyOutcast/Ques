# Production deployment script for Windows
# deploy_production.bat

@echo off
echo 🚀 Starting production deployment...

REM Environment setup
set ENVIRONMENT=production
set PYTHONPATH=%PYTHONPATH%;%CD%

REM Check if .env.production exists
if not exist ".env.production" (
    echo ❌ Error: .env.production file not found!
    echo Please copy .env.production.example and configure it.
    exit /b 1
)

REM Copy production environment
copy .env.production .env

REM Install dependencies
echo 📦 Installing production dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 exit /b %errorlevel%

REM Run database migrations
echo 🗄️ Running database migrations...
alembic upgrade head
if %errorlevel% neq 0 exit /b %errorlevel%

REM Create log directory
if not exist "logs" mkdir logs

REM Validate configuration
echo 🔍 Validating configuration...
python -c "from config.settings import settings; print(f'✅ Configuration loaded for {settings.environment.value} environment')"
if %errorlevel% neq 0 exit /b %errorlevel%

REM Start the application
echo 🌐 Starting production server...
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --workers 1
