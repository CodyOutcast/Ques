"""create_projects_tables_only

Revision ID: projects_only_20250730
Revises: location_final_20250730
Create Date: 2025-07-30 16:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'projects_only_20250730'
down_revision = '006_user_reports'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Check if projects table exists before creating
    connection = op.get_bind()
    result = connection.execute(sa.text("""
        SELECT EXISTS(
            SELECT 1 FROM information_schema.tables 
            WHERE table_name = 'projects'
        )
    """))
    
    if not result.scalar():
        # Create projects table
        op.create_table('projects',
            sa.Column('project_id', sa.Integer(), autoincrement=True, nullable=False),
            sa.Column('short_description', sa.String(length=200), nullable=False),
            sa.Column('long_description', sa.Text(), nullable=True),
            sa.Column('start_time', sa.DateTime(), nullable=False),
            sa.Column('media_link_id', sa.Integer(), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=False),
            sa.Column('updated_at', sa.DateTime(), nullable=False),
            # Removed foreign key constraint to user_links due to composite primary key
            sa.PrimaryKeyConstraint('project_id')
        )
        op.create_index(op.f('ix_projects_project_id'), 'projects', ['project_id'], unique=False)
        
        # Create user_projects table
        op.create_table('user_projects',
            sa.Column('user_id', sa.Integer(), nullable=False),
            sa.Column('project_id', sa.Integer(), nullable=False),
            sa.Column('role', sa.String(length=100), nullable=True),
            sa.Column('joined_at', sa.DateTime(), nullable=False),
            sa.ForeignKeyConstraint(['project_id'], ['projects.project_id'], ),
            sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ),
            sa.PrimaryKeyConstraint('user_id', 'project_id')
        )


def downgrade() -> None:
    # Drop tables if they exist
    op.drop_table('user_projects')
    op.drop_index(op.f('ix_projects_project_id'), table_name='projects')
    op.drop_table('projects')
