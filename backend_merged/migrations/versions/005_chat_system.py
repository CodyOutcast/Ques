"""Add chat system with greeting/acceptance flow

Revision ID: 005_chat_system
Revises: 004_system_features
Create Date: 2025-07-29 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '005_chat_system'
down_revision = '004_system_features'
branch_labels = None
depends_on = None

def upgrade():
    # Create enum for chat status
    chat_status_enum = postgresql.ENUM(
        'pending', 'active', 'rejected', 'blocked',
        name='chatstatus'
    )
    chat_status_enum.create(op.get_bind())
    
    # Create chats table
    op.create_table('chats',
        sa.Column('chat_id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('initiator_id', sa.Integer(), nullable=False),
        sa.Column('recipient_id', sa.Integer(), nullable=False),
        sa.Column('status', chat_status_enum, nullable=False, default='pending'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('accepted_at', sa.DateTime(), nullable=True),
        sa.Column('last_message_at', sa.DateTime(), nullable=True),
        sa.Column('greeting_message', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['initiator_id'], ['users.user_id'], ),
        sa.ForeignKeyConstraint(['recipient_id'], ['users.user_id'], ),
        sa.PrimaryKeyConstraint('chat_id')
    )
    
    op.create_index(op.f('ix_chats_chat_id'), 'chats', ['chat_id'], unique=False)
    op.create_index('ix_chats_participants', 'chats', ['initiator_id', 'recipient_id'], unique=False)
    op.create_index('ix_chats_status', 'chats', ['status'], unique=False)
    op.create_index('ix_chats_last_message_at', 'chats', ['last_message_at'], unique=False)
    
    # Create chat_messages table
    op.create_table('chat_messages',
        sa.Column('message_id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('chat_id', sa.Integer(), nullable=False),
        sa.Column('sender_id', sa.Integer(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('is_read', sa.Boolean(), nullable=False, default=False),
        sa.Column('is_greeting', sa.Boolean(), nullable=False, default=False),
        sa.ForeignKeyConstraint(['chat_id'], ['chats.chat_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['sender_id'], ['users.user_id'], ),
        sa.PrimaryKeyConstraint('message_id')
    )
    
    op.create_index(op.f('ix_chat_messages_message_id'), 'chat_messages', ['message_id'], unique=False)
    op.create_index('ix_chat_messages_chat_id', 'chat_messages', ['chat_id'], unique=False)
    op.create_index('ix_chat_messages_created_at', 'chat_messages', ['created_at'], unique=False)
    op.create_index('ix_chat_messages_is_read', 'chat_messages', ['is_read'], unique=False)

def downgrade():
    # Drop tables
    op.drop_index('ix_chat_messages_is_read', table_name='chat_messages')
    op.drop_index('ix_chat_messages_created_at', table_name='chat_messages')
    op.drop_index('ix_chat_messages_chat_id', table_name='chat_messages')
    op.drop_index(op.f('ix_chat_messages_message_id'), table_name='chat_messages')
    op.drop_table('chat_messages')
    
    op.drop_index('ix_chats_last_message_at', table_name='chats')
    op.drop_index('ix_chats_status', table_name='chats')
    op.drop_index('ix_chats_participants', table_name='chats')
    op.drop_index(op.f('ix_chats_chat_id'), table_name='chats')
    op.drop_table('chats')
    
    # Drop enum
    chat_status_enum = postgresql.ENUM(
        'pending', 'active', 'rejected', 'blocked',
        name='chatstatus'
    )
    chat_status_enum.drop(op.get_bind())
