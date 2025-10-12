# Database Structure - Current Schema (October 2025)

This document describes the current actual database structure as implemented in PostgreSQL database.

## Overview

The database contains **41 tables** supporting:

1. **User Management**: Authentication (Phone/WeChat only), profiles, settings
2. **Location System**: Chinese provinces and cities with hierarchical structure
3. **Project & Institution System**: Projects, agent cards, institutions with user relationships
4. **Messaging & Matching**: Chats, messages, matches between users
5. **Membership & Payments**: Subscription management, transactions, refunds
6. **Security & Privacy**: Settings, consent tracking, audit logs, university verification

## Core Tables

### 1. User Management Tables

#### `users` (Core user table - implied from foreign keys)
Referenced by all user-related tables.

#### `user_profiles`
Stores detailed user profile information.

| Column | Type | Description |
|--------|------|-------------|
| `id` | BIGINT | Primary key |
| `user_id` | BIGINT | Foreign key to users |
| `name` | VARCHAR(100) | User display name |
| `birthday` | DATE | User's birthday |
| `age` | INTEGER | Calculated age |
| `gender` | VARCHAR(50) | User gender |
| `province_id` | INTEGER | FK to provinces |
| `city_id` | INTEGER | FK to cities |
| `location` | VARCHAR(200) | Location string |
| `profile_photo` | TEXT | Profile photo URL |
| `one_sentence_intro` | TEXT | Brief introduction |
| `hobbies` | JSONB | Array of hobbies |
| `languages` | JSONB | Array of languages |
| `skills` | JSONB | Array of skills |
| `resources` | JSONB | Array of resources |
| `goals` | TEXT | User goals |
| `demands` | JSONB | What user is looking for |
| `current_university` | VARCHAR(200) | University name |
| `university_email` | VARCHAR(200) | University email |
| `university_verified` | BOOLEAN | Verification status |
| `wechat_id` | VARCHAR(100) | WeChat ID |
| `wechat_verified` | BOOLEAN | WeChat verification |
| `is_profile_complete` | BOOLEAN | Profile completeness |
| `profile_visibility` | VARCHAR(20) | Visibility setting |
| `project_count` | INTEGER | Number of projects |
| `institution_count` | INTEGER | Number of institutions |
| `last_active` | TIMESTAMP | Last activity time |
| `profile_image_description` | TEXT | AI-generated image description |

**Indexes:** age, birthday, city, gender, completion status

#### `user_auth`
Authentication providers (Phone and WeChat only).

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER | Primary key |
| `user_id` | INTEGER | FK to users |
| `provider_type` | VARCHAR(6) | "PHONE" or "WECHAT" |
| `provider_id` | VARCHAR(255) | Phone number or WeChat ID |
| `password_hash` | VARCHAR(255) | Not used for Phone/WeChat |
| `is_verified` | BOOLEAN | Verification status |
| `is_primary` | BOOLEAN | Primary auth method |
| `created_at` | TIMESTAMP | Creation time |
| `verified_at` | TIMESTAMP | Verification time |
| `last_login` | TIMESTAMP | Last login time |

### 2. Location Tables

#### `provinces`
Chinese provinces and municipalities.

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER | Primary key |
| `name_en` | VARCHAR(100) | English name |
| `name_cn` | VARCHAR(100) | Chinese name |

**Indexes:** name_en, name_cn

#### `cities`
Chinese cities with province references.

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER | Primary key |
| `province_id` | INTEGER | FK to provinces |
| `name_en` | VARCHAR(100) | English name |
| `name_cn` | VARCHAR(100) | Chinese name |

**Indexes:** province_id, name_en, name_cn

### 3. Project System Tables

#### `projects`
Core project information.

