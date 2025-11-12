"""alter umrah requisition table add column

Revision ID: 1822fe9fa8c2
Revises: b62f7bc62690
Create Date: 2025-11-12 12:17:30.000296

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '1822fe9fa8c2'
down_revision: Union[str, Sequence[str], None] = 'b62f7bc62690'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('umrah_requisition', sa.Column('mobile_no', sa.String(), nullable=True), schema='core')
    op.add_column('umrah_requisition', sa.Column('food', sa.Boolean(), nullable=True), schema='core')
    op.add_column('umrah_requisition', sa.Column('flight_date_option_1', postgresql.JSONB(astext_type=sa.Text()), nullable=True), schema='core')
    op.add_column('umrah_requisition', sa.Column('flight_date_option_2', postgresql.JSONB(astext_type=sa.Text()), nullable=True), schema='core')

    op.add_column('flight_request', sa.Column('duration', sa.String(), nullable=True), schema='core')

def downgrade() -> None:
    op.drop_column('umrah_requisition', 'flight_date_option_2', schema='core')
    op.drop_column('flight_request', 'duration', schema='core')
    op.drop_column('umrah_requisition', 'food', schema='core')
    op.drop_column('umrah_requisition', 'mobile_no', schema='core')
    op.drop_column('umrah_requisition', 'flight_date_option_1', schema='core')