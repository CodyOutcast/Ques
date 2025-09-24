@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo 🚀 腾讯云服务器部署脚本

:: 检查参数
if "%1"=="" (
    echo ❌ 请提供服务器IP地址
    echo 使用方法: deploy-server.bat ^<服务器IP^> [用户名]
    echo 例如: deploy-server.bat 123.456.789.0 root
    pause
    exit /b 1
)

set SERVER_IP=%1
set USERNAME=%2
if "%USERNAME%"=="" set USERNAME=root

echo 🚀 开始部署到腾讯云服务器: %SERVER_IP%

:: 检查是否在正确的目录
if not exist "package.json" (
    echo ❌ 错误：请在项目根目录运行此脚本
    pause
    exit /b 1
)

:: 构建项目
echo 📦 正在构建项目...
call npm run build

:: 检查构建是否成功
if not exist "dist" (
    echo ❌ 构建失败：dist 目录不存在
    pause
    exit /b 1
)

echo ✅ 构建完成

:: 创建压缩包 (使用 7zip 或 WinRAR，如果没有则提示用户)
echo 📁 创建部署包...
cd dist

:: 尝试使用 tar (Windows 10 1903+ 内置)
tar -czf "../deploy-package.tar.gz" * 2>nul

if not exist "../deploy-package.tar.gz" (
    echo ℹ️ 系统不支持 tar，尝试使用 PowerShell 压缩...
    powershell -command "Compress-Archive -Path * -DestinationPath ../deploy-package.zip -Force"
    cd ..
    ren deploy-package.zip deploy-package.tar.gz
) else (
    cd ..
)

if not exist "deploy-package.tar.gz" (
    echo ❌ 压缩失败：无法创建部署包
    echo 💡 请确保系统支持 tar 命令或安装 7zip
    pause
    exit /b 1
)

echo ✅ 部署包创建完成

:: 上传到服务器 (需要配置 SSH)
echo 🔄 上传到服务器...
echo ℹ️ 正在使用 SCP 上传文件...

scp deploy-package.tar.gz %USERNAME%@%SERVER_IP%:/tmp/ 2>nul

if errorlevel 1 (
    echo ❌ 上传失败：请确保已配置 SSH 密钥或安装 OpenSSH
    echo 💡 您可以手动将 deploy-package.tar.gz 上传到服务器 /tmp/ 目录
    pause
    exit /b 1
)

echo ✅ 文件上传完成

:: 在服务器上部署
echo 📋 在服务器上部署...

ssh %USERNAME%@%SERVER_IP% "sudo mkdir -p /var/www/ques-tinder-project && sudo chown -R www-data:www-data /var/www/ques-tinder-project && cd /var/www/ques-tinder-project && sudo tar -xzf /tmp/deploy-package.tar.gz && sudo chown -R www-data:www-data . && sudo chmod -R 755 . && rm /tmp/deploy-package.tar.gz && echo '✅ 服务器部署完成'"

if errorlevel 1 (
    echo ❌ 服务器部署失败
    pause
    exit /b 1
)

:: 清理本地临时文件
del deploy-package.tar.gz

echo 🎉 部署完成！
echo 🔗 访问地址: http://%SERVER_IP%
echo 📱 如需配置域名，请参考 nginx-config.conf 文件
echo.
echo 🔧 故障排除:
echo - 如果无法访问，请检查腾讯云安全组是否开放 80 端口
echo - 确保服务器防火墙允许 80 端口: sudo ufw allow 80

pause 