| Column | Type | Description |
|--------|------|-------------|
| `project_id` | INTEGER | Primary key |
| `creator_id` | INTEGER | FK to users (project owner) |
| `title` | VARCHAR(200) | Project title |
| `description` | TEXT | Full description |
| `short_description` | VARCHAR(500) | Brief description |
| `long_description` | TEXT | Detailed description |
| `start_time` | TIMESTAMP | Project start date |
| `media_link_id` | INTEGER | Optional media reference |
| `status` | VARCHAR(8) | Project status |
| `category` | VARCHAR(50) | Project category |
| `industry` | VARCHAR(50) | Industry sector |
| `project_type` | VARCHAR(13) | Type of project |
| `stage` | VARCHAR(50) | Current stage |
| `looking_for` | JSON | What project needs |
| `skills_needed` | JSON | Required skills |
| `image_urls` | JSON | Project images |
| `video_url` | VARCHAR(512) | Video URL |
| `demo_url` | VARCHAR(512) | Demo URL |
| `pitch_deck_url` | VARCHAR(512) | Pitch deck URL |
| `funding_goal` | INTEGER | Funding target |
| `equity_offered` | INTEGER | Equity percentage |
| `current_valuation` | INTEGER | Current valuation |
| `revenue` | INTEGER | Current revenue |
| `vector_id` | VARCHAR(255) | Vector DB reference |
| `feature_tags` | JSON | Feature tags |
| `is_active` | BOOLEAN | Active status |
| `is_featured` | BOOLEAN | Featured status |
| `is_verified` | BOOLEAN | Verification status |
| `moderation_status` | VARCHAR(8) | Moderation status |
| `view_count` | INTEGER | View counter |
| `like_count` | INTEGER | Like counter |
| `interest_count` | INTEGER | Interest counter |

#### `project_card_slots`
User project card slots system.

| Column | Type | Description |
|--------|------|-------------|
| `slot_id` | INTEGER | Primary key |
| `user_id` | INTEGER | FK to users |
| `slot_number` | INTEGER | Slot position |
| `slot_name` | VARCHAR(100) | Slot name |
| `status` | VARCHAR(20) | Slot status |
| `source` | VARCHAR(20) | Content source |
| `title` | VARCHAR(200) | Project title |
| `description` | TEXT | Project description |
| `short_description` | VARCHAR(500) | Brief description |
| `category` | VARCHAR(50) | Project category |
| `industry` | VARCHAR(50) | Industry |
| `project_type` | VARCHAR(50) | Project type |
| `stage` | VARCHAR(50) | Project stage |
| `looking_for` | JSON | Requirements |
| `skills_needed` | JSON | Skills needed |
| `image_urls` | JSON | Images |
| `video_url` | VARCHAR(512) | Video URL |
| `demo_url` | VARCHAR(512) | Demo URL |
| `pitch_deck_url` | VARCHAR(512) | Pitch deck |
| `funding_goal` | INTEGER | Funding goal |
| `equity_offered` | INTEGER | Equity offered |
| `current_valuation` | INTEGER | Valuation |
| `revenue` | INTEGER | Revenue |
| `ai_recommendation_id` | VARCHAR(100) | AI recommendation ID |
| `ai_confidence_score` | DOUBLE PRECISION | AI confidence |
| `ai_reasoning` | TEXT | AI reasoning |
| `original_query` | VARCHAR(500) | Original search query |
| `activated_at` | TIMESTAMP | Activation time |
| `project_card_id` | INTEGER | Related project card |

### 4. Institution System Tables

#### `institutions`
Institution/organization information.

| Column | Type | Description |
|--------|------|-------------|
| `id` | BIGINT | Primary key |
| `name` | VARCHAR(255) | Institution name |
| `name_en` | VARCHAR(255) | English name |
| `type` | VARCHAR(50) | Institution type |
| `city_id` | INTEGER | FK to cities |
| `province_id` | INTEGER | FK to provinces |
| `description` | TEXT | Description |
| `website` | VARCHAR(512) | Website URL |
| `logo_url` | VARCHAR(512) | Logo URL |
| `is_verified` | BOOLEAN | Verification status |
| `is_active` | BOOLEAN | Active status |
| `created_at` | TIMESTAMP | Creation time |
| `updated_at` | TIMESTAMP | Update time |

**Indexes:** location, name, type, verification status

#### `user_institutions`
User-institution relationships.

