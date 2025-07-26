"""
Tencent Cloud SES (Simple Email Service) integration for sending verification emails
"""
import os
import json
import logging
from typing import Optional
from datetime import datetime
import hmac
import hashlib
import requests
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

class TencentEmailService:
    """Service for sending emails through Tencent Cloud SES"""
    
    def __init__(self):
        self.secret_id = os.getenv('TENCENT_SECRET_ID')
        self.secret_key = os.getenv('TENCENT_SECRET_KEY')
        self.region = "ap-hongkong"  # or your preferred region
        self.service = "ses"
        self.version = "2020-10-02"
        self.endpoint = f"https://{self.service}.tencentcloudapi.com"
        
        if not self.secret_id or not self.secret_key:
            logger.warning("Tencent Cloud credentials not configured. Email sending will use mock mode.")
    
    def _sign(self, secret_key: bytes, message: str) -> bytes:
        """Generate HMAC-SHA256 signature"""
        if isinstance(secret_key, str):
            secret_key = secret_key.encode('utf-8')
        return hmac.new(secret_key, message.encode('utf-8'), hashlib.sha256).digest()
    
    def _get_authorization(self, payload: str, timestamp: str) -> str:
        """Generate Tencent Cloud API authorization header"""
        if not self.secret_id or not self.secret_key:
            return ""
            
        # Create canonical request
        http_method = "POST"
        canonical_uri = "/"
        canonical_querystring = ""
        canonical_headers = f"content-type:application/json; charset=utf-8\nhost:{self.service}.tencentcloudapi.com\n"
        signed_headers = "content-type;host"
        hashed_request_payload = hashlib.sha256(payload.encode('utf-8')).hexdigest()
        
        canonical_request = f"{http_method}\n{canonical_uri}\n{canonical_querystring}\n{canonical_headers}\n{signed_headers}\n{hashed_request_payload}"
        
        # Create string to sign
        algorithm = "TC3-HMAC-SHA256"
        date = timestamp[:10]
        credential_scope = f"{date}/{self.service}/tc3_request"
        hashed_canonical_request = hashlib.sha256(canonical_request.encode('utf-8')).hexdigest()
        string_to_sign = f"{algorithm}\n{timestamp}\n{credential_scope}\n{hashed_canonical_request}"
        
        # Calculate signature
        secret_date = self._sign(f"TC3{self.secret_key}".encode('utf-8'), date)
        secret_service = self._sign(secret_date, self.service)
        secret_signing = self._sign(secret_service, "tc3_request")
        signature = hmac.new(secret_signing, string_to_sign.encode('utf-8'), hashlib.sha256).hexdigest()
        
        # Create authorization header
        authorization = f"{algorithm} Credential={self.secret_id}/{credential_scope}, SignedHeaders={signed_headers}, Signature={signature}"
        return authorization
    
    def send_verification_email(self, to_email: str, code: str, purpose: str) -> bool:
        """
        Send verification email using Tencent Cloud SES
        
        Args:
            to_email: Recipient email address
            code: Verification code
            purpose: Purpose of verification (registration, login, password_reset)
        
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        try:
            if not self.secret_id or not self.secret_key:
                # Mock mode for development
                logger.info(f"📧 [MOCK] Sending verification email to {to_email}: Code {code} for {purpose}")
                return True
            
            # Prepare email content
            subject_map = {
                "registration": "Welcome to Project Tinder - Verify Your Email",
                "login": "Project Tinder - Login Verification Code",
                "password_reset": "Project Tinder - Password Reset Code"
            }
            
            subject = subject_map.get(purpose, "Project Tinder - Verification Code")
            
            html_content = f"""
            <html>
            <body>
                <h2>Project Tinder</h2>
                <p>Your verification code is: <strong style="font-size: 24px; color: #007bff;">{code}</strong></p>
                <p>This code will expire in 10 minutes.</p>
                <p>If you didn't request this code, please ignore this email.</p>
                <br>
                <p>Best regards,<br>Project Tinder Team</p>
            </body>
            </html>
            """
            
            text_content = f"""
            Project Tinder
            
            Your verification code is: {code}
            
            This code will expire in 10 minutes.
            If you didn't request this code, please ignore this email.
            
            Best regards,
            Project Tinder Team
            """
            
            # Prepare API request
            timestamp = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
            
            payload = {
                "Action": "SendEmail",
                "Version": self.version,
                "Region": self.region,
                "FromEmailAddress": "noreply@projecttinder.com",  # Configure your verified sender
                "Destination": [to_email],
                "Subject": subject,
                "ReplyToAddresses": ["noreply@projecttinder.com"],
                "Template": {
                    "TemplateData": json.dumps({
                        "code": code,
                        "purpose": purpose
                    })
                },
                "Simple": {
                    "Subject": subject,
                    "Html": html_content,
                    "Text": text_content
                }
            }
            
            payload_str = json.dumps(payload)
            authorization = self._get_authorization(payload_str, timestamp)
            
            headers = {
                "Authorization": authorization,
                "Content-Type": "application/json; charset=utf-8",
                "Host": f"{self.service}.tencentcloudapi.com",
                "X-TC-Action": "SendEmail",
                "X-TC-Timestamp": timestamp,
                "X-TC-Version": self.version,
                "X-TC-Region": self.region
            }
            
            # Send request
            response = requests.post(self.endpoint, headers=headers, data=payload_str, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            if "Error" in result:
                logger.error(f"Tencent SES API error: {result['Error']}")
                return False
            
            logger.info(f"Verification email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send verification email to {to_email}: {e}")
            return False

# Global instance
email_service = TencentEmailService()
