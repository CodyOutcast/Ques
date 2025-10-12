# Whispers and Province_ID Implementation Summary

**Date**: October 6, 2025

## ✅ What Was Added

### 1. **Whisper Model** (`models/whispers.py`)
Added full Whisper model matching the existing `whispers` table in production database.

**Table Structure**:
- `id`: BIGINT (Primary Key)
- `sender_id`: BIGINT → users.id
- `recipient_id`: BIGINT → users.id
- `greeting_message`: TEXT (required)
- `sender_wechat_id`: VARCHAR(100)
- `swipe_id`: BIGINT → user_swipes.id (optional - links whisper to a specific swipe)
- `is_read`: BOOLEAN (default: false)
- `read_at`: TIMESTAMP
- `reply_to_whisper_id`: BIGINT → whispers.id (self-referential for threading)
- `from_template`: BOOLEAN (default: false)
- `expires_at`: TIMESTAMP
- `created_at`: TIMESTAMP
- `updated_at`: TIMESTAMP

**Relationships Added**:
- `sender` → User (sent_whispers)
- `recipient` → User (received_whispers)
- `swipe` → UserSwipe (whispers)
- `reply_to` → Whisper (self-referential)

### 2. **User Model Updates**
Added whisper relationships to User model:
```python
sent_whispers = relationship("Whisper", foreign_keys="Whisper.sender_id", back_populates="sender")
received_whispers = relationship("Whisper", foreign_keys="Whisper.recipient_id", back_populates="recipient")
```

### 3. **UserSwipe Model Updates**
Added whispers relationship:
```python
whispers = relationship("Whisper", foreign_keys="Whisper.swipe_id", back_populates="swipe")
```

### 4. **Model Registration**
Added Whisper to `models/__init__.py` exports.

## 📋 About Province_ID

### Current State:
- **`province_id` is NOT in the `users` table**
- **`province_id` IS in the `user_profiles` table**

The location data (province_id, city_id, location) is stored in the `user_profiles` table, not the `users` table.

**Schema**:
```sql
user_profiles:
  - province_id → provinces.id
  - city_id → cities.id  
  - location VARCHAR(200)
```

**Relationships Already Exist**:
- `UserProfile.province` → Province
- `UserProfile.city` → City
- `Province.user_profiles` ← back reference
- `City.user_profiles` ← back reference

### Why This Design?
The `users` table is minimal with only authentication/status data:
- id, phone_number, wechat_id, user_status, timestamps

All demographic and profile data (including location) is in `user_profiles`:
- name, birthday, age, gender
- **province_id, city_id, location**
- profile_photo, hobbies, languages, skills, etc.

## 🎯 Usage Examples

### Creating a Whisper:
```python
from models import Whisper

whisper = Whisper(
    sender_id=user1_id,
    recipient_id=user2_id,
    greeting_message="Hey! I noticed we're both interested in...",
    swipe_id=swipe.id,  # Optional: link to the swipe that triggered this
    from_template=False
)
db.add(whisper)
db.commit()
```

### Accessing Whispers:
```python
# Get all whispers sent by a user
sent_whispers = user.sent_whispers

# Get all whispers received by a user
received_whispers = user.received_whispers

# Get whispers related to a specific swipe
swipe_whispers = swipe.whispers
```

### Accessing Location (Province):
```python
# Access user's province through profile
user_province = user.profile.province  # Province object
province_name = user.profile.province.name_cn  # e.g., "广东省"

# Get all users in a province
province = db.query(Province).filter(Province.name_cn == "广东省").first()
users_in_province = [profile.user for profile in province.user_profiles]
```

## ✅ Current Model Status

**6 Active Models** (matching production database):
1. ✅ `users.py` → `users` table
2. ✅ `user_profiles.py` → `user_profiles` table (contains province_id)
3. ✅ `likes.py` → `user_swipes` table
4. ✅ `user_reports.py` → `user_reports` table
5. ✅ `locations.py` → `provinces`, `cities` tables
6. ✅ `whispers.py` → `whispers` table ⭐ **NEW**

## 🔧 Testing

All models tested and working:
```bash
python test_models_simple.py
```

Result: ✅ All model tests passed!

## 📌 Important Notes

1. **Whispers table already existed** in the database - we just added the Python model
2. **Province_ID is in user_profiles**, not users - this is correct design
3. All relationships are properly configured with back_populates
4. Models match actual production database schema
5. Swipe direction constraint: accepts only 'left' or 'right' (not 'like'/'dislike')

## 🚀 Next Steps

If you want to work with whispers in your API:
1. Create WhisperService in `services/whisper_service.py`
2. Add API endpoints in your router
3. Implement whisper templates system
4. Add read status tracking
5. Implement expiration logic
