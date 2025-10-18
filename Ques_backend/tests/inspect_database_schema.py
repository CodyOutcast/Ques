#!/usr/bin/env python3
"""
Database Schema Inspector
Check current PostgreSQL database tables and generate updated schema documentation
"""

import os
import sys
from sqlalchemy import create_engine, text, MetaData, inspect
from config.database import db_config
from datetime import datetime

def get_database_schema():
    """
    Connect to PostgreSQL and retrieve current database schema
    """
    try:
        # Create engine
        engine = create_engine(db_config.database_url)
        
        # Get inspector
        inspector = inspect(engine)
        
        # Get all table names
        table_names = inspector.get_table_names()
        
        print(f"🔍 Found {len(table_names)} tables in database: {db_config.PG_DATABASE}")
        print("=" * 60)
        
        schema_info = {
            "tables": {},
            "database": db_config.PG_DATABASE,
            "timestamp": datetime.now().isoformat()
        }
        
        for table_name in sorted(table_names):
            print(f"\n📋 Table: {table_name}")
            print("-" * 40)
            
            # Get columns
            columns = inspector.get_columns(table_name)
            foreign_keys = inspector.get_foreign_keys(table_name)
            indexes = inspector.get_indexes(table_name)
            primary_key = inspector.get_pk_constraint(table_name)
            
            table_info = {
                "columns": {},
                "primary_key": primary_key,
                "foreign_keys": foreign_keys,
                "indexes": indexes
            }
            
            # Process columns
            for col in columns:
                col_name = col['name']
                col_type = str(col['type'])
                nullable = col['nullable']
                default = col.get('default', None)
                
                print(f"  {col_name:25} {col_type:20} {'NULL' if nullable else 'NOT NULL':10} {f'DEFAULT {default}' if default else ''}")
                
                table_info["columns"][col_name] = {
                    "type": col_type,
                    "nullable": nullable,
                    "default": default
                }
            
            # Show primary key
            if primary_key and primary_key['constrained_columns']:
                print(f"\n  🔑 Primary Key: {', '.join(primary_key['constrained_columns'])}")
            
            # Show foreign keys
            if foreign_keys:
                print(f"\n  🔗 Foreign Keys:")
                for fk in foreign_keys:
                    local_cols = ', '.join(fk['constrained_columns'] or [])
                    ref_table = fk['referred_table'] or 'unknown'
                    ref_cols = ', '.join(fk['referred_columns'] or [])
                    print(f"    {local_cols} -> {ref_table}({ref_cols})")
            
            # Show indexes
            if indexes:
                print(f"\n  📇 Indexes:")
                for idx in indexes:
                    cols = ', '.join(idx['column_names'] or [])
                    unique = "UNIQUE" if idx.get('unique', False) else ""
                    name = idx.get('name', 'unnamed_index')
                    print(f"    {name}: {cols} {unique}")
            
            schema_info["tables"][table_name] = table_info
            
        return schema_info
        
    except Exception as e:
        print(f"❌ Error connecting to database: {e}")
        return None

def generate_markdown_schema(schema_info):
    """
    Generate markdown documentation from schema info
    """
    
    md_content = f"""# Current Database Schema - {schema_info['database']}

**Generated on:** {datetime.fromisoformat(schema_info['timestamp']).strftime('%Y-%m-%d %H:%M:%S')}

## Overview

This document contains the current actual database schema as found in PostgreSQL database `{schema_info['database']}`.

**Total Tables:** {len(schema_info['tables'])}

## Tables

"""

    # Generate table documentation
    for table_name, table_info in sorted(schema_info['tables'].items()):
        md_content += f"""### {table_name}

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
"""
        
        for col_name, col_info in table_info['columns'].items():
            nullable = "Yes" if col_info['nullable'] else "No"
            default = col_info['default'] or ""
            col_type = col_info['type']
            
            md_content += f"| `{col_name}` | {col_type} | {nullable} | {default} |  |\n"
        
        # Add constraints
        if table_info['primary_key'] and table_info['primary_key']['constrained_columns']:
            pk_cols = ', '.join(table_info['primary_key']['constrained_columns'])
            md_content += f"\n**Primary Key:** {pk_cols}\n"
        
        if table_info['foreign_keys']:
            md_content += f"\n**Foreign Keys:**\n"
            for fk in table_info['foreign_keys']:
                local_cols = ', '.join(fk['constrained_columns'] or [])
                ref_table = fk['referred_table'] or 'unknown'
                ref_cols = ', '.join(fk['referred_columns'] or [])
                md_content += f"- `{local_cols}` → `{ref_table}({ref_cols})`\n"
        
        if table_info['indexes']:
            md_content += f"\n**Indexes:**\n"
            for idx in table_info['indexes']:
                cols = ', '.join(idx['column_names'] or [])
                unique = " (UNIQUE)" if idx.get('unique', False) else ""
                name = idx.get('name', 'unnamed_index')
                md_content += f"- `{name}`: {cols}{unique}\n"
        
        md_content += "\n---\n\n"
    
    return md_content

def main():
    """Main function"""
    print("🔍 DATABASE SCHEMA INSPECTOR")
    print("=" * 50)
    
    # Check database connection
    schema_info = get_database_schema()
    
    if not schema_info:
        print("❌ Failed to retrieve database schema")
        return 1
    
    # Generate markdown documentation
    print("\n📝 Generating markdown documentation...")
    md_content = generate_markdown_schema(schema_info)
    
    # Write to file
    output_file = "DATABASE_CURRENT_SCHEMA.md"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(md_content)
    
    print(f"✅ Schema documentation written to: {output_file}")
    
    # Also show summary
    print(f"\n📊 SUMMARY:")
    print(f"   Database: {schema_info['database']}")
    print(f"   Tables: {len(schema_info['tables'])}")
    
    table_list = list(schema_info['tables'].keys())
    print(f"   Table List: {', '.join(sorted(table_list))}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())