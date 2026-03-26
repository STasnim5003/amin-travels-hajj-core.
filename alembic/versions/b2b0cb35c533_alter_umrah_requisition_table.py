"""alter umrah requisition table

Revision ID: b2b0cb35c533
Revises: 04209c6b6f9b
Create Date: 2026-03-26 14:25:27.855162

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b2b0cb35c533'
down_revision: Union[str, Sequence[str], None] = '04209c6b6f9b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'umrah_requisition',
        sa.Column(
            'umrah_requisition_code',
            sa.String(),
            nullable=False,
            unique=True,
            server_default=sa.text(
                "'UMR-' || LPAD(nextval('core.invoice_seq')::text, 6, '0')"
            )
        ),
        schema="core"
    )

    op.add_column('umrah_customer_billing', sa.Column('umrah_requisition_code', sa.String(), nullable=False), schema="core")

    op.create_index(
        'ix_umrah_requisition_code',
        'umrah_requisition',
        ['umrah_requisition_code'],
        unique=True,
        schema='core'
    )

    # ✅ Index on umrah_customer_billing.umrah_requisition_code
    op.create_index(
        'ix_ucb_umrah_requisition_code',
        'umrah_customer_billing',
        ['umrah_requisition_code'],
        schema='core'
    )

    # ✅ Index on agency_name (for filtering)
    op.create_index(
        'ix_umrah_requisition_agency_name',
        'umrah_requisition',
        ['agency_name'],
        schema='core'
    )


def downgrade() -> None:

    op.drop_index('ix_umrah_requisition_agency_name', table_name='umrah_requisition', schema='core')
    op.drop_index('ix_ucb_umrah_requisition_code', table_name='umrah_customer_billing', schema='core')
    op.drop_index('ix_umrah_requisition_code', table_name='umrah_requisition', schema='core')

    # Drop columns
    op.drop_column('umrah_customer_billing', 'umrah_requisition_code', schema="core")
    op.drop_column('umrah_requisition', 'umrah_requisition_code', schema="core")