"""alter payment table

Revision ID: f62b2767eecd
Revises: 5e39aa0d2bb4
Create Date: 2025-10-10 16:01:04.345518

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'f62b2767eecd'
down_revision: Union[str, Sequence[str], None] = '5e39aa0d2bb4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('admin_user', sa.Column('total_available_amount', sa.Integer(), nullable=True, server_default="0"), schema='core')
    op.add_column('payment', sa.Column('tracking_id', sa.String(), nullable=True), schema='core')
    op.add_column('payment',sa.Column('receipt', postgresql.JSON(), nullable=True),schema='core')

def downgrade() -> None:
    op.drop_column('payment', 'tracking_id', schema='core')
    op.drop_column('payment', 'receipt', schema='core')
    op.drop_column('admin_user', 'total_available_amount', schema='core')
