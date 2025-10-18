-- =====================================================
-- WeChat Mini App Database Schema Setup Script
-- Database: PostgreSQL 15+
-- Purpose: Complete database initialization for user discovery system
-- =====================================================

-- Drop existing tables and types if they exist (for clean setup)
DROP TABLE IF EXISTS user_reports CASCADE;
DROP TABLE IF EXISTS whispers CASCADE;
DROP TABLE IF EXISTS user_swipes CASCADE;
DROP TABLE IF EXISTS user_quotas CASCADE;
DROP TABLE IF EXISTS memberships CASCADE;
DROP TABLE IF EXISTS user_institutions CASCADE;
DROP TABLE IF EXISTS institutions CASCADE;
DROP TABLE IF EXISTS user_projects CASCADE;
DROP TABLE IF EXISTS user_profiles CASCADE;
DROP TABLE IF EXISTS cities CASCADE;
DROP TABLE IF EXISTS provinces CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- Drop existing types
DROP TYPE IF EXISTS user_status_enum CASCADE;
DROP TYPE IF EXISTS profile_visibility_enum CASCADE;
DROP TYPE IF EXISTS plan_type_enum CASCADE;
DROP TYPE IF EXISTS membership_status_enum CASCADE;
DROP TYPE IF EXISTS payment_method_enum CASCADE;
DROP TYPE IF EXISTS swipe_direction_enum CASCADE;
DROP TYPE IF EXISTS report_type_enum CASCADE;
DROP TYPE IF EXISTS report_status_enum CASCADE;

-- =====================================================
-- 1. CREATE USERS TABLE
-- =====================================================
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    phone_number VARCHAR(20) UNIQUE NULL,
    wechat_id VARCHAR(50) UNIQUE NULL,
    user_status VARCHAR(20) NOT NULL DEFAULT 'inactive',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Ensure at least one authentication method is provided
    CONSTRAINT chk_auth_method CHECK (
        phone_number IS NOT NULL OR wechat_id IS NOT NULL
    ),
    CONSTRAINT chk_user_status CHECK (
        user_status IN ('active', 'inactive', 'suspended', 'deleted')
    )
);

-- Create indexes for users table
CREATE INDEX idx_users_phone ON users(phone_number);
CREATE INDEX idx_users_wechat_id ON users(wechat_id);
CREATE INDEX idx_users_status ON users(user_status);
CREATE INDEX idx_users_created_at ON users(created_at);

-- Create trigger to update updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- 2. CREATE PROVINCES AND CITIES TABLES
-- =====================================================
CREATE TABLE provinces (
    id INTEGER PRIMARY KEY,
    name_en VARCHAR(100) NOT NULL,
    name_cn VARCHAR(100) NOT NULL
);

CREATE INDEX idx_provinces_name_en ON provinces(name_en);
CREATE INDEX idx_provinces_name_cn ON provinces(name_cn);

CREATE TABLE cities (
    id INTEGER PRIMARY KEY,
    province_id INTEGER NOT NULL,
    name_en VARCHAR(100) NOT NULL,
    name_cn VARCHAR(100) NOT NULL,
    
    FOREIGN KEY (province_id) REFERENCES provinces(id) ON DELETE CASCADE
);

CREATE INDEX idx_cities_province_id ON cities(province_id);
CREATE INDEX idx_cities_name_en ON cities(name_en);
CREATE INDEX idx_cities_name_cn ON cities(name_cn);

-- =====================================================
-- 3. CREATE USER PROFILES TABLE
-- =====================================================
CREATE TABLE user_profiles (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    birthday DATE NULL,
    age INTEGER NULL,
    gender VARCHAR(50) NULL,
    province_id INTEGER NULL,
    city_id INTEGER NULL,
    location VARCHAR(200) NULL,
    profile_photo TEXT NULL,
    one_sentence_intro TEXT NULL,
    hobbies JSONB NULL,
    languages JSONB NULL,
    skills JSONB NULL,
    resources JSONB NULL,
    goals TEXT NULL,
    demands JSONB NULL,
    current_university VARCHAR(200) NULL,
    university_email VARCHAR(200) NULL,
    university_verified BOOLEAN NOT NULL DEFAULT FALSE,
    wechat_id VARCHAR(100) NULL,
    wechat_verified BOOLEAN NOT NULL DEFAULT FALSE,
    is_profile_complete BOOLEAN NOT NULL DEFAULT FALSE,
    profile_visibility VARCHAR(20) NOT NULL DEFAULT 'public',
    project_count INTEGER NOT NULL DEFAULT 0,
    institution_count INTEGER NOT NULL DEFAULT 0,
    last_active TIMESTAMP NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (province_id) REFERENCES provinces(id) ON DELETE SET NULL,
    FOREIGN KEY (city_id) REFERENCES cities(id) ON DELETE SET NULL,
    CONSTRAINT chk_profile_visibility CHECK (
        profile_visibility IN ('public', 'friends', 'private')
    )
);

