#!/usr/bin/env python3
"""
Clean up unnecessary files from the backend_merged directory
"""

import os
import glob

def cleanup_files():
    """Remove unnecessary test, debug, and temporary files"""
    
    print("🧹 Cleaning up unnecessary files...")
    print("=" * 50)
    
    # Define files to remove
    files_to_remove = [
        # Test files (keeping only essential ones)
        "test_20_guarantee.py",
        "test_agent_direct.py", 
        "test_ai_agent_integration.py",
        "test_api_endpoints.py",
        "test_api_simple.py",
        "test_auto_tags.py",
        "test_auto_tags_database.py",
        "test_auto_tags_simple.py",
        "test_card_limits.py",
        "test_database_connection.py",
        "test_db_simple.py",
        "test_fixed_unifuncs.py",
        "test_membership_comprehensive.py",
        "test_membership_system.py",
        "test_minimal_subscription.py",
        "test_payment_comprehensive.py",
        "test_payment_integration.py",
        "test_pricing.py",
        "test_production_auto_tags.py",
        "test_project_ideas_generation.py",
        "test_scraping_comprehensive.py",
        "test_subscription_simple.py",
        "test_subscription_sql.py",
        "test_subscription_system.py",
        "test_unifuncs_agent.py",
        "test_unifuncs_basic.py",
        "test_unifuncs_direct.py",
        "test_unifuncs_ideas.py",
        "test_vector_recommendations.py",
        
        # Debug files
        "debug_unifuncs.py",
        "debug_unifuncs_step_by_step.py",
        
        # Check/utility files (keeping essential ones)
        "check_alembic_state.py",
        "check_available_tags.py",
        "check_database_tables.py",
        "check_projects_structure.py",
        "check_users.py",
        "check_user_links_data.py",
        "check_vector_db.py",
        
        # Demo files
        "demo_auto_tags.py",
        "demo_vector_recommendations.py",
        
        # Temporary files
        "alipay_endpoints_temp.py",
        "test.db",
        "card.json",
        
        # Old/backup files
        "robust_project_agent.py",
        
        # Status/report files
        "membership_status_report.py",
        
        # Cleanup utilities (no longer needed)
        "cleanup_for_github.py",
        "db_utils.py",
        "fix_alembic_revision.py",
        
        # Verification files
        "verify_setup.py",
        
        # MacOS files
        ".DS_Store"
    ]
    
    removed_count = 0
    for filename in files_to_remove:
        if os.path.exists(filename):
            try:
                os.remove(filename)
                print(f"✅ Removed: {filename}")
                removed_count += 1
            except Exception as e:
                print(f"❌ Failed to remove {filename}: {e}")
        else:
            print(f"ℹ️  Not found: {filename}")
    
    # Remove __pycache__ directories
    pycache_dirs = glob.glob("**/__pycache__", recursive=True)
    for pycache_dir in pycache_dirs:
        try:
            import shutil
            shutil.rmtree(pycache_dir)
            print(f"✅ Removed: {pycache_dir}")
            removed_count += 1
        except Exception as e:
            print(f"❌ Failed to remove {pycache_dir}: {e}")
    
    print(f"\n🎉 Cleanup complete! Removed {removed_count} files/directories")
    
    # Show remaining important files
    print(f"\n📋 Remaining important files:")
    important_files = [
        "main.py",
        "requirements.txt",
        "alembic.ini",
        "Dockerfile",
        "docker-compose.production.yml",
        "nginx.conf",
        "README.md",
        ".env"
    ]
    
    for filename in important_files:
        if os.path.exists(filename):
            print(f"✅ {filename}")
        else:
            print(f"❌ Missing: {filename}")

if __name__ == "__main__":
    cleanup_files()
