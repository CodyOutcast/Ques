"""Add chat system tables only

Revision ID: chat_system_only
Revises: create_user_settings_table
Create Date: 2025-10-17 19:20:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'chat_system_only'
down_revision = 'create_user_settings_table'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add chat system tables only - no modifications to existing tables"""
    
    # Create chat_sessions table
    op.create_table('chat_sessions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_chat_sessions_id'), 'chat_sessions', ['id'], unique=False)
    op.create_index(op.f('ix_chat_sessions_user_id'), 'chat_sessions', ['user_id'], unique=False)
    op.create_index(op.f('ix_chat_sessions_created_at'), 'chat_sessions', ['created_at'], unique=False)

    # Create chat_messages table
    op.create_table('chat_messages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('session_id', sa.Integer(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('is_ai_response', sa.Boolean(), nullable=False, default=False),
        sa.Column('timestamp', sa.TIMESTAMP(), nullable=False),
        sa.ForeignKeyConstraint(['session_id'], ['chat_sessions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_chat_messages_id'), 'chat_messages', ['id'], unique=False)
    op.create_index(op.f('ix_chat_messages_session_id'), 'chat_messages', ['session_id'], unique=False)
    op.create_index(op.f('ix_chat_messages_timestamp'), 'chat_messages', ['timestamp'], unique=False)

    # Create message_recommendations table
    op.create_table('message_recommendations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('message_id', sa.Integer(), nullable=False),
        sa.Column('recommended_user_ids', postgresql.ARRAY(sa.Integer()), nullable=False),
        sa.Column('batch_id', sa.String(50), nullable=True),
        sa.Column('search_context', sa.Text(), nullable=True),
        sa.Column('total_found', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False),
        sa.ForeignKeyConstraint(['message_id'], ['chat_messages.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_message_recommendations_id'), 'message_recommendations', ['id'], unique=False)
    op.create_index(op.f('ix_message_recommendations_message_id'), 'message_recommendations', ['message_id'], unique=False)
    op.create_index(op.f('ix_message_recommendations_batch_id'), 'message_recommendations', ['batch_id'], unique=False)

    # Create suggested_queries table
    op.create_table('suggested_queries',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('message_id', sa.Integer(), nullable=False),
        sa.Column('query_text', sa.String(500), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False),
        sa.ForeignKeyConstraint(['message_id'], ['chat_messages.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_suggested_queries_id'), 'suggested_queries', ['id'], unique=False)
    op.create_index(op.f('ix_suggested_queries_message_id'), 'suggested_queries', ['message_id'], unique=False)


def downgrade() -> None:
    """Remove chat system tables"""
    
    # Drop tables in reverse order (respecting foreign key constraints)
    op.drop_table('suggested_queries')
    op.drop_table('message_recommendations')
    op.drop_table('chat_messages')
    op.drop_table('chat_sessions')