-- Create indexes for user_profiles
CREATE INDEX idx_user_profiles_user_id ON user_profiles(user_id);
CREATE INDEX idx_user_profiles_location ON user_profiles(location);
CREATE INDEX idx_user_profiles_province ON user_profiles(province_id);
CREATE INDEX idx_user_profiles_city ON user_profiles(city_id);
CREATE INDEX idx_user_profiles_age ON user_profiles(age);
CREATE INDEX idx_user_profiles_birthday ON user_profiles(birthday);
CREATE INDEX idx_user_profiles_gender ON user_profiles(gender);
CREATE INDEX idx_user_profiles_visibility ON user_profiles(profile_visibility);
CREATE INDEX idx_user_profiles_project_count ON user_profiles(project_count DESC);
CREATE INDEX idx_user_profiles_institution_count ON user_profiles(institution_count DESC);
CREATE INDEX idx_user_profiles_last_active ON user_profiles(last_active);
CREATE INDEX idx_user_profiles_university ON user_profiles(current_university);
CREATE INDEX idx_user_profiles_complete ON user_profiles(is_profile_complete);

-- Create trigger for user_profiles updated_at
CREATE TRIGGER trigger_user_profiles_updated_at
    BEFORE UPDATE ON user_profiles
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- 4. CREATE AGE CALCULATION TRIGGER
-- =====================================================
CREATE OR REPLACE FUNCTION calculate_age_from_birthday()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.birthday IS NOT NULL THEN
        NEW.age := EXTRACT(YEAR FROM AGE(CURRENT_DATE, NEW.birthday));
    ELSE
        NEW.age := NULL;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_age_on_birthday
    BEFORE INSERT OR UPDATE OF birthday ON user_profiles
    FOR EACH ROW
    EXECUTE FUNCTION calculate_age_from_birthday();

