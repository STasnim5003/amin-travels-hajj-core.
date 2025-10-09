"""alter payment table add payable id

Revision ID: 1bd62b0bc74c
Revises: 3c4724da5d89
Create Date: 2025-10-09 14:42:15.296783

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1bd62b0bc74c'
down_revision: Union[str, Sequence[str], None] = '3c4724da5d89'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column('payment', 'parent_transaction_id', schema='core')
    op.add_column('payment', sa.Column('payable_id', sa.Integer(), nullable=True), schema='core')

def downgrade() -> None:
    op.drop_column('payment', 'payable_id', schema='core')
    op.add_column('payment', sa.Column('payable_id', sa.String(), nullable=True), schema='core')