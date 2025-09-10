# PowerShell Deployment Script for Windows
# deploy_to_cvm.ps1

param(
    [switch]$DryRun = $false,
    [switch]$Verbose = $false
)

# Configuration
$LOCAL_PATH = "D:\Ques\backend_merged\"
$REMOTE_USER = "ubuntu"
$REMOTE_HOST = "134.175.220.232"
$REMOTE_PATH = "/home/ubuntu/backend_merged/"
$SSH_KEY = "C:\Users\WilliamJonathan\.ssh\ques_cvm_key.pem"

Write-Host "🚀 Deploying Ques Backend to CVM..." -ForegroundColor Green
Write-Host "==================================" -ForegroundColor Green
Write-Host "Local:  $LOCAL_PATH" -ForegroundColor Yellow
Write-Host "Remote: $REMOTE_USER@$REMOTE_HOST`:$REMOTE_PATH" -ForegroundColor Yellow
Write-Host "SSH Key: $SSH_KEY" -ForegroundColor Yellow
Write-Host ""

# Check if SSH key exists
if (-not (Test-Path $SSH_KEY)) {
    Write-Host "❌ SSH key not found: $SSH_KEY" -ForegroundColor Red
    exit 1
}

# Test SSH connection
Write-Host "🔐 Testing SSH connection..." -ForegroundColor Cyan
$testConnection = ssh -i $SSH_KEY -o ConnectTimeout=10 "$REMOTE_USER@$REMOTE_HOST" "echo 'SSH connection successful'" 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ SSH connection working" -ForegroundColor Green
} else {
    Write-Host "❌ SSH connection failed:" -ForegroundColor Red
    Write-Host $testConnection -ForegroundColor Red
    exit 1
}

# Create remote directory
Write-Host "📁 Preparing remote directory..." -ForegroundColor Cyan
ssh -i $SSH_KEY "$REMOTE_USER@$REMOTE_HOST" "mkdir -p $REMOTE_PATH && echo 'Remote directory ready'"

# Check if we have rsync available
$rsyncAvailable = $false
try {
    rsync --version | Out-Null
    $rsyncAvailable = $true
    Write-Host "✅ rsync available" -ForegroundColor Green
} catch {
    Write-Host "⚠️ rsync not found in PATH, trying alternative methods..." -ForegroundColor Yellow
}

if ($rsyncAvailable) {
    # Use rsync
    Write-Host "📦 Using rsync for efficient sync..." -ForegroundColor Cyan
    
    $rsyncArgs = @(
        "-avz"
        "--progress"
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
        "-e"
        "ssh -i `"$SSH_KEY`""
        "$LOCAL_PATH"
        "$REMOTE_USER@$REMOTE_HOST`:$REMOTE_PATH"
    )
    
    if ($DryRun) {
        Write-Host "📋 DRY RUN - showing what would be synced:" -ForegroundColor Yellow
        $rsyncArgs = @("--dry-run") + $rsyncArgs
    }
    
    & rsync @rsyncArgs
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Sync completed successfully!" -ForegroundColor Green
    } else {
        Write-Host "❌ Sync failed with exit code: $LASTEXITCODE" -ForegroundColor Red
        exit 1
    }
    
} else {
    # Fallback to SCP
    Write-Host "📦 Using SCP as fallback..." -ForegroundColor Yellow
    Write-Host "⚠️ This will copy ALL files (less efficient than rsync)" -ForegroundColor Yellow
    
    if (-not $DryRun) {
        $confirm = Read-Host "Continue with SCP? (y/n)"
        if ($confirm -ne "y" -and $confirm -ne "Y") {
            Write-Host "❌ Deployment cancelled" -ForegroundColor Red
            exit 0
        }
        
        # Use SCP to copy files
        scp -i $SSH_KEY -r "$LOCAL_PATH*" "$REMOTE_USER@$REMOTE_HOST`:$REMOTE_PATH"
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Files copied successfully!" -ForegroundColor Green
        } else {
            Write-Host "❌ SCP failed" -ForegroundColor Red
            exit 1
        }
    }
}
}

if (-not $DryRun) {
    # Optional: Install dependencies
    $installDeps = Read-Host "📦 Install Python dependencies on server? (y/n)"
    if ($installDeps -eq "y" -or $installDeps -eq "Y") {
        Write-Host "📦 Installing dependencies..." -ForegroundColor Cyan
        ssh -i $SSH_KEY "$REMOTE_USER@$REMOTE_HOST" "cd $REMOTE_PATH; pip3 install -r requirements.txt"
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Dependencies installed!" -ForegroundColor Green
        } else {
            Write-Host "⚠️ Dependency installation had issues" -ForegroundColor Yellow
        }
    }
    
    Write-Host ""
    Write-Host "🎯 Deployment Summary:" -ForegroundColor Green
    Write-Host "✅ Files synchronized to CVM" -ForegroundColor Green
    Write-Host "🌐 Server: http://134.175.220.232:8000" -ForegroundColor Yellow
    Write-Host "🔗 SSH: ssh -i `"$SSH_KEY`" $REMOTE_USER@$REMOTE_HOST" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Cyan
    Write-Host "1. SSH into the server and start your application" -ForegroundColor White
    Write-Host "2. Run: cd $REMOTE_PATH; python3 -m uvicorn main:app --host 0.0.0.0 --port 8000" -ForegroundColor White
}

Write-Host "🎉 Deployment script completed!" -ForegroundColor Green
