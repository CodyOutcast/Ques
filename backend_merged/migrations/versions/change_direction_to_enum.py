"""Convert user_swipes direction column from VARCHAR to ENUM

Revision ID: change_direction_to_enum
Revises: 
Create Date: 2025-09-03 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'change_direction_to_enum'
down_revision = None  # Update this with your latest revision
branch_labels = None
depends_on = None

def upgrade() -> None:
    """Upgrade the database by converting direction column to ENUM"""
    
    # Create the ENUM type
    swipe_direction_enum = postgresql.ENUM('like', 'dislike', name='swipedirection')
    swipe_direction_enum.create(op.get_bind())
    
    # Convert the column to use the ENUM type
    # Using USING clause to convert existing string values to enum values
    op.execute("""
        ALTER TABLE user_swipes 
        ALTER COLUMN direction TYPE swipedirection 
        USING direction::swipedirection
    """)

def downgrade() -> None:
    """Downgrade by converting back to VARCHAR"""
    
    # Convert back to VARCHAR
    op.alter_column('user_swipes', 'direction',
                    type_=sa.String(20),
                    existing_type=postgresql.ENUM('like', 'dislike', name='swipedirection'))
    
    # Drop the ENUM type
    op.execute("DROP TYPE IF EXISTS swipedirection")
