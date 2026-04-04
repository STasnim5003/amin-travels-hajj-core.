"""alter umrah requisition add column

Revision ID: d6e6646fab04
Revises: 2a34df15bbb7
Create Date: 2026-04-04 13:49:30.412425

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd6e6646fab04'
down_revision: Union[str, Sequence[str], None] = '2a34df15bbb7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('umrah_requisition', sa.Column('train', sa.Boolean(), nullable=True), schema='core')
    op.add_column('umrah_requisition', sa.Column('guide', sa.Boolean(), nullable=True), schema='core')
    op.add_column('umrah_b2b_payements', sa.Column('invoice_no', sa.String(), nullable=True), schema='core')

def downgrade() -> None:
    op.drop_column('umrah_requisition', 'guide', schema='core')
    op.drop_column('umrah_requisition', 'train', schema='core')
    op.drop_column('umrah_b2b_payements', 'invoice_no', schema='core')
