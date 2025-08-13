"""Phase 3: Projects and Content System

Revision ID: 003_projects_content
Revises: 002_matching_messaging
Create Date: 2025-07-29 13:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '003_projects_content'
down_revision = '002_matching_messaging'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create projects table (rich project system)
    op.create_table('projects',
        sa.Column('project_id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('creator_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('short_description', sa.String(length=500), nullable=True),
        sa.Column('category', sa.String(length=50), nullable=True),
        sa.Column('industry', sa.String(length=50), nullable=True),
        sa.Column('project_type', sa.String(length=50), nullable=False),
        sa.Column('stage', sa.String(length=50), nullable=True),
        sa.Column('looking_for', sa.JSON(), nullable=True),
        sa.Column('skills_needed', sa.JSON(), nullable=True),
        sa.Column('image_urls', sa.JSON(), nullable=True),
        sa.Column('video_url', sa.String(length=512), nullable=True),
        sa.Column('demo_url', sa.String(length=512), nullable=True),
        sa.Column('pitch_deck_url', sa.String(length=512), nullable=True),
        sa.Column('funding_goal', sa.Integer(), nullable=True),
        sa.Column('equity_offered', sa.Integer(), nullable=True),
        sa.Column('current_valuation', sa.Integer(), nullable=True),
        sa.Column('revenue', sa.Integer(), nullable=True),
        sa.Column('vector_id', sa.String(length=255), nullable=True),
        sa.Column('feature_tags', sa.JSON(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_featured', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_verified', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('moderation_status', sa.String(length=20), nullable=False, server_default='pending'),
        sa.Column('moderation_notes', sa.Text(), nullable=True),
        sa.Column('view_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('like_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('interest_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('published_at', sa.DateTime(), nullable=True),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['creator_id'], ['users.user_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('project_id'),
        sa.CheckConstraint('project_type IN (\'startup\', \'side_project\', \'investment\', \'collaboration\')', name='projects_type_check'),
        sa.CheckConstraint('moderation_status IN (\'pending\', \'approved\', \'rejected\')', name='projects_moderation_check'),
        sa.CheckConstraint('funding_goal IS NULL OR funding_goal > 0', name='projects_funding_check'),
        sa.CheckConstraint('equity_offered IS NULL OR (equity_offered > 0 AND equity_offered <= 10000)', name='projects_equity_check')
    )
    op.create_index(op.f('ix_projects_project_id'), 'projects', ['project_id'], unique=False)
    op.create_index(op.f('ix_projects_creator_id'), 'projects', ['creator_id'], unique=False)
    op.create_index(op.f('ix_projects_is_active'), 'projects', ['is_active'], unique=False)
    op.create_index(op.f('ix_projects_category'), 'projects', ['category'], unique=False)
    op.create_index(op.f('ix_projects_project_type'), 'projects', ['project_type'], unique=False)
    op.create_index(op.f('ix_projects_created_at'), 'projects', ['created_at'], unique=False)
    op.create_index(op.f('ix_projects_vector_id'), 'projects', ['vector_id'], unique=False)
    op.create_index(op.f('ix_projects_discovery'), 'projects', ['is_active', 'moderation_status', 'created_at'], unique=False)
    
    # Create project_features table
    op.create_table('project_features',
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('feature_name', sa.String(length=50), nullable=False),
        sa.Column('weight', sa.Integer(), nullable=False, server_default='100'),
        sa.Column('source', sa.String(length=20), nullable=False, server_default='creator'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['project_id'], ['projects.project_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('project_id', 'feature_name'),
        sa.CheckConstraint('weight >= 0 AND weight <= 100', name='project_features_weight_check'),
        sa.CheckConstraint('source IN (\'creator\', \'ai\', \'moderator\')', name='project_features_source_check')
    )
    op.create_index(op.f('ix_project_features_feature_name'), 'project_features', ['feature_name'], unique=False)
    
    # Create project_links table
    op.create_table('project_links',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('link_url', sa.String(length=512), nullable=False),
        sa.Column('link_type', sa.String(length=50), nullable=True),
        sa.Column('link_title', sa.String(length=100), nullable=True),
        sa.Column('is_verified', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['project_id'], ['projects.project_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_project_links_id'), 'project_links', ['id'], unique=False)
    op.create_index(op.f('ix_project_links_project_id'), 'project_links', ['project_id'], unique=False)
    
    # Create project_updates table
    op.create_table('project_updates',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('author_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('update_type', sa.String(length=50), nullable=False, server_default='general'),
        sa.Column('image_urls', sa.JSON(), nullable=True),
        sa.Column('video_url', sa.String(length=512), nullable=True),
        sa.Column('is_public', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_pinned', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['author_id'], ['users.user_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['project_id'], ['projects.project_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint('update_type IN (\'general\', \'milestone\', \'funding\', \'team\')', name='project_updates_type_check')
    )
    op.create_index(op.f('ix_project_updates_id'), 'project_updates', ['id'], unique=False)
    op.create_index(op.f('ix_project_updates_project_id'), 'project_updates', ['project_id'], unique=False)
    op.create_index(op.f('ix_project_updates_author_id'), 'project_updates', ['author_id'], unique=False)
    op.create_index(op.f('ix_project_updates_created_at'), 'project_updates', ['created_at'], unique=False)
    
    # Create likes table (flexible like system)
    op.create_table('likes',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('liker_id', sa.Integer(), nullable=False),
        sa.Column('liked_item_id', sa.Integer(), nullable=False),
        sa.Column('liked_item_type', sa.String(length=50), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('like_strength', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('granted_chat_access', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('session_id', sa.String(length=100), nullable=True),
        sa.Column('source_page', sa.String(length=50), nullable=True),
        sa.Column('response_time_ms', sa.Integer(), nullable=True),
        sa.Column('is_unliked', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('unliked_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['liker_id'], ['users.user_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('liker_id', 'liked_item_id', 'liked_item_type', name='uq_likes_liker_item'),
        sa.CheckConstraint('liked_item_type IN (\'profile\', \'project\', \'post\')', name='likes_item_type_check'),
        sa.CheckConstraint('like_strength > 0', name='likes_strength_check')
    )
    op.create_index(op.f('ix_likes_id'), 'likes', ['id'], unique=False)
    op.create_index(op.f('ix_likes_liker_id'), 'likes', ['liker_id'], unique=False)
    op.create_index(op.f('ix_likes_liked_item'), 'likes', ['liked_item_id', 'liked_item_type'], unique=False)
    op.create_index(op.f('ix_likes_timestamp'), 'likes', ['timestamp'], unique=False)
    
    # Create interests table (detailed project interest tracking)
    op.create_table('interests',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('interest_type', sa.String(length=50), nullable=False),
        sa.Column('interest_level', sa.Integer(), nullable=False, server_default='50'),
        sa.Column('message', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='pending'),
        sa.Column('response_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('responded_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['project_id'], ['projects.project_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'project_id', 'interest_type', name='uq_interests_user_project_type'),
        sa.CheckConstraint('interest_type IN (\'invest\', \'join\', \'collaborate\', \'follow\')', name='interests_type_check'),
        sa.CheckConstraint('interest_level >= 0 AND interest_level <= 100', name='interests_level_check'),
        sa.CheckConstraint('status IN (\'pending\', \'accepted\', \'rejected\', \'withdrawn\')', name='interests_status_check')
    )
    op.create_index(op.f('ix_interests_id'), 'interests', ['id'], unique=False)
    op.create_index(op.f('ix_interests_user_id'), 'interests', ['user_id'], unique=False)
    op.create_index(op.f('ix_interests_project_id'), 'interests', ['project_id'], unique=False)
    op.create_index(op.f('ix_interests_status'), 'interests', ['status'], unique=False)


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('interests')
    op.drop_table('likes')
    op.drop_table('project_updates')
    op.drop_table('project_links')
    op.drop_table('project_features')
    op.drop_table('projects')
