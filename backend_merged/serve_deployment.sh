#!/bin/bash
# 📡 HTTP Server Deployment Method
# Run this on your local machine to serve files to your CVM

echo "🌐 Starting HTTP server for deployment..."
echo "Your CVM (172.16.0.16) can download files from this server"

# Get local IP
LOCAL_IP=$(ipconfig | grep "IPv4" | grep -v "127.0.0.1" | head -1 | awk '{print $NF}')
PORT=8080

echo "📦 Serving deployment_package on: http://$LOCAL_IP:$PORT"
echo ""
echo "🔧 Commands to run on your CVM (via web console):"
echo "----------------------------------------"
echo "cd /opt"
echo "wget -r -np -nH --cut-dirs=1 http://$LOCAL_IP:$PORT/deployment_package/"
echo "# OR using curl:"
echo "curl -O http://$LOCAL_IP:$PORT/deployment_package.tar.gz"
echo "tar -xzf deployment_package.tar.gz -C /opt/ques-backend/"
echo ""
echo "🚀 Then run migration:"
echo "cd /opt/ques-backend"
echo "alembic upgrade head"
echo "sudo systemctl restart ques-backend"
echo ""

# Create tarball for easier download
cd deployment_package
tar -czf ../deployment_package.tar.gz .
cd ..

# Start Python HTTP server
echo "🌐 Starting HTTP server... (Press Ctrl+C to stop)"
python3 -m http.server $PORT
