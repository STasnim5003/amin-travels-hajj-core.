"""alter umrah vendor billing

Revision ID: 26b038c0d3cf
Revises: cbc276a0fdfc
Create Date: 2026-06-15 00:16:20.941863

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '26b038c0d3cf'
down_revision: Union[str, Sequence[str], None] = 'cbc276a0fdfc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column('umrah_vendor_billing', 'bill', schema='core')
    op.drop_column('umrah_vendor_billing', 'credit', schema='core')
    op.drop_column('umrah_vendor_billing', 'guest_name', schema='core')
    op.add_column('umrah_vendor_billing', sa.Column('amount', sa.Float, nullable=False), schema='core')
    op.add_column('umrah_vendor_billing', sa.Column('category', sa.TEXT, nullable=False), schema='core')


def downgrade() -> None:
    op.drop_column('umrah_vendor_billing', 'amount', schema='core')
    op.drop_column('umrah_vendor_billing', 'category', schema='core')
