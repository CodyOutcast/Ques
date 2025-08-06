#!/usr/bin/env python3
"""
🧹 Cleanup Unnecessary Files for GitHub Upload
Remove development files, test files, and temporary files before GitHub upload
"""
import os
import shutil
import glob

def remove_files_and_folders():
    """Remove unnecessary files and folders"""
    
    # Files to remove (keep only essential ones)
    files_to_remove = [
        # Test files
        "test_*.py",
        "verify_*.py",
        "check_*.py",
        
        # Development/setup files
        "frontend_*.py",
        "image_access_demo.py",
        "messaging_demo.py",
        "deploy.py",
        "migrate.py",
        "migrate_chat_tables.py",
        "setup.py",
        "setup_database.py",
        "cleanup_for_github.py",
        "restore_env_files.py",
        "cleanup_unnecessary_files.py",  # This file itself
        
        # Temporary files
        "*.pyc",
        "*.pyo",
        
        # Environment files (except examples)
        ".env",
        ".env.staging", 
        ".env.production",
        
        # Implementation docs (not needed in main repo)
        "CHAT_HIGHLIGHTING_IMPLEMENTATION.md",
        "CLEANUP_SUMMARY.md", 
        "LOCATION_IMPLEMENTATION.md",
        "MESSAGING_SYSTEM.md",
        "PROJECTS_IMPLEMENTATION.md",
        "GITHUB_UPLOAD_READY.md",
        
        # Deployment scripts (keep only essential ones)
        "deploy_production.bat",
        "deploy_production.sh",
        
        # Database utilities
        "db_utils.py",
        "create_vectordb_collection.py",
        "production_recommendation_service.py",
    ]
    
    # Folders to remove
    folders_to_remove = [
        "__pycache__",
        "logs",
    ]
    
    print("🧹 Cleaning up unnecessary files...")
    
    # Remove files
    removed_files = []
    for pattern in files_to_remove:
        for file_path in glob.glob(pattern):
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    removed_files.append(file_path)
                    print(f"  ❌ Removed: {file_path}")
                except Exception as e:
                    print(f"  ⚠️  Could not remove {file_path}: {e}")
    
    # Remove folders
    removed_folders = []
    for folder in folders_to_remove:
        if os.path.exists(folder):
            try:
                shutil.rmtree(folder)
                removed_folders.append(folder)
                print(f"  📁❌ Removed folder: {folder}")
            except Exception as e:
                print(f"  ⚠️  Could not remove {folder}: {e}")
    
    print(f"\n✅ Cleanup complete!")
    print(f"   📄 Files removed: {len(removed_files)}")
    print(f"   📁 Folders removed: {len(removed_folders)}")
    
    return removed_files, removed_folders

def list_remaining_files():
    """List files that will remain"""
    print("\n📋 Files remaining for GitHub upload:")
    
    essential_files = []
    for root, dirs, files in os.walk("."):
        # Skip hidden directories and __pycache__
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
        
        for file in files:
            if not file.startswith('.') and not file.endswith('.pyc'):
                file_path = os.path.join(root, file).replace('.\\', '')
                essential_files.append(file_path)
    
    essential_files.sort()
    for file in essential_files:
        print(f"  ✅ {file}")
    
    print(f"\n📊 Total files for upload: {len(essential_files)}")
    return essential_files

if __name__ == "__main__":
    print("🚀 Preparing repository for GitHub upload...")
    print("=" * 50)
    
    # Remove unnecessary files
    removed_files, removed_folders = remove_files_and_folders()
    
    # List remaining files
    remaining_files = list_remaining_files()
    
    print("\n" + "=" * 50)
    print("🎉 Repository is ready for GitHub upload!")
    print("\nNext steps:")
    print("1. git add .")
    print("2. git commit -m 'Clean repository for production'")
    print("3. git push origin main")
