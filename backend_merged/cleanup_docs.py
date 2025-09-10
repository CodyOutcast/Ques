#!/usr/bin/env python3
"""
Clean up outdated documentation files
"""

import os

def cleanup_docs():
    """Remove outdated documentation files"""
    
    print("📚 Cleaning up documentation files...")
    print("=" * 50)
    
    # Files to remove (outdated or redundant documentation)
    docs_to_remove = [
        "AI_AGENT_CONCURRENCY_ANALYSIS.md",
        "AI_AGENT_SEARCH_INTEGRATION_REPORT.md", 
        "ANTI_BLOCKING_GUIDE.md",
        "ANTI_BLOCKING_IMPLEMENTATION.md",
        "AUTO_TAG_IMPLEMENTATION_SUMMARY.md",
        "VECTOR_RECOMMENDATIONS_SUMMARY.md",
        "MEMBERSHIP_SYSTEM_SUMMARY.md",  # Subscription system is now complete
        "SUBSCRIPTION_SETUP_GUIDE.md",   # No longer needed after implementation
        "PAYMENT_METHODS_GUIDE.md",      # Implementation complete
        "QUICK_SETUP_REFERENCE.md",      # Redundant with main README
        "GITHUB_DEPLOYMENT.md"           # Specific deployment info, keep in main README
    ]
    
    # Keep these essential docs:
    # - README.md (main documentation)
    # - API_CONTRACT.md (API reference)
    # - COMPLETE_SETUP_GUIDE.md (comprehensive setup)
    
    removed_count = 0
    for filename in docs_to_remove:
        if os.path.exists(filename):
            try:
                os.remove(filename)
                print(f"✅ Removed: {filename}")
                removed_count += 1
            except Exception as e:
                print(f"❌ Failed to remove {filename}: {e}")
        else:
            print(f"ℹ️  Not found: {filename}")
    
    print(f"\n🎉 Documentation cleanup complete! Removed {removed_count} files")
    
    # Show remaining documentation
    print(f"\n📋 Remaining documentation:")
    remaining_docs = [
        "README.md",
        "API_CONTRACT.md", 
        "COMPLETE_SETUP_GUIDE.md"
    ]
    
    for filename in remaining_docs:
        if os.path.exists(filename):
            print(f"✅ {filename}")
        else:
            print(f"❌ Missing: {filename}")

if __name__ == "__main__":
    cleanup_docs()
