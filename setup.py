#!/usr/bin/env python3
"""
Ques Merged Backend - Quick Setup Script
This script automates the initial setup process for the merged backend.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def print_step(step_num, title):
    """Print a formatted step header"""
    print(f"\n🚀 Step {step_num}: {title}")
    print("=" * 50)

def print_success(message):
    """Print a success message"""
    print(f"✅ {message}")

def print_error(message):
    """Print an error message"""
    print(f"❌ {message}")

def print_warning(message):
    """Print a warning message"""
    print(f"⚠️  {message}")

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print_error("Python 3.8 or higher is required")
        sys.exit(1)
    print_success(f"Python {sys.version_info.major}.{sys.version_info.minor} detected")

def check_postgresql():
    """Check if PostgreSQL is available"""
    try:
        result = subprocess.run(['psql', '--version'], 
                              capture_output=True, text=True, check=True)
        print_success(f"PostgreSQL detected: {result.stdout.strip()}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print_warning("PostgreSQL not found in PATH. Please ensure PostgreSQL is installed and accessible.")
        return False

def create_env_file():
    """Create .env file from template if it doesn't exist"""
    if os.path.exists('.env'):
        print_warning(".env file already exists, skipping creation")
        return
    
    if os.path.exists('.env.example'):
        shutil.copy('.env.example', '.env')
        print_success("Created .env file from template")
        print_warning("Please edit .env file with your actual configuration values")
    else:
        print_error(".env.example template not found")

def install_dependencies():
    """Install Python dependencies"""
    try:
        print("Installing Python dependencies...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], 
                      check=True)
        print_success("Dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print_error(f"Failed to install dependencies: {e}")
        sys.exit(1)

def setup_database():
    """Set up the database and run migrations"""
    try:
        print("Setting up database and running migrations...")
        subprocess.run([sys.executable, 'migrate.py', 'check'], check=True)
        subprocess.run([sys.executable, 'migrate.py', 'migrate'], check=True)
        print_success("Database setup completed successfully")
    except subprocess.CalledProcessError as e:
        print_error(f"Database setup failed: {e}")
        print_warning("Please check your database configuration in .env file")
        return False
    return True

def create_directories():
    """Create necessary directories"""
    directories = [
        'logs',
        'uploads',
        'uploads/profiles',
        'uploads/projects',
        'uploads/temp'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print_success(f"Created directory: {directory}")

def print_next_steps():
    """Print next steps for the user"""
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next Steps:")
    print("1. Edit the .env file with your actual configuration values")
    print("2. Ensure PostgreSQL is running and accessible")
    print("3. Configure your vector database credentials")
    print("4. Set up WeChat OAuth credentials (if using)")
    print("5. Configure email service credentials")
    print("\n🚀 To start the development server:")
    print("   uvicorn main:app --reload")
    print("\n📚 For more information, see:")
    print("   - DATABASE_SCHEMA.md for database details")
    print("   - MIGRATION_GUIDE.md for migration help")
    print("   - README.md for API documentation")

def main():
    """Main setup function"""
    print("🎯 Ques Merged Backend Setup")
    print("=" * 50)
    
    # Step 1: Check Python version
    print_step(1, "Checking Python Version")
    check_python_version()
    
    # Step 2: Check PostgreSQL
    print_step(2, "Checking PostgreSQL")
    pg_available = check_postgresql()
    
    # Step 3: Create environment file
    print_step(3, "Setting up Environment Configuration")
    create_env_file()
    
    # Step 4: Install dependencies
    print_step(4, "Installing Dependencies")
    install_dependencies()
    
    # Step 5: Create directories
    print_step(5, "Creating Directory Structure")
    create_directories()
    
    # Step 6: Setup database (only if PostgreSQL is available)
    if pg_available:
        print_step(6, "Setting up Database")
        db_success = setup_database()
        if not db_success:
            print_warning("Database setup failed, but you can retry later with: python migrate.py migrate")
    else:
        print_step(6, "Database Setup (Skipped)")
        print_warning("PostgreSQL not detected. Please install PostgreSQL and run: python migrate.py migrate")
    
    # Final steps
    print_next_steps()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_error("\nSetup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"Setup failed with error: {e}")
        sys.exit(1)
