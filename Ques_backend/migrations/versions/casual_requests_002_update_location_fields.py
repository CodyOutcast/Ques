"""Update casual_requests location to use province_id

Revision ID: casual_requests_002
Revises: casual_requests_001
Create Date: 2024-10-20 21:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'casual_requests_002'
down_revision = 'casual_requests_001'
branch_labels = None
depends_on = None


def upgrade():
    """Update casual_requests to use province_id instead of location string"""
    # Add new columns
    op.add_column('casual_requests', sa.Column('province_id', sa.Integer(), nullable=True))
    op.add_column('casual_requests', sa.Column('city_id', sa.Integer(), nullable=True))
    
    # Create foreign key constraints
    op.create_foreign_key('fk_casual_requests_province_id', 'casual_requests', 'provinces', ['province_id'], ['id'])
    op.create_foreign_key('fk_casual_requests_city_id', 'casual_requests', 'cities', ['city_id'], ['id'])
    
    # Create indexes for efficient location-based queries
    op.create_index('idx_casual_requests_province_id', 'casual_requests', ['province_id'])
    op.create_index('idx_casual_requests_city_id', 'casual_requests', ['city_id'])
    op.create_index('idx_casual_requests_location_combo', 'casual_requests', ['province_id', 'city_id'])
    
    # Update existing index to use new location fields
    op.drop_index('idx_casual_requests_active_location', table_name='casual_requests')
    op.create_index('idx_casual_requests_active_location', 'casual_requests', ['is_active', 'province_id', 'city_id'])
    
    # Remove old location column (after data migration if needed)
    # Note: In production, you'd want to migrate data first
    op.drop_column('casual_requests', 'location')


def downgrade():
    """Revert casual_requests location changes"""
    # Add back location column
    op.add_column('casual_requests', sa.Column('location', sa.VARCHAR(length=100), nullable=True))
    
    # Remove new indexes
    op.drop_index('idx_casual_requests_active_location', table_name='casual_requests')
    op.drop_index('idx_casual_requests_location_combo', table_name='casual_requests')
    op.drop_index('idx_casual_requests_city_id', table_name='casual_requests')
    op.drop_index('idx_casual_requests_province_id', table_name='casual_requests')
    
    # Remove foreign key constraints
    op.drop_constraint('fk_casual_requests_city_id', 'casual_requests', type_='foreignkey')
    op.drop_constraint('fk_casual_requests_province_id', 'casual_requests', type_='foreignkey')
    
    # Remove new columns
    op.drop_column('casual_requests', 'city_id')
    op.drop_column('casual_requests', 'province_id')
    
    # Recreate old index
    op.create_index('idx_casual_requests_active_location', 'casual_requests', ['is_active', 'location'])