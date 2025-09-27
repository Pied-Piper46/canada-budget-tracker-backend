"""remove institution_name and add account_official_name to accounts table

Revision ID: e9d801f12f2a
Revises: 044d186218d5
Create Date: 2025-09-26 18:45:34.050617

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'e9d801f12f2a'
down_revision: Union[str, Sequence[str], None] = '044d186218d5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create new production schema
    op.execute("CREATE SCHEMA IF NOT EXISTS canada_budget_tracker_production")

    # Create accounts table with new structure
    op.create_table('accounts',
        sa.Column('account_id', sa.String(length=255), nullable=False),
        sa.Column('account_name', sa.String(length=100), nullable=True),
        sa.Column('account_official_name', sa.String(length=100), nullable=True),
        sa.Column('account_type', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('last_synced_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('account_id'),
        schema='canada_budget_tracker_production'
    )

    # Create custom_categories table
    op.create_table('custom_categories',
        sa.Column('category_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.PrimaryKeyConstraint('category_id'),
        sa.UniqueConstraint('name'),
        schema='canada_budget_tracker_production'
    )

    # Create sync_cursors table
    op.create_table('sync_cursors',
        sa.Column('account_id', sa.String(length=255), nullable=False),
        sa.Column('cursor', sa.String(length=255), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.ForeignKeyConstraint(['account_id'], ['canada_budget_tracker_production.accounts.account_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('account_id'),
        schema='canada_budget_tracker_production'
    )

    # Create transactions table
    op.create_table('transactions',
        sa.Column('transaction_id', sa.String(length=255), nullable=False),
        sa.Column('account_id', sa.String(length=255), nullable=True),
        sa.Column('amount', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('transaction_date', sa.Date(), nullable=False),
        sa.Column('merchant_name', sa.String(length=255), nullable=True),
        sa.Column('name', sa.String(length=255), nullable=True),
        sa.Column('pending', sa.Boolean(), nullable=True),
        sa.Column('pending_transaction_id', sa.String(length=255), nullable=True),
        sa.Column('personal_finance_category_primary', sa.String(length=100), nullable=True),
        sa.Column('personal_finance_category_detailed', sa.String(length=100), nullable=True),
        sa.Column('custom_category_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('is_removed', sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(['account_id'], ['canada_budget_tracker_production.accounts.account_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('transaction_id'),
        schema='canada_budget_tracker_production'
    )

    # Create indexes for better query performance
    op.create_index('idx_transactions_account_id', 'transactions', ['account_id'], unique=False, schema='canada_budget_tracker_production')
    op.create_index('idx_transactions_date', 'transactions', ['transaction_date'], unique=False, schema='canada_budget_tracker_production')
    op.create_index('idx_transactions_category', 'transactions', ['personal_finance_category_primary'], unique=False, schema='canada_budget_tracker_production')
    op.create_index('idx_transactions_pending', 'transactions', ['pending'], unique=False, schema='canada_budget_tracker_production')
    op.create_index('idx_transactions_is_removed', 'transactions', ['is_removed'], unique=False, schema='canada_budget_tracker_production')

    # Create additional foreign key constraint for custom categories
    op.create_foreign_key(
        'fk_custom_category',
        'transactions',
        'custom_categories',
        ['custom_category_id'],
        ['category_id'],
        ondelete='SET NULL',
        source_schema='canada_budget_tracker_production',
        referent_schema='canada_budget_tracker_production'
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Drop foreign key constraints first
    op.drop_constraint('fk_custom_category', 'transactions', schema='canada_budget_tracker_production')

    # Drop indexes
    op.drop_index('idx_transactions_is_removed', 'transactions', schema='canada_budget_tracker_production')
    op.drop_index('idx_transactions_pending', 'transactions', schema='canada_budget_tracker_production')
    op.drop_index('idx_transactions_category', 'transactions', schema='canada_budget_tracker_production')
    op.drop_index('idx_transactions_date', 'transactions', schema='canada_budget_tracker_production')
    op.drop_index('idx_transactions_account_id', 'transactions', schema='canada_budget_tracker_production')

    # Drop tables in reverse order (due to foreign keys)
    op.drop_table('transactions', schema='canada_budget_tracker_production')
    op.drop_table('sync_cursors', schema='canada_budget_tracker_production')
    op.drop_table('custom_categories', schema='canada_budget_tracker_production')
    op.drop_table('accounts', schema='canada_budget_tracker_production')

    # Drop schema if empty
    op.execute("DROP SCHEMA IF EXISTS canada_budget_tracker_production")
