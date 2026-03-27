"""alter umrah vendor billing

Revision ID: 1c532a2ff623
Revises: 001807f7b4b3
Create Date: 2026-03-27 17:18:50.122906

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1c532a2ff623'
down_revision: Union[str, Sequence[str], None] = '001807f7b4b3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE SEQUENCE core.umrah_vendor_billing_invoice_seq START 1;")
    op.drop_column('umrah_vendor_billing', 'invoice_no', schema='core')

    op.add_column(
        'umrah_vendor_billing',
        sa.Column(
            'invoice_no',
            sa.String(),
            nullable=False,
            unique=True,
            server_default=sa.text(
                "'INV-' || LPAD(nextval('core.umrah_vendor_billing_invoice_seq')::text, 6, '0')"
            )
        ),
        schema="core"
    )


def downgrade() -> None:
    op.execute("DROP SEQUENCE core.umrah_vendor_billing_invoice_seq;")
    op.drop_column('umrah_vendor_billing', 'invoice_no', schema='core')
