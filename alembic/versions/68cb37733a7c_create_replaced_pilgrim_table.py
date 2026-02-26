"""create replaced pilgrim table

Revision ID: 68cb37733a7c
Revises: 26bc1a639e35
Create Date: 2026-02-26 14:04:11.305569

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '68cb37733a7c'
down_revision: Union[str, Sequence[str], None] = '26bc1a639e35'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'replaced_pilgrim',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True, index=True),
        sa.Column('tracking_id', sa.String, nullable=False),
        sa.Column('name_en', sa.String, nullable=False),
        sa.Column('replaced_tracking_id', sa.String, nullable=False),
        sa.Column('replaced_name_en', sa.String, nullable=False),
        sa.Column('agency_name', sa.String, nullable=True),
        sa.Column('created_at', sa.DateTime(),
                  server_default=sa.text("(NOW() AT TIME ZONE 'UTC') + interval '6 hours'"), nullable=False),
        sa.Column('updated_at', sa.DateTime(),
                  server_default=sa.text("(NOW() AT TIME ZONE 'UTC') + interval '6 hours'"), nullable=False),
        sa.Column('created_by', sa.String(), nullable=True),
        sa.Column('updated_by', sa.String(), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        schema='core'
    )


def downgrade() -> None:
    op.drop_table('replaced_pilgrim', schema='core')
