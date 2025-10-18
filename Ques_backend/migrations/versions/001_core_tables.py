"""Phase 1: Core Tables - Users, Authentication, and Social Features

Revision ID: 001_core_tables
Revises: 
Create Date: 2025-07-29 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_core_tables'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create users table (enhanced from both backends)
    op.create_table('users',
        sa.Column('user_id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('bio', sa.String(length=500), nullable=True),
        sa.Column('verification_status', sa.String(length=50), nullable=False, server_default='pending'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('last_active', sa.DateTime(), nullable=True),
        sa.Column('vector_id', sa.String(length=255), nullable=True),
        sa.Column('feature_tags', sa.JSON(), nullable=True),
        sa.Column('profile_image_url', sa.String(length=512), nullable=True),
        sa.Column('location', sa.String(length=100), nullable=True),
        sa.Column('age', sa.Integer(), nullable=True),
        sa.Column('is_discoverable', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('preferred_match_distance', sa.Integer(), nullable=False, server_default='50'),
        sa.PrimaryKeyConstraint('user_id'),
        sa.CheckConstraint('age IS NULL OR age >= 18', name='users_age_check'),
        sa.CheckConstraint('preferred_match_distance > 0', name='users_distance_check')
    )
    op.create_index(op.f('ix_users_user_id'), 'users', ['user_id'], unique=False)
    op.create_index(op.f('ix_users_vector_id'), 'users', ['vector_id'], unique=False)
    op.create_index(op.f('ix_users_location'), 'users', ['location'], unique=False)
    op.create_index(op.f('ix_users_is_discoverable'), 'users', ['is_discoverable'], unique=False)
    
    # Create authentication provider enum
    auth_provider_enum = postgresql.ENUM('email', 'wechat', 'phone', 'google', name='authprovidertype', create_type=False)
    auth_provider_enum.create(op.get_bind(), checkfirst=True)
    
    # Create user_auth table (multi-provider authentication)
    op.create_table('user_auth',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('provider_type', auth_provider_enum, nullable=False),
        sa.Column('provider_id', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=True),
        sa.Column('is_verified', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_primary', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('failed_login_attempts', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('locked_until', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('verified_at', sa.DateTime(), nullable=True),
        sa.Column('last_login', sa.DateTime(), nullable=True),
        sa.Column('last_failed_login', sa.DateTime(), nullable=True),
        sa.Column('provider_data', sa.String(length=1000), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('provider_type', 'provider_id', name='uq_user_auth_provider')
    )
    op.create_index(op.f('ix_user_auth_id'), 'user_auth', ['id'], unique=False)
    op.create_index(op.f('ix_user_auth_user_id'), 'user_auth', ['user_id'], unique=False)
    op.create_index(op.f('ix_user_auth_provider'), 'user_auth', ['provider_type', 'provider_id'], unique=False)
    
    # Create verification_codes table
    op.create_table('verification_codes',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('provider_type', auth_provider_enum, nullable=False),
        sa.Column('provider_id', sa.String(length=255), nullable=False),
        sa.Column('code', sa.String(length=10), nullable=False),
        sa.Column('hashed_code', sa.String(length=255), nullable=False),
        sa.Column('purpose', sa.String(length=50), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('used_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('attempts', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('max_attempts', sa.Integer(), nullable=False, server_default='3'),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.String(length=500), nullable=True),
        sa.Column('is_rate_limited', sa.Boolean(), nullable=False, server_default='false'),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint('attempts <= max_attempts', name='verification_codes_attempts_check')
    )
    op.create_index(op.f('ix_verification_codes_id'), 'verification_codes', ['id'], unique=False)
    op.create_index(op.f('ix_verification_codes_provider'), 'verification_codes', ['provider_type', 'provider_id'], unique=False)
    op.create_index(op.f('ix_verification_codes_expires_at'), 'verification_codes', ['expires_at'], unique=False)
    
    # Create refresh_tokens table
    op.create_table('refresh_tokens',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('token_hash', sa.String(length=255), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('last_used', sa.DateTime(), nullable=True),
        sa.Column('is_revoked', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('device_id', sa.String(length=255), nullable=True),
        sa.Column('device_name', sa.String(length=100), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.String(length=500), nullable=True),
        sa.Column('parent_token_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['parent_token_id'], ['refresh_tokens.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('token_hash', name='uq_refresh_tokens_token_hash')
    )
    op.create_index(op.f('ix_refresh_tokens_id'), 'refresh_tokens', ['id'], unique=False)
    op.create_index(op.f('ix_refresh_tokens_user_id'), 'refresh_tokens', ['user_id'], unique=False)
    op.create_index(op.f('ix_refresh_tokens_expires_at'), 'refresh_tokens', ['expires_at'], unique=False)
    
    # Create user_features table (normalized feature tags)
    op.create_table('user_features',
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('feature_name', sa.String(length=50), nullable=False),
        sa.Column('confidence_score', sa.Integer(), nullable=False, server_default='100'),
        sa.Column('source', sa.String(length=20), nullable=False, server_default='user'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('user_id', 'feature_name'),
        sa.CheckConstraint('confidence_score >= 0 AND confidence_score <= 100', name='user_features_confidence_check'),
        sa.CheckConstraint('source IN (\'user\', \'ai\', \'inferred\')', name='user_features_source_check')
    )
    op.create_index(op.f('ix_user_features_feature_name'), 'user_features', ['feature_name'], unique=False)
    
    # Create user_links table
    op.create_table('user_links',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('link_url', sa.String(length=512), nullable=False),
        sa.Column('link_type', sa.String(length=50), nullable=True),
        sa.Column('link_title', sa.String(length=100), nullable=True),
        sa.Column('is_verified', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_links_id'), 'user_links', ['id'], unique=False)
    op.create_index(op.f('ix_user_links_user_id'), 'user_links', ['user_id'], unique=False)
    
    # Create user_swipes table (enhanced swipe tracking)
    op.create_table('user_swipes',
        sa.Column('swipe_id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('swiper_id', sa.Integer(), nullable=False),
        sa.Column('target_id', sa.Integer(), nullable=False),
        sa.Column('direction', sa.String(length=20), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('session_id', sa.String(length=100), nullable=True),
        sa.Column('device_type', sa.String(length=20), nullable=True),
        sa.Column('response_time_ms', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['swiper_id'], ['users.user_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['target_id'], ['users.user_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('swipe_id'),
        sa.UniqueConstraint('swiper_id', 'target_id', name='uq_user_swipes_swiper_target'),
        sa.CheckConstraint('swiper_id != target_id', name='user_swipes_no_self_swipe'),
        sa.CheckConstraint('direction IN (\'like\', \'dislike\', \'super_like\')', name='user_swipes_direction_check')
    )
    op.create_index(op.f('ix_user_swipes_swipe_id'), 'user_swipes', ['swipe_id'], unique=False)
    op.create_index(op.f('ix_user_swipes_swiper_id'), 'user_swipes', ['swiper_id'], unique=False)
    op.create_index(op.f('ix_user_swipes_target_id'), 'user_swipes', ['target_id'], unique=False)
    op.create_index(op.f('ix_user_swipes_direction'), 'user_swipes', ['direction'], unique=False)


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('user_swipes')
    op.drop_table('user_links')
    op.drop_table('user_features')
    op.drop_table('refresh_tokens')
    op.drop_table('verification_codes')
    op.drop_table('user_auth')
    op.drop_table('users')
    
    # Drop enum
    auth_provider_enum = postgresql.ENUM('email', 'wechat', 'phone', 'google', name='authprovidertype')
    auth_provider_enum.drop(op.get_bind(), checkfirst=True)
