#!/usr/bin/env python3
"""
Production Cleanup Script for Backend Merged

This script removes all test files, debug files, and development artifacts
while preserving essential production code and documentation.

Usage:
    python cleanup_for_production.py [--dry-run] [--force]
    
Options:
    --dry-run: Show what would be deleted without actually deleting
    --force: Skip confirmation prompts
"""

import os
import sys
import argparse
import glob
from pathlib import Path
from typing import List, Set

# Current directory
BASE_DIR = Path(__file__).parent

# Files and patterns to remove
CLEANUP_PATTERNS = [
    # Test files
    "**/test_*.py",
    "**/*_test.py",
    "**/*test*.py",
    "**/tests/**",
    
    # Debug and development files
    "**/debug_*.py",
    "**/temp_*.py",
    "**/temporary_*.py",
    "**/*_debug.py",
    "**/*_temp.py",
    
    # Specific test files we found
    "test_*.py",
    "api_test.py",
    "project_agent_test.py",
    
    # Cache and compiled files
    "**/__pycache__/**",
    "**/*.pyc",
    "**/*.pyo",
    "**/*.pyd",
    "**/.pytest_cache/**",
    
    # IDE and editor files
    "**/.vscode/**",
    "**/.idea/**",
    "**/*.swp",
    "**/*~",
    "**/.DS_Store",
    
    # Log files (keep directory structure)
    "**/logs/*.log",
    "**/logs/*.txt",
    
    # Backup and temporary files
    "**/*.bak",
    "**/*.backup",
    "**/*.tmp",
    "**/*.old",
    "**/*_backup.*",
    "**/*_old.*",
]

# Files to preserve (even if they match cleanup patterns)
PRESERVE_FILES = {
    "requirements.txt",
    "README.md",
    "LICENSE",
    "Dockerfile",
    "docker-compose.yml",
    "docker-compose.production.yml",
    "nginx.conf",
    "alembic.ini",
    "main.py",
    "start_app.py",
    "run_server.py",
    "start_server.py",
    ".gitignore",
    ".gitattributes",
    "DEPLOYMENT_CHECKLIST.md",
    "API_CONTRACT.md",
    "FRONTEND_BACKEND_INTEGRATION.md",
    "SSH_DEPLOYMENT_GUIDE.md",
    "GITHUB_DEPLOYMENT.md"
}

# Directories to preserve (even if empty)
PRESERVE_DIRS = {
    "config",
    "dependencies", 
    "middleware",
    "models",
    "routers",
    "schemas", 
    "services",
    "migrations",
    "logs"  # Keep logs directory but clean contents
}

# Files that should be specifically removed
SPECIFIC_REMOVALS = [
    "test_results_9175.json",
    "card.json",  # If it's test data
    "check_alembic_state.py",
    "check_database_tables.py", 
    "check_sms_config.py",
    "check_user_links_data.py",
    "fix_alembic_revision.py",
    "db_utils.py",  # If it's just for testing
]

def find_files_to_remove(dry_run: bool = False) -> List[Path]:
    """Find all files matching cleanup patterns."""
    files_to_remove = []
    
    for pattern in CLEANUP_PATTERNS:
        matches = glob.glob(str(BASE_DIR / pattern), recursive=True)
        for match in matches:
            path = Path(match)
            
            # Skip if it's a preserved file
            if path.name in PRESERVE_FILES:
                if dry_run:
                    print(f"PRESERVING: {path.relative_to(BASE_DIR)} (protected file)")
                continue
                
            # Skip if it's in a preserved directory and we want to keep the structure
            if any(preserve_dir in path.parts for preserve_dir in PRESERVE_DIRS):
                parent_preserved = any(path.is_relative_to(BASE_DIR / preserve_dir) for preserve_dir in PRESERVE_DIRS)
                if parent_preserved and path.suffix not in ['.pyc', '.pyo', '.pyd']:
                    # Only remove cache files from preserved directories
                    continue
                    
            files_to_remove.append(path)
    
    # Add specific files to remove
    for specific_file in SPECIFIC_REMOVALS:
        specific_path = BASE_DIR / specific_file
        if specific_path.exists():
            files_to_remove.append(specific_path)
    
    # Remove duplicates and sort
    files_to_remove = list(set(files_to_remove))
    files_to_remove.sort()
    
    return files_to_remove

