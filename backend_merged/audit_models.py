#!/usr/bin/env python3

import os
import re
import glob

def audit_model_usage():
    """Audit which model files are actually used in the codebase"""
    
    # Get all model files
    model_files = []
    for f in os.listdir('models'):
        if f.endswith('.py') and not f.startswith('__') and not f.endswith('.bak') and not f.endswith('.unused'):
            model_name = f[:-3]  # Remove .py extension
            model_files.append(model_name)
    
    print("🔍 Model Usage Audit")
    print("=" * 50)
    
    # Check each model file for imports
    used_models = set()
    unused_models = set()
    
    # Search for imports in all Python files
    python_files = glob.glob('**/*.py', recursive=True)
    
    for model_name in model_files:
        found_usage = False
        import_patterns = [
            f'from models.{model_name} import',
            f'import models.{model_name}',
            f'models.{model_name}.'
        ]
        
        for py_file in python_files:
            if py_file.startswith('models/'):
                continue  # Skip model files themselves
            
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                for pattern in import_patterns:
                    if pattern in content:
                        found_usage = True
                        used_models.add(model_name)
                        break
                
                if found_usage:
                    break
                    
            except Exception as e:
                continue
        
        if not found_usage:
            unused_models.add(model_name)
    
    # Print results
    print(f"✅ USED MODELS ({len(used_models)}):")
    for model in sorted(used_models):
        print(f"   - {model}.py")
    
    print(f"\n❌ UNUSED MODELS ({len(unused_models)}):")
    for model in sorted(unused_models):
        print(f"   - {model}.py")
    
    # Check for backup/old files
    backup_files = []
    for f in os.listdir('models'):
        if f.endswith('.bak') or f.endswith('.unused') or f.endswith('.old'):
            backup_files.append(f)
    
    if backup_files:
        print(f"\n🗃️  BACKUP/OLD FILES ({len(backup_files)}):")
        for backup in backup_files:
            print(f"   - {backup}")
    
    # Check for potential duplicates
    print(f"\n🔍 POTENTIAL ISSUES:")
    
    # Check users vs users_new
    if 'users' in model_files and 'users_new' in model_files:
        print("   ⚠️  Both users.py and users_new.py exist")
    
    # Check matches vs matches_fixed
    if 'matches' in model_files and 'matches_fixed' in model_files:
        print("   ⚠️  Both matches.py and matches_fixed.py exist")
        
    return used_models, unused_models, backup_files

if __name__ == "__main__":
    audit_model_usage()
