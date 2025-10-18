"""Add location tables, user statistics, and birthday-based age system

Revision ID: add_location_statistics_birthday
Revises: location_final_20250730
Create Date: 2025-09-27 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import text

# revision identifiers, used by Alembic.
revision = 'add_location_statistics_birthday'
down_revision = 'location_final_20250730'
branch_labels = None
depends_on = None

def upgrade():
    # Create provinces table
    op.create_table('provinces',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name_en', sa.String(length=100), nullable=False),
        sa.Column('name_cn', sa.String(length=100), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_provinces_id'), 'provinces', ['id'], unique=False)

    # Create cities table
    op.create_table('cities',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('province_id', sa.Integer(), nullable=False),
        sa.Column('name_en', sa.String(length=100), nullable=False),
        sa.Column('name_cn', sa.String(length=100), nullable=False),
        sa.ForeignKeyConstraint(['province_id'], ['provinces.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_cities_id'), 'cities', ['id'], unique=False)

    # Create institutions table
    op.create_table('institutions',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('name_en', sa.String(length=255), nullable=True),
        sa.Column('type', sa.String(length=50), nullable=False),
        sa.Column('city_id', sa.Integer(), nullable=True),
        sa.Column('province_id', sa.Integer(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('website', sa.String(length=512), nullable=True),
        sa.Column('logo_url', sa.String(length=512), nullable=True),
        sa.Column('is_verified', sa.Integer(), nullable=False, default=0),
        sa.Column('is_active', sa.Integer(), nullable=False, default=1),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['city_id'], ['cities.id'], ),
        sa.ForeignKeyConstraint(['province_id'], ['provinces.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_institutions_id'), 'institutions', ['id'], unique=False)

    # Create user_project_counts table
    op.create_table('user_project_counts',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('owned_projects', sa.Integer(), nullable=False, default=0),
        sa.Column('collaborated_projects', sa.Integer(), nullable=False, default=0),
        sa.Column('total_projects', sa.Integer(), nullable=False, default=0),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )
    op.create_index(op.f('ix_user_project_counts_id'), 'user_project_counts', ['id'], unique=False)

    # Create user_institution_counts table
    op.create_table('user_institution_counts',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('educational_institutions', sa.Integer(), nullable=False, default=0),
        sa.Column('work_institutions', sa.Integer(), nullable=False, default=0),
        sa.Column('other_institutions', sa.Integer(), nullable=False, default=0),
        sa.Column('total_institutions', sa.Integer(), nullable=False, default=0),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )
    op.create_index(op.f('ix_user_institution_counts_id'), 'user_institution_counts', ['id'], unique=False)

    # Create user_institutions junction table
    op.create_table('user_institutions',
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('institution_id', sa.Integer(), nullable=False),
        sa.Column('role', sa.String(length=100), nullable=True),
        sa.Column('start_date', sa.DateTime(), nullable=True),
        sa.Column('end_date', sa.DateTime(), nullable=True),
        sa.Column('is_current', sa.Integer(), nullable=False, default=1),
        sa.Column('position', sa.String(length=100), nullable=True),
        sa.Column('department', sa.String(length=100), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['institution_id'], ['institutions.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ),
        sa.PrimaryKeyConstraint('user_id', 'institution_id')
    )

    # Add new columns to users table
    op.add_column('users', sa.Column('birthday', sa.Date(), nullable=True))
    op.add_column('users', sa.Column('age', sa.Integer(), nullable=True))
    op.add_column('users', sa.Column('province_id', sa.Integer(), nullable=True))
    op.add_column('users', sa.Column('city_id', sa.Integer(), nullable=True))
    
    # Add foreign key constraints for new location columns
    op.create_foreign_key('fk_users_province_id', 'users', 'provinces', ['province_id'], ['id'])
    op.create_foreign_key('fk_users_city_id', 'users', 'cities', ['city_id'], ['id'])

    # Create function to calculate age from birthday
    op.execute(text("""
        CREATE OR REPLACE FUNCTION calculate_age_from_birthday()
        RETURNS TRIGGER AS $$
        BEGIN
            IF NEW.birthday IS NOT NULL THEN
                NEW.age := EXTRACT(YEAR FROM AGE(CURRENT_DATE, NEW.birthday));
            ELSE
                NEW.age := NULL;
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """))

    # Create trigger to automatically update age when birthday is inserted/updated
    op.execute(text("""
        CREATE TRIGGER trigger_update_age_on_birthday
            BEFORE INSERT OR UPDATE OF birthday ON users
            FOR EACH ROW
            EXECUTE FUNCTION calculate_age_from_birthday();
    """))

    # Create function to check for birthday and increment age
    op.execute(text("""
        CREATE OR REPLACE FUNCTION check_birthday_and_increment_age()
        RETURNS void AS $$
        BEGIN
            UPDATE users 
            SET age = age + 1
            WHERE birthday IS NOT NULL 
              AND EXTRACT(MONTH FROM birthday) = EXTRACT(MONTH FROM CURRENT_DATE)
              AND EXTRACT(DAY FROM birthday) = EXTRACT(DAY FROM CURRENT_DATE)
              AND age IS NOT NULL;
        END;
        $$ LANGUAGE plpgsql;
    """))

    # Create a function to update project counts
    op.execute(text("""
        CREATE OR REPLACE FUNCTION update_user_project_counts()
        RETURNS TRIGGER AS $$
        DECLARE
            target_user_id INTEGER;
            owned_count INTEGER;
            collaborated_count INTEGER;
        BEGIN
            -- Determine which user_id to update
            IF TG_OP = 'DELETE' THEN
                target_user_id := OLD.user_id;
            ELSE
                target_user_id := NEW.user_id;
            END IF;

            -- Count owned projects (creator_id in projects table)
            SELECT COUNT(*) INTO owned_count
            FROM projects 
            WHERE creator_id = target_user_id;

            -- Count collaborated projects (excluding owned ones)
            SELECT COUNT(*) INTO collaborated_count
            FROM user_projects up
            JOIN projects p ON up.project_id = p.project_id
            WHERE up.user_id = target_user_id AND p.creator_id != target_user_id;

            -- Insert or update the counts
            INSERT INTO user_project_counts (user_id, owned_projects, collaborated_projects, total_projects, created_at, updated_at)
            VALUES (target_user_id, owned_count, collaborated_count, owned_count + collaborated_count, NOW(), NOW())
            ON CONFLICT (user_id) 
            DO UPDATE SET 
                owned_projects = EXCLUDED.owned_projects,
                collaborated_projects = EXCLUDED.collaborated_projects,
                total_projects = EXCLUDED.total_projects,
                updated_at = NOW();

            RETURN COALESCE(NEW, OLD);
        END;
        $$ LANGUAGE plpgsql;
    """))

    # Create triggers for project count updates
    op.execute(text("""
        CREATE TRIGGER trigger_update_project_counts_on_user_project
            AFTER INSERT OR UPDATE OR DELETE ON user_projects
            FOR EACH ROW
            EXECUTE FUNCTION update_user_project_counts();
    """))

    op.execute(text("""
        CREATE TRIGGER trigger_update_project_counts_on_project
            AFTER INSERT OR UPDATE OR DELETE ON projects
            FOR EACH ROW
            EXECUTE FUNCTION update_user_project_counts();
    """))

def downgrade():
    # Drop triggers
    op.execute(text("DROP TRIGGER IF EXISTS trigger_update_project_counts_on_project ON projects;"))
    op.execute(text("DROP TRIGGER IF EXISTS trigger_update_project_counts_on_user_project ON user_projects;"))
    op.execute(text("DROP TRIGGER IF EXISTS trigger_update_age_on_birthday ON users;"))
    
    # Drop functions
    op.execute(text("DROP FUNCTION IF EXISTS update_user_project_counts();"))
    op.execute(text("DROP FUNCTION IF EXISTS check_birthday_and_increment_age();"))
    op.execute(text("DROP FUNCTION IF EXISTS calculate_age_from_birthday();"))
    
    # Drop foreign key constraints
    op.drop_constraint('fk_users_city_id', 'users', type_='foreignkey')
    op.drop_constraint('fk_users_province_id', 'users', type_='foreignkey')
    
    # Remove columns from users table
    op.drop_column('users', 'city_id')
    op.drop_column('users', 'province_id')
    op.drop_column('users', 'age')
    op.drop_column('users', 'birthday')
    
    # Drop tables
    op.drop_table('user_institutions')
    op.drop_index(op.f('ix_user_institution_counts_id'), table_name='user_institution_counts')
    op.drop_table('user_institution_counts')
    op.drop_index(op.f('ix_user_project_counts_id'), table_name='user_project_counts')
    op.drop_table('user_project_counts')
    op.drop_index(op.f('ix_institutions_id'), table_name='institutions')
    op.drop_table('institutions')
    op.drop_index(op.f('ix_cities_id'), table_name='cities')
    op.drop_table('cities')
    op.drop_index(op.f('ix_provinces_id'), table_name='provinces')
    op.drop_table('provinces')