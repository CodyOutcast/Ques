"""Add payment tables

Revision ID: 20250902_1502
Revises: membership_system_001
Create Date: 2025-01-20 15:02:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20250902_1502'
down_revision = 'membership_system_001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create membership_transactions table
    op.create_table('membership_transactions',
        sa.Column('transaction_id', sa.String(length=64), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('membership_type', sa.String(length=10), nullable=False),
        sa.Column('amount', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=False),
        sa.Column('payment_method', sa.String(length=20), nullable=False),
        sa.Column('payment_provider_order_id', sa.String(length=64), nullable=True),
        sa.Column('payment_provider_transaction_id', sa.String(length=64), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('paid_at', sa.DateTime(), nullable=True),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ),
        sa.PrimaryKeyConstraint('transaction_id')
    )
    op.create_index(op.f('ix_membership_transactions_user_id'), 'membership_transactions', ['user_id'], unique=False)
    op.create_index(op.f('ix_membership_transactions_status'), 'membership_transactions', ['status'], unique=False)
    op.create_index(op.f('ix_membership_transactions_created_at'), 'membership_transactions', ['created_at'], unique=False)

    # Create payment_refunds table
    op.create_table('payment_refunds',
        sa.Column('refund_id', sa.String(length=64), nullable=False),
        sa.Column('transaction_id', sa.String(length=64), nullable=False),
        sa.Column('amount', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('reason', sa.String(length=255), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('provider_refund_id', sa.String(length=64), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('processed_at', sa.DateTime(), nullable=True),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(['transaction_id'], ['membership_transactions.transaction_id'], ),
        sa.PrimaryKeyConstraint('refund_id')
    )
    op.create_index(op.f('ix_payment_refunds_transaction_id'), 'payment_refunds', ['transaction_id'], unique=False)
    op.create_index(op.f('ix_payment_refunds_status'), 'payment_refunds', ['status'], unique=False)

    # Create payment_webhook_logs table
    op.create_table('payment_webhook_logs',
        sa.Column('log_id', sa.Integer(), nullable=False),
        sa.Column('provider', sa.String(length=32), nullable=False),
        sa.Column('event_type', sa.String(length=64), nullable=False),
        sa.Column('transaction_id', sa.String(length=64), nullable=True),
        sa.Column('raw_data', sa.Text(), nullable=False),
        sa.Column('processed', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('processed_at', sa.DateTime(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('log_id')
    )
    op.create_index(op.f('ix_payment_webhook_logs_log_id'), 'payment_webhook_logs', ['log_id'], unique=False)
    op.create_index(op.f('ix_payment_webhook_logs_provider'), 'payment_webhook_logs', ['provider'], unique=False)
    op.create_index(op.f('ix_payment_webhook_logs_transaction_id'), 'payment_webhook_logs', ['transaction_id'], unique=False)


def downgrade() -> None:
    # Drop tables
    op.drop_index(op.f('ix_payment_webhook_logs_transaction_id'), table_name='payment_webhook_logs')
    op.drop_index(op.f('ix_payment_webhook_logs_provider'), table_name='payment_webhook_logs')
    op.drop_index(op.f('ix_payment_webhook_logs_log_id'), table_name='payment_webhook_logs')
    op.drop_table('payment_webhook_logs')
    
    op.drop_index(op.f('ix_payment_refunds_status'), table_name='payment_refunds')
    op.drop_index(op.f('ix_payment_refunds_transaction_id'), table_name='payment_refunds')
    op.drop_table('payment_refunds')
    
    op.drop_index(op.f('ix_membership_transactions_created_at'), table_name='membership_transactions')
    op.drop_index(op.f('ix_membership_transactions_status'), table_name='membership_transactions')
    op.drop_index(op.f('ix_membership_transactions_user_id'), table_name='membership_transactions')
    op.drop_table('membership_transactions')
