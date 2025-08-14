"""Add project_idea_requests table for quota system

Revision ID: 010_project_idea_requests
Revises: 009_tags_and_file_types
Create Date: 2025-08-13 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '010_project_idea_requests'
down_revision = '009_tags_and_file_types'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create project_idea_requests table for quota tracking
    op.create_table('project_idea_requests',
        sa.Column('request_id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.user_id'), nullable=False),
        sa.Column('cost', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('query', sa.Text(), nullable=True),
        sa.Column('search_id', sa.Integer(), nullable=True),
        sa.Column('success', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('processing_time_seconds', sa.Float(), nullable=True),
        sa.Column('total_sources_found', sa.Integer(), nullable=True),
        sa.Column('total_ideas_extracted', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('request_id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ondelete='CASCADE')
    )
    
    # Create indexes for performance
    op.create_index(op.f('ix_project_idea_requests_user_id'), 'project_idea_requests', ['user_id'], unique=False)
    op.create_index(op.f('ix_project_idea_requests_created_at'), 'project_idea_requests', ['created_at'], unique=False)
    op.create_index(op.f('ix_project_idea_requests_user_date'), 'project_idea_requests', ['user_id', 'created_at'], unique=False)


def downgrade() -> None:
    # Drop indexes first
    op.drop_index(op.f('ix_project_idea_requests_user_date'), table_name='project_idea_requests')
    op.drop_index(op.f('ix_project_idea_requests_created_at'), table_name='project_idea_requests')
    op.drop_index(op.f('ix_project_idea_requests_user_id'), table_name='project_idea_requests')
    
    # Drop table
    op.drop_table('project_idea_requests')
