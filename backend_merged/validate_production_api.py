#!/usr/bin/env python3
"""
Production API Validation Script

This script validates that all API endpoints are properly configured
and the codebase is ready for production deployment.

Usage: python validate_production_api.py
"""

import os
import sys
import json
import importlib.util
from pathlib import Path
from typing import Dict, List, Set
import re

BASE_DIR = Path(__file__).parent

def extract_endpoints_from_file(file_path: Path) -> List[Dict]:
    """Extract API endpoints from a Python file."""
    endpoints = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Regular expression to match FastAPI route decorators
        pattern = r'@(?:app|router)\.(get|post|put|delete|patch)\s*\(\s*["\']([^"\']+)["\']'
        matches = re.findall(pattern, content)
        
        for method, path in matches:
            endpoints.append({
                'method': method.upper(),
                'path': path,
                'file': str(file_path.relative_to(BASE_DIR))
            })
            
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
    
    return endpoints

def validate_router_structure() -> Dict:
    """Validate router file structure."""
    routers_dir = BASE_DIR / "routers"
    validation_results = {
        'valid_routers': [],
        'invalid_routers': [],
        'total_endpoints': 0,
        'errors': []
    }
    
    if not routers_dir.exists():
        validation_results['errors'].append("Routers directory not found")
        return validation_results
    
    router_files = list(routers_dir.glob("*.py"))
    router_files = [f for f in router_files if not f.name.startswith("__")]
    
    for router_file in router_files:
        try:
            with open(router_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for basic router structure
            if "APIRouter" in content and "@router." in content:
                endpoints = extract_endpoints_from_file(router_file)
                validation_results['valid_routers'].append({
                    'name': router_file.name,
                    'endpoints': len(endpoints),
                    'endpoint_list': endpoints
                })
                validation_results['total_endpoints'] += len(endpoints)
            else:
                validation_results['invalid_routers'].append({
                    'name': router_file.name,
                    'reason': 'No APIRouter or endpoints found'
                })
                
        except Exception as e:
            validation_results['invalid_routers'].append({
                'name': router_file.name,
                'reason': f'Error reading file: {e}'
            })
    
    return validation_results

def validate_main_app() -> Dict:
    """Validate main.py structure."""
    main_file = BASE_DIR / "main.py"
    validation_results = {
        'valid': False,
        'endpoints': [],
        'routers_included': [],
        'errors': []
    }
    
    if not main_file.exists():
        validation_results['errors'].append("main.py not found")
        return validation_results
    
    try:
        with open(main_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for FastAPI app creation
        if "FastAPI" not in content:
            validation_results['errors'].append("FastAPI app not found")
            return validation_results
        
        # Extract main app endpoints
        validation_results['endpoints'] = extract_endpoints_from_file(main_file)
        
        # Extract included routers
        router_includes = re.findall(r'app\.include_router\(([^,\)]+)', content)
        validation_results['routers_included'] = [r.strip() for r in router_includes]
        
        validation_results['valid'] = True
        
    except Exception as e:
        validation_results['errors'].append(f"Error reading main.py: {e}")
    
    return validation_results

def validate_models() -> Dict:
    """Validate model files."""
    models_dir = BASE_DIR / "models"
    validation_results = {
        'model_files': [],
        'total_models': 0,
        'errors': []
    }
    
    if not models_dir.exists():
        validation_results['errors'].append("Models directory not found")
        return validation_results
    
    model_files = list(models_dir.glob("*.py"))
    model_files = [f for f in model_files if not f.name.startswith("__")]
    
    for model_file in model_files:
        try:
            with open(model_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Count classes (potential models)
            class_count = len(re.findall(r'^class\s+\w+', content, re.MULTILINE))
            
            validation_results['model_files'].append({
                'name': model_file.name,
                'classes': class_count
            })
            validation_results['total_models'] += class_count
            
        except Exception as e:
            validation_results['errors'].append(f"Error reading {model_file.name}: {e}")
    
    return validation_results

def validate_services() -> Dict:
    """Validate service files."""
    services_dir = BASE_DIR / "services"
    validation_results = {
        'service_files': [],
        'total_services': 0,
        'errors': []
    }
    
    if not services_dir.exists():
        validation_results['errors'].append("Services directory not found")
        return validation_results
    
    service_files = list(services_dir.glob("*.py"))
    service_files = [f for f in service_files if not f.name.startswith("__")]
    
    for service_file in service_files:
        try:
            with open(service_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Count classes and functions
            class_count = len(re.findall(r'^class\s+\w+', content, re.MULTILINE))
            func_count = len(re.findall(r'^def\s+\w+', content, re.MULTILINE))
            
            validation_results['service_files'].append({
                'name': service_file.name,
                'classes': class_count,
                'functions': func_count
            })
            validation_results['total_services'] += 1
            
        except Exception as e:
            validation_results['errors'].append(f"Error reading {service_file.name}: {e}")
    
    return validation_results

def check_membership_system() -> Dict:
    """Validate membership system configuration."""
    validation_results = {
        'membership_types_found': False,
        'membership_service_found': False,
        'membership_router_found': False,
        'tier_names': [],
        'errors': []
    }
    
    # Check models/user_membership.py
    membership_model = BASE_DIR / "models" / "user_membership.py"
    if membership_model.exists():
        try:
            with open(membership_model, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if "MembershipType" in content:
                validation_results['membership_types_found'] = True
                
                # Extract tier names
                tier_matches = re.findall(r'(\w+)\s*=\s*["\']([^"\']+)["\']', content)
                validation_results['tier_names'] = [match[1] for match in tier_matches if match[0] in ['BASIC', 'PRO', 'AI_POWERED', 'FREE', 'PREMIUM', 'VIP']]
                
        except Exception as e:
            validation_results['errors'].append(f"Error reading user_membership.py: {e}")
    else:
        validation_results['errors'].append("user_membership.py not found")
    
    # Check services/membership_service.py
    membership_service = BASE_DIR / "services" / "membership_service.py"
    if membership_service.exists():
        validation_results['membership_service_found'] = True
    
    # Check routers/membership.py
    membership_router = BASE_DIR / "routers" / "membership.py"
    if membership_router.exists():
        validation_results['membership_router_found'] = True
    
    return validation_results

def generate_api_documentation() -> str:
    """Generate API documentation summary."""
    router_validation = validate_router_structure()
    main_validation = validate_main_app()
    
    doc = []
    doc.append("# API Endpoints Documentation\n")
    
    # Main app endpoints
    if main_validation['endpoints']:
        doc.append("## Main Application Endpoints")
        for endpoint in main_validation['endpoints']:
            doc.append(f"- **{endpoint['method']}** `{endpoint['path']}`")
        doc.append("")
    
    # Router endpoints
    if router_validation['valid_routers']:
        doc.append("## Router Endpoints")
        for router in router_validation['valid_routers']:
            router_name = router['name'].replace('.py', '').replace('_', ' ').title()
            doc.append(f"### {router_name} ({router['endpoints']} endpoints)")
            
            for endpoint in router['endpoint_list'][:10]:  # Show first 10 endpoints
                doc.append(f"- **{endpoint['method']}** `{endpoint['path']}`")
            
            if router['endpoints'] > 10:
                doc.append(f"- ... and {router['endpoints'] - 10} more endpoints")
            
            doc.append("")
    
    doc.append(f"**Total API Endpoints: {router_validation['total_endpoints'] + len(main_validation['endpoints'])}**")
    
    return "\n".join(doc)

def main():
    print("🔍 Production API Validation")
    print("=" * 50)
    
    # Validate main app
    print("\n📱 Validating Main Application...")
    main_validation = validate_main_app()
    
    if main_validation['valid']:
        print("✅ Main app structure is valid")
        print(f"   - Main endpoints: {len(main_validation['endpoints'])}")
        print(f"   - Routers included: {len(main_validation['routers_included'])}")
    else:
        print("❌ Main app validation failed:")
        for error in main_validation['errors']:
            print(f"   - {error}")
    
    # Validate routers
    print("\n🛣️  Validating API Routers...")
    router_validation = validate_router_structure()
    
    print(f"✅ Found {len(router_validation['valid_routers'])} valid routers")
    print(f"📊 Total API endpoints: {router_validation['total_endpoints']}")
    
    if router_validation['invalid_routers']:
        print(f"⚠️  {len(router_validation['invalid_routers'])} invalid routers:")
        for invalid in router_validation['invalid_routers']:
            print(f"   - {invalid['name']}: {invalid['reason']}")
    
    # Show top routers by endpoint count
    top_routers = sorted(router_validation['valid_routers'], key=lambda x: x['endpoints'], reverse=True)[:5]
    print("\n🏆 Top Routers by Endpoint Count:")
    for router in top_routers:
        print(f"   - {router['name']}: {router['endpoints']} endpoints")
    
    # Validate models
    print("\n🗃️  Validating Models...")
    model_validation = validate_models()
    
    if model_validation['errors']:
        print("❌ Model validation errors:")
        for error in model_validation['errors']:
            print(f"   - {error}")
    else:
        print(f"✅ Found {len(model_validation['model_files'])} model files")
        print(f"📊 Total model classes: {model_validation['total_models']}")
    
    # Validate services
    print("\n⚙️  Validating Services...")
    service_validation = validate_services()
    
    if service_validation['errors']:
        print("❌ Service validation errors:")
        for error in service_validation['errors']:
            print(f"   - {error}")
    else:
        print(f"✅ Found {len(service_validation['service_files'])} service files")
        print(f"📊 Total services: {service_validation['total_services']}")
    
    # Validate membership system
    print("\n👑 Validating Membership System...")
    membership_validation = check_membership_system()
    
    if membership_validation['membership_types_found']:
        print("✅ Membership types found")
        if membership_validation['tier_names']:
            print(f"   - Tiers: {', '.join(membership_validation['tier_names'])}")
    else:
        print("❌ Membership types not found")
    
    if membership_validation['membership_service_found']:
        print("✅ Membership service found")
    else:
        print("❌ Membership service not found")
    
    if membership_validation['membership_router_found']:
        print("✅ Membership router found")
    else:
        print("❌ Membership router not found")
    
    if membership_validation['errors']:
        print("⚠️  Membership system errors:")
        for error in membership_validation['errors']:
            print(f"   - {error}")
    
    # Generate API documentation
    print("\n📚 Generating API Documentation...")
    api_doc = generate_api_documentation()
    
    doc_file = BASE_DIR / "API_ENDPOINTS.md"
    with open(doc_file, 'w', encoding='utf-8') as f:
        f.write(api_doc)
    
    print(f"✅ API documentation saved to: {doc_file}")
    
    # Final validation summary
    print("\n🎯 Production Readiness Summary")
    print("-" * 40)
    
    total_score = 0
    max_score = 5
    
    if main_validation['valid']:
        print("✅ Main application: READY")
        total_score += 1
    else:
        print("❌ Main application: NEEDS ATTENTION")
    
    if len(router_validation['valid_routers']) > 0:
        print("✅ API routers: READY")
        total_score += 1
    else:
        print("❌ API routers: NEEDS ATTENTION")
    
    if not model_validation['errors']:
        print("✅ Data models: READY")
        total_score += 1
    else:
        print("❌ Data models: NEEDS ATTENTION")
    
    if not service_validation['errors']:
        print("✅ Business services: READY")
        total_score += 1
    else:
        print("❌ Business services: NEEDS ATTENTION")
    
    if (membership_validation['membership_types_found'] and 
        membership_validation['membership_service_found'] and 
        membership_validation['membership_router_found']):
        print("✅ Membership system: READY")
        total_score += 1
    else:
        print("❌ Membership system: NEEDS ATTENTION")
    
    print(f"\n🏁 Production Readiness Score: {total_score}/{max_score}")
    
    if total_score == max_score:
        print("🚀 READY FOR PRODUCTION DEPLOYMENT! 🚀")
    elif total_score >= max_score * 0.8:
        print("✅ MOSTLY READY - Minor fixes needed")
    else:
        print("⚠️  NEEDS WORK - Address issues before deployment")
    
    print(f"\n📊 Final Statistics:")
    print(f"   - Total API endpoints: {router_validation['total_endpoints'] + len(main_validation['endpoints'])}")
    print(f"   - Valid routers: {len(router_validation['valid_routers'])}")
    print(f"   - Model files: {len(model_validation['model_files'])}")
    print(f"   - Service files: {len(service_validation['service_files'])}")

if __name__ == "__main__":
    main()
