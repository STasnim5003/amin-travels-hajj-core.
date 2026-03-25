"""alter umrah requisition table

Revision ID: 0befab704cc0
Revises: 4fefe854a304
Create Date: 2026-03-25 14:40:50.055417

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0befab704cc0'
down_revision: Union[str, Sequence[str], None] = '4fefe854a304'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE SEQUENCE core.invoice_seq START 1;")

    op.add_column(
        'umrah_requisition',
        sa.Column(
            'total_due',
            sa.Float(),
            nullable=False,
            server_default=sa.text("0")
        ),
        schema="core"
    )

    op.add_column(
        'umrah_requisition',
        sa.Column(
            'total_payment',
            sa.Float(),
            nullable=False,
            server_default=sa.text("0")
        ),
        schema="core"
    )

    op.add_column(
        'umrah_requisition',
        sa.Column(
            'invoice_no',
            sa.String(),
            nullable=False,
            unique=True,
            server_default=sa.text(
                "'INV-' || LPAD(nextval('core.invoice_seq')::text, 6, '0')"
            )
        ),
        schema="core"
    )


def downgrade() -> None:
    # 🔹 Drop columns
    op.drop_column('umrah_requisition', 'invoice_no', schema="core")
    op.drop_column('umrah_requisition', 'total_payment', schema="core")
    op.drop_column('umrah_requisition', 'total_due', schema="core")

    # 🔹 Drop sequence
    op.execute("DROP SEQUENCE core.invoice_seq;")
