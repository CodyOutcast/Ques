"""Create user_settings table

Revision ID: create_user_settings_table  
Revises: create_new_swipe_system
Create Date: 2025-10-17 16:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'create_user_settings_table'
down_revision = 'create_new_swipe_system'
branch_labels = None
depends_on = None


def upgrade():
    """
    Create user_settings table with all settings from frontend API
    """
    
    # Create user_settings table
    op.create_table('user_settings',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        
        # Notification Settings
        sa.Column('email_notifications', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('push_notifications', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('whisper_requests', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('friend_requests', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('matches_notifications', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('messages_notifications', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('system_notifications', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('gifts_notifications', sa.Boolean(), nullable=False, server_default='true'),
        
        # User Preferences
        sa.Column('search_mode', sa.String(length=20), nullable=False, server_default='inside'),
        sa.Column('auto_accept_matches', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('show_online_status', sa.Boolean(), nullable=False, server_default='true'),
        
        # Whisper Settings
        sa.Column('custom_message', sa.Text(), nullable=True),
        sa.Column('whisper_auto_accept', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('whisper_show_status', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('whisper_enable_notifications', sa.Boolean(), nullable=False, server_default='true'),
        
        # Additional Settings
        sa.Column('language', sa.String(length=10), nullable=False, server_default='en'),
        sa.Column('theme', sa.String(length=20), nullable=False, server_default='light'),
        sa.Column('timezone', sa.String(length=50), nullable=False, server_default='UTC'),
        
        # Timestamps
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), nullable=False),
        
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.UniqueConstraint('user_id')
    )
    
    # Create indexes
    op.create_index(op.f('ix_user_settings_id'), 'user_settings', ['id'], unique=False)
    op.create_index(op.f('ix_user_settings_user_id'), 'user_settings', ['user_id'], unique=True)
    op.create_index(op.f('ix_user_settings_search_mode'), 'user_settings', ['search_mode'], unique=False)
    op.create_index(op.f('ix_user_settings_created_at'), 'user_settings', ['created_at'], unique=False)
    op.create_index('idx_user_settings_notifications', 'user_settings', ['email_notifications', 'push_notifications'], unique=False)


def downgrade():
    """
    Drop user_settings table
    """
    op.drop_table('user_settings')