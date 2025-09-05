"""Add project slots tables

Revision ID: 20250905_1200_project_slots
Revises: 20250902_1502
Create Date: 2025-09-05 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20250905_1200_project_slots'
down_revision = '20250902_1502'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create project_card_slots table
    op.create_table('project_card_slots',
        sa.Column('slot_id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('slot_number', sa.Integer(), nullable=False),
        sa.Column('slot_name', sa.String(length=100), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='empty'),
        sa.Column('source', sa.String(length=20), nullable=True),
        
        # Project content fields
        sa.Column('title', sa.String(length=200), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('short_description', sa.String(length=500), nullable=True),
        sa.Column('category', sa.String(length=50), nullable=True),
        sa.Column('industry', sa.String(length=50), nullable=True),
        sa.Column('project_type', sa.String(length=50), nullable=True),
        sa.Column('stage', sa.String(length=50), nullable=True),
        
        # JSON fields for lists
        sa.Column('looking_for', sa.JSON(), nullable=True),
        sa.Column('skills_needed', sa.JSON(), nullable=True),
        sa.Column('image_urls', sa.JSON(), nullable=True),
        
        # URL fields
        sa.Column('video_url', sa.String(length=512), nullable=True),
        sa.Column('demo_url', sa.String(length=512), nullable=True),
        sa.Column('pitch_deck_url', sa.String(length=512), nullable=True),
        
        # Financial fields
        sa.Column('funding_goal', sa.Integer(), nullable=True),
        sa.Column('equity_offered', sa.Integer(), nullable=True),
        sa.Column('current_valuation', sa.Integer(), nullable=True),
        sa.Column('revenue', sa.Integer(), nullable=True),
        
        # AI recommendation fields
        sa.Column('ai_recommendation_id', sa.String(length=100), nullable=True),
        sa.Column('ai_confidence_score', sa.Float(), nullable=True),
        sa.Column('ai_reasoning', sa.Text(), nullable=True),
        sa.Column('original_query', sa.String(length=500), nullable=True),
        
        # Activation tracking
        sa.Column('is_activated', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('activated_at', sa.DateTime(), nullable=True),
        sa.Column('project_card_id', sa.Integer(), nullable=True),
        
        # Timestamps
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        
        # Constraints
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('slot_id'),
        sa.UniqueConstraint('user_id', 'slot_number', name='unique_user_slot_number')
    )
    
    # Create indexes for project_card_slots
    op.create_index('ix_project_card_slots_slot_id', 'project_card_slots', ['slot_id'])
    op.create_index('ix_project_card_slots_user_id', 'project_card_slots', ['user_id'])
    op.create_index('ix_project_card_slots_status', 'project_card_slots', ['status'])
    op.create_index('ix_project_card_slots_created_at', 'project_card_slots', ['created_at'])
    
    # Create user_slot_configurations table
    op.create_table('user_slot_configurations',
        sa.Column('config_id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('base_slots', sa.Integer(), nullable=False, server_default='2'),
        sa.Column('bonus_slots', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('membership_slots_permanent', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('membership_expires_at', sa.DateTime(), nullable=True),
        sa.Column('auto_save_recommendations', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('stop_recommendations_on_save', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        
        # Constraints
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('config_id'),
        sa.UniqueConstraint('user_id', name='unique_user_slot_config')
    )
    
    # Create indexes for user_slot_configurations
    op.create_index('ix_user_slot_configurations_config_id', 'user_slot_configurations', ['config_id'])
    op.create_index('ix_user_slot_configurations_user_id', 'user_slot_configurations', ['user_id'], unique=True)
    
    # Create ai_recommendation_swipes table
    op.create_table('ai_recommendation_swipes',
        sa.Column('swipe_id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('ai_recommendation_id', sa.String(length=100), nullable=False),
        sa.Column('direction', sa.String(length=10), nullable=False),
        sa.Column('query', sa.String(length=500), nullable=True),
        sa.Column('saved_to_slot', sa.Integer(), nullable=True),
        sa.Column('recommendation_data', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        
        # Constraints
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('swipe_id'),
        sa.UniqueConstraint('user_id', 'ai_recommendation_id', name='unique_user_recommendation_swipe')
    )
    
    # Create indexes for ai_recommendation_swipes
    op.create_index('ix_ai_recommendation_swipes_swipe_id', 'ai_recommendation_swipes', ['swipe_id'])
    op.create_index('ix_ai_recommendation_swipes_user_id', 'ai_recommendation_swipes', ['user_id'])
    op.create_index('ix_ai_recommendation_swipes_ai_recommendation_id', 'ai_recommendation_swipes', ['ai_recommendation_id'])
    op.create_index('ix_ai_recommendation_swipes_created_at', 'ai_recommendation_swipes', ['created_at'])


def downgrade() -> None:
    # Drop indexes and tables in reverse order
    op.drop_index('ix_ai_recommendation_swipes_created_at', table_name='ai_recommendation_swipes')
    op.drop_index('ix_ai_recommendation_swipes_ai_recommendation_id', table_name='ai_recommendation_swipes')
    op.drop_index('ix_ai_recommendation_swipes_user_id', table_name='ai_recommendation_swipes')
    op.drop_index('ix_ai_recommendation_swipes_swipe_id', table_name='ai_recommendation_swipes')
    op.drop_table('ai_recommendation_swipes')
    
    op.drop_index('ix_user_slot_configurations_user_id', table_name='user_slot_configurations')
    op.drop_index('ix_user_slot_configurations_config_id', table_name='user_slot_configurations')
    op.drop_table('user_slot_configurations')
    
    op.drop_index('ix_project_card_slots_created_at', table_name='project_card_slots')
    op.drop_index('ix_project_card_slots_status', table_name='project_card_slots')
    op.drop_index('ix_project_card_slots_user_id', table_name='project_card_slots')
    op.drop_index('ix_project_card_slots_slot_id', table_name='project_card_slots')
    op.drop_table('project_card_slots')
