"""
Enhanced Notification Service with TPNS Integration
Handles all notification types including push notifications via TPNS
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from enum import Enum
from sqlalchemy.orm import Session

from models.users import User
from services.tpns_service import tpns_service, PushMessage
from services.email_service import EmailService
from services.sms_service import SMSService

logger = logging.getLogger(__name__)

class NotificationType(Enum):
    FRIEND_REQUEST = "friend_request"
    MESSAGE = "message"
    MATCH = "match"
    SYSTEM = "system"
    GIFT = "gift"
    PAYMENT = "payment"
    VERIFICATION = "verification"
    REMINDER = "reminder"

class NotificationPriority(Enum):
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4

class DeliveryChannel(Enum):
    PUSH = "push"
    EMAIL = "email"
    SMS = "sms"
    IN_APP = "in_app"

class NotificationService:
    """Enhanced notification service with multi-channel delivery"""
    
    def __init__(self):
        self.email_service = EmailService()
        self.sms_service = SMSService() if hasattr(locals(), 'SMSService') else None
        logger.info("NotificationService initialized with TPNS integration")
    
    def _get_user_notification_preferences(self, db: Session, user_id: int) -> Dict[str, bool]:
        """Get user notification preferences from database"""
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return self._get_default_preferences()
            
            # In a real implementation, you'd have a notification_preferences table
            # For now, return default preferences
            return {
                "push_notifications": True,
                "email_notifications": True,
                "sms_notifications": False,
                "friend_requests": True,
                "matches": True,
                "messages": True,
                "system": True,
                "gifts": True,
                "payment": True
            }
        except Exception as e:
            logger.error(f"Error getting user preferences: {e}")
            return self._get_default_preferences()
    
    def _get_default_preferences(self) -> Dict[str, bool]:
        """Get default notification preferences"""
        return {
            "push_notifications": True,
            "email_notifications": True,
            "sms_notifications": False,
            "friend_requests": True,
            "matches": True,
            "messages": True,
            "system": True,
            "gifts": True,
            "payment": True
        }
    
    def _should_send_notification(self, preferences: Dict[str, bool], 
                                notification_type: NotificationType,
                                delivery_channel: DeliveryChannel) -> bool:
        """Check if notification should be sent based on user preferences"""
        # Check if the delivery channel is enabled
        channel_key = f"{delivery_channel.value}_notifications"
        if not preferences.get(channel_key, True):
            return False
        
        # Check if the notification type is enabled
        type_key = notification_type.value.replace('_', 's')  # friend_request -> friend_requests
        if type_key == "friend_request":
            type_key = "friend_requests"
        
        return preferences.get(type_key, True)
    
    async def send_notification(self, 
                              db: Session,
                              user_id: int,
                              notification_type: NotificationType,
                              title: str,
                              content: str,
                              custom_data: Optional[Dict[str, Any]] = None,
                              channels: Optional[List[DeliveryChannel]] = None,
                              priority: NotificationPriority = NotificationPriority.NORMAL) -> Dict[str, Any]:
        """Send notification through specified channels"""
        
        if channels is None:
            channels = [DeliveryChannel.PUSH, DeliveryChannel.IN_APP]
        
        results = {}
        preferences = self._get_user_notification_preferences(db, user_id)
        
        # Get user info
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            logger.error(f"User {user_id} not found")
            return {"error": "User not found"}
        
        # Send through each requested channel
        for channel in channels:
            if not self._should_send_notification(preferences, notification_type, channel):
                results[channel.value] = {"skipped": True, "reason": "User preferences"}
                continue
            
            try:
                if channel == DeliveryChannel.PUSH:
                    result = await self._send_push_notification(
                        user_id, title, content, custom_data, priority
                    )
                    results[channel.value] = result
                
                elif channel == DeliveryChannel.EMAIL:
                    result = await self._send_email_notification(
                        user.email, title, content, custom_data
                    )
                    results[channel.value] = result
                
                elif channel == DeliveryChannel.SMS:
                    result = await self._send_sms_notification(
                        user.phone_number, content
                    )
                    results[channel.value] = result
                
                elif channel == DeliveryChannel.IN_APP:
                    result = await self._store_in_app_notification(
                        db, user_id, notification_type, title, content, custom_data
                    )
                    results[channel.value] = result
                
            except Exception as e:
                logger.error(f"Error sending {channel.value} notification: {e}")
                results[channel.value] = {"error": str(e)}
        
        return results
    
    async def _send_push_notification(self, user_id: int, title: str, content: str,
                                    custom_data: Optional[Dict[str, Any]] = None,
                                    priority: NotificationPriority = NotificationPriority.NORMAL) -> Dict[str, Any]:
        """Send push notification via TPNS"""
        try:
            # Enhance custom data with notification metadata
            enhanced_custom_data = {
                "timestamp": datetime.now().isoformat(),
                "priority": priority.value,
                **(custom_data or {})
            }
            
            # Send push notification
            results = tpns_service.send_notification_to_user(
                str(user_id), title, content, enhanced_custom_data
            )
            
            # Log results
            success_count = sum(1 for result in results.values() if result.success)
            logger.info(f"Push notification sent to user {user_id}: {success_count}/{len(results)} platforms successful")
            
            return {
                "success": success_count > 0,
                "platforms": {
                    platform: {
                        "success": result.success,
                        "push_id": result.push_id,
                        "message": result.message,
                        "error_code": result.error_code
                    }
                    for platform, result in results.items()
                }
            }
            
        except Exception as e:
            logger.error(f"Error sending push notification: {e}")
            return {"error": str(e)}
    
    async def _send_email_notification(self, email: str, title: str, content: str,
                                     custom_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Send email notification"""
        try:
            success = await self.email_service.send_notification_email(
                email, title, content, custom_data
            )
            
            return {
                "success": success,
                "message": "Email sent successfully" if success else "Email failed to send"
            }
            
        except Exception as e:
            logger.error(f"Error sending email notification: {e}")
            return {"error": str(e)}
    
    async def _send_sms_notification(self, phone_number: str, content: str) -> Dict[str, Any]:
        """Send SMS notification"""
        try:
            if not self.sms_service:
                return {"skipped": True, "reason": "SMS service not available"}
            
            success = await self.sms_service.send_notification_sms(phone_number, content)
            
            return {
                "success": success,
                "message": "SMS sent successfully" if success else "SMS failed to send"
            }
            
        except Exception as e:
            logger.error(f"Error sending SMS notification: {e}")
            return {"error": str(e)}
    
    async def _store_in_app_notification(self, db: Session, user_id: int,
                                       notification_type: NotificationType,
                                       title: str, content: str,
                                       custom_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Store notification for in-app display"""
        try:
            # In a real implementation, you'd store this in a notifications table
            logger.info(f"Storing in-app notification for user {user_id}: {title}")
            
            # Mock storage - in reality you'd insert into database
            notification_data = {
                "user_id": user_id,
                "type": notification_type.value,
                "title": title,
                "content": content,
                "custom_data": custom_data,
                "created_at": datetime.now().isoformat(),
                "read": False
            }
            
            return {
                "success": True,
                "message": "In-app notification stored",
                "notification_id": f"notif_{user_id}_{int(datetime.now().timestamp())}"
            }
            
        except Exception as e:
            logger.error(f"Error storing in-app notification: {e}")
            return {"error": str(e)}
    
    # Convenience methods for specific notification types
    
    async def send_friend_request_notification(self, db: Session, target_user_id: int,
                                             sender_name: str, sender_id: int,
                                             message: Optional[str] = None) -> Dict[str, Any]:
        """Send friend request notification"""
        title = "New Friend Request"
        content = f"{sender_name} wants to connect with you"
        if message:
            content += f": \"{message}\""
        
        custom_data = {
            "type": "friend_request",
            "sender_id": sender_id,
            "sender_name": sender_name,
            "action": "open_friend_requests"
        }
        
        return await self.send_notification(
            db=db,
            user_id=target_user_id,
            notification_type=NotificationType.FRIEND_REQUEST,
            title=title,
            content=content,
            custom_data=custom_data,
            channels=[DeliveryChannel.PUSH, DeliveryChannel.IN_APP],
            priority=NotificationPriority.NORMAL
        )
    
    async def send_match_notification(self, db: Session, user_id: int, 
                                    match_name: str, match_id: int) -> Dict[str, Any]:
        """Send new match notification"""
        title = "New Match! 🎉"
        content = f"You have a new match with {match_name}"
        
        custom_data = {
            "type": "match",
            "match_id": match_id,
            "match_name": match_name,
            "action": "open_matches"
        }
        
        return await self.send_notification(
            db=db,
            user_id=user_id,
            notification_type=NotificationType.MATCH,
            title=title,
            content=content,
            custom_data=custom_data,
            channels=[DeliveryChannel.PUSH, DeliveryChannel.IN_APP],
            priority=NotificationPriority.HIGH
        )
    
    async def send_message_notification(self, db: Session, user_id: int,
                                      sender_name: str, sender_id: int,
                                      message_preview: str) -> Dict[str, Any]:
        """Send new message notification"""
        title = f"Message from {sender_name}"
        content = message_preview[:100] + "..." if len(message_preview) > 100 else message_preview
        
        custom_data = {
            "type": "message",
            "sender_id": sender_id,
            "sender_name": sender_name,
            "action": "open_chat"
        }
        
        return await self.send_notification(
            db=db,
            user_id=user_id,
            notification_type=NotificationType.MESSAGE,
            title=title,
            content=content,
            custom_data=custom_data,
            channels=[DeliveryChannel.PUSH, DeliveryChannel.IN_APP],
            priority=NotificationPriority.NORMAL
        )
    
    async def send_gift_notification(self, db: Session, user_id: int,
                                   sender_name: str, gift_type: str, amount: int) -> Dict[str, Any]:
        """Send gift received notification"""
        title = f"Gift from {sender_name} 🎁"
        content = f"You received {amount} {gift_type} from {sender_name}"
        
        custom_data = {
            "type": "gift",
            "sender_name": sender_name,
            "gift_type": gift_type,
            "amount": amount,
            "action": "open_gifts"
        }
        
        return await self.send_notification(
            db=db,
            user_id=user_id,
            notification_type=NotificationType.GIFT,
            title=title,
            content=content,
            custom_data=custom_data,
            channels=[DeliveryChannel.PUSH, DeliveryChannel.IN_APP],
            priority=NotificationPriority.NORMAL
        )
    
    async def send_system_notification(self, db: Session, user_id: int,
                                     title: str, content: str,
                                     action: Optional[str] = None) -> Dict[str, Any]:
        """Send system notification"""
        custom_data = {
            "type": "system",
            "action": action or "open_app"
        }
        
        return await self.send_notification(
            db=db,
            user_id=user_id,
            notification_type=NotificationType.SYSTEM,
            title=title,
            content=content,
            custom_data=custom_data,
            channels=[DeliveryChannel.PUSH, DeliveryChannel.IN_APP, DeliveryChannel.EMAIL],
            priority=NotificationPriority.NORMAL
        )
    
    async def send_payment_notification(self, db: Session, user_id: int,
                                      payment_type: str, amount: float,
                                      status: str) -> Dict[str, Any]:
        """Send payment notification"""
        title = "Payment Update"
        if status == "success":
            content = f"Payment of ${amount:.2f} for {payment_type} was successful"
        elif status == "failed":
            content = f"Payment of ${amount:.2f} for {payment_type} failed"
        else:
            content = f"Payment of ${amount:.2f} for {payment_type} is {status}"
        
        custom_data = {
            "type": "payment",
            "payment_type": payment_type,
            "amount": amount,
            "status": status,
            "action": "open_payments"
        }
        
        priority = NotificationPriority.HIGH if status == "failed" else NotificationPriority.NORMAL
        
        return await self.send_notification(
            db=db,
            user_id=user_id,
            notification_type=NotificationType.PAYMENT,
            title=title,
            content=content,
            custom_data=custom_data,
            channels=[DeliveryChannel.PUSH, DeliveryChannel.IN_APP, DeliveryChannel.EMAIL],
            priority=priority
        )
    
    async def send_broadcast_notification(self, db: Session, title: str, content: str,
                                        user_ids: Optional[List[int]] = None,
                                        notification_type: NotificationType = NotificationType.SYSTEM) -> Dict[str, Any]:
        """Send broadcast notification to multiple users or all users"""
        try:
            if user_ids is None:
                # Send to all users - use TPNS broadcast
                results = tpns_service.send_broadcast_notification(title, content)
                return {
                    "broadcast": True,
                    "tpns_results": results
                }
            else:
                # Send to specific users
                results = []
                for user_id in user_ids:
                    result = await self.send_notification(
                        db=db,
                        user_id=user_id,
                        notification_type=notification_type,
                        title=title,
                        content=content,
                        channels=[DeliveryChannel.PUSH, DeliveryChannel.IN_APP]
                    )
                    results.append({"user_id": user_id, "result": result})
                
                return {
                    "broadcast": False,
                    "individual_results": results
                }
                
        except Exception as e:
            logger.error(f"Error sending broadcast notification: {e}")
            return {"error": str(e)}
    
    def bind_user_device(self, user_id: int, device_token: str, platform: str) -> bool:
        """Bind user account to device token for push notifications"""
        try:
            return tpns_service.bind_account(str(user_id), device_token, platform)
        except Exception as e:
            logger.error(f"Error binding user device: {e}")
            return False
    
    def unbind_user_device(self, user_id: int, device_token: str, platform: str) -> bool:
        """Unbind user account from device token"""
        try:
            return tpns_service.unbind_account(str(user_id), device_token, platform)
        except Exception as e:
            logger.error(f"Error unbinding user device: {e}")
            return False


# Global notification service instance
notification_service = NotificationService()