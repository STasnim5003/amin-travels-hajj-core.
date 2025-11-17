"""alter umrah requisition table

Revision ID: f3cdeb71feb5
Revises: 4da3d5e1a47f
Create Date: 2025-11-17 16:46:33.257212

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'f3cdeb71feb5'
down_revision: Union[str, Sequence[str], None] = '4da3d5e1a47f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('umrah_requisition', sa.Column('return_date_option_1', postgresql.JSONB(astext_type=sa.Text()), nullable=True), schema='core')
    op.add_column('umrah_requisition', sa.Column('return_date_option_2', postgresql.JSONB(astext_type=sa.Text()), nullable=True), schema='core')
    op.add_column('umrah_requisition', sa.Column('return_date_final', postgresql.JSONB(astext_type=sa.Text()), nullable=True), schema='core')
    op.add_column('umrah_requisition', sa.Column('exchange_rate', sa.Float, nullable=True), schema='core')


def downgrade() -> None:
    op.drop_column('umrah_requisition', 'return_date_option_1', schema='core')
    op.drop_column('umrah_requisition', 'return_date_option_2', schema='core')
    op.drop_column('umrah_requisition', 'return_date_final', schema='core')
    op.drop_column('umrah_requisition', 'exchange_rate', schema='core')