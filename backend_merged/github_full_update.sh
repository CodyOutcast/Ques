# 🔄 Full GitHub Repository Update
# Use this if you want to sync everything from GitHub

# Replace with your actual GitHub repository URL
REPO_URL="https://github.com/YOUR_GITHUB_USERNAME/YOUR_REPO_NAME.git"

cd /opt

echo "📦 Updating from GitHub repository..."

# Method 1: If you already have a git repository
if [ -d "ques-backend/.git" ]; then
    echo "Pulling latest changes..."
    cd ques-backend
    git pull origin main
else
    # Method 2: Fresh clone
    echo "Cloning repository..."
    git clone $REPO_URL ques-backend-new
    
    # Backup current deployment
    mv ques-backend ques-backend-backup-$(date +%Y%m%d_%H%M%S)
    mv ques-backend-new ques-backend
fi

cd ques-backend

echo "Installing dependencies..."
pip3 install -r requirements.txt

echo "Running migration..."
alembic upgrade head

echo "Restarting application..."
sudo systemctl restart ques-backend

echo "🎉 Full deployment complete!"
