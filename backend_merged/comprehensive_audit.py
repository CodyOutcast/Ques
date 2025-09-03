#!/usr/bin/env python3

import os
import re
from sqlalchemy import create_engine, text
from config.database import db_config

def comprehensive_model_audit():
    """Comprehensive audit of models vs database tables"""
    
    # Get actual database tables
    engine = create_engine(db_config.database_url)
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name != 'alembic_version'
            AND table_name NOT LIKE 'pg_%'
            ORDER BY table_name
        """))
        actual_tables = set(row[0] for row in result.fetchall())
    
    # Get model-defined tables
    model_tables = {}
    model_files = []
    
    for filename in os.listdir('models'):
        if filename.endswith('.py') and not filename.startswith('__') and not filename.endswith('.bak') and not filename.endswith('.unused'):
            model_files.append(filename)
            filepath = os.path.join('models', filename)
            
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                matches = re.findall(r'__tablename__\s*=\s*["\']([^"\']+)["\']', content)
                for table_name in matches:
                    if table_name not in model_tables:
                        model_tables[table_name] = []
                    model_tables[table_name].append(filename)
            except Exception as e:
                print(f'Error reading {filename}: {e}')
    
    model_defined_tables = set(model_tables.keys())
    
    print("🔍 COMPREHENSIVE MODEL AUDIT")
    print("=" * 60)
    
    # Tables with models
    tables_with_models = actual_tables & model_defined_tables
    print(f"✅ TABLES WITH MODELS ({len(tables_with_models)}):")
    for table in sorted(tables_with_models):
        files = model_tables[table]
        if len(files) > 1:
            print(f"   ❌ {table} -> CONFLICT: {', '.join(files)}")
        else:
            print(f"   ✅ {table} -> {files[0]}")
    
    # Tables without models
    tables_without_models = actual_tables - model_defined_tables
    print(f"\n❓ TABLES WITHOUT MODELS ({len(tables_without_models)}):")
    for table in sorted(tables_without_models):
        print(f"   - {table}")
    
    # Models without tables
    models_without_tables = model_defined_tables - actual_tables
    print(f"\n🗃️  MODELS WITHOUT TABLES ({len(models_without_tables)}):")
    for table in sorted(models_without_tables):
        files = model_tables[table]
        print(f"   - {table} -> {', '.join(files)}")
    
    # Check for backup/unused files
    backup_files = []
    for f in os.listdir('models'):
        if f.endswith('.bak') or f.endswith('.unused') or f.endswith('.old'):
            backup_files.append(f)
    
    if backup_files:
        print(f"\n🗃️  BACKUP/OLD FILES ({len(backup_files)}):")
        for backup in backup_files:
            print(f"   - {backup}")
    
    # Check for unused model files
    print(f"\n📁 ALL MODEL FILES ({len(model_files)}):")
    
    # Check which models are imported in __init__.py
    init_file = 'models/__init__.py'
    imported_models = set()
    try:
        with open(init_file, 'r', encoding='utf-8') as f:
            content = f.read()
            # Find imports like "from .filename import"
            imports = re.findall(r'from \.([a-zA-Z_]+) import', content)
            imported_models = set(f"{imp}.py" for imp in imports)
    except Exception as e:
        print(f"Error reading __init__.py: {e}")
    
    for filename in sorted(model_files):
        if filename in imported_models:
            print(f"   ✅ {filename} (imported in __init__.py)")
        else:
            print(f"   ❓ {filename} (not imported)")
    
    return {
        'actual_tables': actual_tables,
        'model_tables': model_tables,
        'tables_with_models': tables_with_models,
        'tables_without_models': tables_without_models,
        'models_without_tables': models_without_tables,
        'backup_files': backup_files,
        'imported_models': imported_models
    }

if __name__ == "__main__":
    comprehensive_model_audit()
