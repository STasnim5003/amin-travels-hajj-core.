"""Add payment_status to users, remove from payment_info

Revision ID: 477046cef457
Revises: 7e3336f2616a
Create Date: 2025-08-12 15:15:08.669465

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '477046cef457'
down_revision: Union[str, Sequence[str], None] = '7e3336f2616a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Add `payment_status` to `core.users`
    op.add_column('users', sa.Column('payment_status', sa.String(), nullable=False, server_default="PENDING"), schema='core')

    # Drop `payment_status` from `core.payment_info`
    with op.batch_alter_table('payment_info', schema='core') as batch_op:
        batch_op.drop_column('payment_status')


def downgrade():
    # Revert changes
    with op.batch_alter_table('payment_info', schema='core') as batch_op:
        batch_op.add_column(sa.Column('payment_status', sa.Integer(), nullable=False))

    op.drop_column('users', 'payment_status', schema='core')