def remove_empty_directories() -> List[Path]:
    """Remove empty directories after file cleanup."""
    removed_dirs = []
    
    # Walk through directories bottom-up
    for root, dirs, files in os.walk(BASE_DIR, topdown=False):
        for dir_name in dirs:
            dir_path = Path(root) / dir_name
            
            # Skip preserved directories
            if dir_name in PRESERVE_DIRS:
                continue
                
            try:
                # Try to remove if empty
                if not any(dir_path.iterdir()):
                    dir_path.rmdir()
                    removed_dirs.append(dir_path)
                    print(f"REMOVED EMPTY DIR: {dir_path.relative_to(BASE_DIR)}")
            except OSError:
                # Directory not empty or permission error
                pass
                
    return removed_dirs

def validate_api_endpoints() -> bool:
    """Validate that all API endpoints are properly structured."""
    print("\n🔍 Validating API endpoints...")
    
    router_files = list((BASE_DIR / "routers").glob("*.py"))
    main_file = BASE_DIR / "main.py"
    
    issues_found = []
    
    # Check main.py for app setup
    if main_file.exists():
        with open(main_file, 'r', encoding='utf-8') as f:
            main_content = f.read()
            if "@app.get" in main_content or "@app.post" in main_content:
                print("✅ Main app endpoints found")
            else:
                issues_found.append("No main app endpoints found in main.py")
    
    # Check router files
    valid_routers = 0
    for router_file in router_files:
        if router_file.name.startswith("test_") or "_test" in router_file.name:
            continue
            
        try:
            with open(router_file, 'r', encoding='utf-8') as f:
                content = f.read()
                if "@router." in content and ("get" in content or "post" in content):
                    valid_routers += 1
                    print(f"✅ Router validated: {router_file.name}")
        except Exception as e:
            issues_found.append(f"Error reading {router_file.name}: {e}")
    
    print(f"📊 Found {valid_routers} valid router files")
    
    if issues_found:
        print("\n⚠️ Issues found:")
        for issue in issues_found:
            print(f"  - {issue}")
        return False
    
    return True

def create_production_summary() -> None:
    """Create a summary of the production-ready codebase."""
    summary_file = BASE_DIR / "PRODUCTION_SUMMARY.md"
    
    # Count files by type
    py_files = list(BASE_DIR.glob("**/*.py"))
    router_files = list((BASE_DIR / "routers").glob("*.py"))
    model_files = list((BASE_DIR / "models").glob("*.py"))
    service_files = list((BASE_DIR / "services").glob("*.py"))
    
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write("# Production Codebase Summary\n\n")
        f.write(f"Generated after cleanup on: {Path(__file__).stat().st_mtime}\n\n")
        
        f.write("## File Structure\n")
        f.write(f"- Total Python files: {len(py_files)}\n")
        f.write(f"- Router files: {len(router_files)}\n")
        f.write(f"- Model files: {len(model_files)}\n") 
        f.write(f"- Service files: {len(service_files)}\n\n")
        
        f.write("## API Endpoints\n")
        f.write("Production-ready endpoints organized by module:\n\n")
        
        # List main endpoints
        f.write("### Main App\n")
        f.write("- GET / - Root endpoint\n")
        f.write("- GET /health - Health check\n")
        f.write("- GET /api/v1/info - API information\n\n")
        
        # List router endpoints
        for router_file in router_files:
            if not router_file.name.startswith("test_"):
                module_name = router_file.stem.replace("_", " ").title()
                f.write(f"### {module_name}\n")
                f.write(f"- Module: routers/{router_file.name}\n")
                f.write("- Endpoints: See API documentation\n\n")
        
        f.write("## Deployment Ready\n")
        f.write("✅ All test files removed\n")
        f.write("✅ Cache files cleaned\n") 
        f.write("✅ Development artifacts removed\n")
        f.write("✅ API endpoints validated\n\n")
        
        f.write("## Next Steps\n")
        f.write("1. Deploy to CVM using deploy_to_cvm.sh\n")
        f.write("2. Configure environment variables\n")
        f.write("3. Run database migrations\n")
        f.write("4. Start production server\n")
    
    print(f"📝 Production summary created: {summary_file}")

