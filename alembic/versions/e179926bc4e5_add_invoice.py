"""add invoice

Revision ID: e179926bc4e5
Revises: 5cc09b970d36
Create Date: 2026-07-23 14:05:38.542606

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'e179926bc4e5'
down_revision: Union[str, Sequence[str], None] = '5cc09b970d36'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('umrah_b2b_payements', sa.Column('office_code', sa.String(), nullable=True), schema='core')
    op.add_column('umrah_b2b_payements', sa.Column('paid_amount', sa.Float(), nullable=True), schema='core')
    op.add_column('umrah_b2b_payements', sa.Column('due', sa.Float(), nullable=True), schema='core')
    op.add_column('umrah_b2b_payements', sa.Column('invoice_no_and_paid_amount', postgresql.JSONB(astext_type=sa.Text()), nullable=True), schema='core')


def downgrade() -> None:
    op.drop_column('umrah_b2b_payements', 'office_code', schema='core')
    op.drop_column('umrah_b2b_payements', 'paid_amount', schema='core')
    op.drop_column('umrah_b2b_payements', 'due', schema='core')
    op.drop_column('umrah_b2b_payements', 'invoice_no_and_paid_amount', schema='core')
