# 🚀 项目部署指南

本文档提供多种部署方案，包括公开和私有部署选项。

## 📋 目录

1. [腾讯云服务器部署 (推荐)](#-腾讯云服务器部署-推荐)
2. [其他部署方案](#-其他部署方案)
3. [故障排除](#-故障排除)

## 🏗️ 腾讯云服务器部署 (推荐)

### ✨ 优势
- ✅ **完全私有** - 代码保持闭源
- ✅ **国内访问** - 无需翻墙，访问快速
- ✅ **完全控制** - 可自定义域名、SSL证书
- ✅ **成本可控** - 使用自己的服务器资源

### 📋 前置要求

- 腾讯云服务器 (Ubuntu 18.04+ 推荐)
- 服务器已配置 SSH 密钥登录
- 本地安装 OpenSSH 客户端

### 🛠️ 部署步骤

#### 步骤 1: 服务器环境初始化

在您的**腾讯云服务器**上运行：

```bash
# 下载服务器初始化脚本
curl -O https://your-domain.com/server-setup.sh
# 或者手动上传 server-setup.sh 文件到服务器

# 赋予执行权限
chmod +x server-setup.sh

# 运行初始化脚本
./server-setup.sh
```

这个脚本会自动：
- 安装和配置 Nginx
- 创建项目目录
- 配置防火墙规则
- 设置正确的文件权限

#### 步骤 2: 配置腾讯云安全组

1. 登录腾讯云控制台
2. 进入 **云服务器 CVM** → **安全组**
3. 编辑您的安全组规则
4. 添加入站规则：
   - 协议端口: `TCP:80`
   - 授权对象: `0.0.0.0/0`
   - 策略: `允许`

#### 步骤 3: 本地部署

在您的**本地开发机器**上：

**Linux/Mac 用户:**
```bash
# 赋予执行权限
chmod +x deploy-server.sh

# 部署到服务器 (替换为您的服务器IP)
./deploy-server.sh <你的服务器IP> root
```

**Windows 用户:**
```cmd
# 直接运行批处理文件
deploy-server.bat <你的服务器IP> root
```

**或使用 npm 命令:**
```bash
npm run deploy:server
# 然后手动运行相应的部署脚本
```

#### 步骤 4: 验证部署

1. 在浏览器中访问: `http://<你的服务器IP>`
2. 应用应该正常加载并可以使用
3. 生成二维码分享给用户

### 🔧 后续更新

每次更新代码后，只需重新运行部署脚本：

```bash
# Linux/Mac
./deploy-server.sh <服务器IP>

# Windows
deploy-server.bat <服务器IP>
```

### 🌐 配置域名 (可选)

如果您有域名，可以：

1. 将域名解析到服务器IP
2. 编辑 `/etc/nginx/sites-available/ques-tinder-project`
3. 将 `server_name _;` 改为 `server_name your-domain.com www.your-domain.com;`
4. 重启 Nginx: `sudo systemctl restart nginx`

### 🔒 配置 HTTPS (推荐)

使用 Let's Encrypt 免费证书：

```bash
# 安装 certbot
sudo apt install certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# 自动续期
sudo crontab -e
# 添加: 0 12 * * * /usr/bin/certbot renew --quiet
```

## 🔄 其他部署方案

### Vercel (需翻墙)
```bash
vercel --prod
```

### Gitee Pages (免费但需公开仓库)
```bash
npm run deploy:gitee
```

### Netlify
```bash
netlify deploy --prod --dir=dist
```

## 🛠️ 故障排除

### 无法访问网站

1. **检查服务器状态:**
   ```bash
   sudo systemctl status nginx
   ```

2. **检查端口是否开放:**
   ```bash
   sudo netstat -tulnp | grep :80
   ```

3. **检查防火墙:**
   ```bash
   sudo ufw status
   sudo ufw allow 80
   ```

4. **检查腾讯云安全组:** 确保开放了 80 端口

### 部署脚本失败

1. **SSH 连接问题:**
   - 确保已配置 SSH 密钥
   - 尝试手动 SSH 连接: `ssh root@<服务器IP>`

2. **权限问题:**
   - 确保使用 root 用户或有 sudo 权限的用户

3. **网络问题:**
   - 检查服务器网络连接
   - 尝试手动上传文件测试

### 应用功能异常

1. **API 调用失败:**
   - 如果您的应用需要调用后端API，请配置 Nginx 代理
   - 编辑 `nginx-config.conf` 中的 API 代理部分

2. **静态资源 404:**
   - 检查 `dist` 目录是否完整
   - 重新构建: `npm run build`

## 📞 获取帮助

如果遇到问题，请检查：
1. 服务器日志: `sudo tail -f /var/log/nginx/error.log`
2. Nginx 状态: `sudo systemctl status nginx`
3. 项目目录权限: `ls -la /var/www/ques-tinder-project`

## 📊 性能优化建议

1. **启用 Gzip 压缩** (已配置)
2. **设置静态资源缓存** (已配置)
3. **使用 CDN** (可选)
4. **启用 HTTP/2** (需要 HTTPS)

---

**部署成功后，您将获得:**
- ✅ 稳定的国内访问链接
- ✅ 可生成二维码分享
- ✅ 完全的代码隐私保护
- ✅ 专业的网站性能 