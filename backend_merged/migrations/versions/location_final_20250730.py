"""add_user_location_fields_only

Revision ID: location_final_20250730
Revises: add_user_location_fields
Create Date: 2025-07-30 15:30:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'location_final_20250730'
down_revision = '005_chat_system'
branch_labels = None
depends_on = None


def upgrade():
    # ### Add location columns to users table if they don't exist ###
    
    # Check if columns exist before adding them
    connection = op.get_bind()
    
    # Check for latitude column
    result = connection.execute(sa.text("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'users' AND column_name = 'latitude'
    """))
    
    if not result.fetchone():
        op.add_column('users', sa.Column('latitude', sa.String(length=20), nullable=True))
        op.add_column('users', sa.Column('longitude', sa.String(length=20), nullable=True))
        op.add_column('users', sa.Column('city', sa.String(length=100), nullable=True))
        op.add_column('users', sa.Column('state', sa.String(length=100), nullable=True))
        op.add_column('users', sa.Column('country', sa.String(length=100), nullable=True))
        op.add_column('users', sa.Column('postal_code', sa.String(length=20), nullable=True))
        op.add_column('users', sa.Column('address', sa.String(length=500), nullable=True))
        
        # Create indexes for location-based queries
        op.create_index('ix_users_latitude', 'users', ['latitude'])
        op.create_index('ix_users_longitude', 'users', ['longitude'])
        op.create_index('ix_users_city', 'users', ['city'])
        op.create_index('ix_users_state', 'users', ['state'])


def downgrade():
    # ### Remove location columns and indexes ###
    op.drop_index('ix_users_state', table_name='users')
    op.drop_index('ix_users_city', table_name='users')
    op.drop_index('ix_users_longitude', table_name='users')
    op.drop_index('ix_users_latitude', table_name='users')
    op.drop_column('users', 'address')
    op.drop_column('users', 'postal_code')
    op.drop_column('users', 'country')
    op.drop_column('users', 'state')
    op.drop_column('users', 'city')
    op.drop_column('users', 'longitude')
    op.drop_column('users', 'latitude')