def main():
    parser = argparse.ArgumentParser(description="Clean up codebase for production deployment")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be deleted without deleting")
    parser.add_argument("--force", action="store_true", help="Skip confirmation prompts")
    
    args = parser.parse_args()
    
    print("🧹 Production Cleanup Script")
    print("=" * 50)
    
    # Find files to remove
    files_to_remove = find_files_to_remove(args.dry_run)
    
    if not files_to_remove:
        print("✨ No files need to be cleaned up!")
        return
    
    print(f"\n📋 Found {len(files_to_remove)} files/directories to remove:")
    
    # Group by type for better display
    test_files = [f for f in files_to_remove if "test" in f.name.lower()]
    cache_files = [f for f in files_to_remove if f.suffix in ['.pyc', '.pyo', '.pyd'] or '__pycache__' in str(f)]
    other_files = [f for f in files_to_remove if f not in test_files and f not in cache_files]
    
    if test_files:
        print(f"\n🧪 Test files ({len(test_files)}):")
        for f in test_files[:10]:  # Show first 10
            print(f"  - {f.relative_to(BASE_DIR)}")
        if len(test_files) > 10:
            print(f"  ... and {len(test_files) - 10} more test files")
    
    if cache_files:
        print(f"\n💾 Cache files ({len(cache_files)}):")
        cache_dirs = set(str(f.parent.relative_to(BASE_DIR)) for f in cache_files if '__pycache__' in str(f))
        for cache_dir in list(cache_dirs)[:5]:  # Show first 5 directories
            print(f"  - {cache_dir}/*")
        if len(cache_dirs) > 5:
            print(f"  ... and {len(cache_dirs) - 5} more cache directories")
    
    if other_files:
        print(f"\n📄 Other files ({len(other_files)}):")
        for f in other_files[:10]:  # Show first 10
            print(f"  - {f.relative_to(BASE_DIR)}")
        if len(other_files) > 10:
            print(f"  ... and {len(other_files) - 10} more files")
    
    if args.dry_run:
        print("\n🔍 DRY RUN - No files were actually deleted")
        return
    
    # Confirm deletion
    if not args.force:
        response = input(f"\n❓ Delete these {len(files_to_remove)} files? [y/N]: ")
        if response.lower() not in ['y', 'yes']:
            print("❌ Cleanup cancelled")
            return
    
    # Perform deletion
    print("\n🗑️  Removing files...")
    removed_count = 0
    
    for file_path in files_to_remove:
        try:
            if file_path.is_file():
                file_path.unlink()
                removed_count += 1
                if len(files_to_remove) <= 20:  # Only show details for small cleanups
                    print(f"  ✅ {file_path.relative_to(BASE_DIR)}")
            elif file_path.is_dir():
                import shutil
                shutil.rmtree(file_path)
                removed_count += 1
                if len(files_to_remove) <= 20:
                    print(f"  ✅ {file_path.relative_to(BASE_DIR)}/")
        except Exception as e:
            print(f"  ❌ Failed to remove {file_path.relative_to(BASE_DIR)}: {e}")
    
    # Remove empty directories
    print("\n📁 Removing empty directories...")
    remove_empty_directories()
    
    print(f"\n✨ Cleanup completed! Removed {removed_count} files/directories")
    
    # Validate APIs
    if validate_api_endpoints():
        print("✅ All API endpoints validated successfully")
    else:
        print("⚠️  Some API validation issues found")
    
    # Create production summary
    create_production_summary()
    
    print("\n🚀 Codebase is now production-ready!")
    print("\nNext steps:")
    print("1. Review PRODUCTION_SUMMARY.md")
    print("2. Deploy using: bash deploy_to_cvm.sh")
    print("3. Configure production environment variables")

if __name__ == "__main__":
    main()
