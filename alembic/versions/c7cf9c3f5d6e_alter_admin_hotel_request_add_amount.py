"""alter admin table add amount

Revision ID: c7cf9c3f5d6e
Revises: 0d0b78ef77c8
Create Date: 2025-12-25 23:02:45.691002

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'c7cf9c3f5d6e'
down_revision: Union[str, Sequence[str], None] = '0d0b78ef77c8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('admin', sa.Column('bdt', sa.Float(), nullable=True, default=0), schema="core")
    op.add_column('admin', sa.Column('sar', sa.Float(), nullable=True, default=0), schema="core")

    op.add_column('hotel_request', sa.Column('price_per_hajji', postgresql.JSON(astext_type=sa.Text()),nullable=True), schema="core")
    op.add_column('hotel_request', sa.Column('grand_total', postgresql.JSON(astext_type=sa.Text()),nullable=True), schema="core")
    op.add_column('hotel_request', sa.Column('nusuk_request_file_category', sa.String(), nullable=True), schema="core")

def downgrade() -> None:
    op.drop_column('admin', 'sar', schema='core')
    op.drop_column('admin', 'bdt', schema='core')

    op.drop_column('hotel_request', 'grand_total', schema='core')
    op.drop_column('hotel_request', 'price_per_hajji', schema='core')
    op.drop_column('hotel_request', 'nusuk_request_file_category', schema='core')
