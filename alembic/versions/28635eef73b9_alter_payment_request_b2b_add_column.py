"""alter payment request b2b add column

Revision ID: 28635eef73b9
Revises: 0eb45edb54ee
Create Date: 2026-01-21 12:25:59.532244

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '28635eef73b9'
down_revision: Union[str, Sequence[str], None] = '0eb45edb54ee'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('payment_request_b2b', sa.Column('exchanged_amount', sa.Float(), nullable=True), schema='core')


def downgrade() -> None:
    op.drop_column('payment_request_b2b', 'exchanged_amount',schema='core')
