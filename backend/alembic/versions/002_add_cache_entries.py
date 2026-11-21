"""002_add_cache_entries

Revision ID: 002_add_cache_entries
Revises: 001_initial_schema
Create Date: 2026-11-21

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = '002_add_cache_entries'
down_revision: str | None = '001_initial_schema'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        'cache_entries',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('application_id', sa.String(length=36), nullable=False),
        sa.Column('organization_id', sa.String(length=36), nullable=False),
        sa.Column('cache_key', sa.String(length=64), nullable=False),
        sa.Column('embedding', sa.JSON(), nullable=False),
        sa.Column('query_text', sa.Text(), nullable=False),
        sa.Column('response_content', sa.Text(), nullable=False),
        sa.Column('model', sa.String(length=255), nullable=False),
        sa.Column('prompt_version', sa.String(length=50), nullable=False),
        sa.Column('metadata_info', sa.JSON(), nullable=True),
        sa.Column('tokens_saved', sa.Float(), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['application_id'], ['applications.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_cache_entries_application_id'), 'cache_entries', ['application_id'], unique=False)
    op.create_index(op.f('ix_cache_entries_cache_key'), 'cache_entries', ['cache_key'], unique=False)
    op.create_index(op.f('ix_cache_entries_created_at'), 'cache_entries', ['created_at'], unique=False)
    op.create_index(op.f('ix_cache_entries_expires_at'), 'cache_entries', ['expires_at'], unique=False)
    op.create_index(op.f('ix_cache_entries_organization_id'), 'cache_entries', ['organization_id'], unique=False)


def downgrade() -> None:
    op.drop_table('cache_entries')
