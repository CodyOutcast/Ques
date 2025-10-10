# Windows PowerShell Deployment Script
# Deploy built frontend files to Tencent Cloud Server

param(
    [string]$ServerIP = "134.175.220.232",
    [string]$SSHKeyPath = "C:\Users\R\Desktop\cvm.pem",
    [string]$Username = "ubuntu"
)

# Configuration variables
$BuildDirectory = ".\Ques_Frontend\build"
$ServerDirectory = "/var/www/ques-frontend"

Write-Host "=== Ques Frontend Deployment Script ===" -ForegroundColor Green
Write-Host "Target Server: $ServerIP" -ForegroundColor Cyan
Write-Host "Time: $(Get-Date)" -ForegroundColor Gray
Write-Host ""

# Check if build directory exists
Write-Host "Step 1: Checking build files..." -ForegroundColor Yellow
if (!(Test-Path $BuildDirectory)) {
    Write-Host "[ERROR] Build directory not found: $BuildDirectory" -ForegroundColor Red
    Write-Host "Please run the following commands first:" -ForegroundColor Yellow
    Write-Host "  cd Ques_Frontend" -ForegroundColor White
    Write-Host "  npm run build" -ForegroundColor White
    exit 1
}

# Check build directory content
$buildFiles = Get-ChildItem $BuildDirectory -Recurse
if ($buildFiles.Count -eq 0) {
    Write-Host "[ERROR] Build directory is empty" -ForegroundColor Red
    exit 1
}

Write-Host "[SUCCESS] Build files check passed ($($buildFiles.Count) files)" -ForegroundColor Green

# Check SSH connection
Write-Host ""
Write-Host "Step 2: Testing SSH connection..." -ForegroundColor Yellow
try {
    $sshTest = ssh -i $SSHKeyPath -o ConnectTimeout=10 -o BatchMode=yes $Username@$ServerIP "echo 'SSH connection successful'"
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[SUCCESS] SSH connection is working" -ForegroundColor Green
    } else {
        throw "SSH connection failed"
    }
} catch {
    Write-Host "[ERROR] SSH connection failed, please check:" -ForegroundColor Red
    Write-Host "  - Server IP: $ServerIP" -ForegroundColor White
    Write-Host "  - SSH key path: $SSHKeyPath" -ForegroundColor White
    Write-Host "  - Username: $Username" -ForegroundColor White
    exit 1
}

# Clean server directory
Write-Host ""
Write-Host "Step 3: Cleaning server directory..." -ForegroundColor Yellow
try {
    ssh -i $SSHKeyPath $Username@$ServerIP "sudo rm -rf $ServerDirectory/*"
    ssh -i $SSHKeyPath $Username@$ServerIP "sudo mkdir -p $ServerDirectory"
    ssh -i $SSHKeyPath $Username@$ServerIP "sudo chown -R ubuntu:ubuntu $ServerDirectory"
    Write-Host "[SUCCESS] Server directory cleaned" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Failed to clean server directory" -ForegroundColor Red
    exit 1
}

# Upload files
Write-Host ""
Write-Host "Step 4: Uploading build files..." -ForegroundColor Yellow
try {
    Write-Host "  Uploading files to server..." -ForegroundColor Gray
    
    # Use scp to upload files
    $scpCommand = "scp"
    $scpArgs = @(
        "-i", $SSHKeyPath,
        "-r",
        "$BuildDirectory\*",
        "${Username}@${ServerIP}:${ServerDirectory}/"
    )
    
    & $scpCommand $scpArgs
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[SUCCESS] Files uploaded successfully" -ForegroundColor Green
    } else {
        throw "File upload failed"
    }
} catch {
    Write-Host "[ERROR] File upload failed" -ForegroundColor Red
    exit 1
}

# Configure Nginx
Write-Host ""
Write-Host "Step 5: Configuring Nginx..." -ForegroundColor Yellow

