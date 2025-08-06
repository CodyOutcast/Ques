"""
Debug script to check environment variable loading
"""
import os
import sys

# Add the backend path to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Try loading dotenv manually
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ dotenv loaded successfully")
except ImportError:
    print("❌ dotenv not available")

# Check environment variables
print("\n🔍 CHECKING ENVIRONMENT VARIABLES:")
print("=" * 40)

env_vars = [
    'TENCENT_SECRET_ID',
    'TENCENT_SECRET_KEY', 
    'TENCENT_REGION',
    'ENABLE_CONTENT_MODERATION',
    'TENCENT_MODERATION_BIZ_TYPE'
]

for var in env_vars:
    value = os.getenv(var)
    if value:
        # Mask sensitive values
        if 'SECRET' in var:
            masked_value = value[:8] + "..." if len(value) > 8 else "***"
            print(f"  {var}: {masked_value}")
        else:
            print(f"  {var}: {value}")
    else:
        print(f"  {var}: ❌ NOT SET")

# Test settings loading
print("\n🛠️ TESTING SETTINGS LOADING:")
print("=" * 40)

try:
    from config.settings import get_settings
    settings = get_settings()
    
    print(f"  TENCENT_SECRET_ID: {getattr(settings, 'TENCENT_SECRET_ID', 'NOT SET')[:8] + '...' if getattr(settings, 'TENCENT_SECRET_ID', None) else 'NOT SET'}")
    print(f"  TENCENT_SECRET_KEY: {getattr(settings, 'TENCENT_SECRET_KEY', 'NOT SET')[:8] + '...' if getattr(settings, 'TENCENT_SECRET_KEY', None) else 'NOT SET'}")
    print(f"  TENCENT_REGION: {getattr(settings, 'TENCENT_REGION', 'NOT SET')}")
    print(f"  ENABLE_CONTENT_MODERATION: {getattr(settings, 'ENABLE_CONTENT_MODERATION', 'NOT SET')}")
    
    print("✅ Settings loaded successfully")
except Exception as e:
    print(f"❌ Settings loading failed: {e}")
    import traceback
    traceback.print_exc()
