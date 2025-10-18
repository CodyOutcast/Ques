# Tencent TPNS (Push Notification Service) Integration Guide

## Overview

This document provides a complete guide for integrating Tencent TPNS (Tencent Push Notification Service) with the Ques backend system. TPNS allows you to send push notifications to mobile devices (Android and iOS) efficiently and reliably.

## Prerequisites

1. **Tencent Cloud Account**: You need a valid Tencent Cloud account
2. **TPNS Service**: TPNS service must be activated in your Tencent Cloud console
3. **Mobile Apps**: Android and/or iOS mobile applications with FCM/APNS integration

## Setup Steps

### 1. Enable TPNS in Tencent Cloud Console

1. Visit [Tencent Cloud Console](https://console.cloud.tencent.com/)
2. Navigate to **Mobile Push** > **TPNS**
3. Create a new application or select an existing one
4. Get your Access ID and Secret Key for each platform (Android/iOS)

### 2. Configure Environment Variables

Add these variables to your `.env` file:

```env
# Tencent Push Notification Service (TPNS) Configuration
TPNS_ANDROID_ACCESS_ID=your_android_access_id_here
TPNS_ANDROID_SECRET_KEY=your_android_secret_key_here
TPNS_IOS_ACCESS_ID=your_ios_access_id_here
TPNS_IOS_SECRET_KEY=your_ios_secret_key_here
```

**How to get these values:**
1. In TPNS console, go to **Configuration Management** > **Basic Configuration**
2. Copy the Access ID and Secret Key for Android platform
3. Copy the Access ID and Secret Key for iOS platform
4. Replace the placeholder values in your `.env` file

### 3. Mobile App Integration

#### Android (FCM Integration)
```kotlin
// In your Android app, integrate FCM and get device token
FirebaseMessaging.getInstance().token.addOnCompleteListener { task ->
    if (!task.isSuccessful) {
        Log.w(TAG, "Fetching FCM registration token failed", task.exception)
        return@addOnCompleteListener
    }

    // Get new FCM registration token
    val token = task.result
    Log.d(TAG, "FCM Registration Token: $token")
    
    // Send token to your server
    registerDeviceWithServer(token, "android")
}
```

#### iOS (APNS Integration)
```swift
// In your iOS app, register for push notifications
UNUserNotificationCenter.current().requestAuthorization(options: [.alert, .sound, .badge]) { granted, error in
    if granted {
        DispatchQueue.main.async {
            UIApplication.shared.registerForRemoteNotifications()
        }
    }
}

// Handle device token
func application(_ application: UIApplication, didRegisterForRemoteNotificationsWithDeviceToken deviceToken: Data) {
    let token = deviceToken.map { String(format: "%02.2hhx", $0) }.joined()
    print("APNS Token: \(token)")
    
    // Send token to your server
    registerDeviceWithServer(token: token, platform: "ios")
}
```

### 4. API Endpoints

The backend provides several endpoints for TPNS integration:

#### Device Registration
```http
POST /api/v1/tpns/device/register
Authorization: Bearer {token}
Content-Type: application/json

{
  "device_token": "fcm_or_apns_token",
  "platform": "android", // or "ios"
  "app_version": "1.0.0",
  "device_model": "iPhone 13",
  "os_version": "15.0"
}
```

#### Send Test Push Notification
```http
POST /api/v1/tpns/push/test
Authorization: Bearer {token}
Content-Type: application/json

{
  "title": "Test Notification",
  "content": "This is a test push notification",
  "platform": "all",
  "custom_data": {
    "action": "open_app",
    "screen": "home"
  }
}
```

#### Enhanced Notification Sending
```http
POST /api/v1/notifications/send
Authorization: Bearer {token}
Content-Type: application/json

{
  "target_user_id": 123,
  "notification_type": "friend_request",
  "title": "New Friend Request",
  "content": "John wants to connect with you",
  "channels": ["push", "in_app", "email"],
  "priority": "normal",
  "custom_data": {
    "sender_id": 456,
    "action": "open_friend_requests"
  }
}
```

## Notification Types

The system supports several notification types:

1. **Friend Request** (`friend_request`)
   - New friend requests
   - Friend request responses

2. **Match** (`match`)
   - New matches found
   - Match interactions

3. **Message** (`message`)
   - New chat messages
   - Message replies

4. **System** (`system`)
   - App updates
   - System announcements
   - Maintenance notices

5. **Gift** (`gift`)
   - Received gifts
   - Gift confirmations

6. **Payment** (`payment`)
   - Payment confirmations
   - Payment failures
   - Subscription updates

## Usage Examples

### Send Friend Request Notification
```python
from services.notification_service import notification_service
from sqlalchemy.orm import Session

# In your route handler
result = await notification_service.send_friend_request_notification(
    db=db,
    target_user_id=123,
    sender_name="John Doe",
    sender_id=456,
    message="Would love to collaborate on a project!"
)
```

### Send Match Notification
```python
result = await notification_service.send_match_notification(
    db=db,
    user_id=123,
    match_name="Jane Smith",
    match_id=789
)
```

### Send Custom Notification
```python
from services.notification_service import NotificationType, DeliveryChannel, NotificationPriority

result = await notification_service.send_notification(
    db=db,
    user_id=123,
    notification_type=NotificationType.SYSTEM,
    title="App Update Available",
    content="A new version of Ques is available with exciting features!",
    channels=[DeliveryChannel.PUSH, DeliveryChannel.IN_APP],
    priority=NotificationPriority.NORMAL,
    custom_data={
        "action": "open_store",
        "update_version": "2.1.0"
    }
)
```

### Broadcast Notification
```python
# Send to specific users
result = await notification_service.send_broadcast_notification(
    db=db,
    title="Maintenance Notice",
    content="The app will be under maintenance from 2-4 AM UTC",
    user_ids=[123, 456, 789],
    notification_type=NotificationType.SYSTEM
)

# Send to all users
result = await notification_service.send_broadcast_notification(
    db=db,
    title="New Feature Launch",
    content="Check out our new AI matching feature!",
    user_ids=None,  # None means all users
    notification_type=NotificationType.SYSTEM
)
```

## User Preferences

Users can control their notification preferences:

### Get Preferences
```http
GET /api/v1/tpns/preferences
Authorization: Bearer {token}
```

### Update Preferences
```http
PUT /api/v1/tpns/preferences
Authorization: Bearer {token}
Content-Type: application/json

{
  "push_notifications": true,
  "email_notifications": true,
  "sms_notifications": false,
  "friend_requests": true,
  "matches": true,
  "messages": true,
  "system": false,
  "gifts": true,
  "payment": true
}
```

## Push Notification Analytics

### Get Push Statistics
```http
GET /api/v1/tpns/push/statistics/{push_id}?platform=android
Authorization: Bearer {token}
```

Response:
```json
{
  "push_id": "12345",
  "platform": "android",
  "sent_count": 1000,
  "delivered_count": 950,
  "clicked_count": 320,
  "details": {
    "push_active_num": 1000,
    "arrive_num": 950,
    "click_num": 320,
    "clean_num": 45
  }
}
```

## Error Handling

The TPNS service includes comprehensive error handling:

1. **Configuration Errors**: Missing or invalid TPNS credentials
2. **Network Errors**: Connection issues with TPNS API
3. **Authentication Errors**: Invalid signatures or expired tokens
4. **Rate Limiting**: TPNS API rate limits
5. **Platform Errors**: Android/iOS specific issues

Example error response:
```json
{
  "success": false,
  "message": "Android TPNS credentials not configured",
  "error_code": 1001
}
```

## Best Practices

1. **Device Token Management**
   - Register device tokens when users log in
   - Unregister tokens when users log out
   - Handle token refresh on mobile apps

2. **Notification Timing**
   - Consider user time zones
   - Avoid sending notifications during sleeping hours
   - Implement quiet hours feature

3. **Content Guidelines**
   - Keep titles under 50 characters
   - Keep content under 200 characters
   - Use clear, actionable language

4. **Testing**
   - Use test environment for development
   - Test on both Android and iOS
   - Verify notification delivery and interaction

5. **Performance**
   - Batch notifications when possible
   - Use appropriate priority levels
   - Monitor delivery rates and adjust

## Troubleshooting

### Common Issues

1. **Push notifications not delivered**
   - Check TPNS credentials in `.env`
   - Verify device token registration
   - Check TPNS console for error logs

2. **Invalid signature errors**
   - Verify Access ID and Secret Key
   - Check timestamp synchronization
   - Ensure proper URL encoding

3. **Platform-specific issues**
   - Android: Verify FCM integration
   - iOS: Check APNS certificate validity
   - Test with different device types

### Debug Configuration
```http
GET /api/v1/tpns/config
Authorization: Bearer {token}
```

This returns configuration status for debugging:
```json
{
  "android_configured": true,
  "ios_configured": false,
  "region": "ap-guangzhou",
  "api_host": "https://api.tpns.tencent.com",
  "service_initialized": true
}
```

## Security Considerations

1. **Credential Protection**
   - Keep TPNS credentials secure
   - Use environment variables, never hardcode
   - Rotate credentials periodically

2. **User Privacy**
   - Respect user notification preferences
   - Implement opt-out mechanisms
   - Handle sensitive data carefully

3. **Rate Limiting**
   - Implement client-side rate limiting
   - Monitor API usage
   - Use appropriate retry strategies

## Migration and Updates

When updating TPNS integration:

1. Test in development environment first
2. Plan for backward compatibility
3. Update mobile apps if needed
4. Monitor error rates after deployment
5. Have rollback plan ready

## Support and Resources

- [Tencent TPNS Documentation](https://cloud.tencent.com/document/product/548)
- [TPNS Console](https://console.cloud.tencent.com/tpns)
- [API Reference](https://cloud.tencent.com/document/api/548/39064)

For technical support, contact your Tencent Cloud support team or refer to the official documentation.