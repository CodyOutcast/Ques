"""Drop old user_swipes table and create new swipe_records table

Revision ID: create_new_swipe_system
Revises: 
Create Date: 2025-10-17 15:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'create_new_swipe_system'
down_revision = None  # Update this if there are previous migrations
branch_labels = None
depends_on = None


def upgrade():
    """
    Drop old user_swipes table and create new swipe_records table
    that matches the frontend API structure exactly
    """
    
    # Drop old user_swipes table if it exists
    op.execute("""
        DROP TABLE IF EXISTS user_swipes CASCADE;
    """)
    
    # Create new swipe_records table
    op.create_table('swipe_records',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('target_user_id', sa.String(), nullable=False),
        sa.Column('action', sa.String(length=20), nullable=False),
        sa.Column('search_query', sa.String(length=500), nullable=True),
        sa.Column('search_mode', sa.String(length=20), nullable=True),
        sa.Column('match_score', sa.DECIMAL(precision=5, scale=4), nullable=True),
        sa.Column('source_context', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    )
    
    # Create indexes
    op.create_index(op.f('ix_swipe_records_id'), 'swipe_records', ['id'], unique=False)
    op.create_index(op.f('ix_swipe_records_user_id'), 'swipe_records', ['user_id'], unique=False)
    op.create_index(op.f('ix_swipe_records_target_user_id'), 'swipe_records', ['target_user_id'], unique=False)
    op.create_index(op.f('ix_swipe_records_action'), 'swipe_records', ['action'], unique=False)
    op.create_index(op.f('ix_swipe_records_created_at'), 'swipe_records', ['created_at'], unique=False)


def downgrade():
    """
    Revert changes - recreate old user_swipes table and drop new swipe_records table
    """
    
    # Drop new table
    op.drop_table('swipe_records')
    
    # Recreate old user_swipes table (simplified version)
    op.create_table('user_swipes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('swiper_id', sa.Integer(), nullable=False),
        sa.Column('swiped_user_id', sa.Integer(), nullable=False),
        sa.Column('swipe_direction', sa.String(length=10), nullable=False),
        sa.Column('match_score', sa.DECIMAL(precision=5, scale=4), nullable=True),
        sa.Column('swipe_context', sa.String(length=200), nullable=True),
        sa.Column('triggered_whisper', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['swiper_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['swiped_user_id'], ['users.id'], ),
    )