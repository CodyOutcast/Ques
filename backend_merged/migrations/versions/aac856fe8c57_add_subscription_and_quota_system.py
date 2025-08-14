"""Add subscription and quota system

Revision ID: aac856fe8c57
Revises: 010_project_idea_requests
Create Date: 2025-08-14 12:29:35.123456

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'aac856fe8c57'
down_revision = '010_project_idea_requests'
branch_labels = None
depends_on = None


def upgrade():
    # Create subscription type enum only if it doesn't exist
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE subscriptiontype AS ENUM ('free', 'pro', 'enterprise');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    
    # Create user_subscriptions table
    op.create_table('user_subscriptions',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('subscription_type', postgresql.ENUM('free', 'pro', 'enterprise', name='subscriptiontype', create_type=False), nullable=False, server_default='free'),
        sa.Column('monthly_quota_limit', sa.Integer(), nullable=False, server_default='30'),
        sa.Column('current_period_start', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('current_period_end', sa.DateTime(), nullable=False),
        sa.Column('current_period_usage', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_requests_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ondelete='CASCADE'),
        sa.UniqueConstraint('user_id', name='uq_user_subscriptions_user_id')
    )
    
    # Create indexes for user_subscriptions
    op.create_index('ix_user_subscriptions_user_id', 'user_subscriptions', ['user_id'])
    op.create_index('ix_user_subscriptions_subscription_type', 'user_subscriptions', ['subscription_type'])
    op.create_index('ix_user_subscriptions_current_period_end', 'user_subscriptions', ['current_period_end'])
    
    # Add subscription_id column to existing project_idea_requests table
    op.add_column('project_idea_requests', sa.Column('subscription_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_project_idea_requests_subscription', 'project_idea_requests', 'user_subscriptions', ['subscription_id'], ['id'], ondelete='CASCADE')
    op.create_index('ix_project_idea_requests_subscription_id', 'project_idea_requests', ['subscription_id'])
    
    # Populate subscription_id for existing records
    op.execute("""
        -- First, create default subscriptions for all users
        INSERT INTO user_subscriptions (user_id, subscription_type, monthly_quota_limit, current_period_start, current_period_end)
        SELECT DISTINCT u.user_id, 'free'::subscriptiontype, 30, DATE_TRUNC('month', NOW()), DATE_TRUNC('month', NOW()) + INTERVAL '1 month' - INTERVAL '1 day'
        FROM users u
        WHERE NOT EXISTS (SELECT 1 FROM user_subscriptions us WHERE us.user_id = u.user_id);
        
        -- Update existing project_idea_requests with subscription_id
        UPDATE project_idea_requests pir 
        SET subscription_id = us.id
        FROM user_subscriptions us 
        WHERE pir.user_id = us.user_id;
    """)
    
    # Make subscription_id NOT NULL after populating
    op.alter_column('project_idea_requests', 'subscription_id', nullable=False)
    
    # Create trigger to update subscription usage
    op.execute("""
        CREATE OR REPLACE FUNCTION update_subscription_usage()
        RETURNS TRIGGER AS $$
        BEGIN
            UPDATE user_subscriptions 
            SET current_period_usage = current_period_usage + 1,
                total_requests_count = total_requests_count + 1,
                updated_at = NOW()
            WHERE id = NEW.subscription_id;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        
        CREATE TRIGGER trigger_update_subscription_usage
            AFTER INSERT ON project_idea_requests
            FOR EACH ROW
            EXECUTE FUNCTION update_subscription_usage();
    """)


def downgrade():
    # Drop trigger and function
    op.execute("DROP TRIGGER IF EXISTS trigger_update_subscription_usage ON project_idea_requests;")
    op.execute("DROP FUNCTION IF EXISTS update_subscription_usage();")
    
    # Remove subscription_id column from project_idea_requests
    op.drop_index('ix_project_idea_requests_subscription_id', table_name='project_idea_requests')
    op.drop_constraint('fk_project_idea_requests_subscription', 'project_idea_requests', type_='foreignkey')
    op.drop_column('project_idea_requests', 'subscription_id')
    
    # Drop indexes for user_subscriptions
    op.drop_index('ix_user_subscriptions_current_period_end', table_name='user_subscriptions')
    op.drop_index('ix_user_subscriptions_subscription_type', table_name='user_subscriptions')
    op.drop_index('ix_user_subscriptions_user_id', table_name='user_subscriptions')
    
    # Drop user_subscriptions table
    op.drop_table('user_subscriptions')
    
    # Drop enum type
    op.execute("DROP TYPE IF EXISTS subscriptiontype;")
