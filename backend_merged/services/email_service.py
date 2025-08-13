"""
Email service for sending verification emails
"""

import os
import logging
from typing import Optional
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        self.smtp_host = os.getenv("SMTP_HOST")
        self.smtp_port = os.getenv("SMTP_PORT")
        self.smtp_username = os.getenv("SMTP_USERNAME")
        self.smtp_password = os.getenv("SMTP_PASSWORD")
        self.from_email = os.getenv("FROM_EMAIL", "noreply@yourapp.com")
    
    async def send_verification_email(self, to_email: str, verification_code: str) -> bool:
        """
        Send email verification code
        """
        try:
            # For now, just log the verification code
            # In production, integrate with actual email service (SendGrid, SES, etc.)
            logger.info(f"📧 Sending verification email to {to_email}")
            logger.info(f"🔑 Verification code: {verification_code}")
            
            # TODO: Implement actual email sending
            # Example with SMTP:
            # import smtplib
            # from email.mime.text import MIMEText
            # from email.mime.multipart import MIMEMultipart
            
            subject = "Verify Your Email Address"
            body = f"""
            Welcome to our app!
            
            Your verification code is: {verification_code}
            
            This code will expire in 15 minutes.
            
            If you didn't create an account, please ignore this email.
            """
            
            print(f"📧 Email would be sent to {to_email}")
            print(f"Subject: {subject}")
            print(f"Body: {body}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to send verification email: {e}")
            return False
    
    async def send_password_reset_email(self, to_email: str, reset_token: str) -> bool:
        """
        Send password reset email
        """
        try:
            logger.info(f"📧 Sending password reset email to {to_email}")
            logger.info(f"🔑 Reset token: {reset_token}")
            
            subject = "Password Reset Request"
            body = f"""
            A password reset was requested for your account.
            
            Reset token: {reset_token}
            
            If you didn't request this, please ignore this email.
            """
            
            print(f"📧 Password reset email would be sent to {to_email}")
            print(f"Subject: {subject}")
            print(f"Body: {body}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to send password reset email: {e}")
            return False

# Convenience functions
email_service = EmailService()

async def send_verification_email(to_email: str, verification_code: str) -> bool:
    """Send verification email - convenience function"""
    return await email_service.send_verification_email(to_email, verification_code)

def send_password_reset_email(to_email: str, reset_code: str) -> bool:
    """Send password reset email - convenience function (sync version)"""
    import asyncio
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(email_service.send_password_reset_email(to_email, reset_code))
    finally:
        loop.close()
