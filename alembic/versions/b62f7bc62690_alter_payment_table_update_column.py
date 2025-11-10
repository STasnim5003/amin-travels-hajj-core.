"""alter payment table update column

Revision ID: b62f7bc62690
Revises: 12fc456c2c25
Create Date: 2025-11-10 13:59:45.254138

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b62f7bc62690'
down_revision: Union[str, Sequence[str], None] = '12fc456c2c25'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('payment', sa.Column('cheque_no', sa.String, nullable=True), schema='core')
    op.add_column('payment', sa.Column('cheque_bank', sa.String, nullable=True), schema='core')
    op.add_column('payment', sa.Column('voucher_no', sa.String, nullable=True), schema='core')


def downgrade() -> None:
    op.drop_column('payment', 'cheque_no', schema='core')
    op.drop_column('payment', 'cheque_bank', schema='core')
    op.drop_column('payment', 'voucher_no', schema='core')
