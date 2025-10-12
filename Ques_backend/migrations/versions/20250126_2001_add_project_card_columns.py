"""Add comprehensive project card columns

Revision ID: 20250126_2001
Revises: 20250126_2000
Create Date: 2025-01-26 20:01:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20250126_2001'
down_revision = '20250126_2000'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add missing columns to projects table
    op.add_column('projects', sa.Column('title', sa.String(200), nullable=True))
    op.add_column('projects', sa.Column('description', sa.Text(), nullable=True))
    op.add_column('projects', sa.Column('category', sa.String(50), nullable=True))
    op.add_column('projects', sa.Column('industry', sa.String(50), nullable=True))
    op.add_column('projects', sa.Column('project_type', sa.String(50), nullable=True))
    op.add_column('projects', sa.Column('stage', sa.String(50), nullable=True))
    op.add_column('projects', sa.Column('looking_for', sa.JSON(), nullable=True))
    op.add_column('projects', sa.Column('skills_needed', sa.JSON(), nullable=True))
    op.add_column('projects', sa.Column('image_urls', sa.JSON(), nullable=True))
    op.add_column('projects', sa.Column('video_url', sa.String(500), nullable=True))
    op.add_column('projects', sa.Column('demo_url', sa.String(500), nullable=True))
    op.add_column('projects', sa.Column('pitch_deck_url', sa.String(500), nullable=True))
    op.add_column('projects', sa.Column('funding_goal', sa.BigInteger(), nullable=True))
    op.add_column('projects', sa.Column('equity_offered', sa.Float(), nullable=True))
    op.add_column('projects', sa.Column('current_valuation', sa.BigInteger(), nullable=True))
    op.add_column('projects', sa.Column('revenue', sa.BigInteger(), nullable=True))
    op.add_column('projects', sa.Column('vector_id', sa.String(), nullable=True))
    op.add_column('projects', sa.Column('feature_tags', sa.JSON(), nullable=True))
    op.add_column('projects', sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'))
    op.add_column('projects', sa.Column('is_featured', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('projects', sa.Column('is_verified', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('projects', sa.Column('moderation_status', sa.String(20), nullable=False, server_default='pending'))
    op.add_column('projects', sa.Column('moderation_notes', sa.Text(), nullable=True))
    op.add_column('projects', sa.Column('view_count', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('projects', sa.Column('like_count', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('projects', sa.Column('interest_count', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('projects', sa.Column('published_at', sa.DateTime(), nullable=True))
    op.add_column('projects', sa.Column('expires_at', sa.DateTime(), nullable=True))
    
    # Add indexes for better performance
    op.create_index('ix_projects_title', 'projects', ['title'])
    op.create_index('ix_projects_category', 'projects', ['category'])
    op.create_index('ix_projects_industry', 'projects', ['industry'])
    op.create_index('ix_projects_project_type', 'projects', ['project_type'])
    op.create_index('ix_projects_stage', 'projects', ['stage'])
    op.create_index('ix_projects_is_active', 'projects', ['is_active'])
    op.create_index('ix_projects_is_featured', 'projects', ['is_featured'])
    op.create_index('ix_projects_moderation_status', 'projects', ['moderation_status'])
    op.create_index('ix_projects_published_at', 'projects', ['published_at'])
    op.create_index('ix_projects_creator_id', 'projects', ['creator_id'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_projects_creator_id', 'projects')
    op.drop_index('ix_projects_published_at', 'projects')
    op.drop_index('ix_projects_moderation_status', 'projects')
    op.drop_index('ix_projects_is_featured', 'projects')
    op.drop_index('ix_projects_is_active', 'projects')
    op.drop_index('ix_projects_stage', 'projects')
    op.drop_index('ix_projects_project_type', 'projects')
    op.drop_index('ix_projects_industry', 'projects')
    op.drop_index('ix_projects_category', 'projects')
    op.drop_index('ix_projects_title', 'projects')
    
    # Remove columns
    op.drop_column('projects', 'expires_at')
    op.drop_column('projects', 'published_at')
    op.drop_column('projects', 'interest_count')
    op.drop_column('projects', 'like_count')
    op.drop_column('projects', 'view_count')
    op.drop_column('projects', 'moderation_notes')
    op.drop_column('projects', 'moderation_status')
    op.drop_column('projects', 'is_verified')
    op.drop_column('projects', 'is_featured')
    op.drop_column('projects', 'is_active')
    op.drop_column('projects', 'feature_tags')
    op.drop_column('projects', 'vector_id')
    op.drop_column('projects', 'revenue')
    op.drop_column('projects', 'current_valuation')
    op.drop_column('projects', 'equity_offered')
    op.drop_column('projects', 'funding_goal')
    op.drop_column('projects', 'pitch_deck_url')
    op.drop_column('projects', 'demo_url')
    op.drop_column('projects', 'video_url')
    op.drop_column('projects', 'image_urls')
    op.drop_column('projects', 'skills_needed')
    op.drop_column('projects', 'looking_for')
    op.drop_column('projects', 'stage')
    op.drop_column('projects', 'project_type')
    op.drop_column('projects', 'industry')
    op.drop_column('projects', 'category')
    op.drop_column('projects', 'description')
    op.drop_column('projects', 'title')
