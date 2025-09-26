"""pilgrim view table

Revision ID: fa719f172387
Revises: 6e39ce8fe3c7
Create Date: 2025-09-26 18:42:14.707690

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'fa719f172387'
down_revision: Union[str, Sequence[str], None] = '6e39ce8fe3c7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('pilgrim_view_field',
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('view_name', sa.String(), nullable=True),
    sa.Column('username', sa.String(), nullable=True),
    sa.Column('field_name', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text("(NOW() AT TIME ZONE 'UTC') + interval '6 hours'"), nullable=False),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text("(NOW() AT TIME ZONE 'UTC') + interval '6 hours'"), nullable=False),
    sa.Column('created_by', sa.String(), nullable=True),
    sa.Column('updated_by', sa.String(), nullable=True),
    sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    schema='core'
    )
    op.create_index(op.f('ix_core_pilgrims_view__id'), 'pilgrim_view_field', ['id'], unique=False, schema='core')



def downgrade() -> None:
    op.drop_index(op.f('ix_core_pilgrims_view__id'), table_name='pilgrim_view_field', schema='core')
    op.drop_table('pilgrim_view_field', schema='core')
