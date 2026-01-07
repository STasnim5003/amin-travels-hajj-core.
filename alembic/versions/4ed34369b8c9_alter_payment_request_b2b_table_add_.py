"""alter payment_request_b2b table add column

Revision ID: 4ed34369b8c9
Revises: e302e6903a16
Create Date: 2026-01-07 15:39:46.798840

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4ed34369b8c9'
down_revision: Union[str, Sequence[str], None] = 'e302e6903a16'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('payment_request_b2b', sa.Column('purpose', sa.String(), nullable=True), schema='core')
    op.add_column('payment_request_b2b', sa.Column('payment_date', sa.String(), nullable=True), schema='core')
    op.add_column('payment_request_b2b', sa.Column('details', sa.String(), nullable=True), schema='core')
    op.add_column('payment_request_b2b', sa.Column('amount', sa.Float(), nullable=True), schema='core')
    op.add_column('payment_request_b2b', sa.Column('exchange_rate', sa.Float(), nullable=True), schema='core')
    op.add_column('payment_request_b2b', sa.Column('sector', sa.String(), nullable=True), schema='core')
    op.add_column('payment_request_b2b', sa.Column('remarks', sa.String(), nullable=True), schema='core')
    op.add_column('payment_request_b2b', sa.Column('nusuk_request_id', sa.String(), nullable=True), schema='core')


def downgrade() -> None:
    op.drop_column('payment_request_b2b', 'nusuk_request_id', schema='core')
    op.drop_column('payment_request_b2b', 'remarks', schema='core')
    op.drop_column('payment_request_b2b', 'sector', schema='core')
    op.drop_column('payment_request_b2b', 'exchange_rate', schema='core')
    op.drop_column('payment_request_b2b', 'amount', schema='core')
    op.drop_column('payment_request_b2b', 'payment_date', schema='core')
    op.drop_column('payment_request_b2b', 'details', schema='core')
    op.drop_column('payment_request_b2b', 'purpose', schema='core')
