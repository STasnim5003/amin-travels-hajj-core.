"""alter admin user payment status

Revision ID: f16a172ae350
Revises: 8a57cf29f09c
Create Date: 2025-10-16 18:56:50.015760

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'f16a172ae350'
down_revision: Union[str, Sequence[str], None] = '8a57cf29f09c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('admin_user', sa.Column('is_payment_distributed', sa.Boolean(), nullable=True, server_default=sa.text('false')), schema='core')
    # op.drop_column('payment', 'pilgrims_id', schema='core')
    op.add_column('payment', sa.Column('pilgrims_tracking_id', postgresql.JSONB(astext_type=sa.Text()), nullable=True), schema='core')
    # op.drop_column('payment', 'total_payable',schema='core')
    # op.drop_column('payment', 'total_due',schema='core')


def downgrade() -> None:
    op.drop_column('admin_user', 'is_payment_distributed', schema='core')
    op.drop_column('payment', 'pilgrims_tracking_id', schema='core')
