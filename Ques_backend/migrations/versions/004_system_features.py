"""Phase 4: System Features - Security, Moderation, and Analytics

Revision ID: 004_system_features
Revises: 003_projects_content
Create Date: 2025-07-29 13:30:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '004_system_features'
down_revision = '003_projects_content'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create security_logs table
    op.create_table('security_logs',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('event_type', sa.String(length=50), nullable=False),
        sa.Column('event_status', sa.String(length=20), nullable=False),
        sa.Column('event_description', sa.String(length=500), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.String(length=500), nullable=True),
        sa.Column('provider_type', sa.String(length=20), nullable=True),
        sa.Column('endpoint', sa.String(length=100), nullable=True),
        sa.Column('risk_score', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('flags', sa.String(length=200), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint('event_status IN (\'success\', \'failure\', \'suspicious\')', name='security_logs_status_check'),
        sa.CheckConstraint('risk_score >= 0 AND risk_score <= 100', name='security_logs_risk_check')
    )
    op.create_index(op.f('ix_security_logs_id'), 'security_logs', ['id'], unique=False)
    op.create_index(op.f('ix_security_logs_user_id'), 'security_logs', ['user_id'], unique=False)
    op.create_index(op.f('ix_security_logs_event_type'), 'security_logs', ['event_type'], unique=False)
    op.create_index(op.f('ix_security_logs_created_at'), 'security_logs', ['created_at'], unique=False)
    op.create_index(op.f('ix_security_logs_ip_address'), 'security_logs', ['ip_address'], unique=False)
    
    # Create user_sessions table
    op.create_table('user_sessions',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('session_token', sa.String(length=255), nullable=False),
        sa.Column('device_id', sa.String(length=255), nullable=True),
        sa.Column('device_name', sa.String(length=100), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.String(length=500), nullable=True),
        sa.Column('location', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('last_activity', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('session_token', name='uq_user_sessions_session_token')
    )
    op.create_index(op.f('ix_user_sessions_id'), 'user_sessions', ['id'], unique=False)
    op.create_index(op.f('ix_user_sessions_user_id'), 'user_sessions', ['user_id'], unique=False)
    op.create_index(op.f('ix_user_sessions_expires_at'), 'user_sessions', ['expires_at'], unique=False)
    
    # Create user_blocks table
    op.create_table('user_blocks',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('blocker_id', sa.Integer(), nullable=False),
        sa.Column('blocked_id', sa.Integer(), nullable=False),
        sa.Column('reason', sa.String(length=100), nullable=True),
        sa.Column('block_type', sa.String(length=20), nullable=False, server_default='full'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('unblocked_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['blocked_id'], ['users.user_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['blocker_id'], ['users.user_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('blocker_id', 'blocked_id', name='uq_user_blocks_blocker_blocked'),
        sa.CheckConstraint('blocker_id != blocked_id', name='user_blocks_no_self_block'),
        sa.CheckConstraint('block_type IN (\'full\', \'messages_only\', \'visibility_only\')', name='user_blocks_type_check')
    )
    op.create_index(op.f('ix_user_blocks_id'), 'user_blocks', ['id'], unique=False)
    op.create_index(op.f('ix_user_blocks_blocker_id'), 'user_blocks', ['blocker_id'], unique=False)
    op.create_index(op.f('ix_user_blocks_blocked_id'), 'user_blocks', ['blocked_id'], unique=False)
    
    # Create user_activities table
    op.create_table('user_activities',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('activity_type', sa.String(length=50), nullable=False),
        sa.Column('target_type', sa.String(length=50), nullable=True),
        sa.Column('target_id', sa.Integer(), nullable=True),
        sa.Column('session_id', sa.String(length=100), nullable=True),
        sa.Column('page_source', sa.String(length=50), nullable=True),
        sa.Column('device_type', sa.String(length=20), nullable=True),
        sa.Column('user_agent', sa.String(length=500), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('activity_data', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_activities_id'), 'user_activities', ['id'], unique=False)
    op.create_index(op.f('ix_user_activities_user_id'), 'user_activities', ['user_id'], unique=False)
    op.create_index(op.f('ix_user_activities_activity_type'), 'user_activities', ['activity_type'], unique=False)
    op.create_index(op.f('ix_user_activities_created_at'), 'user_activities', ['created_at'], unique=False)
    op.create_index(op.f('ix_user_activities_analytics'), 'user_activities', ['user_id', 'created_at'], unique=False)
    
    # Create reported_content table
    op.create_table('reported_content',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('reporter_id', sa.Integer(), nullable=False),
        sa.Column('content_type', sa.String(length=50), nullable=False),
        sa.Column('content_id', sa.Integer(), nullable=False),
        sa.Column('reported_user_id', sa.Integer(), nullable=True),
        sa.Column('report_reason', sa.String(length=100), nullable=False),
        sa.Column('report_description', sa.Text(), nullable=True),
        sa.Column('severity', sa.String(length=20), nullable=False, server_default='medium'),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='pending'),
        sa.Column('moderator_id', sa.Integer(), nullable=True),
        sa.Column('moderator_notes', sa.Text(), nullable=True),
        sa.Column('action_taken', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('resolved_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['moderator_id'], ['users.user_id'], ),
        sa.ForeignKeyConstraint(['reported_user_id'], ['users.user_id'], ),
        sa.ForeignKeyConstraint(['reporter_id'], ['users.user_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint('content_type IN (\'user\', \'project\', \'message\')', name='reported_content_type_check'),
        sa.CheckConstraint('severity IN (\'low\', \'medium\', \'high\', \'critical\')', name='reported_content_severity_check'),
        sa.CheckConstraint('status IN (\'pending\', \'investigating\', \'resolved\', \'dismissed\')', name='reported_content_status_check')
    )
    op.create_index(op.f('ix_reported_content_id'), 'reported_content', ['id'], unique=False)
    op.create_index(op.f('ix_reported_content_reporter_id'), 'reported_content', ['reporter_id'], unique=False)
    op.create_index(op.f('ix_reported_content_status'), 'reported_content', ['status'], unique=False)
    op.create_index(op.f('ix_reported_content_created_at'), 'reported_content', ['created_at'], unique=False)
    
    # Create system_notifications table
    op.create_table('system_notifications',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('notification_type', sa.String(length=50), nullable=False, server_default='general'),
        sa.Column('target_user_ids', sa.JSON(), nullable=True),
        sa.Column('target_user_criteria', sa.JSON(), nullable=True),
        sa.Column('priority', sa.String(length=20), nullable=False, server_default='normal'),
        sa.Column('delivery_method', sa.JSON(), nullable=False, server_default='["in_app"]'),
        sa.Column('scheduled_for', sa.DateTime(), nullable=True),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_sent', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('sent_at', sa.DateTime(), nullable=True),
        sa.Column('total_recipients', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('delivered_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('read_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('click_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint('notification_type IN (\'general\', \'update\', \'maintenance\', \'feature\')', name='system_notifications_type_check'),
        sa.CheckConstraint('priority IN (\'low\', \'normal\', \'high\', \'urgent\')', name='system_notifications_priority_check')
    )
    op.create_index(op.f('ix_system_notifications_id'), 'system_notifications', ['id'], unique=False)
    op.create_index(op.f('ix_system_notifications_is_active'), 'system_notifications', ['is_active'], unique=False)
    op.create_index(op.f('ix_system_notifications_scheduled_for'), 'system_notifications', ['scheduled_for'], unique=False)
    
    # Create user_notifications table
    op.create_table('user_notifications',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('notification_type', sa.String(length=50), nullable=False),
        sa.Column('related_user_id', sa.Integer(), nullable=True),
        sa.Column('related_project_id', sa.Integer(), nullable=True),
        sa.Column('related_match_id', sa.Integer(), nullable=True),
        sa.Column('action_url', sa.String(length=255), nullable=True),
        sa.Column('action_data', sa.JSON(), nullable=True),
        sa.Column('is_read', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_clicked', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('read_at', sa.DateTime(), nullable=True),
        sa.Column('clicked_at', sa.DateTime(), nullable=True),
        sa.Column('delivery_method', sa.String(length=20), nullable=False, server_default='in_app'),
        sa.Column('delivered_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['related_match_id'], ['matches.match_id'], ),
        sa.ForeignKeyConstraint(['related_project_id'], ['projects.project_id'], ),
        sa.ForeignKeyConstraint(['related_user_id'], ['users.user_id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint('notification_type IN (\'match\', \'message\', \'like\', \'system\')', name='user_notifications_type_check'),
        sa.CheckConstraint('delivery_method IN (\'in_app\', \'email\', \'push\')', name='user_notifications_delivery_check')
    )
    op.create_index(op.f('ix_user_notifications_id'), 'user_notifications', ['id'], unique=False)
    op.create_index(op.f('ix_user_notifications_user_id'), 'user_notifications', ['user_id'], unique=False)
    op.create_index(op.f('ix_user_notifications_is_read'), 'user_notifications', ['is_read'], unique=False)
    op.create_index(op.f('ix_user_notifications_created_at'), 'user_notifications', ['created_at'], unique=False)
    op.create_index(op.f('ix_user_notifications_user_unread'), 'user_notifications', ['user_id', 'is_read'], unique=False)
    
    # Create feature_flags table
    op.create_table('feature_flags',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('flag_name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('flag_type', sa.String(length=20), nullable=False, server_default='boolean'),
        sa.Column('default_value', sa.Text(), nullable=True),
        sa.Column('target_percentage', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('target_user_criteria', sa.JSON(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_permanent', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('starts_at', sa.DateTime(), nullable=True),
        sa.Column('ends_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('flag_name', name='uq_feature_flags_flag_name'),
        sa.CheckConstraint('flag_type IN (\'boolean\', \'string\', \'number\', \'json\')', name='feature_flags_type_check'),
        sa.CheckConstraint('target_percentage >= 0 AND target_percentage <= 100', name='feature_flags_percentage_check')
    )
    op.create_index(op.f('ix_feature_flags_id'), 'feature_flags', ['id'], unique=False)
    op.create_index(op.f('ix_feature_flags_is_active'), 'feature_flags', ['is_active'], unique=False)
    
    # Create user_feature_flags table
    op.create_table('user_feature_flags',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('flag_id', sa.Integer(), nullable=False),
        sa.Column('override_value', sa.Text(), nullable=True),
        sa.Column('is_enabled', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['flag_id'], ['feature_flags.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'flag_id', name='uq_user_feature_flags_user_flag')
    )
    op.create_index(op.f('ix_user_feature_flags_id'), 'user_feature_flags', ['id'], unique=False)
    op.create_index(op.f('ix_user_feature_flags_user_id'), 'user_feature_flags', ['user_id'], unique=False)


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('user_feature_flags')
    op.drop_table('feature_flags')
    op.drop_table('user_notifications')
    op.drop_table('system_notifications')
    op.drop_table('reported_content')
    op.drop_table('user_activities')
    op.drop_table('user_blocks')
    op.drop_table('user_sessions')
    op.drop_table('security_logs')
