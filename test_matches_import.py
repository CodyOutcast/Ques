#!/usr/bin/env python3

print("Testing matches import specifically...")

try:
    import routers.matches as matches_module
    print("✅ Matches module imported")
    print("Has router attribute:", hasattr(matches_module, 'router'))
    
    if hasattr(matches_module, 'router'):
        print("Router type:", type(matches_module.router))
    else:
        print("Available attributes:", [attr for attr in dir(matches_module) if not attr.startswith('_')])
        
except Exception as e:
    print(f"❌ Error importing matches: {e}")
    import traceback
    traceback.print_exc()
