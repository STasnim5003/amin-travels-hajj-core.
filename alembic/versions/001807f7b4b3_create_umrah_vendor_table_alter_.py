"""create umrah vendor table & alter requisition

Revision ID: 001807f7b4b3
Revises: b2b0cb35c533
Create Date: 2026-03-27 15:11:23.781360

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '001807f7b4b3'
down_revision: Union[str, Sequence[str], None] = 'b2b0cb35c533'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('umrah_vendor_billing',
        sa.Column('id', sa.Integer, autoincrement=True, primary_key=True, index=True),
        sa.Column('umrah_requisition_code', sa.String, nullable=False),
        sa.Column('invoice_no', sa.String, nullable=False),
        sa.Column('guest_name', sa.String, nullable=False),
        sa.Column('vendor_name', sa.String, nullable=False),
        sa.Column('description', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('bill', sa.Float, nullable=False),
        sa.Column('credit', sa.Float, nullable=False),
        sa.Column('payment_date', sa.String, nullable=False),
        sa.Column('remarks', sa.String, nullable=True),
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

    op.create_index(
        'ix_umrah_vendor_billing_umrah_requisition_code',
        'umrah_vendor_billing',
        ['umrah_requisition_code'],
        unique=False,
        schema='core'
    )


def downgrade() -> None:
    op.drop_index(
        'ix_umrah_vendor_billing_umrah_requisition_code',
        table_name='umrah_vendor_billing',
        schema='core'
    )
    op.drop_table('umrah_vendor_billing', schema='core')
