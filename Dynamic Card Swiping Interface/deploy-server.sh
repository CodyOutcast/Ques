#!/bin/bash

# 腾讯云服务器部署脚本
# 使用方法: ./deploy-server.sh your-server-ip username

SERVER_IP="$1"
USERNAME="${2:-root}"
PROJECT_NAME="ques-tinder-project"
REMOTE_PATH="/var/www/$PROJECT_NAME"

# 检查参数
if [ -z "$SERVER_IP" ]; then
    echo "❌ 请提供服务器IP地址"
    echo "使用方法: ./deploy-server.sh <服务器IP> [用户名]"
    echo "例如: ./deploy-server.sh 123.456.789.0 root"
    exit 1
fi

echo "🚀 开始部署到腾讯云服务器: $SERVER_IP"

# 构建项目
echo "📦 正在构建项目..."
npm run build

if [ ! -d "dist" ]; then
    echo "❌ 构建失败：dist 目录不存在"
    exit 1
fi

echo "✅ 构建完成"

# 创建压缩包
echo "📁 创建部署包..."
cd dist
tar -czf "../deploy-package.tar.gz" *
cd ..

echo "✅ 部署包创建完成"

# 上传到服务器
echo "🔄 上传到服务器..."
scp deploy-package.tar.gz $USERNAME@$SERVER_IP:/tmp/

# 在服务器上解压和部署
echo "📋 在服务器上部署..."
ssh $USERNAME@$SERVER_IP << 'EOF'
    # 创建项目目录
    sudo mkdir -p /var/www/ques-tinder-project
    
    # 备份旧版本（如果存在）
    if [ -d "/var/www/ques-tinder-project/backup" ]; then
        sudo rm -rf /var/www/ques-tinder-project/backup
    fi
    
    if [ "$(ls -A /var/www/ques-tinder-project 2>/dev/null)" ]; then
        sudo mkdir -p /var/www/ques-tinder-project/backup
        sudo mv /var/www/ques-tinder-project/* /var/www/ques-tinder-project/backup/ 2>/dev/null || true
    fi
    
    # 解压新版本
    cd /var/www/ques-tinder-project
    sudo tar -xzf /tmp/deploy-package.tar.gz
    
    # 设置权限
    sudo chown -R www-data:www-data /var/www/ques-tinder-project
    sudo chmod -R 755 /var/www/ques-tinder-project
    
    # 清理临时文件
    rm /tmp/deploy-package.tar.gz
    
    echo "✅ 服务器部署完成"
EOF

# 清理本地临时文件
rm deploy-package.tar.gz

echo "🎉 部署完成！"
echo "🔗 访问地址: http://$SERVER_IP"
echo "📱 如需配置域名，请参考 nginx-config.conf 文件" 