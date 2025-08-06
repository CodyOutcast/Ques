"""
Prepare files for GitHub drag-and-drop upload
This script creates a clean copy of the project without sensitive files
"""
import os
import shutil
import sys

def prepare_for_upload():
    """Create a clean version for GitHub upload"""
    
    # Create upload directory
    upload_dir = "../questrial_upload"
    if os.path.exists(upload_dir):
        shutil.rmtree(upload_dir)
    os.makedirs(upload_dir)
    
    # Files and directories to exclude
    exclude_files = {
        '.env',  # Contains real credentials
        '.git',  # Git history (will be uploaded fresh)
        '__pycache__',
        'logs',
        '*.pyc',
        '*.log',
        '.DS_Store',
        'Thumbs.db',
        'prepare_upload.py'  # This script itself
    }
    
    exclude_patterns = {
        'test_',
        'check_',
        'verify_',
        'debug_'
    }
    
    copied_files = 0
    excluded_files = 0
    
    print("🧹 Preparing clean files for GitHub upload...")
    print(f"📁 Creating upload directory: {upload_dir}")
    
    # Copy files
    for root, dirs, files in os.walk('.'):
        # Skip hidden directories and __pycache__
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__' and d != 'logs']
        
        for file in files:
            file_path = os.path.join(root, file)
            rel_path = os.path.relpath(file_path, '.')
            
            # Check if file should be excluded
            should_exclude = False
            
            # Check exact filename matches
            if file in exclude_files:
                should_exclude = True
                reason = f"Sensitive file: {file}"
            
            # Check pattern matches
            elif any(file.startswith(pattern) for pattern in exclude_patterns):
                should_exclude = True
                reason = f"Test/debug file: {file}"
            
            # Check file extensions
            elif file.endswith(('.pyc', '.log', '.tmp')):
                should_exclude = True
                reason = f"Temporary file: {file}"
            
            if should_exclude:
                excluded_files += 1
                print(f"❌ Excluded: {rel_path} ({reason})")
            else:
                # Create destination directory
                dest_path = os.path.join(upload_dir, rel_path)
                dest_dir = os.path.dirname(dest_path)
                os.makedirs(dest_dir, exist_ok=True)
                
                # Copy file
                shutil.copy2(file_path, dest_path)
                copied_files += 1
                print(f"✅ Copied: {rel_path}")
    
    print(f"\n📊 Summary:")
    print(f"✅ Files copied: {copied_files}")
    print(f"❌ Files excluded: {excluded_files}")
    print(f"📁 Upload directory: {upload_dir}")
    
    print(f"\n🚀 Ready for upload!")
    print(f"💡 Next steps:")
    print(f"   1. Go to: https://github.com/WilliamJokuS/questrial")
    print(f"   2. Click 'uploading an existing file'")
    print(f"   3. Drag and drop ALL files from: {upload_dir}")
    print(f"   4. Add commit message: 'Clean production-ready backend'")
    print(f"   5. Click 'Commit changes'")
    
    print(f"\n⚠️  IMPORTANT:")
    print(f"   - Your .env file was excluded (contains real credentials)")
    print(f"   - .env.example is included (safe template)")
    print(f"   - No test files or logs included")

if __name__ == "__main__":
    prepare_for_upload()
