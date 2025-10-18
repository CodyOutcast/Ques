# Missing API Endpoints Implementation Guide

## 🏗️ Implementation Plan for Missing Endpoints

Based on our API analysis, here's detailed guidance for implementing the missing endpoints:

---

## 2. AI Profile Enhancement System ❌

### **What's Needed:**
```python
# New files to create:
- routers/ai_profile_enhancement.py
- services/ai_profile_enhancement_service.py  
- schemas/ai_profile_schemas.py
```

### **Implementation Details:**

#### Database Changes:
```sql
-- Add to user_profiles table or create new table
ALTER TABLE user_profiles ADD COLUMN ai_analysis_data JSONB;
ALTER TABLE user_profiles ADD COLUMN last_ai_analysis TIMESTAMP;

-- Or create dedicated table:
CREATE TABLE ai_profile_analyses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id BIGINT REFERENCES users(id),
    analysis_type VARCHAR(50), -- 'skills', 'personality', 'interests'
    analysis_data JSONB,
    suggestions JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### API Endpoints:
```python
# /api/v1/ai/profile/analyze
POST /ai/profile/analyze
- Input: user_id, analysis_type ('skills', 'personality', 'interests')  
- Uses DeepSeek API to analyze user profile text
- Returns: analysis score, personality insights, improvement suggestions

# /api/v1/ai/profile/suggestions  
GET /ai/profile/suggestions/{user_id}
- Returns: personalized improvement suggestions
- Cached results from previous analysis

# /api/v1/ai/profile/enhance
POST /ai/profile/enhance  
- Input: profile section, enhancement_type
- Auto-generates improved profile descriptions
```

#### Service Implementation:
```python
class AIProfileEnhancementService:
    def analyze_profile(self, user_profile: dict) -> dict:
        # Use DeepSeek API to analyze:
        # - Writing quality of bio/intro
        # - Skills completeness  
        # - Personality indicators
        # - Photo quality assessment
        
    def generate_suggestions(self, analysis: dict) -> List[str]:
        # Generate actionable improvement suggestions
        
    def enhance_text(self, text: str, enhancement_type: str) -> str:
        # Use AI to improve profile text quality
```

---

## 3. Contact Management System ❌

### **What's Needed:**
```python
# New files:
- routers/contacts.py
- services/contact_service.py
- models/contacts.py
- schemas/contact_schemas.py
```

### **Database Schema:**
```sql
CREATE TABLE user_contacts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id BIGINT NOT NULL REFERENCES users(id),
    contact_user_id BIGINT NOT NULL REFERENCES users(id), 
    contact_type VARCHAR(20) DEFAULT 'friend', -- 'friend', 'blocked', 'favorite'
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT,
    UNIQUE(user_id, contact_user_id)
);

CREATE INDEX idx_user_contacts_user_id ON user_contacts(user_id);
CREATE INDEX idx_user_contacts_type ON user_contacts(contact_type);
```

### **API Endpoints:**
```python
# /api/v1/contacts/add
POST /contacts/add
- Input: contact_user_id, contact_type, notes
- Adds user to contacts list

# /api/v1/contacts/get  
GET /contacts/get?type=friend&page=1&limit=20
- Returns: paginated contacts list with user profiles

# /api/v1/contacts/remove
DELETE /contacts/remove/{contact_user_id}
- Removes user from contacts

# /api/v1/contacts/update
PUT /contacts/update/{contact_user_id}  
- Updates contact type or notes

# /api/v1/contacts/search
GET /contacts/search?query=name
- Search within contacts
```

---

## 4. Notification System ❌

### **What's Needed:**
```python
# New files:
- routers/notifications.py
- services/notification_service.py  
- models/notifications.py
- schemas/notification_schemas.py
- services/push_notification_service.py (for mobile)
```

### **Database Schema:**
```sql
CREATE TABLE notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id BIGINT NOT NULL REFERENCES users(id),
    type VARCHAR(50) NOT NULL, -- 'match', 'message', 'swipe', 'system' 
    title VARCHAR(255) NOT NULL,
    body TEXT,
    data JSONB, -- Additional notification data
    read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP
);

