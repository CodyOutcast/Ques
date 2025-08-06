# Ques Backend - PowerShell Deployment Script for Windows Development
# Run this on Windows to prepare files for Linux deployment

param(
    [switch]$PrepareUpload,
    [switch]$CreateDeploymentPackage,
    [string]$OutputPath = ".\deployment_package"
)

# Colors for output
function Write-ColoredOutput {
    param([string]$Message, [string]$Color = "White")
    
    $colors = @{
        "Red" = "Red"
        "Green" = "Green" 
        "Yellow" = "Yellow"
        "Blue" = "Blue"
        "White" = "White"
    }
    
    Write-Host $Message -ForegroundColor $colors[$Color]
}

function Write-Step {
    param([string]$Message)
    Write-ColoredOutput "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] $Message" "Blue"
}

function Write-Success {
    param([string]$Message)
    Write-ColoredOutput "[SUCCESS] $Message" "Green"
}

function Write-Warning {
    param([string]$Message)
    Write-ColoredOutput "[WARNING] $Message" "Yellow"
}

function Write-Error {
    param([string]$Message)
    Write-ColoredOutput "[ERROR] $Message" "Red"
}

# Main deployment preparation function
function Prepare-Deployment {
    Write-Step "Starting Ques Backend deployment preparation..."
    
    # Check if we're in the right directory
    if (-not (Test-Path "main.py") -or -not (Test-Path "requirements.txt")) {
        Write-Error "Please run this script from the backend_merged directory"
        exit 1
    }
    
    # Create deployment package directory
    if (Test-Path $OutputPath) {
        Remove-Item $OutputPath -Recurse -Force
    }
    New-Item -ItemType Directory -Path $OutputPath | Out-Null
    
    Write-Step "Creating deployment package at: $OutputPath"
    
    # Files and directories to include in deployment
    $IncludePatterns = @(
        "*.py",
        "*.txt", 
        "*.yml",
        "*.yaml",
        "*.conf",
        "*.ini",
        "*.md",
        "*.sh",
        ".env.example",
        ".env.production.example",
        "config\*",
        "dependencies\*",
        "middleware\*", 
        "migrations\*",
        "models\*",
        "routers\*",
        "schemas\*",
        "services\*"
    )
    
    # Files and directories to exclude
    $ExcludePatterns = @(
        ".env",
        "__pycache__",
        "*.pyc",
        "*.pyo", 
        "*.log",
        "logs\*",
        "test_*.py",
        "check_*.py",
        "debug_*.py",
        "verify_*.py",
        ".git",
        ".gitignore"
    )
    
    Write-Step "Copying deployment files..."
    
    # Copy files based on patterns
    foreach ($pattern in $IncludePatterns) {
        $files = Get-ChildItem -Path $pattern -Recurse -ErrorAction SilentlyContinue
        foreach ($file in $files) {
            # Check if file should be excluded
            $shouldExclude = $false
            foreach ($excludePattern in $ExcludePatterns) {
                if ($file.Name -like $excludePattern -or $file.FullName -like "*$excludePattern*") {
                    $shouldExclude = $true
                    break
                }
            }
            
            if (-not $shouldExclude) {
                $relativePath = $file.FullName.Substring($PWD.Path.Length + 1)
                $destPath = Join-Path $OutputPath $relativePath
                $destDir = Split-Path $destPath -Parent
                
                if (-not (Test-Path $destDir)) {
                    New-Item -ItemType Directory -Path $destDir -Force | Out-Null
                }
                
                Copy-Item $file.FullName $destPath
                Write-Host "  Copied: $relativePath" -ForegroundColor Gray
            }
        }
    }
    
    Write-Success "Deployment package created successfully!"
    
    # Create deployment instructions
    $instructions = @"
# 🚀 Deployment Instructions

Your Ques Backend deployment package has been prepared!

## 📦 Package Contents:
- All application code and configuration files
- Docker deployment files
- Database migrations
- API documentation
- Deployment scripts and guides

## 🌐 Next Steps for Cloud Deployment:

### 1. Upload to your CVM server:
```bash
# Method 1: Using SCP
scp -r deployment_package/ root@YOUR_CVM_IP:/opt/ques-backend/

# Method 2: Using rsync
rsync -avz deployment_package/ root@YOUR_CVM_IP:/opt/ques-backend/
```

### 2. Run deployment on your CVM:
```bash
ssh root@YOUR_CVM_IP
cd /opt/ques-backend
chmod +x deploy_to_cvm.sh
./deploy_to_cvm.sh
```

### 3. Configure your production environment:
- Edit .env.production with your actual credentials
- Configure Tencent Cloud services
- Set up your domain and SSL certificates

## 📋 Important Files to Review:
- CVM_DEPLOYMENT_GUIDE.md - Complete deployment guide
- DEPLOYMENT_CHECKLIST.md - Deployment verification checklist  
- .env.production.example - Production environment template
- deploy_to_cvm.sh - Automated deployment script

## 🔧 Pre-Deployment Requirements:
✅ Tencent Cloud CVM instance ready
✅ PostgreSQL database configured  
✅ Domain name and SSL certificate (recommended)
✅ Tencent Cloud services configured (SMS, Email, COS, etc.)
✅ All API keys and credentials ready

Happy Deploying! 🎉
"@
    
    $instructions | Out-File -FilePath "$OutputPath\DEPLOYMENT_INSTRUCTIONS.txt" -Encoding UTF8
    
    Write-Step "Created deployment instructions at: $OutputPath\DEPLOYMENT_INSTRUCTIONS.txt"
    
    # Create a simple upload script
    $uploadScript = @"
#!/bin/bash
# Quick upload script for deployment package

read -p "Enter your CVM IP address: " CVM_IP
read -p "Enter your SSH user (default: root): " SSH_USER
SSH_USER=${SSH_USER:-root}

echo "Uploading deployment package to ${SSH_USER}@${CVM_IP}..."

# Create directory on remote server
ssh ${SSH_USER}@${CVM_IP} "mkdir -p /opt/ques-backend"

# Upload files
rsync -avz --progress ./ ${SSH_USER}@${CVM_IP}:/opt/ques-backend/

echo "Upload complete! Now run the deployment script on your CVM:"
echo "ssh ${SSH_USER}@${CVM_IP}"
echo "cd /opt/ques-backend"
echo "chmod +x deploy_to_cvm.sh"
echo "./deploy_to_cvm.sh"
"@
    
    $uploadScript | Out-File -FilePath "$OutputPath\upload_to_cvm.sh" -Encoding UTF8
    
    # Create Windows batch file for upload
    $windowsUpload = @"
@echo off
set /p CVM_IP="Enter your CVM IP address: "
set /p SSH_USER="Enter your SSH user (default: root): "
if "%SSH_USER%"=="" set SSH_USER=root

echo Uploading deployment package to %SSH_USER%@%CVM_IP%...

REM Using WinSCP or similar tool would be recommended for Windows
echo Please use WinSCP, FileZilla, or similar tool to upload this folder to:
echo %SSH_USER%@%CVM_IP%:/opt/ques-backend/
echo.
echo Or use WSL/Git Bash to run: upload_to_cvm.sh
pause
"@
    
    $windowsUpload | Out-File -FilePath "$OutputPath\upload_to_cvm.bat" -Encoding ASCII
    
    Write-Success "Created upload scripts:"
    Write-Host "  - upload_to_cvm.sh (Linux/macOS/WSL)" -ForegroundColor Gray
    Write-Host "  - upload_to_cvm.bat (Windows)" -ForegroundColor Gray
    
    # Show summary
    $fileCount = (Get-ChildItem -Path $OutputPath -Recurse -File).Count
    $packageSize = [math]::Round(((Get-ChildItem -Path $OutputPath -Recurse | Measure-Object -Property Length -Sum).Sum / 1MB), 2)
    
    Write-Success "🎉 Deployment package ready!"
    Write-Host ""
    Write-Host "📊 Package Summary:" -ForegroundColor Cyan
    Write-Host "  Files: $fileCount" -ForegroundColor Gray
    Write-Host "  Size: ${packageSize} MB" -ForegroundColor Gray
    Write-Host "  Location: $OutputPath" -ForegroundColor Gray
    Write-Host ""
    Write-Host "📋 Next Steps:" -ForegroundColor Cyan
    Write-Host "  1. Review DEPLOYMENT_INSTRUCTIONS.txt" -ForegroundColor Gray
    Write-Host "  2. Upload package to your CVM server" -ForegroundColor Gray
    Write-Host "  3. Run deploy_to_cvm.sh on your CVM" -ForegroundColor Gray
    Write-Host "  4. Configure production environment" -ForegroundColor Gray
    Write-Host ""
}

# Script execution
if ($PrepareUpload -or $CreateDeploymentPackage) {
    Prepare-Deployment
} else {
    Write-Host "Ques Backend Deployment Helper" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Usage:" -ForegroundColor Yellow
    Write-Host "  .\deploy_windows.ps1 -PrepareUpload" -ForegroundColor Gray
    Write-Host "  .\deploy_windows.ps1 -CreateDeploymentPackage" -ForegroundColor Gray
    Write-Host "  .\deploy_windows.ps1 -CreateDeploymentPackage -OutputPath 'C:\temp\ques-deploy'" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Options:" -ForegroundColor Yellow
    Write-Host "  -PrepareUpload           : Create deployment package for CVM upload" -ForegroundColor Gray
    Write-Host "  -CreateDeploymentPackage : Same as PrepareUpload" -ForegroundColor Gray  
    Write-Host "  -OutputPath              : Specify output directory (default: .\deployment_package)" -ForegroundColor Gray
    Write-Host ""
    Write-Host "This script prepares your backend for deployment to Tencent Cloud CVM." -ForegroundColor Green
}
