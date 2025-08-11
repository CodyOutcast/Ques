"""Add status field to projects table

Revision ID: 007_project_status
Revises: projects_only_20250730
Create Date: 2025-08-06 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import Enum

# revision identifiers, used by Alembic.
revision = '007_project_status'
down_revision = 'projects_only_20250730'
branch_labels = None
depends_on = None

def upgrade():
    # Check if the enum type already exists
    connection = op.get_bind()
    result = connection.execute(sa.text("""
        SELECT EXISTS(
            SELECT 1 FROM pg_type WHERE typname = 'projectstatus'
        )
    """))
    
    enum_exists = result.scalar()
    
    if not enum_exists:
        # Create the enum type if it doesn't exist
        project_status = sa.Enum('ongoing', 'on_hold', 'finished', name='projectstatus')
        project_status.create(op.get_bind())
        default_value = 'ongoing'
    else:
        # Enum exists, check what values it has and use appropriate default
        enum_result = connection.execute(sa.text("SELECT unnest(enum_range(NULL::projectstatus))"))
        enum_values = [row[0] for row in enum_result]
        print(f"Found existing enum values: {enum_values}")
        
        # Use the first available value as default (handle both UPPERCASE and lowercase)
        if 'ongoing' in enum_values:
            default_value = 'ongoing'
        elif 'ONGOING' in enum_values:
            default_value = 'ONGOING'
        else:
            default_value = enum_values[0]  # Use first available value
    
    # Check if status column already exists
    column_result = connection.execute(sa.text("""
        SELECT EXISTS(
            SELECT 1 FROM information_schema.columns 
            WHERE table_name = 'projects' AND column_name = 'status'
        )
    """))
    
    if not column_result.scalar():
        # Add the status column to projects table only if it doesn't exist
        op.add_column('projects', sa.Column('status', sa.Enum(name='projectstatus'), nullable=False, server_default=default_value))
        print(f"Added status column with default value: {default_value}")
    else:
        print("Status column already exists, skipping column addition")

def downgrade():
    # Remove the status column
    op.drop_column('projects', 'status')
    
    # Drop the enum type
    project_status = sa.Enum('ongoing', 'on_hold', 'finished', name='projectstatus')
    project_status.drop(op.get_bind())
