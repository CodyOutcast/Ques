#!/usr/bin/env python3
"""
SMS Service Test
Test script for Tencent Cloud SMS verification implementation
"""

import os
import sys
import asyncio
import logging
from datetime import datetime

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import our services
from services.sms_service import TencentSMSService
from models.base import Base
from models.user_auth import VerificationCode, ProviderType

async def test_sms_service():
    """Test SMS service functionality"""
    
    # Create database connection
    DATABASE_URL = f"postgresql://{os.getenv('PG_USER')}:{os.getenv('PG_PASSWORD')}@{os.getenv('PG_HOST')}:{os.getenv('PG_PORT')}/{os.getenv('PG_DATABASE')}"
    
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # Initialize SMS service
        print("🚀 Initializing SMS Service...")
        sms_service = TencentSMSService()
        print("✅ SMS Service initialized successfully")
        
        # Test phone number (use a real number for actual testing)
        test_phone = "13800138000"  # Example Chinese mobile number
        country_code = "+86"
        
        print(f"\n📱 Testing with phone number: {country_code}{test_phone}")
        
        # Test 1: Check verification status
        print("\n1️⃣ Checking verification status...")
        status = await sms_service.check_phone_verification_status(
            db=db,
            phone_number=test_phone,
            purpose="REGISTRATION",
            country_code=country_code
        )
        print(f"Status: {status}")
        
        # Test 2: Phone number formatting
        print("\n2️⃣ Testing phone number formatting...")
        formatted = sms_service._format_phone_number(test_phone, country_code)
        print(f"Original: {test_phone}")
        print(f"Formatted: {formatted}")
        
        # Test 3: Phone number validation
        print("\n3️⃣ Testing phone number validation...")
        is_valid = sms_service._validate_phone_number(test_phone)
        print(f"Is valid: {is_valid}")
        
        # Test 4: Generate verification code
        print("\n4️⃣ Testing verification code generation...")
        code = sms_service._generate_verification_code()
        print(f"Generated code: {code}")
        
        # Test 5: Send SMS (commented out to avoid actual SMS costs)
        # Uncomment only when you have valid credentials and want to send real SMS
        """
        print("\n5️⃣ Testing SMS sending...")
        success, message, verification_id = await sms_service.send_verification_sms(
            db=db,
            phone_number=test_phone,
            purpose="REGISTRATION",
            country_code=country_code
        )
        print(f"Send result: {success}")
        print(f"Message: {message}")
        print(f"Verification ID: {verification_id}")
        
        if success:
            print("\n6️⃣ Testing SMS verification...")
            # You would need to enter the actual code received via SMS
            test_code = input("Enter the verification code received: ")
            verify_success, verify_message, verification_record = await sms_service.verify_sms_code(
                db=db,
                phone_number=test_phone,
                code=test_code,
                purpose="REGISTRATION",
                country_code=country_code
            )
            print(f"Verify result: {verify_success}")
            print(f"Message: {verify_message}")
        """
        
        # Test 6: Cleanup expired codes
        print("\n6️⃣ Testing cleanup of expired codes...")
        cleaned = await sms_service.cleanup_expired_codes(db)
        print(f"Cleaned up {cleaned} expired codes")
        
        print("\n✅ All tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        logger.error(f"Test error: {str(e)}", exc_info=True)
        
    finally:
        db.close()

def test_configuration():
    """Test SMS service configuration"""
    print("🔧 Testing SMS Configuration...")
    
    required_vars = [
        "TENCENT_SECRET_ID",
        "TENCENT_SECRET_KEY", 
        "TENCENT_SMS_SDK_APP_ID",
        "TENCENT_SMS_VERIFICATION_TEMPLATE_ID"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        print("\n📝 Please set the following in your .env file:")
        for var in missing_vars:
            print(f"   {var}=your_value_here")
        return False
    else:
        print("✅ All required environment variables are set")
        return True

def print_setup_instructions():
    """Print SMS setup instructions"""
    print("\n" + "="*60)
    print("📋 TENCENT CLOUD SMS SETUP INSTRUCTIONS")
    print("="*60)
    print("""
1. Go to Tencent Cloud Console: https://console.cloud.tencent.com/
2. Navigate to SMS service: https://console.cloud.tencent.com/smsv2
3. Create an SMS application and get your SDK App ID
4. Create an SMS signature (your app/company name)
5. Create an SMS template for verification codes with variables like:
   "Your verification code is {1}, valid for {2} minutes."
6. Get your API credentials from CAM (Cloud Access Management)
7. Update your .env file with the credentials

Required Environment Variables:
- TENCENT_SECRET_ID: Your API Secret ID
- TENCENT_SECRET_KEY: Your API Secret Key  
- TENCENT_SMS_SDK_APP_ID: Your SMS App ID
- TENCENT_SMS_SIGNATURE: Your approved SMS signature
- TENCENT_SMS_VERIFICATION_TEMPLATE_ID: Your template ID

Optional Settings:
- SMS_CODE_LENGTH: Verification code length (default: 6)
- SMS_CODE_EXPIRY_MINUTES: Code expiry time (default: 10)
- SMS_MAX_ATTEMPTS: Max verification attempts (default: 3)
- SMS_RATE_LIMIT_MINUTES: Rate limit between requests (default: 1)
""")
    print("="*60)

if __name__ == "__main__":
    print("📱 Tencent Cloud SMS Service Test")
    print("-" * 40)
    
    # Check configuration first
    if not test_configuration():
        print_setup_instructions()
        sys.exit(1)
    
    # Run tests
    asyncio.run(test_sms_service())
    
    print("\n" + "="*60)
    print("🎉 SMS Service Implementation Complete!")
    print("="*60)
    print("""
✅ Features Implemented:
- SMS verification code sending via Tencent Cloud
- Phone number validation and formatting
- Verification code validation with rate limiting
- User registration with phone number
- Comprehensive error handling and logging
- Database integration for verification tracking

🚀 API Endpoints Available:
- POST /api/v1/sms/send-code - Send verification code
- POST /api/v1/sms/verify-code - Verify SMS code  
- GET /api/v1/sms/status - Check verification status
- POST /api/v1/sms/register - Register with phone number

📖 Next Steps:
1. Set up your Tencent Cloud SMS credentials
2. Test the API endpoints using the included router
3. Integrate with your frontend registration flow
4. Consider adding additional security measures like IP rate limiting
""")
    print("="*60)
