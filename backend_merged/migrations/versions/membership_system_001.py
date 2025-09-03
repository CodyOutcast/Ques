"""
Add user membership tables for paid/free user tiers

Revision ID: membership_system_001
Revises: 
Create Date: 2025-09-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = 'membership_system_001'
down_revision = None  # Update this based on your latest migration
branch_labels = None
depends_on = None

def upgrade():
    # Create membership type enum
    membership_type_enum = sa.Enum('FREE', 'PAID', 'PREMIUM', name='membershiptype')
    membership_type_enum.create(op.get_bind())
    
    # Create user_memberships table
    op.create_table('user_memberships',
        sa.Column('membership_id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('membership_type', membership_type_enum, nullable=False, default='FREE'),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('start_date', sa.DateTime(), nullable=False),
        sa.Column('end_date', sa.DateTime(), nullable=True),
        sa.Column('auto_renew', sa.Boolean(), nullable=False, default=False),
        sa.Column('payment_method', sa.String(50), nullable=True),
        sa.Column('subscription_id', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ondelete='CASCADE'),
        sa.UniqueConstraint('user_id')
    )
    
    # Create indexes
    op.create_index('ix_user_memberships_membership_id', 'user_memberships', ['membership_id'])
    op.create_index('ix_user_memberships_user_id', 'user_memberships', ['user_id'])
    op.create_index('ix_user_memberships_membership_type', 'user_memberships', ['membership_type'])
    op.create_index('ix_user_memberships_is_active', 'user_memberships', ['is_active'])
    
    # Create user_usage_logs table
    op.create_table('user_usage_logs',
        sa.Column('log_id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('membership_id', sa.Integer(), nullable=False),
        sa.Column('action_type', sa.String(50), nullable=False),
        sa.Column('action_count', sa.Integer(), nullable=False, default=1),
        sa.Column('hour_timestamp', sa.DateTime(), nullable=False),
        sa.Column('day_timestamp', sa.DateTime(), nullable=False),
        sa.Column('metadata', sa.String(500), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['membership_id'], ['user_memberships.membership_id'], ondelete='CASCADE')
    )
    
    # Create indexes for usage logs
    op.create_index('ix_user_usage_logs_log_id', 'user_usage_logs', ['log_id'])
    op.create_index('ix_user_usage_logs_user_id', 'user_usage_logs', ['user_id'])
    op.create_index('ix_user_usage_logs_action_type', 'user_usage_logs', ['action_type'])
    op.create_index('ix_user_usage_logs_hour_timestamp', 'user_usage_logs', ['hour_timestamp'])
    op.create_index('ix_user_usage_logs_day_timestamp', 'user_usage_logs', ['day_timestamp'])
    
    # Create composite indexes for performance
    op.create_index('ix_user_usage_logs_user_action_hour', 'user_usage_logs', 
                   ['user_id', 'action_type', 'hour_timestamp'])
    op.create_index('ix_user_usage_logs_user_action_day', 'user_usage_logs', 
                   ['user_id', 'action_type', 'day_timestamp'])

def downgrade():
    # Drop indexes
    op.drop_index('ix_user_usage_logs_user_action_day', 'user_usage_logs')
    op.drop_index('ix_user_usage_logs_user_action_hour', 'user_usage_logs')
    op.drop_index('ix_user_usage_logs_day_timestamp', 'user_usage_logs')
    op.drop_index('ix_user_usage_logs_hour_timestamp', 'user_usage_logs')
    op.drop_index('ix_user_usage_logs_action_type', 'user_usage_logs')
    op.drop_index('ix_user_usage_logs_user_id', 'user_usage_logs')
    op.drop_index('ix_user_usage_logs_log_id', 'user_usage_logs')
    
    op.drop_index('ix_user_memberships_is_active', 'user_memberships')
    op.drop_index('ix_user_memberships_membership_type', 'user_memberships')
    op.drop_index('ix_user_memberships_user_id', 'user_memberships')
    op.drop_index('ix_user_memberships_membership_id', 'user_memberships')
    
    # Drop tables
    op.drop_table('user_usage_logs')
    op.drop_table('user_memberships')
    
    # Drop enum
    membership_type_enum = sa.Enum('FREE', 'PAID', 'PREMIUM', name='membershiptype')
    membership_type_enum.drop(op.get_bind())
