# Database Schema Documentation

**Database**: postgres  
**Host**: gz-postgres-7aqk65fn.sql.tencentcdb.com:29158  
**Generated**: 06/10/2025 14:57

## 📋 Tables Overview

Total Tables: 13

- `cities`
- `institutions`
- `memberships`
- `provinces`
- `user_institutions`
- `user_profiles`
- `user_projects`
- `user_quotas`
- `user_reports`
- `user_swipes`
- `users`
- `verification_codes`
- `whispers`

---

## 📊 Detailed Schema

### `cities`

| Column Name | Data Type | Nullable | Default | Primary Key |
|-------------|-----------|----------|---------|-------------|
| `id` | INTEGER | ❌ No | None | 🔑 Yes |
| `province_id` | INTEGER | ❌ No | None |  |
| `name_en` | VARCHAR(100) | ❌ No | None |  |
| `name_cn` | VARCHAR(100) | ❌ No | None |  |

**Foreign Keys:**

- `province_id` → `provinces.id`

**Indexes:**

- `idx_cities_name_cn`: name_cn
- `idx_cities_name_en`: name_en
- `idx_cities_province_id`: province_id

---

### `institutions`

| Column Name | Data Type | Nullable | Default | Primary Key |
|-------------|-----------|----------|---------|-------------|
| `id` | BIGINT | ❌ No | nextval('institutions_id_seq'::regclass) | 🔑 Yes |
| `name` | VARCHAR(255) | ❌ No | None |  |
| `name_en` | VARCHAR(255) | ✅ Yes | None |  |
| `type` | VARCHAR(50) | ❌ No | None |  |
| `city_id` | INTEGER | ✅ Yes | None |  |
| `province_id` | INTEGER | ✅ Yes | None |  |
| `description` | TEXT | ✅ Yes | None |  |
| `website` | VARCHAR(512) | ✅ Yes | None |  |
| `logo_url` | VARCHAR(512) | ✅ Yes | None |  |
| `is_verified` | BOOLEAN | ❌ No | false |  |
| `is_active` | BOOLEAN | ❌ No | true |  |
| `created_at` | TIMESTAMP | ❌ No | CURRENT_TIMESTAMP |  |
| `updated_at` | TIMESTAMP | ❌ No | CURRENT_TIMESTAMP |  |

**Foreign Keys:**

- `city_id` → `cities.id`
- `province_id` → `provinces.id`

**Indexes:**

- `idx_institutions_location`: city_id, province_id
- `idx_institutions_name`: name
- `idx_institutions_type`: type
- `idx_institutions_verified`: is_verified

---

### `memberships`

| Column Name | Data Type | Nullable | Default | Primary Key |
|-------------|-----------|----------|---------|-------------|
| `id` | BIGINT | ❌ No | nextval('memberships_id_seq'::regclass) | 🔑 Yes |
| `user_id` | BIGINT | ❌ No | None |  |
| `plan_type` | VARCHAR(20) | ❌ No | 'basic'::character varying |  |
| `receives_total` | INTEGER | ❌ No | 3 |  |
| `receives_used` | INTEGER | ❌ No | 0 |  |
| `receives_remaining` | INTEGER | ✅ Yes | None |  |
| `monthly_price` | NUMERIC(10, 2) | ❌ No | 0.00 |  |
| `plan_start_date` | DATE | ❌ No | None |  |
| `plan_end_date` | DATE | ✅ Yes | None |  |
| `status` | VARCHAR(20) | ❌ No | 'active'::character varying |  |
| `auto_renewal` | BOOLEAN | ❌ No | true |  |
| `payment_method` | VARCHAR(20) | ✅ Yes | None |  |
| `last_payment_date` | DATE | ✅ Yes | None |  |
| `last_reset_date` | DATE | ✅ Yes | None |  |
| `next_reset_date` | DATE | ❌ No | None |  |
| `created_at` | TIMESTAMP | ❌ No | CURRENT_TIMESTAMP |  |
| `updated_at` | TIMESTAMP | ❌ No | CURRENT_TIMESTAMP |  |

**Foreign Keys:**

- `user_id` → `users.id`

**Indexes:**

- `idx_memberships_plan_type`: plan_type
- `idx_memberships_reset_date`: next_reset_date
- `idx_memberships_status`: status
- `idx_memberships_user_id`: user_id
- `memberships_user_id_key`: user_id (UNIQUE)

---

### `provinces`

| Column Name | Data Type | Nullable | Default | Primary Key |
|-------------|-----------|----------|---------|-------------|
| `id` | INTEGER | ❌ No | None | 🔑 Yes |
| `name_en` | VARCHAR(100) | ❌ No | None |  |
| `name_cn` | VARCHAR(100) | ❌ No | None |  |

