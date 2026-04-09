"""alter vendor price table

Revision ID: 7cb5624c2b63
Revises: 98d66ec29f1a
Create Date: 2026-04-09 11:47:04.356232

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '7cb5624c2b63'
down_revision: Union[str, Sequence[str], None] = '98d66ec29f1a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('umrah_vendor_prices', sa.Column("guide_vendors_price", postgresql.JSONB(astext_type=sa.Text()), nullable=True), schema='core')


def downgrade() -> None:
    op.drop_column('umrah_vendor_prices', 'guide_vendors_price', schema='core')