| Column | Type | Description |
|--------|------|-------------|
| `user_id` | BIGINT | FK to users (composite PK) |
| `institution_id` | BIGINT | FK to institutions (composite PK) |
| `role` | VARCHAR(100) | User role |
| `start_date` | DATE | Start date |
| `end_date` | DATE | End date (null if current) |
| `is_current` | BOOLEAN | Current status |
| `position` | VARCHAR(100) | Position/title |
| `department` | VARCHAR(100) | Department |
| `description` | TEXT | Additional details |
| `created_at` | TIMESTAMP | Creation time |
| `updated_at` | TIMESTAMP | Update time |

**Primary Key:** (user_id, institution_id)
**Indexes:** user_id, institution_id, current status, dates

### 5. AI Agent Card System

#### `agent_cards`
AI-generated project recommendation cards.

| Column | Type | Description |
|--------|------|-------------|
| `card_id` | INTEGER | Primary key |
| `project_idea_title` | VARCHAR(300) | Project title |
| `project_scope` | VARCHAR(11) | Project scope |
| `description` | TEXT | Project description |
| `key_features` | JSON | Key features |
| `estimated_timeline` | VARCHAR(50) | Timeline estimate |
| `difficulty_level` | VARCHAR(12) | Difficulty level |
| `required_skills` | JSON | Required skills |
| `similar_examples` | JSON | Similar examples |
| `relevance_score` | DOUBLE PRECISION | AI relevance score |
| `ai_agent_id` | VARCHAR(255) | AI agent identifier |
| `generation_prompt` | TEXT | Generation prompt |
| `generation_timestamp` | TIMESTAMP | Generation time |
| `is_active` | BOOLEAN | Active status |

#### `agent_card_swipes`
User interactions with agent cards.

| Column | Type | Description |
|--------|------|-------------|
| `swipe_id` | INTEGER | Primary key |
| `user_id` | INTEGER | FK to users |
| `card_id` | INTEGER | FK to agent_cards |
| `action` | VARCHAR(5) | Swipe action (LIKE/PASS) |
| `swipe_context` | JSON | Context data |
| `swiped_at` | TIMESTAMP | Swipe time |

#### `agent_card_likes`
Liked agent cards with details.

| Column | Type | Description |
|--------|------|-------------|
| `like_id` | INTEGER | Primary key |
| `user_id` | INTEGER | FK to users |
| `card_id` | INTEGER | FK to agent_cards |
| `interest_level` | INTEGER | Interest level (1-10) |
| `notes` | TEXT | User notes |
| `is_active` | BOOLEAN | Active status |
| `liked_at` | TIMESTAMP | Like time |

#### `user_agent_card_preferences`
User preferences for AI card generation.

| Column | Type | Description |
|--------|------|-------------|
| `preference_id` | INTEGER | Primary key |
| `user_id` | INTEGER | FK to users (unique) |
| `preferred_difficulty_levels` | JSON | Preferred difficulties |
| `preferred_project_scopes` | JSON | Preferred scopes |
| `preferred_skills` | JSON | Preferred skills |
| `excluded_skills` | JSON | Excluded skills |
| `min_relevance_score` | DOUBLE PRECISION | Minimum relevance |
| `max_cards_per_day` | INTEGER | Daily card limit |
| `preferred_timeline_min` | VARCHAR(20) | Min timeline |
| `preferred_timeline_max` | VARCHAR(20) | Max timeline |
| `daily_cards_enabled` | BOOLEAN | Daily cards enabled |
| `weekly_summary_enabled` | BOOLEAN | Weekly summary enabled |

### 6. Messaging & Matching System

#### `matches`
User matches for communication.

| Column | Type | Description |
|--------|------|-------------|
| `match_id` | INTEGER | Primary key |
| `user1_id` | INTEGER | FK to users |
| `user2_id` | INTEGER | FK to users |
| `timestamp` | TIMESTAMP | Match time |
| `is_active` | BOOLEAN | Active status |
| `match_reason` | VARCHAR(200) | Match reason |
| `chat_enabled` | BOOLEAN | Chat permission |
| `video_call_enabled` | BOOLEAN | Video call permission |
| `last_message_at` | TIMESTAMP | Last message time |
| `last_activity_at` | TIMESTAMP | Last activity |
| `compatibility_score` | INTEGER | Compatibility score |