**Indexes:**

- `idx_provinces_name_cn`: name_cn
- `idx_provinces_name_en`: name_en

---

### `user_institutions`

| Column Name | Data Type | Nullable | Default | Primary Key |
|-------------|-----------|----------|---------|-------------|
| `user_id` | BIGINT | ❌ No | None | 🔑 Yes |
| `institution_id` | BIGINT | ❌ No | None | 🔑 Yes |
| `role` | VARCHAR(100) | ✅ Yes | None |  |
| `start_date` | DATE | ✅ Yes | None |  |
| `end_date` | DATE | ✅ Yes | None |  |
| `is_current` | BOOLEAN | ❌ No | true |  |
| `position` | VARCHAR(100) | ✅ Yes | None |  |
| `department` | VARCHAR(100) | ✅ Yes | None |  |
| `description` | TEXT | ✅ Yes | None |  |
| `created_at` | TIMESTAMP | ❌ No | CURRENT_TIMESTAMP |  |
| `updated_at` | TIMESTAMP | ❌ No | CURRENT_TIMESTAMP |  |

**Foreign Keys:**

- `institution_id` → `institutions.id`
- `user_id` → `users.id`

**Indexes:**

- `idx_user_institutions_current`: user_id, is_current
- `idx_user_institutions_dates`: start_date, end_date
- `idx_user_institutions_institution_id`: institution_id
- `idx_user_institutions_user_id`: user_id

---

### `user_profiles`

| Column Name | Data Type | Nullable | Default | Primary Key |
|-------------|-----------|----------|---------|-------------|
| `id` | BIGINT | ❌ No | nextval('user_profiles_id_seq'::regclass) | 🔑 Yes |
| `user_id` | BIGINT | ❌ No | None |  |
| `name` | VARCHAR(100) | ❌ No | None |  |
| `birthday` | DATE | ✅ Yes | None |  |
| `age` | INTEGER | ✅ Yes | None |  |
| `gender` | VARCHAR(50) | ✅ Yes | None |  |
| `province_id` | INTEGER | ✅ Yes | None |  |
| `city_id` | INTEGER | ✅ Yes | None |  |
| `location` | VARCHAR(200) | ✅ Yes | None |  |
| `profile_photo` | TEXT | ✅ Yes | None |  |
| `one_sentence_intro` | TEXT | ✅ Yes | None |  |
| `hobbies` | JSONB | ✅ Yes | None |  |
| `languages` | JSONB | ✅ Yes | None |  |
| `skills` | JSONB | ✅ Yes | None |  |
| `resources` | JSONB | ✅ Yes | None |  |
| `goals` | TEXT | ✅ Yes | None |  |
| `demands` | JSONB | ✅ Yes | None |  |
| `current_university` | VARCHAR(200) | ✅ Yes | None |  |
| `university_email` | VARCHAR(200) | ✅ Yes | None |  |
| `university_verified` | BOOLEAN | ❌ No | false |  |
| `wechat_id` | VARCHAR(100) | ✅ Yes | None |  |
| `wechat_verified` | BOOLEAN | ❌ No | false |  |
| `is_profile_complete` | BOOLEAN | ❌ No | false |  |
| `profile_visibility` | VARCHAR(20) | ❌ No | 'public'::character varying |  |
| `project_count` | INTEGER | ❌ No | 0 |  |
| `institution_count` | INTEGER | ❌ No | 0 |  |
| `last_active` | TIMESTAMP | ✅ Yes | None |  |
| `created_at` | TIMESTAMP | ❌ No | CURRENT_TIMESTAMP |  |
| `updated_at` | TIMESTAMP | ❌ No | CURRENT_TIMESTAMP |  |
| `profile_image_description` | TEXT | ✅ Yes | None |  |

**Foreign Keys:**

- `city_id` → `cities.id`
- `province_id` → `provinces.id`
- `user_id` → `users.id`

**Indexes:**

- `idx_user_profiles_age`: age
- `idx_user_profiles_birthday`: birthday
- `idx_user_profiles_city`: city_id
- `idx_user_profiles_complete`: is_profile_complete
- `idx_user_profiles_gender`: gender
- `idx_user_profiles_institution_count`: institution_count
- `idx_user_profiles_last_active`: last_active
- `idx_user_profiles_location`: location
- `idx_user_profiles_project_count`: project_count
- `idx_user_profiles_province`: province_id
- `idx_user_profiles_university`: current_university
- `idx_user_profiles_user_id`: user_id
- `idx_user_profiles_visibility`: profile_visibility
- `user_profiles_user_id_key`: user_id (UNIQUE)

