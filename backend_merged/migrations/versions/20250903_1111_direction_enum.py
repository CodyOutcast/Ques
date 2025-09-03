"""convert_user_swipes_direction_to_enum

Revision ID: 20250903_1111_direction_enum
Revises: 20250126_2001
Create Date: 2025-01-27 11:11:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20250903_1111_direction_enum'
down_revision = '20250126_2001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Drop the existing enum type if it exists
    op.execute('DROP TYPE IF EXISTS swipedirection')
    
    # Create the enum type with lowercase values
    swipe_direction_enum = postgresql.ENUM('like', 'dislike', name='swipedirection')
    swipe_direction_enum.create(op.get_bind())
    
    # Alter the column to use the enum
    op.alter_column('user_swipes', 'direction',
                    type_=swipe_direction_enum,
                    postgresql_using='direction::swipedirection')


def downgrade() -> None:
    # Convert back to VARCHAR
    op.alter_column('user_swipes', 'direction',
                    type_=sa.String(20),
                    postgresql_using='direction::varchar')
    
    # Drop the enum type
    op.execute('DROP TYPE IF EXISTS swipedirection')