#### `chats`
Chat sessions between users.

| Column | Type | Description |
|--------|------|-------------|
| `chat_id` | INTEGER | Primary key |
| `initiator_id` | INTEGER | FK to users (chat starter) |
| `recipient_id` | INTEGER | FK to users (chat recipient) |
| `status` | VARCHAR(8) | Chat status |
| `created_at` | TIMESTAMP | Creation time |
| `accepted_at` | TIMESTAMP | Acceptance time |
| `last_message_at` | TIMESTAMP | Last message time |
| `greeting_message` | TEXT | Initial greeting |

#### `chat_messages`
Individual messages in chats.

| Column | Type | Description |
|--------|------|-------------|
| `message_id` | INTEGER | Primary key |
| `chat_id` | INTEGER | FK to chats |
| `sender_id` | INTEGER | FK to users |
| `content` | TEXT | Message content |
| `created_at` | TIMESTAMP | Send time |
| `updated_at` | TIMESTAMP | Edit time |
| `is_read` | BOOLEAN | Read status |
| `is_greeting` | BOOLEAN | Greeting message flag |

#### `messages`
Legacy message system (alternative to chat_messages).

| Column | Type | Description |
|--------|------|-------------|
| `message_id` | INTEGER | Primary key |
| `match_id` | INTEGER | FK to matches |
| `sender_id` | INTEGER | FK to users |
| `text` | TEXT | Message text |
| `timestamp` | TIMESTAMP | Send time |
| `is_read` | BOOLEAN | Read status |

### 7. Membership & Payment System

#### `memberships`
User membership/subscription information.

| Column | Type | Description |
|--------|------|-------------|
| `id` | BIGINT | Primary key |
| `user_id` | BIGINT | FK to users (unique) |
| `plan_type` | VARCHAR(20) | Plan type (basic/premium/pro) |
| `receives_total` | INTEGER | Total receives allowed |
| `receives_used` | INTEGER | Receives used this period |
| `receives_remaining` | INTEGER | Remaining receives |
| `monthly_price` | NUMERIC(10,2) | Monthly price |
| `plan_start_date` | DATE | Plan start date |
| `plan_end_date` | DATE | Plan end date |
| `status` | VARCHAR(20) | Status (active/expired/cancelled) |
| `auto_renewal` | BOOLEAN | Auto-renewal enabled |
| `payment_method` | VARCHAR(20) | Payment method |
| `last_payment_date` | DATE | Last payment date |
| `last_reset_date` | DATE | Last quota reset |
| `next_reset_date` | DATE | Next quota reset |

#### `membership_transactions`
Payment transactions for memberships.

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER | Primary key |
| `user_id` | INTEGER | FK to users |
| `order_id` | VARCHAR(100) | Unique order ID |
| `transaction_id` | VARCHAR(100) | Payment transaction ID |
| `amount` | DOUBLE PRECISION | Transaction amount |
| `currency` | VARCHAR(3) | Currency code |
| `payment_method` | VARCHAR(10) | Payment method |
| `payment_status` | VARCHAR(9) | Payment status |
| `plan_type` | VARCHAR(20) | Membership plan |
| `plan_duration_days` | INTEGER | Plan duration |
| `prepay_id` | VARCHAR(100) | Prepayment ID |
| `payment_params` | TEXT | Payment parameters |
| `created_at` | TIMESTAMP | Creation time |
| `paid_at` | TIMESTAMP | Payment completion time |
| `expires_at` | TIMESTAMP | Expiration time |
| `user_ip` | VARCHAR(45) | User IP address |
| `user_agent` | VARCHAR(500) | User agent |
| `error_message` | TEXT | Error message if failed |
| `notification_data` | TEXT | Payment notification data |

