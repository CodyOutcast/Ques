"""Add profile_image_url to users and creator_id to projects

Revision ID: 20250126_2000
Revises: aac856fe8c57
Create Date: 2025-01-26 20:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20250126_2000'
down_revision = 'aac856fe8c57'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add profile_image_url to users table
    op.add_column('users', sa.Column('profile_image_url', sa.String(500), nullable=True))
    
    # Add creator_id to projects table
    op.add_column('projects', sa.Column('creator_id', sa.Integer(), nullable=True))
    
    # Add foreign key constraint for creator_id
    op.create_foreign_key(
        'fk_projects_creator_id',
        'projects', 'users',
        ['creator_id'], ['user_id']
    )


def downgrade() -> None:
    # Drop foreign key constraint
    op.drop_constraint('fk_projects_creator_id', 'projects', type_='foreignkey')
    
    # Remove columns
    op.drop_column('projects', 'creator_id')
    op.drop_column('users', 'profile_image_url')
