# Simple PowerShell Deployment Script for CVM
# deploy_simple.ps1

# Configuration
$LOCAL_PATH = "D:\Ques\backend_merged"
$REMOTE_USER = "ubuntu"
$REMOTE_HOST = "134.175.220.232"
$REMOTE_PATH = "/home/ubuntu/backend_merged"
$SSH_KEY = "C:\Users\WilliamJonathan\.ssh\ques_cvm_key.pem"

Write-Host "🚀 Deploying Ques Backend to CVM..." -ForegroundColor Green
Write-Host "==================================" -ForegroundColor Green

# Check if SSH key exists
if (-not (Test-Path $SSH_KEY)) {
    Write-Host "❌ SSH key not found: $SSH_KEY" -ForegroundColor Red
    exit 1
}

Write-Host "✅ SSH key found" -ForegroundColor Green

# Test SSH connection
Write-Host "🔐 Testing SSH connection..." -ForegroundColor Cyan
$testResult = ssh -i $SSH_KEY -o ConnectTimeout=10 "$REMOTE_USER@$REMOTE_HOST" "echo 'Connection successful'" 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ SSH connection working" -ForegroundColor Green
} else {
    Write-Host "❌ SSH connection failed" -ForegroundColor Red
    Write-Host $testResult -ForegroundColor Red
    exit 1
}

# Create remote directory
Write-Host "📁 Creating remote directory..." -ForegroundColor Cyan
ssh -i $SSH_KEY "$REMOTE_USER@$REMOTE_HOST" "mkdir -p $REMOTE_PATH"

# Check for rsync
$hasRsync = $false
try {
    rsync --version | Out-Null
    $hasRsync = $true
    Write-Host "✅ rsync found" -ForegroundColor Green
} catch {
    Write-Host "⚠️ rsync not found, will use SCP" -ForegroundColor Yellow
}

if ($hasRsync) {
    Write-Host "📦 Using rsync to sync files..." -ForegroundColor Cyan
    
    # Build rsync command
    $excludes = @(
        "--exclude=__pycache__"
        "--exclude=*.pyc" 
        "--exclude=.git"
        "--exclude=logs/"
        "--exclude=*.log"
        "--exclude=.env"
        "--exclude=test_*.py"
        "--exclude=*.pem"
        "--exclude=venv/"
        "--exclude=.vscode/"
    )
    
    $rsyncCmd = "rsync -avz --progress $($excludes -join ' ') -e `"ssh -i `'$SSH_KEY`'`" `"$LOCAL_PATH/`" `"$REMOTE_USER@$REMOTE_HOST`:$REMOTE_PATH/`""
    
    Write-Host "Running: $rsyncCmd" -ForegroundColor Yellow
    
    # Execute rsync
    Invoke-Expression $rsyncCmd
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Rsync completed successfully!" -ForegroundColor Green
    } else {
        Write-Host "❌ Rsync failed" -ForegroundColor Red
        exit 1
    }
} else {
    # Fallback to SCP
    Write-Host "📦 Using SCP to copy files..." -ForegroundColor Cyan
    Write-Host "⚠️ This copies all files (less efficient)" -ForegroundColor Yellow
    
    $confirm = Read-Host "Continue with SCP? (y/n)"
    if ($confirm -ne "y") {
        Write-Host "❌ Cancelled" -ForegroundColor Red
        exit 0
    }
    
    # Copy files with SCP
    scp -i $SSH_KEY -r "$LOCAL_PATH\*" "$REMOTE_USER@$REMOTE_HOST`:$REMOTE_PATH/"
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ SCP completed successfully!" -ForegroundColor Green
    } else {
        Write-Host "❌ SCP failed" -ForegroundColor Red
        exit 1
    }
}

# Install dependencies
$installDeps = Read-Host "📦 Install Python dependencies? (y/n)"
if ($installDeps -eq "y") {
    Write-Host "📦 Installing dependencies..." -ForegroundColor Cyan
    ssh -i $SSH_KEY "$REMOTE_USER@$REMOTE_HOST" "cd $REMOTE_PATH; pip3 install -r requirements.txt"
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Dependencies installed!" -ForegroundColor Green
    } else {
        Write-Host "⚠️ Dependency installation issues" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "🎯 Deployment completed!" -ForegroundColor Green
Write-Host "🌐 Your backend: http://134.175.220.232:8000" -ForegroundColor Yellow
Write-Host "🔗 SSH command: ssh -i `"$SSH_KEY`" $REMOTE_USER@$REMOTE_HOST" -ForegroundColor Yellow
Write-Host ""
Write-Host "Next: SSH to server and run:" -ForegroundColor Cyan
Write-Host "cd $REMOTE_PATH" -ForegroundColor White
Write-Host "python3 -m uvicorn main:app --host 0.0.0.0 --port 8000" -ForegroundColor White