---

### `user_projects`

| Column Name | Data Type | Nullable | Default | Primary Key |
|-------------|-----------|----------|---------|-------------|
| `id` | BIGINT | ❌ No | nextval('user_projects_id_seq'::regclass) | 🔑 Yes |
| `user_id` | BIGINT | ❌ No | None |  |
| `title` | VARCHAR(200) | ❌ No | None |  |
| `role` | VARCHAR(100) | ✅ Yes | None |  |
| `description` | TEXT | ✅ Yes | None |  |
| `reference_links` | JSONB | ✅ Yes | None |  |
| `project_order` | INTEGER | ❌ No | 0 |  |
| `is_featured` | BOOLEAN | ❌ No | false |  |
| `created_at` | TIMESTAMP | ❌ No | CURRENT_TIMESTAMP |  |
| `updated_at` | TIMESTAMP | ❌ No | CURRENT_TIMESTAMP |  |

**Foreign Keys:**

- `user_id` → `users.id`

**Indexes:**

- `idx_user_projects_featured`: user_id, is_featured
- `idx_user_projects_order`: user_id, project_order
- `idx_user_projects_user_id`: user_id

---

### `user_quotas`

| Column Name | Data Type | Nullable | Default | Primary Key |
|-------------|-----------|----------|---------|-------------|
| `id` | BIGINT | ❌ No | nextval('user_quotas_id_seq'::regclass) | 🔑 Yes |
| `user_id` | BIGINT | ❌ No | None |  |
| `plan_type` | VARCHAR(20) | ❌ No | 'basic'::character varying |  |
| `whispers_sent_today` | INTEGER | ❌ No | 0 |  |
| `whispers_sent_limit` | INTEGER | ❌ No | 5 |  |
| `ai_searches_today` | INTEGER | ❌ No | 0 |  |
| `ai_searches_limit` | INTEGER | ❌ No | 3 |  |
| `quota_reset_date` | DATE | ❌ No | None |  |
| `last_reset_date` | DATE | ✅ Yes | None |  |
| `created_at` | TIMESTAMP | ❌ No | CURRENT_TIMESTAMP |  |
| `updated_at` | TIMESTAMP | ❌ No | CURRENT_TIMESTAMP |  |

**Foreign Keys:**

- `user_id` → `users.id`

**Indexes:**

- `idx_user_quotas_plan_type`: plan_type
- `idx_user_quotas_reset_date`: quota_reset_date
- `idx_user_quotas_user_id`: user_id
- `user_quotas_user_id_key`: user_id (UNIQUE)

---

### `user_reports`

| Column Name | Data Type | Nullable | Default | Primary Key |
|-------------|-----------|----------|---------|-------------|
| `id` | BIGINT | ❌ No | nextval('user_reports_id_seq'::regclass) | 🔑 Yes |
| `reporter_id` | BIGINT | ❌ No | None |  |
| `reported_user_id` | BIGINT | ❌ No | None |  |
| `report_type` | VARCHAR(50) | ❌ No | None |  |
| `description_text` | TEXT | ❌ No | None |  |
| `proof_image_url` | VARCHAR(500) | ✅ Yes | None |  |
| `proof_image_data` | TEXT | ✅ Yes | None |  |
| `status` | VARCHAR(20) | ❌ No | 'pending'::character varying |  |
| `moderator_id` | BIGINT | ✅ Yes | None |  |
| `moderator_notes` | TEXT | ✅ Yes | None |  |
| `moderator_action` | VARCHAR(100) | ✅ Yes | None |  |
| `resolved_at` | TIMESTAMP | ✅ Yes | None |  |
| `created_at` | TIMESTAMP | ❌ No | CURRENT_TIMESTAMP |  |
| `updated_at` | TIMESTAMP | ❌ No | CURRENT_TIMESTAMP |  |

**Foreign Keys:**

- `moderator_id` → `users.id`
- `reported_user_id` → `users.id`
- `reporter_id` → `users.id`

**Indexes:**

- `idx_user_reports_moderator`: moderator_id, status
- `idx_user_reports_reported`: reported_user_id, status
- `idx_user_reports_reporter`: reporter_id, created_at
- `idx_user_reports_status`: status, created_at
- `unique_user_report`: reporter_id, reported_user_id (UNIQUE)

---

### `user_swipes`