#### `payment_refunds`
Payment refund records.

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER | Primary key |
| `transaction_id` | INTEGER | FK to membership_transactions |
| `refund_id` | VARCHAR(100) | Unique refund ID |
| `refund_amount` | DOUBLE PRECISION | Refund amount |
| `refund_reason` | VARCHAR(200) | Refund reason |
| `refund_status` | VARCHAR(20) | Refund status |
| `requested_at` | TIMESTAMP | Request time |
| `processed_at` | TIMESTAMP | Processing time |
| `admin_user_id` | INTEGER | Admin who processed |
| `notes` | TEXT | Admin notes |

### 8. Security & Privacy System

#### `user_account_settings`
Comprehensive user privacy and security settings.

| Column | Type | Description |
|--------|------|-------------|
| `user_id` | BIGINT | Primary key, FK to users |
| `profile_visibility` | VARCHAR(20) | Profile visibility (public/private/friends) |
| `show_online_status` | BOOLEAN | Show online status |
| `allow_messages_from` | VARCHAR(20) | Message permissions |
| `show_location` | BOOLEAN | Show location |
| `show_university` | BOOLEAN | Show university |
| `show_age` | BOOLEAN | Show age |
| `block_screenshots` | BOOLEAN | Block screenshots |
| `require_verification` | BOOLEAN | Require verification for interactions |
| `auto_reject_spam` | BOOLEAN | Auto-reject spam |
| `content_filtering` | VARCHAR(20) | Content filtering level |
| `two_factor_enabled` | BOOLEAN | 2FA enabled |
| `login_notifications` | BOOLEAN | Login notifications |
| `session_timeout_minutes` | INTEGER | Session timeout (minutes) |
| `password_change_required` | BOOLEAN | Force password change |
| `allow_whispers` | BOOLEAN | Allow whisper messages |
| `allow_friend_requests` | BOOLEAN | Allow friend requests |
| `auto_accept_matches` | BOOLEAN | Auto-accept matches |
| `message_read_receipts` | BOOLEAN | Message read receipts |
| `typing_indicators` | BOOLEAN | Typing indicators |
| `data_sharing_consent` | BOOLEAN | Data sharing consent |
| `analytics_tracking` | BOOLEAN | Analytics tracking |
| `personalized_ads` | BOOLEAN | Personalized ads |
| `data_export_requested` | BOOLEAN | Data export requested |
| `marketing_emails` | BOOLEAN | Marketing emails |
| `email_notifications` | BOOLEAN | Email notifications |
| `push_notifications` | BOOLEAN | Push notifications |
| `sms_notifications` | BOOLEAN | SMS notifications |

#### `privacy_consents`
GDPR compliance - privacy consent tracking.

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID | Primary key |
| `user_id` | BIGINT | FK to users |
| `consent_type` | VARCHAR(50) | Type of consent |
| `consent_given` | BOOLEAN | Consent status |
| `consent_version` | VARCHAR(20) | Consent version |
| `ip_address` | INET | IP address when given |
| `user_agent` | TEXT | User agent |
| `created_at` | TIMESTAMP | Creation time |
| `expires_at` | TIMESTAMP | Expiration time |

#### `data_export_requests`
GDPR compliance - data export requests.

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID | Primary key |
| `user_id` | BIGINT | FK to users |
| `request_type` | VARCHAR(20) | Export type (full/partial) |
| `status` | VARCHAR(20) | Request status |
| `export_format` | VARCHAR(10) | Export format (json/csv/xml) |
| `export_url` | TEXT | Download URL |
| `expires_at` | TIMESTAMP | URL expiration |
| `completed_at` | TIMESTAMP | Completion time |

#### `account_actions`
Audit trail for account actions.

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID | Primary key |
| `user_id` | BIGINT | FK to users |
| `action_type` | VARCHAR(30) | Action type |
| `reason` | TEXT | Action reason |
| `metadata` | JSONB | Action metadata |
| `ip_address` | INET | IP address |
| `user_agent` | TEXT | User agent |
| `scheduled_for` | TIMESTAMP | Scheduled execution time |
| `completed_at` | TIMESTAMP | Completion time |
| `created_by` | BIGINT | FK to users (admin) |