CREATE TABLE notification_settings (
    user_id BIGINT PRIMARY KEY REFERENCES users(id),
    email_notifications BOOLEAN DEFAULT TRUE,
    push_notifications BOOLEAN DEFAULT TRUE,
    sms_notifications BOOLEAN DEFAULT FALSE,
    notification_types JSONB DEFAULT '{"matches": true, "messages": true, "swipes": false}'
);

CREATE INDEX idx_notifications_user_id ON notifications(user_id);
CREATE INDEX idx_notifications_type ON notifications(type);
CREATE INDEX idx_notifications_read ON notifications(read);
```

### **API Endpoints:**
```python
# /api/v1/notifications/get
GET /notifications/get?page=1&limit=20&unread_only=false
- Returns: paginated notifications list

# /api/v1/notifications/mark-read  
POST /notifications/mark-read
- Input: notification_ids[]
- Marks notifications as read

# /api/v1/notifications/settings
GET/PUT /notifications/settings  
- Get/Update user notification preferences

# /api/v1/notifications/send (internal)
POST /notifications/send
- For system to send notifications
```

---

## 5. Settings Management System ❌

### **What's Needed:**
Settings split into **Display Preferences** (ignore) vs **Account Settings** (implement):

#### **ACCOUNT SETTINGS (Implement These):**
```python
# New files:
- routers/account_settings.py
- services/account_settings_service.py
- models/account_settings.py
```

#### **Critical Account Settings Database Schema:**
```sql
CREATE TABLE user_account_settings (
    user_id BIGINT PRIMARY KEY REFERENCES users(id),
    
    -- Privacy Settings (CRITICAL)
    profile_visibility VARCHAR(20) DEFAULT 'public', -- 'public', 'private', 'friends'
    show_online_status BOOLEAN DEFAULT TRUE,
    allow_messages_from VARCHAR(20) DEFAULT 'everyone', -- 'everyone', 'matches', 'nobody'
    show_location BOOLEAN DEFAULT TRUE,
    show_university BOOLEAN DEFAULT TRUE,
    
    -- Safety Settings (CRITICAL)  
    block_screenshots BOOLEAN DEFAULT FALSE,
    require_verification BOOLEAN DEFAULT FALSE,
    auto_reject_spam BOOLEAN DEFAULT TRUE,
    
    -- Account Security (CRITICAL)
    two_factor_enabled BOOLEAN DEFAULT FALSE,
    login_notifications BOOLEAN DEFAULT TRUE,
    session_timeout_minutes INTEGER DEFAULT 60,
    
    -- Communication Settings (CRITICAL)
    allow_whispers BOOLEAN DEFAULT TRUE,
    allow_friend_requests BOOLEAN DEFAULT TRUE,
    auto_accept_matches BOOLEAN DEFAULT FALSE,
    
    -- Data & Privacy (CRITICAL)
    data_sharing_consent BOOLEAN DEFAULT FALSE,
    analytics_tracking BOOLEAN DEFAULT TRUE,
    personalized_ads BOOLEAN DEFAULT TRUE,
    
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Account deactivation/deletion tracking
CREATE TABLE account_actions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id BIGINT REFERENCES users(id),
    action_type VARCHAR(20), -- 'deactivate', 'delete', 'reactivate'
    reason TEXT,
    scheduled_for TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### **CRITICAL Account Settings API:**
```python
# /api/v1/settings/account
GET/PUT /settings/account
- Privacy, security, communication settings
- Data sharing preferences  
- Account visibility controls

# /api/v1/settings/privacy
GET/PUT /settings/privacy  
- Who can see profile, send messages
- Location sharing, university visibility
- Screenshot blocking, verification requirements

# /api/v1/settings/security
GET/PUT /settings/security
- Two-factor authentication setup
- Login notifications, session management
- Password change, security alerts

# /api/v1/settings/data-privacy
GET/PUT /settings/data-privacy
- Data sharing consent management
- Analytics tracking preferences
- Personalized ads settings
- Data export/deletion requests

# /api/v1/settings/account/deactivate
POST /settings/account/deactivate
- Temporary account deactivation
- Reason collection, reactivation timeline

# /api/v1/settings/account/delete  
POST /settings/account/delete
- Permanent account deletion request
- GDPR compliance, data removal scheduling
```

---

## 6. Card Tracking System ❌

### **What's Needed:**
```python
# New files:
- routers/card_tracking.py
- services/analytics_service.py
- models/user_interactions.py
```

### **Database Schema:**
```sql
CREATE TABLE card_interactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    viewer_user_id BIGINT REFERENCES users(id),
    viewed_user_id BIGINT REFERENCES users(id), 
    interaction_type VARCHAR(20), -- 'view', 'profile_click', 'image_click', 'share'
    duration_seconds INTEGER,
    interaction_data JSONB, -- Additional context
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE card_views (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    viewer_user_id BIGINT REFERENCES users(id),
    viewed_user_id BIGINT REFERENCES users(id),
    view_duration INTERVAL,
    scroll_percentage FLOAT,
    sections_viewed JSONB, -- Which profile sections were viewed
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(viewer_user_id, viewed_user_id, DATE(created_at))
);

CREATE INDEX idx_card_interactions_viewer ON card_interactions(viewer_user_id);
CREATE INDEX idx_card_interactions_viewed ON card_interactions(viewed_user_id);
```

### **API Endpoints:**
```python
# /api/v1/tracking/views  
POST /tracking/views
- Records card view with duration and engagement metrics
- Input: viewed_user_id, duration, sections_viewed

# /api/v1/tracking/interactions
POST /tracking/interactions  
- Records specific interactions (clicks, shares)
- Input: interaction_type, target_user_id, context

# /api/v1/tracking/analytics/{user_id}
GET /tracking/analytics/{user_id}
- Returns: who viewed your profile, interaction stats
- Privacy controls apply
```

---

## 7. Session-based Chat System ❌

### **What's Needed:**
Current chat system needs restructuring for session management:

```python
# Enhance existing files:
- routers/chats.py (add session management)
- services/chat_service.py (add session logic)
- models/chats.py (add session model)
```

### **Database Enhancement:**
```sql
-- Add to existing chat system
CREATE TABLE chat_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    chat_id UUID REFERENCES chats(id),
    session_type VARCHAR(20) DEFAULT 'casual', -- 'casual', 'project', 'study'
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP,
    session_data JSONB -- Session context, goals, etc.
);

ALTER TABLE messages ADD COLUMN session_id UUID REFERENCES chat_sessions(id);
```

### **Enhanced API:**
```python
# /api/v1/chat/session/start
POST /chat/session/start
- Input: participant_user_id, session_type, initial_message
- Creates focused chat session with context

# /api/v1/chat/session/{session_id}
GET /chat/session/{session_id}  
- Returns: session details, message history, context
- Structured conversation management

# /api/v1/chat/session/{session_id}/end
POST /chat/session/{session_id}/end
- Formally ends session, archives conversation
```

---

## 🚀 **Implementation Priority:**

1. **CRITICAL (Account Security)**: Settings Management - Account & Privacy settings
2. **HIGH**: Contact Management - Essential for user connections  
3. **HIGH**: Notification System - User engagement critical
4. **MEDIUM**: AI Profile Enhancement - Value-add feature
5. **MEDIUM**: Card Tracking - Analytics and insights
6. **LOW**: Session-based Chat - Enhancement to existing system

## 📋 **Implementation Order Recommendation:**

1. Start with **Account Settings** (security-critical)
2. Implement **Contact Management** (core functionality)  
3. Add **Notification System** (user engagement)
4. Enhance with **AI Profile Features** (competitive advantage)
5. Add **Analytics/Tracking** (business intelligence)
6. Refine **Chat Sessions** (user experience improvement)

Each implementation should include comprehensive error handling, rate limiting, and proper authentication/authorization checks.