# Create nginx configuration content
$nginxConfig = @"
server {
    listen 80;
    server_name $ServerIP;
    root $ServerDirectory;
    index index.html;

    # 支持React Router的单页应用
    location / {
        try_files `$uri `$uri/ /index.html;
    }

    # 静态资源缓存
    location /assets/ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Gzip压缩
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;

    # 安全头部
    add_header X-Content-Type-Options nosniff;
    add_header X-Frame-Options DENY;
    add_header X-XSS-Protection "1; mode=block";
}
"@

# 创建临时配置文件
$tempConfigFile = [System.IO.Path]::GetTempFileName()
$nginxConfig | Out-File -FilePath $tempConfigFile -Encoding UTF8

try {
    # Upload nginx configuration
    scp -i $SSHKeyPath $tempConfigFile "${Username}@${ServerIP}:/tmp/ques-frontend.conf"
    
    # Apply configuration on server
    ssh -i $SSHKeyPath $Username@$ServerIP "sudo cp /tmp/ques-frontend.conf /etc/nginx/sites-available/ques-frontend"
    ssh -i $SSHKeyPath $Username@$ServerIP "sudo ln -sf /etc/nginx/sites-available/ques-frontend /etc/nginx/sites-enabled/"
    ssh -i $SSHKeyPath $Username@$ServerIP "sudo rm -f /etc/nginx/sites-enabled/default"
    ssh -i $SSHKeyPath $Username@$ServerIP "sudo nginx -t"
    ssh -i $SSHKeyPath $Username@$ServerIP "sudo systemctl reload nginx"

    if ($LASTEXITCODE -eq 0) {
        Write-Host "[SUCCESS] Nginx configured successfully" -ForegroundColor Green
    } else {
        throw "Nginx configuration failed"
    }
} catch {
    Write-Host "[ERROR] Nginx configuration failed" -ForegroundColor Red
} finally {
    # Clean up temporary file
    Remove-Item $tempConfigFile -ErrorAction SilentlyContinue
}

# Set file permissions
Write-Host ""
Write-Host "Step 6: Setting file permissions..." -ForegroundColor Yellow
try {
    ssh -i $SSHKeyPath $Username@$ServerIP "sudo chown -R www-data:www-data $ServerDirectory"
    ssh -i $SSHKeyPath $Username@$ServerIP "sudo chmod -R 755 $ServerDirectory"
    Write-Host "[SUCCESS] File permissions set successfully" -ForegroundColor Green
} catch {
    Write-Host "[WARNING] File permissions may have issues, but website should still work" -ForegroundColor Yellow
}

# Verify deployment
Write-Host ""
Write-Host "Step 7: Verifying deployment..." -ForegroundColor Yellow
try {
    Write-Host "  Checking server files..." -ForegroundColor Gray
    $fileList = ssh -i $SSHKeyPath $Username@$ServerIP "ls -la $ServerDirectory"
    Write-Host $fileList -ForegroundColor White
    
    Write-Host "  Testing HTTP response..." -ForegroundColor Gray
    $httpResponse = ssh -i $SSHKeyPath $Username@$ServerIP "curl -s -o /dev/null -w '%{http_code}' http://localhost"
    if ($httpResponse -eq "200") {
        Write-Host "[SUCCESS] HTTP response is normal (status code: $httpResponse)" -ForegroundColor Green
    } else {
        Write-Host "[WARNING] HTTP response is abnormal (status code: $httpResponse)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "[WARNING] Deployment verification had issues, but deployment might be successful" -ForegroundColor Yellow
}

# Deployment complete
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "Deployment Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Website URL: http://$ServerIP" -ForegroundColor Cyan
Write-Host ""
Write-Host "Important Notes:" -ForegroundColor Yellow
Write-Host "1. If you see a blank page, press Ctrl+F5 to force refresh browser cache" -ForegroundColor White
Write-Host "2. Or press F12 -> Application -> Storage -> Clear site data" -ForegroundColor White
Write-Host "3. For HTTPS setup, please contact administrator" -ForegroundColor White
Write-Host ""
Write-Host "Deployment time: $(Get-Date)" -ForegroundColor Gray 