#### `security_logs`
Security event logging.

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER | Primary key |
| `user_id` | INTEGER | FK to users (optional) |
| `event_type` | VARCHAR(50) | Event type |
| `event_status` | VARCHAR(20) | Event status |
| `event_description` | VARCHAR(500) | Event description |
| `ip_address` | VARCHAR(45) | IP address |
| `user_agent` | VARCHAR(500) | User agent |
| `provider_type` | VARCHAR(20) | Auth provider |
| `endpoint` | VARCHAR(255) | API endpoint |
| `risk_score` | INTEGER | Risk score |
| `flags` | VARCHAR(255) | Security flags |

#### `university_verifications`
University email verification system.

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID | Primary key |
| `user_id` | BIGINT | FK to users |
| `email` | VARCHAR(255) | University email |
| `university_name` | VARCHAR(255) | University name |
| `domain` | VARCHAR(100) | Email domain |
| `verification_token` | VARCHAR(255) | Verification token (unique) |
| `verified` | BOOLEAN | Verification status |
| `expires_at` | TIMESTAMP | Token expiration |
| `verified_at` | TIMESTAMP | Verification time |
| `attempts` | INTEGER | Verification attempts |

### 9. Authentication & Session Management

#### `refresh_tokens`
JWT refresh token management.

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER | Primary key |
| `user_id` | INTEGER | FK to users |
| `token_hash` | VARCHAR(255) | Hashed token |
| `device_info` | VARCHAR(255) | Device information |
| `ip_address` | VARCHAR(45) | IP address |
| `expires_at` | TIMESTAMP | Expiration time |
| `created_at` | TIMESTAMP | Creation time |
| `last_used` | TIMESTAMP | Last use time |
| `is_revoked` | BOOLEAN | Revocation status |

### 10. Additional Features

#### `ai_recommendation_swipes`
AI recommendation interaction tracking.

| Column | Type | Description |
|--------|------|-------------|
| `swipe_id` | INTEGER | Primary key |
| `user_id` | INTEGER | FK to users |
| `ai_recommendation_id` | VARCHAR(100) | AI recommendation ID |
| `direction` | VARCHAR(10) | Swipe direction |
| `query` | VARCHAR(500) | Original query |
| `saved_to_slot` | INTEGER | Saved to slot number |
| `recommendation_data` | JSON | Recommendation data |

## Authentication System Update

### Phone and WeChat Only
The authentication system now supports **only** two providers:

1. **PHONE**: SMS-based verification
2. **WECHAT**: WeChat OAuth integration

**Removed:** Email authentication has been completely removed from the system.

## Database Statistics

**Current Database:** postgres  
**Total Tables:** 41  
**Implementation Date:** October 2025

### Table Categories:
- **User Management:** 8 tables (users, profiles, auth, settings)
- **Location System:** 2 tables (provinces, cities)
- **Project System:** 3 tables (projects, slots, recommendations)
- **Institution System:** 2 tables (institutions, user_institutions)
- **AI Agent Cards:** 4 tables (cards, swipes, likes, preferences)  
- **Messaging:** 4 tables (matches, chats, chat_messages, messages)
- **Membership:** 5 tables (memberships, transactions, refunds, webhooks, user_memberships)
- **Security & Privacy:** 7 tables (settings, consents, exports, actions, logs, verifications, tokens)
- **Additional Features:** 6 tables (various tracking and logging)

### Key Relationships:
- **Users** → Central entity referenced by all user-related tables
- **Provinces** → **Cities** → **User Profiles** (hierarchical location)
- **Users** ↔ **Institutions** (many-to-many with roles and dates)
- **Users** → **Projects** (one-to-many creator relationship)
- **Users** ↔ **Matches** ↔ **Chats** → **Messages** (communication flow)
- **Users** → **Memberships** → **Transactions** (payment flow)

## Usage Examples

### 1. Authentication (Phone/WeChat Only)

