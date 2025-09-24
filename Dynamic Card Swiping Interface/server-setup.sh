#!/bin/bash

# 腾讯云服务器初始化脚本
# 在服务器上运行此脚本来安装和配置 Nginx

echo "🚀 开始初始化腾讯云服务器环境..."

# 更新系统
echo "📦 更新系统包..."
sudo apt update && sudo apt upgrade -y

# 安装 Nginx
echo "📦 安装 Nginx..."
sudo apt install nginx -y

# 启动并启用 Nginx
sudo systemctl start nginx
sudo systemctl enable nginx

# 检查 Nginx 状态
sudo systemctl status nginx --no-pager

# 创建项目目录
echo "📁 创建项目目录..."
sudo mkdir -p /var/www/ques-tinder-project
sudo chown -R www-data:www-data /var/www/ques-tinder-project
sudo chmod -R 755 /var/www/ques-tinder-project

# 备份默认 Nginx 配置
echo "💾 备份默认配置..."
sudo cp /etc/nginx/sites-available/default /etc/nginx/sites-available/default.backup

# 创建项目的 Nginx 配置文件
echo "⚙️  创建 Nginx 配置..."
sudo tee /etc/nginx/sites-available/ques-tinder-project > /dev/null << 'EOF'
server {
    listen 80;
    server_name _;  # 接受所有域名和IP访问
    
    root /var/www/ques-tinder-project;
    index index.html index.htm;
    
    # Gzip 压缩
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/javascript
        application/xml+rss
        application/json;
    
    # 处理 SPA 路由
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    # 静态资源缓存
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
        access_log off;
    }
    
    # 安全头
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
    
    # 错误页面
    error_page 404 /index.html;
}
EOF

# 启用站点配置
echo "🔗 启用站点配置..."
sudo ln -sf /etc/nginx/sites-available/ques-tinder-project /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# 测试 Nginx 配置
echo "🧪 测试 Nginx 配置..."
sudo nginx -t

if [ $? -eq 0 ]; then
    echo "✅ Nginx 配置测试通过"
    
    # 重启 Nginx
    echo "🔄 重启 Nginx..."
    sudo systemctl restart nginx
    
    echo "🎉 服务器初始化完成！"
    echo ""
    echo "📋 接下来的步骤："
    echo "1. 在本地运行部署脚本: ./deploy-server.sh <服务器IP>"
    echo "2. 访问 http://<服务器IP> 查看您的应用"
    echo ""
    echo "🔧 配置文件位置:"
    echo "- Nginx 配置: /etc/nginx/sites-available/ques-tinder-project"
    echo "- 项目目录: /var/www/ques-tinder-project"
    echo ""
    echo "🚨 注意: 请确保服务器防火墙允许 80 端口访问"
    
else
    echo "❌ Nginx 配置测试失败，请检查配置"
    exit 1
fi

# 显示服务器 IP
echo "🌐 服务器信息:"
echo "公网IP: $(curl -s http://checkip.amazonaws.com)"
echo "内网IP: $(hostname -I | awk '{print $1}')"

echo ""
echo "🔥 防火墙配置提醒:"
echo "如果无法访问，请检查:"
echo "1. 腾讯云安全组是否开放 80 端口"
echo "2. 服务器防火墙: sudo ufw allow 80" 