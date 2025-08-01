#!/usr/bin/env python3
"""
Production deployment configuration and health checks for Ques Backend
"""

import os
import sys
import subprocess
import time
import requests
from typing import Dict, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProductionDeployment:
    """Production deployment manager"""
    
    def __init__(self):
        self.health_check_url = "http://localhost:8000/health"
        self.info_url = "http://localhost:8000/api/v1/info"
        
    def validate_environment(self) -> bool:
        """Validate production environment variables"""
        required_vars = [
            'PG_HOST', 'PG_PASSWORD', 'SECRET_KEY', 'JWT_SECRET_KEY',
            'DEEPSEEK_API_KEY', 'TENCENT_SECRET_ID', 'TENCENT_SECRET_KEY'
        ]
        
        missing = []
        for var in required_vars:
            if not os.getenv(var):
                missing.append(var)
        
        if missing:
            logger.error(f"Missing required environment variables: {missing}")
            return False
        
        # Check for placeholder values
        placeholders = []
        wechat_app_id = os.getenv('WECHAT_APP_ID', '')
        wechat_secret = os.getenv('WECHAT_SECRET', '')
        
        if wechat_app_id.startswith('your_'):
            placeholders.append('WECHAT_APP_ID')
        if wechat_secret.startswith('your_'):
            placeholders.append('WECHAT_SECRET')
        
        if placeholders:
            logger.warning(f"Placeholder values detected: {placeholders}")
            logger.warning("WeChat OAuth will not work until real credentials are provided")
        
        return True
    
    def run_security_checks(self) -> bool:
        """Run security validation checks"""
        logger.info("🔒 Running security checks...")
        
        # Check if we're in production mode
        env = os.getenv('ENVIRONMENT', '').lower()
        if env != 'production':
            logger.warning(f"ENVIRONMENT is '{env}', not 'production'")
        
        # Check secret key strength
        secret_key = os.getenv('SECRET_KEY', '')
        if len(secret_key) < 32:
            logger.error("SECRET_KEY is too short (minimum 32 characters)")
            return False
        
        # Check if debug is disabled
        debug = os.getenv('DEBUG', 'false').lower()
        if debug == 'true':
            logger.error("DEBUG mode is enabled in production")
            return False
        
        logger.info("✅ Security checks passed")
        return True
    
    def check_database_connection(self) -> bool:
        """Check database connectivity"""
        logger.info("🗄️ Checking database connection...")
        
        try:
            from dependencies.db import get_db
            from sqlalchemy import text
            
            db = next(get_db())
            result = db.execute(text("SELECT 1"))
            db.close()
            
            logger.info("✅ Database connection successful")
            return True
        except Exception as e:
            logger.error(f"❌ Database connection failed: {e}")
            return False
    
    def check_external_services(self) -> Dict[str, bool]:
        """Check external service connectivity"""
        logger.info("🌐 Checking external services...")
        
        services = {}
        
        # Check Vector DB
        try:
            vectordb_endpoint = os.getenv('VECTORDB_ENDPOINT')
            if vectordb_endpoint:
                response = requests.get(f"{vectordb_endpoint}/health", timeout=5)
                services['vectordb'] = response.status_code == 200
            else:
                services['vectordb'] = False
        except:
            services['vectordb'] = False
        
        # Check DeepSeek API
        try:
            deepseek_key = os.getenv('DEEPSEEK_API_KEY')
            if deepseek_key:
                # Simple validation - don't actually call the API in checks
                services['deepseek'] = len(deepseek_key) > 10
            else:
                services['deepseek'] = False
        except:
            services['deepseek'] = False
        
        for service, status in services.items():
            status_icon = "✅" if status else "❌"
            logger.info(f"{status_icon} {service}: {'OK' if status else 'FAILED'}")
        
        return services
    
    def start_production_server(self):
        """Start the production server with optimal settings"""
        logger.info("🚀 Starting production server...")
        
        # Production uvicorn command
        cmd = [
            'uvicorn', 'main:app',
            '--host', '0.0.0.0',
            '--port', '8000',
            '--workers', '4',
            '--worker-class', 'uvicorn.workers.UvicornWorker',
            '--access-log',
            '--no-use-colors',
            '--loop', 'uvloop'
        ]
        
        # Only enable auto-reload in development
        if os.getenv('ENVIRONMENT') == 'development':
            cmd.append('--reload')
        
        logger.info(f"Running: {' '.join(cmd)}")
        subprocess.run(cmd)
    
    def health_check(self, max_retries: int = 5) -> bool:
        """Perform health check on running server"""
        logger.info("🏥 Performing health check...")
        
        for attempt in range(max_retries):
            try:
                response = requests.get(self.health_check_url, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    logger.info(f"✅ Health check passed: {data.get('status', 'unknown')}")
                    return True
            except Exception as e:
                logger.warning(f"Health check attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2)
        
        logger.error("❌ Health check failed after all retries")
        return False
    
    def get_deployment_info(self) -> Dict[str, Any]:
        """Get deployment information"""
        try:
            response = requests.get(self.info_url, timeout=5)
            if response.status_code == 200:
                return response.json()
        except:
            pass
        return {}
    
    def run_full_deployment_check(self) -> bool:
        """Run complete deployment validation"""
        logger.info("🔍 Running full deployment validation...")
        
        checks = [
            ("Environment Variables", self.validate_environment),
            ("Security", self.run_security_checks),
            ("Database", self.check_database_connection),
        ]
        
        all_passed = True
        for check_name, check_func in checks:
            logger.info(f"Running {check_name} check...")
            if not check_func():
                logger.error(f"❌ {check_name} check failed")
                all_passed = False
            else:
                logger.info(f"✅ {check_name} check passed")
        
        # External services are optional but good to check
        self.check_external_services()
        
        if all_passed:
            logger.info("🎉 All deployment checks passed!")
            logger.info("Ready for production deployment")
        else:
            logger.error("💥 Some deployment checks failed")
            logger.error("Please fix the issues before deploying to production")
        
        return all_passed

def main():
    """Main deployment script"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Ques Backend Production Deployment')
    parser.add_argument('action', choices=['check', 'start', 'health'], 
                       help='Action to perform')
    parser.add_argument('--environment', choices=['development', 'staging', 'production'],
                       default='development', help='Environment to deploy to')
    
    args = parser.parse_args()
    
    # Set environment
    os.environ['ENVIRONMENT'] = args.environment
    
    deployment = ProductionDeployment()
    
    if args.action == 'check':
        success = deployment.run_full_deployment_check()
        sys.exit(0 if success else 1)
    
    elif args.action == 'start':
        if args.environment == 'production':
            # Run full check before starting production
            if not deployment.run_full_deployment_check():
                logger.error("Pre-deployment checks failed. Aborting.")
                sys.exit(1)
        
        deployment.start_production_server()
    
    elif args.action == 'health':
        success = deployment.health_check()
        if success:
            info = deployment.get_deployment_info()
            if info:
                logger.info(f"Deployment info: {info}")
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
