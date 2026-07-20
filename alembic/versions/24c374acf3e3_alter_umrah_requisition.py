"""alter umrah requisition

Revision ID: 24c374acf3e3
Revises: 394995d5a8a1
Create Date: 2026-07-20 15:52:03.802898

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '24c374acf3e3'
down_revision: Union[str, Sequence[str], None] = '394995d5a8a1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('umrah_requisition', sa.Column('extra_service_charge', sa.Float(), nullable=True),schema='core')


def downgrade() -> None:
    op.drop_column('umrah_requisition', 'extra_service_charge', schema='core')
