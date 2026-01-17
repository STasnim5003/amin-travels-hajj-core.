"""alter hotel request table add rfq_no column

Revision ID: 03d8b3bb0c48
Revises: 449aec786792
Create Date: 2026-01-17 15:18:22.322015

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '03d8b3bb0c48'
down_revision: Union[str, Sequence[str], None] = '449aec786792'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('hotel_request', sa.Column('rfq_no', sa.Integer(), nullable=True), schema='core')


def downgrade() -> None:
    op.drop_column('hotel_request', 'rfq_no', schema='core')
