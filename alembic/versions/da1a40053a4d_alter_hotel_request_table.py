"""alter hotel request table

Revision ID: da1a40053a4d
Revises: 4ed34369b8c9
Create Date: 2026-01-12 12:21:47.623104

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'da1a40053a4d'
down_revision: Union[str, Sequence[str], None] = '4ed34369b8c9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('hotel_request', sa.Column('cancel_request_status', sa.String(), nullable=True), schema='core')
    op.add_column('hotel_request', sa.Column('remarks', sa.String(), nullable=True), schema='core')


def downgrade() -> None:
    op.drop_column('hotel_request', 'cancel_request_status',schema='core')
    op.drop_column('hotel_request', 'remarks',schema='core')
