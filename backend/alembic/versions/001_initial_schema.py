"""001_initial_schema

Revision ID: 001_initial_schema
Revises:
Create Date: 2026-11-20

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = '001_initial_schema'
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Organizations
    op.create_table(
        'organizations',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # Users
    op.create_table(
        'users',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)

    # Applications
    op.create_table(
        'applications',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('organization_id', sa.String(length=36), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('api_key_hash', sa.String(length=64), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_applications_api_key_hash'), 'applications', ['api_key_hash'], unique=True)
    op.create_index(op.f('ix_applications_organization_id'), 'applications', ['organization_id'], unique=False)

    # Models Registry
    op.create_table(
        'models',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('provider', sa.String(length=100), nullable=False),
        sa.Column('model_name', sa.String(length=255), nullable=False),
        sa.Column('input_price_per_million', sa.Float(), nullable=False),
        sa.Column('output_price_per_million', sa.Float(), nullable=False),
        sa.Column('capabilities', sa.JSON(), nullable=False),
        sa.Column('context_window', sa.Integer(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('pricing_version', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_models_is_active'), 'models', ['is_active'], unique=False)
    op.create_index(op.f('ix_models_model_name'), 'models', ['model_name'], unique=True)
    op.create_index(op.f('ix_models_provider'), 'models', ['provider'], unique=False)

    # Request Logs
    op.create_table(
        'request_logs',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('request_id', sa.String(length=64), nullable=False),
        sa.Column('application_id', sa.String(length=36), nullable=True),
        sa.Column('organization_id', sa.String(length=36), nullable=True),
        sa.Column('provider', sa.String(length=100), nullable=False),
        sa.Column('model', sa.String(length=255), nullable=False),
        sa.Column('input_tokens', sa.Integer(), nullable=False),
        sa.Column('output_tokens', sa.Integer(), nullable=False),
        sa.Column('estimated_cost', sa.Float(), nullable=False),
        sa.Column('actual_cost', sa.Float(), nullable=False),
        sa.Column('latency_ms', sa.Float(), nullable=False),
        sa.Column('cache_hit', sa.Boolean(), nullable=False),
        sa.Column('complexity_score', sa.Float(), nullable=False),
        sa.Column('routing_strategy', sa.String(length=100), nullable=False),
        sa.Column('quality_score', sa.Float(), nullable=True),
        sa.Column('fallback_used', sa.Boolean(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['application_id'], ['applications.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_request_logs_application_id'), 'request_logs', ['application_id'], unique=False)
    op.create_index(op.f('ix_request_logs_created_at'), 'request_logs', ['created_at'], unique=False)
    op.create_index(op.f('ix_request_logs_model'), 'request_logs', ['model'], unique=False)
    op.create_index(op.f('ix_request_logs_organization_id'), 'request_logs', ['organization_id'], unique=False)
    op.create_index(op.f('ix_request_logs_provider'), 'request_logs', ['provider'], unique=False)
    op.create_index(op.f('ix_request_logs_request_id'), 'request_logs', ['request_id'], unique=True)
    op.create_index(op.f('ix_request_logs_status'), 'request_logs', ['status'], unique=False)


def downgrade() -> None:
    op.drop_table('request_logs')
    op.drop_table('models')
    op.drop_table('applications')
    op.drop_table('users')
    op.drop_table('organizations')
