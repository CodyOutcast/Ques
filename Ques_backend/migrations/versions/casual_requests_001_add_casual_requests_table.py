"""Add casual_requests table

Revision ID: casual_requests_001
Revises: 20250126_2001_add_project_card_columns
Create Date: 2024-10-20 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'casual_requests_001'
down_revision = '20250126_2001'  # Latest migration
branch_labels = None
depends_on = None


def upgrade():
    """Create casual_requests table"""
    op.create_table(
        'casual_requests',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.String(length=50), nullable=False),
        sa.Column('query', sa.Text(), nullable=False, comment='Original request text'),
        sa.Column('optimized_query', sa.Text(), nullable=False, comment='AI-optimized request text for better matching'),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('location', sa.String(length=100), nullable=True, comment='Optional location information'),
        sa.Column('preferences', postgresql.JSONB(astext_type=sa.Text()), nullable=True, comment='User preferences as JSON object'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('last_activity_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False, comment='Used for cleaning up expired data'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', name='uq_casual_requests_user_id'),
        comment='Stores casual social activity requests from users'
    )
    
    # Create indexes for efficient queries
    op.create_index('idx_casual_requests_user_id', 'casual_requests', ['user_id'])
    op.create_index('idx_casual_requests_last_activity', 'casual_requests', ['last_activity_at'])
    op.create_index('idx_casual_requests_location', 'casual_requests', ['location'])
    op.create_index('idx_casual_requests_active_location', 'casual_requests', ['is_active', 'location'])
    op.create_index('ix_casual_requests_is_active', 'casual_requests', ['is_active'])


def downgrade():
    """Drop casual_requests table"""
    op.drop_index('ix_casual_requests_is_active', table_name='casual_requests')
    op.drop_index('idx_casual_requests_active_location', table_name='casual_requests')
    op.drop_index('idx_casual_requests_location', table_name='casual_requests')
    op.drop_index('idx_casual_requests_last_activity', table_name='casual_requests')
    op.drop_index('idx_casual_requests_user_id', table_name='casual_requests')
    op.drop_table('casual_requests')