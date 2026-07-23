"""alter table umrah vendor prices

Revision ID: 5cc09b970d36
Revises: 24c374acf3e3
Create Date: 2026-07-23 13:47:22.585915

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5cc09b970d36'
down_revision: Union[str, Sequence[str], None] = '24c374acf3e3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('umrah_vendor_prices', sa.Column('extra_service_charge', sa.Float(), nullable=True), schema='core')


def downgrade() -> None:
    op.drop_column('umrah_vendor_prices', 'extra_service_charge', schema='core')
