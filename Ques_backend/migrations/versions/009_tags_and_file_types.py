"""add tags table and update user_links file_type enum

Revision ID: 009_tags_and_file_types
Revises: 008_message_search_indexes
Create Date: 2025-08-13 11:45:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '009_tags_and_file_types'
down_revision = '008_message_search_indexes'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create tags table
    op.create_table('tags',
        sa.Column('tag_id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('tag_name', sa.String(length=50), nullable=False),
        sa.Column('description', sa.String(length=200), nullable=True),
        sa.Column('category', sa.String(length=30), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('usage_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('tag_id'),
        sa.UniqueConstraint('tag_name', name='uq_tags_tag_name')
    )
    op.create_index(op.f('ix_tags_tag_id'), 'tags', ['tag_id'], unique=False)
    op.create_index(op.f('ix_tags_tag_name'), 'tags', ['tag_name'], unique=False)
    op.create_index(op.f('ix_tags_category'), 'tags', ['category'], unique=False)
    op.create_index(op.f('ix_tags_is_active'), 'tags', ['is_active'], unique=False)
    
    # Create file_type enum for user_links
    file_type_enum = postgresql.ENUM('website', 'media', 'cover', 'avatar', name='filetypeenum', create_type=False)
    file_type_enum.create(op.get_bind(), checkfirst=True)
    
    # First, update existing data to match enum values
    op.execute("""
        UPDATE user_links 
        SET file_type = CASE 
            WHEN file_type = 'text' THEN 'website'
            WHEN file_type = 'document' THEN 'media'
            WHEN file_type = 'image' THEN 'avatar'
            WHEN file_type IS NULL THEN 'website'
            ELSE 'website'
        END
    """)
    
    # Update user_links table to use enum for file_type
    op.alter_column('user_links', 'file_type',
                    type_=file_type_enum,
                    postgresql_using='file_type::filetypeenum')
    
    # Insert some default tags
    op.execute("""
        INSERT INTO tags (tag_name, description, category) VALUES
        ('technology', 'Technology and software related', 'interest'),
        ('startup', 'Startup and entrepreneurship', 'professional'),
        ('fitness', 'Health and fitness activities', 'lifestyle'),
        ('travel', 'Travel and exploration', 'lifestyle'),
        ('music', 'Music and arts', 'creative'),
        ('photography', 'Photography and visual arts', 'creative'),
        ('cooking', 'Cooking and culinary arts', 'lifestyle'),
        ('gaming', 'Video games and gaming', 'entertainment'),
        ('reading', 'Books and literature', 'education'),
        ('sports', 'Sports and athletics', 'physical'),
        ('outdoor', 'Outdoor activities and nature', 'physical'),
        ('art', 'Visual and creative arts', 'creative'),
        ('business', 'Business and finance', 'professional'),
        ('education', 'Learning and education', 'education'),
        ('volunteer', 'Volunteering and community service', 'social')
    """)


def downgrade() -> None:
    # Drop the tags table
    op.drop_table('tags')
    
    # Revert user_links file_type back to VARCHAR
    op.alter_column('user_links', 'file_type',
                    type_=sa.String(length=50),
                    postgresql_using='file_type::text')
    
    # Drop the enum type
    file_type_enum = postgresql.ENUM('website', 'media', 'cover', 'avatar', name='filetypeenum')
    file_type_enum.drop(op.get_bind(), checkfirst=True)
