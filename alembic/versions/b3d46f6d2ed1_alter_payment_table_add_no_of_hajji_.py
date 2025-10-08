"""alter payment table add no of hajji column

Revision ID: b3d46f6d2ed1
Revises: 6777c892da5f
Create Date: 2025-10-08 20:06:47.911578

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b3d46f6d2ed1'
down_revision: Union[str, Sequence[str], None] = '6777c892da5f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('payment', sa.Column('no_of_hajji', sa.Integer(), nullable=True, server_default="0"), schema="core")



def downgrade() -> None:
    op.drop_column("payment", "no_of_hajji", schema='core')
