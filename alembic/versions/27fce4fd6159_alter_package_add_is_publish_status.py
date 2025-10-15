"""alter package add is_publish status

Revision ID: 27fce4fd6159
Revises: 3ef6110de3f8
Create Date: 2025-10-15 12:36:38.992487

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '27fce4fd6159'
down_revision: Union[str, Sequence[str], None] = '3ef6110de3f8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('packages', sa.Column('is_publish', sa.Boolean(), nullable=True, server_default=sa.text('true')), schema='core')
    op.add_column('pilgrim_data', sa.Column('payment_against', sa.String(), nullable=True, server_default=sa.text("'INDIVIDUAL'")), schema='core')
    op.add_column('pilgrim_data', sa.Column('package_price_discount', sa.Integer(), nullable=True, server_default=sa.text('0')), schema='core')
    op.add_column('pilgrim_data', sa.Column('actual_payable', sa.Integer(), nullable=True, server_default=sa.text('0')), schema='core')


def downgrade() -> None:
    op.drop_column('packages', 'is_publish', schema='core')
    op.drop_column('pilgrim_data', 'payment_against', schema='core')
    op.drop_column('pilgrim_data', 'package_price_discount', schema='core')
    op.drop_column('pilgrim_data', 'actual_payable', schema='core')