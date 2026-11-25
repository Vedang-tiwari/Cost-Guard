"""004_add_phase4_tables

Revision ID: 004_add_phase4_tables
Revises: 003_add_budgets_and_evaluations
Create Date: 2026-11-25

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = '004_add_phase4_tables'
down_revision: str | None = '003_add_budgets_and_evaluations'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table('users') as batch_op:
        batch_op.add_column(sa.Column('full_name', sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column('organization_id', sa.String(length=36), nullable=True))
        batch_op.create_index(op.f('ix_users_organization_id'), ['organization_id'], unique=False)
        batch_op.create_foreign_key(
            'fk_users_organization_id', 'organizations', ['organization_id'], ['id'], ondelete='SET NULL'
        )

    with op.batch_alter_table('applications') as batch_op:
        batch_op.add_column(sa.Column('key_prefix', sa.String(length=24), nullable=True))

    op.create_table(
        'optimization_policies',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('organization_id', sa.String(length=36), nullable=False),
        sa.Column('intelligent_routing', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column('routing_strategy', sa.String(length=50), nullable=False, server_default='complexity_based'),
        sa.Column('semantic_cache', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column('cache_similarity_threshold', sa.Float(), nullable=False, server_default='0.88'),
        sa.Column('prompt_optimization', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column('quality_gate_enabled', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column('minimum_quality_score', sa.Float(), nullable=False, server_default='0.85'),
        sa.Column('fallback_to_premium', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column('max_output_tokens', sa.Integer(), nullable=False, server_default='1024'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_optimization_policies_organization_id'), 'optimization_policies', ['organization_id'], unique=True)

    op.create_table(
        'benchmark_runs',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('organization_id', sa.String(length=36), nullable=True),
        sa.Column('reference_model', sa.String(length=255), nullable=False),
        sa.Column('candidate_model', sa.String(length=255), nullable=False),
        sa.Column('total_cases', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('overall_quality_score', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('quality_retention', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('total_reference_cost', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('total_candidate_cost', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('cost_savings_pct', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('category_breakdown', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_benchmark_runs_organization_id'), 'benchmark_runs', ['organization_id'], unique=False)
    op.create_index(op.f('ix_benchmark_runs_created_at'), 'benchmark_runs', ['created_at'], unique=False)


def downgrade() -> None:
    op.drop_table('benchmark_runs')
    op.drop_table('optimization_policies')
    with op.batch_alter_table('applications') as batch_op:
        batch_op.drop_column('key_prefix')
    with op.batch_alter_table('users') as batch_op:
        batch_op.drop_constraint('fk_users_organization_id', type_='foreignkey')
        batch_op.drop_index(op.f('ix_users_organization_id'))
        batch_op.drop_column('organization_id')
        batch_op.drop_column('full_name')
