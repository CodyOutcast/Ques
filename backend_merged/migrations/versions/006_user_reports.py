"""add user reports table

Revision ID: 006_user_reports
Revises: 005_chat_system
Create Date: 2025-08-04 15:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '006_user_reports'
down_revision = 'location_final_20250730'
branch_labels = None
depends_on = None


def upgrade():
    # Create enum types
    report_type_enum = postgresql.ENUM(
        'inappropriate_content', 'harassment', 'spam', 'fake_profile',
        'hate_speech', 'drug_related', 'scam_fraud', 'violence_threats',
        'underage', 'inappropriate_photos', 'catfishing', 'political_content', 'other',
        name='reporttype', create_type=True
    )
    
    report_status_enum = postgresql.ENUM(
        'pending', 'under_review', 'resolved', 'dismissed', 'escalated',
        name='reportstatus', create_type=True
    )
    
    report_action_enum = postgresql.ENUM(
        'no_action', 'warning_issued', 'content_removed', 'profile_suspended',
        'account_banned', 'under_investigation',
        name='reportaction', create_type=True
    )
    
    # Create user_reports table
    op.create_table('user_reports',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('reporter_id', sa.Integer(), nullable=False),
        sa.Column('reported_user_id', sa.Integer(), nullable=False),
        sa.Column('report_type', report_type_enum, nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('proof_text', sa.Text(), nullable=True),
        sa.Column('proof_image_urls', sa.Text(), nullable=True),
        sa.Column('proof_chat_id', sa.Integer(), nullable=True),
        sa.Column('proof_message_id', sa.Integer(), nullable=True),
        sa.Column('status', report_status_enum, nullable=False, server_default='pending'),
        sa.Column('action_taken', report_action_enum, nullable=True, server_default='under_investigation'),
        sa.Column('moderator_id', sa.Integer(), nullable=True),
        sa.Column('moderator_notes', sa.Text(), nullable=True),
        sa.Column('platform_location', sa.String(length=100), nullable=True),
        sa.Column('severity_score', sa.Integer(), nullable=True, server_default='1'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('reviewed_at', sa.DateTime(), nullable=True),
        sa.Column('resolved_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('is_anonymous', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('requires_urgent_review', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('is_repeat_offender', sa.Boolean(), nullable=True, server_default='false'),
        sa.ForeignKeyConstraint(['moderator_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['proof_chat_id'], ['chats.id'], ),
        sa.ForeignKeyConstraint(['proof_message_id'], ['messages.id'], ),
        sa.ForeignKeyConstraint(['reported_user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['reporter_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index(op.f('ix_user_reports_id'), 'user_reports', ['id'], unique=False)
    op.create_index(op.f('ix_user_reports_reporter_id'), 'user_reports', ['reporter_id'], unique=False)
    op.create_index(op.f('ix_user_reports_reported_user_id'), 'user_reports', ['reported_user_id'], unique=False)
    op.create_index(op.f('ix_user_reports_report_type'), 'user_reports', ['report_type'], unique=False)
    op.create_index(op.f('ix_user_reports_status'), 'user_reports', ['status'], unique=False)
    op.create_index(op.f('ix_user_reports_created_at'), 'user_reports', ['created_at'], unique=False)
    
    # Create report_statistics table
    op.create_table('report_statistics',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('date', sa.DateTime(), nullable=False),
        sa.Column('total_reports', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('pending_reports', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('resolved_reports', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('dismissed_reports', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('harassment_reports', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('inappropriate_content_reports', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('spam_reports', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('fake_profile_reports', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('warnings_issued', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('content_removed', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('accounts_suspended', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('accounts_banned', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('average_resolution_time_hours', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('repeat_offender_reports', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_index(op.f('ix_report_statistics_date'), 'report_statistics', ['date'], unique=False)


def downgrade():
    # Drop tables
    op.drop_index(op.f('ix_report_statistics_date'), table_name='report_statistics')
    op.drop_table('report_statistics')
    
    op.drop_index(op.f('ix_user_reports_created_at'), table_name='user_reports')
    op.drop_index(op.f('ix_user_reports_status'), table_name='user_reports')
    op.drop_index(op.f('ix_user_reports_report_type'), table_name='user_reports')
    op.drop_index(op.f('ix_user_reports_reported_user_id'), table_name='user_reports')
    op.drop_index(op.f('ix_user_reports_reporter_id'), table_name='user_reports')
    op.drop_index(op.f('ix_user_reports_id'), table_name='user_reports')
    op.drop_table('user_reports')
    
    # Drop enum types
    op.execute('DROP TYPE IF EXISTS reportaction')
    op.execute('DROP TYPE IF EXISTS reportstatus')
    op.execute('DROP TYPE IF EXISTS reporttype')
