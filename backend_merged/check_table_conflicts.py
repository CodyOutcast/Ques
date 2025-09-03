#!/usr/bin/env python3

import os
import re

def find_table_conflicts():
    table_to_files = {}
    models_dir = 'models'
    
    for filename in os.listdir(models_dir):
        if filename.endswith('.py') and not filename.startswith('__'):
            filepath = os.path.join(models_dir, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Find all tablename definitions
                matches = re.findall(r'__tablename__\s*=\s*["\']([^"\']+)["\']', content)
                for table_name in matches:
                    if table_name not in table_to_files:
                        table_to_files[table_name] = []
                    table_to_files[table_name].append(filename)
            except Exception as e:
                print(f'Error reading {filename}: {e}')
    
    print('📊 Table Name Conflicts Analysis:')
    print('=' * 50)
    
    conflicts = False
    for table_name, files in table_to_files.items():
        if len(files) > 1:
            conflicts = True
            print(f'❌ CONFLICT: Table "{table_name}" defined in {len(files)} files:')
            for file in files:
                print(f'   - {file}')
        else:
            print(f'✅ {table_name} -> {files[0]}')
    
    if not conflicts:
        print('🎉 No table name conflicts found!')
    
    return table_to_files

if __name__ == "__main__":
    find_table_conflicts()
