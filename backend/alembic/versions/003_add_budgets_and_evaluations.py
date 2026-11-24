"""003_add_budgets_and_evaluations

Revision ID: 003_add_budgets_and_evaluations
Revises: 002_add_cache_entries
Create Date: 2026-11-24

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = '003_add_budgets_and_evaluations'
down_revision: str | None = '002_add_cache_entries'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        'budgets',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('organization_id', sa.String(length=36), nullable=False),
        sa.Column('application_id', sa.String(length=36), nullable=True),
        sa.Column('budget_type', sa.String(length=50), nullable=False, server_default='organization'),
        sa.Column('limit_amount', sa.Float(), nullable=False),
        sa.Column('warning_threshold', sa.Float(), nullable=False, server_default='0.8'),
        sa.Column('hard_limit', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column('period', sa.String(length=50), nullable=False, server_default='monthly'),
        sa.Column('current_spend', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='active'),
        sa.Column('reset_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['application_id'], ['applications.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_budgets_application_id'), 'budgets', ['application_id'], unique=False)
    op.create_index(op.f('ix_budgets_organization_id'), 'budgets', ['organization_id'], unique=False)
    op.create_index(op.f('ix_budgets_created_at'), 'budgets', ['created_at'], unique=False)

    op.create_table(
        'evaluations',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('request_id', sa.String(length=64), nullable=False),
        sa.Column('reference_model', sa.String(length=255), nullable=False),
        sa.Column('candidate_model', sa.String(length=255), nullable=False),
        sa.Column('quality_score', sa.Float(), nullable=False),
        sa.Column('evaluation_method', sa.String(length=100), nullable=False),
        sa.Column('passed', sa.Boolean(), nullable=False),
        sa.Column('metrics', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_evaluations_request_id'), 'evaluations', ['request_id'], unique=False)
    op.create_index(op.f('ix_evaluations_created_at'), 'evaluations', ['created_at'], unique=False)


def downgrade() -> None:
    op.drop_table('evaluations')
    op.drop_table('budgets')
