#!/usr/bin/env python3
"""
Clean up root workspace files that are no longer needed
"""

import os
import shutil

def cleanup_root():
    """Remove unnecessary files from root workspace"""
    
    print("🧹 Cleaning up root workspace files...")
    print("=" * 50)
    
    # Files to remove from root
    files_to_remove = [
        "main.py",              # Duplicate of backend_merged/main.py
        "requirements.txt",     # Duplicate of backend_merged/requirements.txt  
        "docker-compose.production.yml",  # Duplicate of backend_merged/docker-compose.production.yml
        "nginx.conf",           # Duplicate of backend_merged/nginx.conf
        "card.json",            # Temporary file
        ".DS_Store",            # MacOS file
        "cleanup_project_structure.py",  # No longer needed
        "PROJECT_CLEANUP_PLAN.md"        # No longer needed
    ]
    
    # Directories to remove
    dirs_to_remove = [
        "temp_Ques_repo",       # Temporary directory
        "logs"                  # Empty logs directory (backend_merged has its own)
    ]
    
    removed_count = 0
    
    # Remove files
    for filename in files_to_remove:
        if os.path.exists(filename):
            try:
                os.remove(filename)
                print(f"✅ Removed file: {filename}")
                removed_count += 1
            except Exception as e:
                print(f"❌ Failed to remove {filename}: {e}")
        else:
            print(f"ℹ️  File not found: {filename}")
    
    # Remove directories
    for dirname in dirs_to_remove:
        if os.path.exists(dirname):
            try:
                shutil.rmtree(dirname)
                print(f"✅ Removed directory: {dirname}")
                removed_count += 1
            except Exception as e:
                print(f"❌ Failed to remove {dirname}: {e}")
        else:
            print(f"ℹ️  Directory not found: {dirname}")
    
    print(f"\n🎉 Root cleanup complete! Removed {removed_count} items")
    
    # Show remaining root files
    print(f"\n📋 Remaining root files:")
    remaining_items = [
        ".git/",
        ".gitignore", 
        ".env",
        "LICENSE",
        "README.md",
        "backend_merged/",
        "archive/"
    ]
    
    for item in remaining_items:
        if os.path.exists(item):
            print(f"✅ {item}")
        else:
            print(f"❌ Missing: {item}")

if __name__ == "__main__":
    # Change to root directory
    os.chdir("d:/Ques")
    cleanup_root()
