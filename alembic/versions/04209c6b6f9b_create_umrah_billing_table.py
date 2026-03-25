"""create umrah billing table

Revision ID: 04209c6b6f9b
Revises: aad6fcbb3405
Create Date: 2026-03-25 15:29:40.126920

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '04209c6b6f9b'
down_revision: Union[str, Sequence[str], None] = '0befab704cc0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('umrah_customer_billing',
        sa.Column('id', sa.Integer, autoincrement=True, primary_key=True, index=True),
        sa.Column('invoice_no', sa.String, nullable=False),
        sa.Column('description', sa.String, nullable=True),
        sa.Column('way_of_payment', sa.String, nullable=True),
        sa.Column('amount', sa.Float, nullable=False),
        sa.Column('date', sa.String, nullable=False),
        sa.Column('remarks', sa.String, nullable=True),
        sa.Column('receipt', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('agency_name', sa.String, nullable=True),
        sa.Column('created_at', sa.DateTime(),
                  server_default=sa.text("(NOW() AT TIME ZONE 'UTC') + interval '6 hours'"),
                  nullable=False),
        sa.Column('updated_at', sa.DateTime(),
                  server_default=sa.text("(NOW() AT TIME ZONE 'UTC') + interval '6 hours'"),
                  nullable=False),
        sa.Column('created_by', sa.String(), nullable=True),
        sa.Column('updated_by', sa.String(), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=False),
        schema='core'
        )


def downgrade() -> None:
    op.drop_table('umrah_customer_billing', schema='core')
