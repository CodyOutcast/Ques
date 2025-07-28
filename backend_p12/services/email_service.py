"""
Tencent Cloud SES (Simple Email Service) integration for sending verification emails
"""
import os
import json
import logging
import hashlib
from typing import Optional
from datetime import datetime
import hmac
import requests
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

class TencentEmailService:
    """Service for sending emails through Tencent Cloud SES"""
    
    def __init__(self):
        self.secret_id = os.getenv('TENCENT_SECRET_ID')
        self.secret_key = os.getenv('TENCENT_SECRET_KEY')
        self.region = os.getenv('TENCENT_SES_REGION', 'ap-guangzhou')  # Configurable region
        self.service = "ses"
        self.version = "2020-10-02"
        self.endpoint = f"https://{self.service}.tencentcloudapi.com"
        
        # Load balancing between sender emails
        self.sender_emails = [
            os.getenv('TENCENT_SENDER_EMAIL', 'ques@ques.site'),
            os.getenv('TENCENT_SENDER_EMAIL_ALT', 'ques@ques.chat')
        ]
        
        if not self.secret_id or not self.secret_key:
            logger.warning("Tencent Cloud credentials not configured. Email sending will use mock mode.")
    
    def _get_sender_email(self, email_address: str) -> str:
        """
        Load balance between sender emails based on recipient email hash
        This ensures consistent sender for the same recipient while distributing load
        """
        # Use hash of recipient email to consistently select sender
        email_hash = hashlib.md5(email_address.encode()).hexdigest()
        sender_index = int(email_hash, 16) % len(self.sender_emails)
        return self.sender_emails[sender_index]
    
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
    
    def send_verification_email(self, to_email: str, code: str, purpose: str, language: str = "en") -> bool:
        """
        Send verification email using Tencent Cloud SES with template
        
        Args:
            to_email: Recipient email address
            code: Verification code
            purpose: Purpose of verification (registration, login, password_reset)
            language: Language for template ("en" for English, "zh" for Chinese)
        
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        try:
            if not self.secret_id or not self.secret_key:
                # Mock mode for development
                logger.info(f"📧 [MOCK] Sending verification email to {to_email}: Code {code} for {purpose} ({language})")
                return True
            
            # Get template ID based on language
            template_id_en = os.getenv('TENCENT_EMAIL_TEMPLATE_ID_EN', os.getenv('TENCENT_EMAIL_TEMPLATE_ID', '33594'))
            template_id_cn = os.getenv('TENCENT_EMAIL_TEMPLATE_ID_CN', '33595')
            
            template_id = template_id_cn if language == "zh" else template_id_en
            sender_email = self._get_sender_email(to_email)  # Use load balancing
            
            if not template_id:
                logger.warning("Template ID not configured. Using fallback method.")
                return self._send_simple_email(to_email, code, purpose, language)
            
            # Prepare API request with template
            timestamp = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
            
            # Template data matching your template: {{verification_code}} and {{expire_time}}
            template_data = {
                "verification_code": code,
                "expire_time": "10"  # 10 minutes validity
            }
            
            payload = {
                "Action": "SendEmail",
                "Version": self.version,
                "Region": self.region,
                "FromEmailAddress": sender_email,
                "Destination": [to_email],
                "Template": {
                    "TemplateID": int(template_id),
                    "TemplateData": json.dumps(template_data)
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
            
            logger.info(f"Verification email sent successfully to {to_email} using template {template_id} ({language}) from {sender_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send verification email to {to_email}: {e}")
            return False
    
    def _send_simple_email(self, to_email: str, code: str, purpose: str, language: str = "en") -> bool:
        """
        Fallback method to send email without template (for development/testing)
        """
        try:
            # Prepare email content matching your template format
            if language == "zh":
                subject_map = {
                    "registration": "邮箱验证 - Ques团队",
                    "login": "登录验证 - Ques团队", 
                    "password_reset": "密码重置 - Ques团队"
                }
                
                subject = subject_map.get(purpose, "验证码 - Ques团队")
                
                # Chinese version of your template
                html_content = f"""
                <html>
                <body>
                    <p>亲爱的用户，</p>
                    <p>您的验证码是 <strong>{code}</strong>。此验证码的有效期为10分钟。</p>
                    <p>请勿与他人分享此验证码。如果您没有请求此验证码，请忽略此邮件。</p>
                    <p>此致,<br>Ques团队</p>
                </body>
                </html>
                """
                
                text_content = f"""亲爱的用户，

您的验证码是 {code}。此验证码的有效期为10分钟。

请勿与他人分享此验证码。如果您没有请求此验证码，请忽略此邮件。

此致,
Ques团队"""
            else:
                # English version (your original template)
                subject_map = {
                    "registration": "Email Verification - Ques Team",
                    "login": "Login Verification - Ques Team", 
                    "password_reset": "Password Reset - Ques Team"
                }
                
                subject = subject_map.get(purpose, "Verification Code - Ques Team")
                
                html_content = f"""
                <html>
                <body>
                    <p>Dear user,</p>
                    <p>Your verification code is <strong>{code}</strong>. This code is valid for 10 minutes.</p>
                    <p>Please do not share this code with others. If you did not request this, please ignore this email.</p>
                    <p>Best regards,<br>Ques Team</p>
                </body>
                </html>
                """
                
                text_content = f"""Dear user,

Your verification code is {code}. This code is valid for 10 minutes.

Please do not share this code with others. If you did not request this, please ignore this email.

Best regards,
Ques Team"""

            # Prepare API request
            timestamp = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
            sender_email = self._get_sender_email(to_email)  # Use load balancing
            
            payload = {
                "Action": "SendEmail",
                "Version": self.version,
                "Region": self.region,
                "FromEmailAddress": sender_email,
                "Destination": [to_email],
                "Subject": subject,
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
            
            logger.info(f"Verification email sent successfully to {to_email} (fallback method) from {sender_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send fallback email to {to_email}: {e}")
            return False

# Global instance
email_service = TencentEmailService()