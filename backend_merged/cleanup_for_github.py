#!/bin/bash
# cleanup_for_github.py - Remove unnecessary files before GitHub upload

import os
import shutil
import glob

def remove_files_and_dirs(patterns):
    """Remove files and directories matching the given patterns"""
    removed = []
    for pattern in patterns:
        matches = glob.glob(pattern, recursive=True)
        for match in matches:
            try:
                if os.path.isdir(match):
                    shutil.rmtree(match)
                    removed.append(f"Directory: {match}")
                else:
                    os.remove(match)
                    removed.append(f"File: {match}")
            except Exception as e:
                print(f"Error removing {match}: {e}")
    return removed

def main():
    # Change to the backend_merged directory
    os.chdir(r"c:\Users\WilliamJonathan\Downloads\Ques\backend_merged")
    
    print("🧹 Cleaning up repository for GitHub upload...")
    
    # Files and directories to remove
    cleanup_patterns = [
        # Python cache files
        "**/__pycache__/",
        "**/*.pyc",
        "**/*.pyo",
        "**/*.pyd",
        ".Python",
        
        # Environment files (keep .env.example)
        ".env",
        
        # Log files
        "logs/",
        "*.log",
        
        # Temporary and debug files
        "check_*.py",
        "fix_*.py",
        "test_*.py",
        "debug_*.py",
        
        # Deployment specific files
        "deploy_*.sh",
        "cvm_*.sh",
        "serve_*.sh",
        "verify_*.sh",
        "github_*.sh",
        "create_migration_*.sh",
        "*.md",  # Remove deployment guides, keep only README.md
        
        # IDE and editor files
        ".vscode/",
        ".idea/",
        "*.swp",
        "*.swo",
        "*~",
        
        # OS generated files
        ".DS_Store",
        "Thumbs.db",
        
        # Build artifacts
        "build/",
        "dist/",
        "*.egg-info/",
        
        # Coverage reports
        "htmlcov/",
        ".coverage",
        ".coverage.*",
        "coverage.xml",
        
        # Pytest cache
        ".pytest_cache/",
        
        # mypy cache
        ".mypy_cache/",
    ]
    
    # Keep these important files
    keep_files = [
        "README.md",
        "API_CONTRACT.md", 
        ".env.example",
        ".gitignore"
    ]
    
    removed_items = []
    
    for pattern in cleanup_patterns:
        matches = glob.glob(pattern, recursive=True)
        for match in matches:
            # Skip files we want to keep
            if any(keep_file in match for keep_file in keep_files):
                continue
                
            try:
                if os.path.isdir(match):
                    shutil.rmtree(match)
                    removed_items.append(f"📁 {match}")
                else:
                    os.remove(match)
                    removed_items.append(f"📄 {match}")
            except Exception as e:
                print(f"❌ Error removing {match}: {e}")
    
    print(f"\n✅ Cleanup complete! Removed {len(removed_items)} items:")
    for item in removed_items:
        print(f"  {item}")
    
    print(f"\n📊 Repository is now clean for GitHub upload!")

if __name__ == "__main__":
    main()
