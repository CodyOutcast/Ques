"""
Settings management service for account security and privacy
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import secrets
import hashlib
# import pyotp  # TODO: Add for two-factor authentication
# import qrcode  # TODO: Add for QR code generation
from io import BytesIO
import base64

from models.settings import (
    UserAccountSettings, AccountAction, UserSecuritySettings, 
    PrivacyConsent, DataExportRequest
)
from models.users import User
from schemas.settings_schemas import (
    AccountSettingsResponse, UpdateAccountSettingsRequest,
    PrivacyConsentRequest, AccountActionRequest, DataExportRequest as DataExportRequestSchema,
    EnableTwoFactorRequest, TwoFactorSetupResponse
)
from services.email_service import EmailService
import logging

logger = logging.getLogger(__name__)


class SettingsService:
    """Service for managing user account settings, security, and privacy"""
    
    def __init__(self, db: Session, email_service: EmailService = None):
        self.db = db
        self.email_service = email_service or EmailService()
    
    def get_account_settings(self, user_id: int) -> Optional[AccountSettingsResponse]:
        """Get user account settings, creating defaults if not exists"""
        try:
            settings = self.db.query(UserAccountSettings).filter(
                UserAccountSettings.user_id == user_id
            ).first()
            
            if not settings:
                # Create default settings
                settings = self._create_default_settings(user_id)
            
            return AccountSettingsResponse(
                privacy={
                    'profile_visibility': settings.profile_visibility,
                    'show_online_status': settings.show_online_status,
                    'allow_messages_from': settings.allow_messages_from,
                    'show_location': settings.show_location,
                    'show_university': settings.show_university,
                    'show_age': settings.show_age
                },
                safety={
                    'block_screenshots': settings.block_screenshots,
                    'require_verification': settings.require_verification,
                    'auto_reject_spam': settings.auto_reject_spam,
                    'content_filtering': settings.content_filtering
                },
                security={
                    'two_factor_enabled': settings.two_factor_enabled,
                    'login_notifications': settings.login_notifications,
                    'session_timeout_minutes': settings.session_timeout_minutes,
                    'password_change_required': settings.password_change_required
                },
                communication={
                    'allow_whispers': settings.allow_whispers,
                    'allow_friend_requests': settings.allow_friend_requests,
                    'auto_accept_matches': settings.auto_accept_matches,
                    'message_read_receipts': settings.message_read_receipts,
                    'typing_indicators': settings.typing_indicators
                },
                data_privacy={
                    'data_sharing_consent': settings.data_sharing_consent,
                    'analytics_tracking': settings.analytics_tracking,
                    'personalized_ads': settings.personalized_ads,
                    'data_export_requested': settings.data_export_requested,
                    'marketing_emails': settings.marketing_emails
                },
                notifications={
                    'email_notifications': settings.email_notifications,
                    'push_notifications': settings.push_notifications,
                    'sms_notifications': settings.sms_notifications
                }
            )
        except Exception as e:
            logger.error(f"Error getting account settings for user {user_id}: {e}")
            return None
    
    def update_account_settings(
        self, 
        user_id: int, 
        updates: UpdateAccountSettingsRequest,
        ip_address: str = None,
        user_agent: str = None
    ) -> bool:
        """Update user account settings"""
        try:
            settings = self.db.query(UserAccountSettings).filter(
                UserAccountSettings.user_id == user_id
            ).first()
            
            if not settings:
                settings = self._create_default_settings(user_id)
            
            # Track what's being updated for audit
            changes = {}
            
            # Update privacy settings
            if updates.privacy:
                for field, value in updates.privacy.dict().items():
                    old_value = getattr(settings, field)
                    if old_value != value:
                        changes[f"privacy.{field}"] = {"old": old_value, "new": value}
                        setattr(settings, field, value)
            
            # Update safety settings
            if updates.safety:
                for field, value in updates.safety.dict().items():
                    old_value = getattr(settings, field)
                    if old_value != value:
                        changes[f"safety.{field}"] = {"old": old_value, "new": value}
                        setattr(settings, field, value)
            
            # Update security settings
            if updates.security:
                for field, value in updates.security.dict().items():
                    old_value = getattr(settings, field)
                    if old_value != value:
                        changes[f"security.{field}"] = {"old": old_value, "new": value}
                        setattr(settings, field, value)
            
            # Update communication settings
            if updates.communication:
                for field, value in updates.communication.dict().items():
                    old_value = getattr(settings, field)
                    if old_value != value:
                        changes[f"communication.{field}"] = {"old": old_value, "new": value}
                        setattr(settings, field, value)
            
            # Update data privacy settings
            if updates.data_privacy:
                for field, value in updates.data_privacy.dict().items():
                    old_value = getattr(settings, field)
                    if old_value != value:
                        changes[f"data_privacy.{field}"] = {"old": old_value, "new": value}
                        setattr(settings, field, value)
            
            # Update notification settings
            if updates.notifications:
                for field, value in updates.notifications.dict().items():
                    old_value = getattr(settings, field)
                    if old_value != value:
                        changes[f"notifications.{field}"] = {"old": old_value, "new": value}
                        setattr(settings, field, value)
            
            # Save changes
            self.db.commit()
            
            # Log privacy update action
            if changes:
                self._log_account_action(
                    user_id=user_id,
                    action_type="privacy_update",
                    reason="Settings updated",
                    metadata={"changes": changes},
                    ip_address=ip_address,
                    user_agent=user_agent
                )
            
            logger.info(f"Updated settings for user {user_id}: {list(changes.keys())}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating settings for user {user_id}: {e}")
            return False
    
    def record_privacy_consent(
        self, 
        user_id: int, 
        consent_request: PrivacyConsentRequest,
        ip_address: str = None,
        user_agent: str = None
    ) -> bool:
        """Record user privacy consent for GDPR compliance"""
        try:
            # Check if consent already exists
            existing = self.db.query(PrivacyConsent).filter(
                and_(
                    PrivacyConsent.user_id == user_id,
                    PrivacyConsent.consent_type == consent_request.consent_type
                )
            ).first()
            
            if existing:
                # Update existing consent
                existing.consent_given = consent_request.consent_given
                existing.consent_version = consent_request.consent_version
                existing.ip_address = ip_address
                existing.user_agent = user_agent
                existing.created_at = datetime.utcnow()
            else:
                # Create new consent record
                consent = PrivacyConsent(
                    user_id=user_id,
                    consent_type=consent_request.consent_type,
                    consent_given=consent_request.consent_given,
                    consent_version=consent_request.consent_version,
                    ip_address=ip_address,
                    user_agent=user_agent
                )
                self.db.add(consent)
            
            self.db.commit()
            logger.info(f"Recorded privacy consent for user {user_id}: {consent_request.consent_type}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error recording privacy consent for user {user_id}: {e}")
            return False
    
    def deactivate_account(
        self, 
        user_id: int, 
        reason: str = None,
        ip_address: str = None,
        user_agent: str = None
    ) -> bool:
        """Deactivate user account"""
        try:
            # Update user status
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                return False
            
            user.user_status = 'deactivated'
            
            # Log deactivation action
            self._log_account_action(
                user_id=user_id,
                action_type="deactivate",
                reason=reason or "User requested account deactivation",
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            self.db.commit()
            logger.info(f"Deactivated account for user {user_id}")
            
            # Send confirmation email
            if self.email_service and user.profile and user.profile.email:
                self.email_service.send_account_deactivation_confirmation(
                    user.profile.email, user.profile.name or "User"
                )
            
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deactivating account for user {user_id}: {e}")
            return False
    
    def schedule_account_deletion(
        self, 
        user_id: int, 
        reason: str,
        confirmation_text: str,
        ip_address: str = None,
        user_agent: str = None
    ) -> Optional[Dict[str, Any]]:
        """Schedule account deletion with 30-day grace period"""
        try:
            if confirmation_text != "DELETE MY ACCOUNT":
                raise ValueError("Invalid confirmation text")
            
            # Schedule deletion for 30 days from now
            scheduled_for = datetime.utcnow() + timedelta(days=30)
            
            # Generate confirmation code
            confirmation_code = secrets.token_urlsafe(16)
            
            # Log deletion action
            action = self._log_account_action(
                user_id=user_id,
                action_type="delete",
                reason=reason,
                scheduled_for=scheduled_for,
                metadata={"confirmation_code": confirmation_code},
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            self.db.commit()
            
            # Send confirmation email with cancellation instructions
            user = self.db.query(User).filter(User.id == user_id).first()
            if self.email_service and user and user.profile and user.profile.email:
                self.email_service.send_account_deletion_scheduled(
                    user.profile.email,
                    user.profile.name or "User",
                    scheduled_for,
                    confirmation_code
                )
            
            logger.info(f"Scheduled account deletion for user {user_id}: {scheduled_for}")
            
            return {
                "scheduled_for": scheduled_for,
                "confirmation_code": confirmation_code,
                "data_export_available": True,
                "export_expires_at": scheduled_for - timedelta(days=1)
            }
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error scheduling account deletion for user {user_id}: {e}")
            return None
    
    def request_data_export(
        self, 
        user_id: int, 
        export_request: DataExportRequestSchema
    ) -> Optional[str]:
        """Create data export request for GDPR compliance"""
        try:
            # Check for existing pending requests
            existing = self.db.query(DataExportRequest).filter(
                and_(
                    DataExportRequest.user_id == user_id,
                    DataExportRequest.status.in_(['pending', 'processing'])
                )
            ).first()
            
            if existing:
                return existing.id
            
            # Create new export request
            export_req = DataExportRequest(
                user_id=user_id,
                request_type=export_request.request_type,
                export_format=export_request.export_format,
                status='pending'
            )
            
            self.db.add(export_req)
            self.db.commit()
            
            # Log data export action
            self._log_account_action(
                user_id=user_id,
                action_type="data_export",
                reason="User requested data export",
                metadata={
                    "export_id": str(export_req.id),
                    "export_type": export_request.request_type,
                    "format": export_request.export_format
                }
            )
            
            logger.info(f"Created data export request for user {user_id}: {export_req.id}")
            return str(export_req.id)
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating data export request for user {user_id}: {e}")
            return None
    
    def _create_default_settings(self, user_id: int) -> UserAccountSettings:
        """Create default account settings for user"""
        settings = UserAccountSettings(user_id=user_id)
        self.db.add(settings)
        self.db.commit()
        return settings
    
    def _log_account_action(
        self,
        user_id: int,
        action_type: str,
        reason: str = None,
        scheduled_for: datetime = None,
        metadata: Dict[str, Any] = None,
        ip_address: str = None,
        user_agent: str = None,
        created_by: int = None
    ) -> AccountAction:
        """Log account action for audit trail"""
        action = AccountAction(
            user_id=user_id,
            action_type=action_type,
            reason=reason,
            scheduled_for=scheduled_for,
            action_metadata=metadata,  # Use the renamed field
            ip_address=ip_address,
            user_agent=user_agent,
            created_by=created_by
        )
        
        self.db.add(action)
        return action
    
    def get_security_score(self, user_id: int) -> Dict[str, Any]:
        """Calculate user security score and recommendations"""
        try:
            settings = self.db.query(UserAccountSettings).filter(
                UserAccountSettings.user_id == user_id
            ).first()
            
            if not settings:
                return {"score": 30, "recommendations": ["Complete your security settings"]}
            
            score = 0
            recommendations = []
            
            # Two-factor authentication (30 points)
            if settings.two_factor_enabled:
                score += 30
            else:
                recommendations.append("Enable two-factor authentication for better security")
            
            # Strong privacy settings (20 points)
            if settings.profile_visibility != 'public':
                score += 10
            if settings.allow_messages_from != 'everyone':
                score += 10
            
            # Safety features (20 points)
            if settings.auto_reject_spam:
                score += 10
            if settings.content_filtering in ['moderate', 'strict']:
                score += 10
            
            # Login security (20 points)
            if settings.login_notifications:
                score += 10
            if settings.session_timeout_minutes <= 120:  # 2 hours or less
                score += 10
            
            # Data privacy (10 points)
            if not settings.data_sharing_consent:
                score += 5
            if not settings.personalized_ads:
                score += 5
            
            # Add recommendations based on missing security features
            if score < 70:
                if not settings.two_factor_enabled:
                    recommendations.append("Enable two-factor authentication")
                if settings.profile_visibility == 'public':
                    recommendations.append("Consider making your profile private or friends-only")
                if settings.allow_messages_from == 'everyone':
                    recommendations.append("Restrict who can message you")
                if not settings.login_notifications:
                    recommendations.append("Enable login notifications")
            
            return {
                "score": min(score, 100),
                "recommendations": recommendations[:3]  # Limit to top 3 recommendations
            }
            
        except Exception as e:
            logger.error(f"Error calculating security score for user {user_id}: {e}")
            return {"score": 0, "recommendations": ["Error calculating security score"]}