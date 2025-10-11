"""alter pilgrim table add payment info

Revision ID: 48111bb8c40c
Revises: f62b2767eecd
Create Date: 2025-10-11 14:40:56.669117

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '48111bb8c40c'
down_revision: Union[str, Sequence[str], None] = 'f62b2767eecd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('pilgrim_data', sa.Column('total_due',sa.Integer(), nullable=True, server_default="0"), schema="core")
    op.add_column('pilgrim_data', sa.Column('total_available_amount',sa.Integer(), nullable=True, server_default="0"), schema="core")


def downgrade() -> None:
    op.drop_column('pilgrim_data', 'total_available_amount', schema="core")
    op.drop_column('pilgrim_data', 'total_due', schema="core")
