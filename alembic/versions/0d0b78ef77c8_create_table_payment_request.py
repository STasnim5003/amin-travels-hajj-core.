"""create table payment request

Revision ID: 0d0b78ef77c8
Revises: c928ec80f98e
Create Date: 2025-11-20 12:59:02.110797

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '0d0b78ef77c8'
down_revision: Union[str, Sequence[str], None] = 'c928ec80f98e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'payment_request_b2b',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True, index=True),
        sa.Column('payment_way', sa.String, nullable=False),
        sa.Column('money_receipt_payment_slip_file', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('reference_number', sa.String, nullable=True),
        sa.Column('transaction_id', sa.String, nullable=True),
        sa.Column('money_receipt_number', sa.String, nullable=True),
        sa.Column('status', sa.String, nullable=True),
        sa.Column('agency_name', sa.String, nullable=True),
        sa.Column('created_at', sa.DateTime(),
                  server_default=sa.text("(NOW() AT TIME ZONE 'UTC') + interval '6 hours'"), nullable=False),
        sa.Column('updated_at', sa.DateTime(),
                  server_default=sa.text("(NOW() AT TIME ZONE 'UTC') + interval '6 hours'"), nullable=False),
        sa.Column('created_by', sa.String(), nullable=True),
        sa.Column('updated_by', sa.String(), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        schema='core'
    )


def downgrade() -> None:
    op.drop_table('payment_request_b2b', schema='core')
