"""Phase 2: Matching and Messaging System

Revision ID: 002_matching_messaging
Revises: 001_core_tables
Create Date: 2025-07-29 12:30:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '002_matching_messaging'
down_revision = '001_core_tables'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create matches table (enhanced matching system)
    op.create_table('matches',
        sa.Column('match_id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user1_id', sa.Integer(), nullable=False),
        sa.Column('user2_id', sa.Integer(), nullable=False),
        sa.Column('matched_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_blocked', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('blocked_by_user_id', sa.Integer(), nullable=True),
        sa.Column('blocked_at', sa.DateTime(), nullable=True),
        sa.Column('match_score', sa.Integer(), nullable=True),
        sa.Column('match_reason', sa.String(length=200), nullable=True),
        sa.Column('chat_enabled', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('video_call_enabled', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('last_message_at', sa.DateTime(), nullable=True),
        sa.Column('last_activity_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['blocked_by_user_id'], ['users.user_id'], ),
        sa.ForeignKeyConstraint(['user1_id'], ['users.user_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user2_id'], ['users.user_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('match_id'),
        sa.UniqueConstraint('user1_id', 'user2_id', name='uq_matches_user1_user2'),
        sa.CheckConstraint('user1_id != user2_id', name='matches_no_self_match'),
        sa.CheckConstraint('match_score IS NULL OR (match_score >= 0 AND match_score <= 100)', name='matches_score_check')
    )
    op.create_index(op.f('ix_matches_match_id'), 'matches', ['match_id'], unique=False)
    op.create_index(op.f('ix_matches_user1_id'), 'matches', ['user1_id'], unique=False)
    op.create_index(op.f('ix_matches_user2_id'), 'matches', ['user2_id'], unique=False)
    op.create_index(op.f('ix_matches_is_active'), 'matches', ['is_active'], unique=False)
    op.create_index(op.f('ix_matches_last_activity_at'), 'matches', ['last_activity_at'], unique=False)
    
    # Create messages table (full-featured messaging)
    op.create_table('messages',
        sa.Column('message_id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('match_id', sa.Integer(), nullable=False),
        sa.Column('sender_id', sa.Integer(), nullable=False),
        sa.Column('message_text', sa.Text(), nullable=False),
        sa.Column('message_type', sa.String(length=20), nullable=False, server_default='text'),
        sa.Column('sent_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('delivered_at', sa.DateTime(), nullable=True),
        sa.Column('read_at', sa.DateTime(), nullable=True),
        sa.Column('is_read', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('is_flagged', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('flag_reason', sa.String(length=100), nullable=True),
        sa.Column('moderation_status', sa.String(length=20), nullable=False, server_default='approved'),
        sa.Column('media_url', sa.String(length=512), nullable=True),
        sa.Column('media_type', sa.String(length=50), nullable=True),
        sa.Column('media_size', sa.Integer(), nullable=True),
        sa.Column('thumbnail_url', sa.String(length=512), nullable=True),
        sa.Column('reply_to_message_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['match_id'], ['matches.match_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['reply_to_message_id'], ['messages.message_id'], ),
        sa.ForeignKeyConstraint(['sender_id'], ['users.user_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('message_id'),
        sa.CheckConstraint('message_type IN (\'text\', \'image\', \'voice\', \'video\')', name='messages_type_check'),
        sa.CheckConstraint('moderation_status IN (\'pending\', \'approved\', \'rejected\')', name='messages_moderation_check')
    )
    op.create_index(op.f('ix_messages_message_id'), 'messages', ['message_id'], unique=False)
    op.create_index(op.f('ix_messages_match_id'), 'messages', ['match_id'], unique=False)
    op.create_index(op.f('ix_messages_sender_id'), 'messages', ['sender_id'], unique=False)
    op.create_index(op.f('ix_messages_sent_at'), 'messages', ['sent_at'], unique=False)
    op.create_index(op.f('ix_messages_is_read'), 'messages', ['is_read'], unique=False)
    op.create_index(op.f('ix_messages_match_sent'), 'messages', ['match_id', 'sent_at'], unique=False)
    
    # Create message_reactions table
    op.create_table('message_reactions',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('message_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('reaction_type', sa.String(length=20), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['message_id'], ['messages.message_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('message_id', 'user_id', name='uq_message_reactions_message_user'),
        sa.CheckConstraint('reaction_type IN (\'like\', \'love\', \'laugh\', \'wow\', \'sad\', \'angry\')', name='message_reactions_type_check')
    )
    op.create_index(op.f('ix_message_reactions_id'), 'message_reactions', ['id'], unique=False)
    op.create_index(op.f('ix_message_reactions_message_id'), 'message_reactions', ['message_id'], unique=False)
    op.create_index(op.f('ix_message_reactions_user_id'), 'message_reactions', ['user_id'], unique=False)
    
    # Create chat_settings table
    op.create_table('chat_settings',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('match_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('notifications_enabled', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('push_notifications', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('email_notifications', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('read_receipts_enabled', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('typing_indicators_enabled', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('theme', sa.String(length=20), nullable=False, server_default='default'),
        sa.Column('nickname_for_other_user', sa.String(length=50), nullable=True),
        sa.Column('is_muted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('muted_until', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['match_id'], ['matches.match_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('match_id', 'user_id', name='uq_chat_settings_match_user')
    )
    op.create_index(op.f('ix_chat_settings_id'), 'chat_settings', ['id'], unique=False)
    op.create_index(op.f('ix_chat_settings_match_id'), 'chat_settings', ['match_id'], unique=False)
    op.create_index(op.f('ix_chat_settings_user_id'), 'chat_settings', ['user_id'], unique=False)


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('chat_settings')
    op.drop_table('message_reactions')
    op.drop_table('messages')
    op.drop_table('matches')