| Column Name | Data Type | Nullable | Default | Primary Key |
|-------------|-----------|----------|---------|-------------|
| `id` | BIGINT | ❌ No | nextval('user_swipes_id_seq'::regclass) | 🔑 Yes |
| `swiper_id` | BIGINT | ❌ No | None |  |
| `swiped_user_id` | BIGINT | ❌ No | None |  |
| `swipe_direction` | VARCHAR(10) | ❌ No | None |  |
| `match_score` | NUMERIC(5, 4) | ✅ Yes | None |  |
| `swipe_context` | VARCHAR(200) | ✅ Yes | None |  |
| `triggered_whisper` | BOOLEAN | ❌ No | false |  |
| `created_at` | TIMESTAMP | ❌ No | CURRENT_TIMESTAMP |  |

**Foreign Keys:**

- `swiped_user_id` → `users.id`
- `swiper_id` → `users.id`

**Indexes:**

- `idx_user_swipes_likes`: swiper_id, swipe_direction, created_at
- `idx_user_swipes_swiped`: swiped_user_id, swipe_direction
- `idx_user_swipes_swiper`: swiper_id, created_at
- `idx_user_swipes_whisper`: triggered_whisper, created_at
- `unique_swipe`: swiper_id, swiped_user_id (UNIQUE)

---

### `users`

| Column Name | Data Type | Nullable | Default | Primary Key |
|-------------|-----------|----------|---------|-------------|
| `id` | BIGINT | ❌ No | nextval('users_id_seq'::regclass) | 🔑 Yes |
| `phone_number` | VARCHAR(20) | ✅ Yes | None |  |
| `wechat_id` | VARCHAR(50) | ✅ Yes | None |  |
| `user_status` | VARCHAR(20) | ❌ No | 'inactive'::character varying |  |
| `created_at` | TIMESTAMP | ❌ No | CURRENT_TIMESTAMP |  |
| `updated_at` | TIMESTAMP | ❌ No | CURRENT_TIMESTAMP |  |

**Indexes:**

- `idx_users_created_at`: created_at
- `idx_users_phone`: phone_number
- `idx_users_status`: user_status
- `idx_users_wechat_id`: wechat_id
- `users_phone_number_key`: phone_number (UNIQUE)
- `users_wechat_id_key`: wechat_id (UNIQUE)

---

### `verification_codes`

| Column Name | Data Type | Nullable | Default | Primary Key |
|-------------|-----------|----------|---------|-------------|
| `id` | INTEGER | ❌ No | nextval('verification_codes_id_seq'::regclass) | 🔑 Yes |
| `provider_type` | VARCHAR(50) | ❌ No | None |  |
| `provider_id` | VARCHAR(255) | ❌ No | None |  |
| `code` | VARCHAR(10) | ❌ No | None |  |
| `purpose` | VARCHAR(50) | ❌ No | None |  |
| `expires_at` | TIMESTAMP | ❌ No | None |  |
| `used_at` | TIMESTAMP | ✅ Yes | None |  |
| `created_at` | TIMESTAMP | ❌ No | CURRENT_TIMESTAMP |  |
| `attempts` | INTEGER | ❌ No | 0 |  |

**Indexes:**

- `idx_verification_codes_created_at`: created_at
- `idx_verification_codes_expires_at`: expires_at
- `idx_verification_codes_provider`: provider_type, provider_id

---

### `whispers`

| Column Name | Data Type | Nullable | Default | Primary Key |
|-------------|-----------|----------|---------|-------------|
| `id` | BIGINT | ❌ No | nextval('whispers_id_seq'::regclass) | 🔑 Yes |
| `sender_id` | BIGINT | ❌ No | None |  |
| `recipient_id` | BIGINT | ❌ No | None |  |
| `greeting_message` | TEXT | ❌ No | None |  |
| `sender_wechat_id` | VARCHAR(100) | ✅ Yes | None |  |
| `swipe_id` | BIGINT | ✅ Yes | None |  |
| `is_read` | BOOLEAN | ❌ No | false |  |
| `read_at` | TIMESTAMP | ✅ Yes | None |  |
| `reply_to_whisper_id` | BIGINT | ✅ Yes | None |  |
| `from_template` | BOOLEAN | ❌ No | false |  |
| `expires_at` | TIMESTAMP | ✅ Yes | None |  |
| `created_at` | TIMESTAMP | ❌ No | CURRENT_TIMESTAMP |  |
| `updated_at` | TIMESTAMP | ❌ No | CURRENT_TIMESTAMP |  |

**Foreign Keys:**

- `recipient_id` → `users.id`
- `reply_to_whisper_id` → `whispers.id`
- `sender_id` → `users.id`
- `swipe_id` → `user_swipes.id`

**Indexes:**

- `idx_whispers_created_at`: created_at
- `idx_whispers_expires_at`: expires_at
- `idx_whispers_is_read`: is_read
- `idx_whispers_recipient`: recipient_id
- `idx_whispers_sender`: sender_id

---

