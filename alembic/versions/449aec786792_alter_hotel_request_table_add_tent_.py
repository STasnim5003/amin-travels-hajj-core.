"""alter hotel request table add tent column

Revision ID: 449aec786792
Revises: 78de787e20ab
Create Date: 2026-01-15 14:49:35.243024

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '449aec786792'
down_revision: Union[str, Sequence[str], None] = '78de787e20ab'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('hotel_request', sa.Column('tent', sa.String(), nullable=True), schema='core')


def downgrade() -> None:
    op.drop_column('hotel_request', 'tent', schema='core')
