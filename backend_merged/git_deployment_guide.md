# 🔄 Git-Based Deployment (Easiest if you have a repo)

## If your code is in a Git repository:

### Step 1: Push your changes to your repository
git add .
git commit -m "Add message search functionality"
git push origin main

### Step 2: On your CVM (via web console), pull the changes:
cd /opt/ques-backend
git pull origin main

### Step 3: Run migration:
alembic upgrade head
sudo systemctl restart ques-backend

## If you don't have a Git repository yet:
1. Create a GitHub/GitLab repository
2. Push your deployment_package contents
3. Clone it on your server
4. This method is cleanest for future updates!