-- =====================================================
-- 5. CREATE USER PROJECTS TABLE
-- =====================================================
CREATE TABLE user_projects (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    title VARCHAR(200) NOT NULL,
    role VARCHAR(100) NULL,
    description TEXT NULL,
    reference_links JSONB NULL,
    project_order INT NOT NULL DEFAULT 0,
    is_featured BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_user_projects_user_id ON user_projects(user_id);
CREATE INDEX idx_user_projects_order ON user_projects(user_id, project_order);
CREATE INDEX idx_user_projects_featured ON user_projects(user_id, is_featured);

CREATE TRIGGER trigger_user_projects_updated_at
    BEFORE UPDATE ON user_projects
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- 6. CREATE INSTITUTIONS TABLE
-- =====================================================
CREATE TABLE institutions (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    name_en VARCHAR(255) NULL,
    type VARCHAR(50) NOT NULL,
    city_id INTEGER NULL,
    province_id INTEGER NULL,
    description TEXT NULL,
    website VARCHAR(512) NULL,
    logo_url VARCHAR(512) NULL,
    is_verified BOOLEAN NOT NULL DEFAULT FALSE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (city_id) REFERENCES cities(id) ON DELETE SET NULL,
    FOREIGN KEY (province_id) REFERENCES provinces(id) ON DELETE SET NULL
);

CREATE INDEX idx_institutions_name ON institutions(name);
CREATE INDEX idx_institutions_type ON institutions(type);
CREATE INDEX idx_institutions_location ON institutions(city_id, province_id);
CREATE INDEX idx_institutions_verified ON institutions(is_verified);

CREATE TRIGGER trigger_institutions_updated_at
    BEFORE UPDATE ON institutions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- 7. CREATE USER INSTITUTIONS TABLE
-- =====================================================
CREATE TABLE user_institutions (
    user_id BIGINT NOT NULL,
    institution_id BIGINT NOT NULL,
    role VARCHAR(100) NULL,
    start_date DATE NULL,
    end_date DATE NULL,
    is_current BOOLEAN NOT NULL DEFAULT TRUE,
    position VARCHAR(100) NULL,
    department VARCHAR(100) NULL,
    description TEXT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    PRIMARY KEY (user_id, institution_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (institution_id) REFERENCES institutions(id) ON DELETE CASCADE
);

CREATE INDEX idx_user_institutions_user_id ON user_institutions(user_id);
CREATE INDEX idx_user_institutions_institution_id ON user_institutions(institution_id);
CREATE INDEX idx_user_institutions_current ON user_institutions(user_id, is_current);
CREATE INDEX idx_user_institutions_dates ON user_institutions(start_date, end_date);

CREATE TRIGGER trigger_user_institutions_updated_at
    BEFORE UPDATE ON user_institutions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- 8. CREATE MEMBERSHIPS TABLE
-- =====================================================
CREATE TABLE memberships (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT UNIQUE NOT NULL,
    plan_type VARCHAR(20) NOT NULL DEFAULT 'basic',
    receives_total INT NOT NULL DEFAULT 3,
    receives_used INT NOT NULL DEFAULT 0,
    receives_remaining INT GENERATED ALWAYS AS (receives_total - receives_used) STORED,
    monthly_price DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    plan_start_date DATE NOT NULL,
    plan_end_date DATE NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    auto_renewal BOOLEAN NOT NULL DEFAULT TRUE,
    payment_method VARCHAR(20) NULL,
    last_payment_date DATE NULL,
    last_reset_date DATE NULL,
    next_reset_date DATE NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    
    CONSTRAINT chk_plan_type CHECK (plan_type IN ('basic', 'pro')),
    CONSTRAINT chk_status CHECK (status IN ('active', 'expired', 'cancelled')),
    CONSTRAINT chk_payment_method CHECK (payment_method IS NULL OR payment_method IN ('wechat_pay', 'alipay', 'manual')),
    CONSTRAINT chk_plan_receives CHECK (
        (plan_type = 'basic' AND receives_total = 3 AND monthly_price = 0.00) OR
        (plan_type = 'pro' AND receives_total = 10 AND monthly_price = 10.00)
    )
);

CREATE INDEX idx_memberships_user_id ON memberships(user_id);
CREATE INDEX idx_memberships_status ON memberships(status);
CREATE INDEX idx_memberships_plan_type ON memberships(plan_type);
CREATE INDEX idx_memberships_reset_date ON memberships(next_reset_date);

CREATE TRIGGER trigger_memberships_updated_at
    BEFORE UPDATE ON memberships
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- 9. CREATE USER QUOTAS TABLE
-- =====================================================
CREATE TABLE user_quotas (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT UNIQUE NOT NULL,
    plan_type VARCHAR(20) NOT NULL DEFAULT 'basic',
    whispers_sent_today INT NOT NULL DEFAULT 0,
    whispers_sent_limit INT NOT NULL DEFAULT 5,
    ai_searches_today INT NOT NULL DEFAULT 0,
    ai_searches_limit INT NOT NULL DEFAULT 3,
    quota_reset_date DATE NOT NULL,
    last_reset_date DATE NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    
    CONSTRAINT chk_quota_plan_type CHECK (plan_type IN ('basic', 'pro')),
    CONSTRAINT chk_quota_limits CHECK (
        (plan_type = 'basic' AND whispers_sent_limit = 5 AND ai_searches_limit = 3) OR
        (plan_type = 'pro' AND whispers_sent_limit = 15 AND ai_searches_limit = 10)
    )
);

CREATE INDEX idx_user_quotas_user_id ON user_quotas(user_id);
CREATE INDEX idx_user_quotas_reset_date ON user_quotas(quota_reset_date);
CREATE INDEX idx_user_quotas_plan_type ON user_quotas(plan_type);

CREATE TRIGGER trigger_user_quotas_updated_at
    BEFORE UPDATE ON user_quotas
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- 10. CREATE USER SWIPES TABLE
-- =====================================================
CREATE TABLE user_swipes (
    id BIGSERIAL PRIMARY KEY,
    swiper_id BIGINT NOT NULL,
    swiped_user_id BIGINT NOT NULL,
    swipe_direction VARCHAR(10) NOT NULL,
    match_score DECIMAL(5,4) NULL,
    swipe_context VARCHAR(200) NULL,
    triggered_whisper BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (swiper_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (swiped_user_id) REFERENCES users(id) ON DELETE CASCADE,
    
    CONSTRAINT chk_swipe_direction CHECK (swipe_direction IN ('left', 'right')),
    CONSTRAINT unique_swipe UNIQUE (swiper_id, swiped_user_id)
);

CREATE INDEX idx_user_swipes_swiper ON user_swipes(swiper_id, created_at);
CREATE INDEX idx_user_swipes_swiped ON user_swipes(swiped_user_id, swipe_direction);
CREATE INDEX idx_user_swipes_likes ON user_swipes(swiper_id, swipe_direction, created_at);
CREATE INDEX idx_user_swipes_whisper ON user_swipes(triggered_whisper, created_at);

-- =====================================================
-- 11. CREATE WHISPERS TABLE
-- =====================================================
CREATE TABLE whispers (
    id BIGSERIAL PRIMARY KEY,
    sender_id BIGINT NOT NULL,
    recipient_id BIGINT NOT NULL,
    greeting_message TEXT NOT NULL,
    sender_wechat_id VARCHAR(100) NULL,
    swipe_id BIGINT NULL,
    is_read BOOLEAN NOT NULL DEFAULT FALSE,
    read_at TIMESTAMP NULL,
    reply_to_whisper_id BIGINT NULL,
    from_template BOOLEAN NOT NULL DEFAULT FALSE,
    expires_at TIMESTAMP NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (sender_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (recipient_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (swipe_id) REFERENCES user_swipes(id) ON DELETE SET NULL,
    FOREIGN KEY (reply_to_whisper_id) REFERENCES whispers(id) ON DELETE SET NULL
);

CREATE INDEX idx_whispers_sender ON whispers(sender_id);
CREATE INDEX idx_whispers_recipient ON whispers(recipient_id);
CREATE INDEX idx_whispers_created_at ON whispers(created_at);
CREATE INDEX idx_whispers_is_read ON whispers(is_read);
CREATE INDEX idx_whispers_expires_at ON whispers(expires_at);

CREATE TRIGGER trigger_whispers_updated_at
    BEFORE UPDATE ON whispers
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- 12. CREATE USER REPORTS TABLE
-- =====================================================
CREATE TABLE user_reports (
    id BIGSERIAL PRIMARY KEY,
    reporter_id BIGINT NOT NULL,
    reported_user_id BIGINT NOT NULL,
    report_type VARCHAR(50) NOT NULL,
    description_text TEXT NOT NULL,
    proof_image_url VARCHAR(500) NULL,
    proof_image_data TEXT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    moderator_id BIGINT NULL,
    moderator_notes TEXT NULL,
    moderator_action VARCHAR(100) NULL,
    resolved_at TIMESTAMP NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (reporter_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (reported_user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (moderator_id) REFERENCES users(id) ON DELETE SET NULL,
    
    CONSTRAINT chk_report_type CHECK (
        report_type IN ('inappropriate_behavior', 'fake_profile', 'harassment', 'spam', 'other')
    ),
    CONSTRAINT chk_report_status CHECK (
        status IN ('pending', 'under_review', 'resolved', 'dismissed')
    ),
    CONSTRAINT unique_user_report UNIQUE (reporter_id, reported_user_id)
);

CREATE INDEX idx_user_reports_reporter ON user_reports(reporter_id, created_at);
CREATE INDEX idx_user_reports_reported ON user_reports(reported_user_id, status);
CREATE INDEX idx_user_reports_status ON user_reports(status, created_at);
CREATE INDEX idx_user_reports_moderator ON user_reports(moderator_id, status);

CREATE TRIGGER trigger_user_reports_updated_at
    BEFORE UPDATE ON user_reports
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- 13. CREATE PROJECT/INSTITUTION COUNT UPDATE TRIGGERS
-- =====================================================

-- Function to update project count
CREATE OR REPLACE FUNCTION update_user_project_count()
RETURNS TRIGGER AS $$
DECLARE
    target_user_id BIGINT;
    total_count INTEGER;
BEGIN
    IF TG_OP = 'DELETE' THEN
        target_user_id := OLD.user_id;
    ELSE
        target_user_id := NEW.user_id;
    END IF;

    SELECT COUNT(*) INTO total_count
    FROM user_projects
    WHERE user_id = target_user_id;

    UPDATE user_profiles
    SET project_count = total_count
    WHERE user_id = target_user_id;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_user_projects_count_insert
    AFTER INSERT ON user_projects
    FOR EACH ROW
    EXECUTE FUNCTION update_user_project_count();

CREATE TRIGGER trigger_user_projects_count_delete
    AFTER DELETE ON user_projects
    FOR EACH ROW
    EXECUTE FUNCTION update_user_project_count();

-- Function to update institution count
CREATE OR REPLACE FUNCTION update_user_institution_count()
RETURNS TRIGGER AS $$
DECLARE
    target_user_id BIGINT;
    total_count INTEGER;
BEGIN
    IF TG_OP = 'DELETE' THEN
        target_user_id := OLD.user_id;
    ELSE
        target_user_id := NEW.user_id;
    END IF;

    SELECT COUNT(*) INTO total_count
    FROM user_institutions
    WHERE user_id = target_user_id;

    UPDATE user_profiles
    SET institution_count = total_count
    WHERE user_id = target_user_id;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_user_institutions_count_insert
    AFTER INSERT ON user_institutions
    FOR EACH ROW
    EXECUTE FUNCTION update_user_institution_count();

CREATE TRIGGER trigger_user_institutions_count_delete
    AFTER DELETE ON user_institutions
    FOR EACH ROW
    EXECUTE FUNCTION update_user_institution_count();

-- =====================================================
-- 14. CREATE HELPFUL FUNCTIONS
-- =====================================================

-- Function to check birthdays and increment age (run daily via cron)
CREATE OR REPLACE FUNCTION check_birthday_and_increment_age()
RETURNS void AS $$
BEGIN
    UPDATE user_profiles 
    SET age = age + 1
    WHERE birthday IS NOT NULL 
      AND EXTRACT(MONTH FROM birthday) = EXTRACT(MONTH FROM CURRENT_DATE)
      AND EXTRACT(DAY FROM birthday) = EXTRACT(DAY FROM CURRENT_DATE)
      AND age IS NOT NULL;
END;
$$ LANGUAGE plpgsql;

-- Function to reset daily quotas (run daily via cron)
CREATE OR REPLACE FUNCTION reset_daily_quotas()
RETURNS void AS $$
BEGIN
    UPDATE user_quotas
    SET whispers_sent_today = 0,
        ai_searches_today = 0,
        last_reset_date = CURRENT_DATE,
        quota_reset_date = CURRENT_DATE + INTERVAL '1 day'
    WHERE quota_reset_date <= CURRENT_DATE;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- SETUP COMPLETE
-- =====================================================

-- Print success message
DO $$
BEGIN
    RAISE NOTICE '====================================================';
    RAISE NOTICE 'Database schema setup completed successfully!';
    RAISE NOTICE '====================================================';
    RAISE NOTICE 'Tables created:';
    RAISE NOTICE '  1. users';
    RAISE NOTICE '  2. provinces';
    RAISE NOTICE '  3. cities';
    RAISE NOTICE '  4. user_profiles';
    RAISE NOTICE '  5. user_projects';
    RAISE NOTICE '  6. institutions';
    RAISE NOTICE '  7. user_institutions';
    RAISE NOTICE '  8. memberships';
    RAISE NOTICE '  9. user_quotas';
    RAISE NOTICE '  10. user_swipes';
    RAISE NOTICE '  11. whispers';
    RAISE NOTICE '  12. user_reports';
    RAISE NOTICE '';
    RAISE NOTICE 'Next steps:';
    RAISE NOTICE '  1. Load location data: psql -d your_db -f load_locations.sql';
    RAISE NOTICE '  2. Set up cron jobs for daily functions';
    RAISE NOTICE '  3. Configure vector database connection';
    RAISE NOTICE '====================================================';
END $$;
