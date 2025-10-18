-- =====================================================
-- Migration: Add profile_image_description column
-- Date: 2025-10-03
-- Purpose: Store AI-generated descriptions of profile images
-- =====================================================

-- Add profile_image_description column to user_profiles
ALTER TABLE user_profiles 
ADD COLUMN IF NOT EXISTS profile_image_description TEXT NULL;

-- Add index for searching by image description
CREATE INDEX IF NOT EXISTS idx_user_profiles_image_description 
ON user_profiles USING gin(to_tsvector('english', profile_image_description));

-- Add comment
COMMENT ON COLUMN user_profiles.profile_image_description IS 'AI-generated description of profile photo using GLM-4V model';
