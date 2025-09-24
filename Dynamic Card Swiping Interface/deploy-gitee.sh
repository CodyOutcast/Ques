#!/bin/bash

# Gitee Pages 自动化部署脚本
echo "🚀 开始部署到 Gitee Pages..."

# 检查是否在正确的目录
if [ ! -f "package.json" ]; then
    echo "❌ 错误：请在项目根目录运行此脚本"
    exit 1
fi

# 构建项目
echo "📦 正在构建项目..."
npm run build

# 检查构建是否成功
if [ ! -d "dist" ]; then
    echo "❌ 构建失败：dist 目录不存在"
    exit 1
fi

echo "✅ 构建成功"

# 提交到 git
echo "📝 提交代码到 git..."
git add .
read -p "输入提交信息 (默认: Update project): " commit_message
commit_message=${commit_message:-"Update project"}
git commit -m "$commit_message"

# 推送到 Gitee
echo "🔄 推送到 Gitee..."
git push gitee main

echo "🎉 部署完成！"
echo "📱 请到 Gitee 仓库页面开启 Pages 服务"
echo "🔗 Pages 设置路径: 仓库页面 → 服务 → Gitee Pages" 