"""create vendor table

Revision ID: 92a20b783b3c
Revises: 1822fe9fa8c2
Create Date: 2025-11-12 14:12:12.999225

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '92a20b783b3c'
down_revision: Union[str, Sequence[str], None] = '1822fe9fa8c2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('vendor',
        sa.Column('id', sa.Integer, primary_key=True,autoincrement=True, nullable=False),
        sa.Column('name', sa.String, nullable=False),
        sa.Column('category', sa.String, nullable=False),
        sa.Column('area', sa.String, nullable=True),
        sa.Column('agency_name', sa.String, nullable=True),
        sa.Column('created_at', sa.DateTime(),
                  server_default=sa.text("(NOW() AT TIME ZONE 'UTC') + interval '6 hours'"),
                  nullable=False),
        sa.Column('updated_at', sa.DateTime(),
                  server_default=sa.text("(NOW() AT TIME ZONE 'UTC') + interval '6 hours'"),
                  nullable=False),
        sa.Column('created_by', sa.String(), nullable=True),
        sa.Column('updated_by', sa.String(), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=False),
        schema='core'
    )


def downgrade() -> None:
    op.drop_table('vendor', schema='core')