```python
# Phone authentication
user_auth = UserAuth(
    user_id=user_id,
    provider_type="PHONE",
    provider_id="+86138XXXXXXXX",
    is_verified=True,
    is_primary=True
)

# WeChat authentication  
user_auth = UserAuth(
    user_id=user_id,
    provider_type="WECHAT",
    provider_id="wechat_openid_123456",
    is_verified=True,
    is_primary=False
)
```

### 2. Location Selection

```python
# Get all provinces
provinces = session.query(Province).all()

# Get cities for a specific province
cities = session.query(City).filter(City.province_id == province_id).all()

# Update user location in profile
user_profile.province_id = selected_province_id
user_profile.city_id = selected_city_id
```

### 3. Institution Management

```python
# Create an institution
institution = Institution(
    name="清华大学",
    name_en="Tsinghua University",
    type="university",
    city_id=1,  # Beijing
    province_id=1,  # Beijing Municipality
    is_verified=True
)

# Link user to institution
user_institution = UserInstitution(
    user_id=user_id,
    institution_id=institution.id,
    role="student",
    position="Computer Science Major",
    department="Software Engineering",
    is_current=True,
    start_date=date(2021, 9, 1)
)
```

### 4. Project Management

```python
# Create a project
project = Project(
    creator_id=user_id,
    title="AI-Powered Learning Platform",
    description="Educational platform using AI...",
    short_description="AI learning platform for students",
    status="ONGOING",
    category="Education",
    industry="EdTech",
    project_type="software",
    stage="development",
    looking_for=["developers", "investors"],
    skills_needed=["Python", "React", "AI/ML"],
    funding_goal=100000,
    is_active=True
)
```

### 5. Privacy Settings Management

```python
# Update user privacy settings
settings = UserAccountSettings(
    user_id=user_id,
    profile_visibility="public",
    show_online_status=True,
    allow_messages_from="everyone",
    show_location=True,
    show_university=True,
    block_screenshots=False,
    two_factor_enabled=True,
    data_sharing_consent=True
)
```

## Important Schema Notes

### 1. Authentication Changes
- **Only Phone and WeChat** authentication supported
- **No email authentication** - completely removed
- WeChat integration requires proper OAuth setup
- SMS verification required for phone authentication

### 2. Data Types & Constraints
- **UUIDs** used for sensitive tables (settings, privacy, security)
- **JSON/JSONB** extensively used for flexible data (skills, features, etc.)
- **Proper indexing** on foreign keys and frequently queried columns
- **Cascade deletes** configured where appropriate

### 3. Privacy & Security (GDPR Compliant)
- Complete **privacy consent tracking** with versioning
- **Data export system** with secure URLs and expiration
- **Account action audit trail** with IP and user agent logging
- **Comprehensive settings** for privacy and security preferences

### 4. Performance Optimizations
- **Strategic indexing** on user_id, timestamps, status fields
- **JSON columns** for flexible schema without performance penalty
- **Unique constraints** prevent duplicate records
- **Default values** reduce null checks and improve performance

### 5. Business Logic Features
- **Membership system** with quota tracking and auto-renewal
- **AI-driven recommendations** with tracking and analytics
- **Project slots system** for user project organization
- **Comprehensive messaging** with multiple chat systems
- **Institution verification** with role-based relationships

## Migration Considerations

When updating models or schemas:

1. **Check foreign key relationships** - 41 tables with complex relationships
2. **Update authentication flows** - Phone/WeChat only
3. **Maintain GDPR compliance** - Privacy consent and data export systems
4. **Preserve user data** - Especially profiles, projects, and membership data
5. **Test payment flows** - Complex transaction and refund systems

## Development Notes

- **Database:** PostgreSQL with full JSONB support
- **Authentication:** Phone SMS + WeChat OAuth only  
- **Privacy:** Full GDPR compliance with consent tracking
- **Payments:** Complete transaction lifecycle with refunds
- **AI Features:** Agent cards, recommendations, project matching
- **Security:** Comprehensive logging, settings, and session management

This schema represents a mature, production-ready system with comprehensive user management, project collaboration, AI-driven recommendations, and full privacy compliance.