"""pilgrim registered column added

Revision ID: d04a22b53dd2
Revises: db7549033d34
Create Date: 2025-10-04 13:23:58.689094

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd04a22b53dd2'
down_revision: Union[str, Sequence[str], None] = 'db7549033d34'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("pilgrim_data", sa.Column("passport_no", sa.String(), nullable=True), schema='core')
    op.add_column("pilgrim_data", sa.Column("passport_expiry_date", sa.String(), nullable=True), schema='core')
    op.add_column("pilgrim_data", sa.Column("payment_status", sa.String(), nullable=True), schema='core')


def downgrade() -> None:
    op.drop_column("pilgrim_data", "payment_status", schema='core')
    op.drop_column("pilgrim_data", "passport_no", schema='core')
    op.drop_column("pilgrim_data", "passport_expiry_date", schema='core')