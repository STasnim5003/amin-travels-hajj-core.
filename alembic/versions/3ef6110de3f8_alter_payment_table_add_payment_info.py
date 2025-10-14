"""alter payment table add payment info

Revision ID: 3ef6110de3f8
Revises: 48111bb8c40c
Create Date: 2025-10-11 16:51:34.580030

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3ef6110de3f8'
down_revision: Union[str, Sequence[str], None] = '48111bb8c40c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('payment', sa.Column('total_payable', sa.Integer(), nullable=True, server_default="0"), schema='core')
    op.add_column('payment', sa.Column('total_payment', sa.Integer(), nullable=True, server_default="0"), schema='core')
    op.add_column('payment', sa.Column('total_due', sa.Integer(), nullable=True, server_default="0"), schema='core')


def downgrade() -> None:
    op.drop_column('payment', 'total_payable', schema='core')
    op.drop_column('payment', 'total_payment', schema='core')
    op.drop_column('payment', 'total_due', schema='core')
