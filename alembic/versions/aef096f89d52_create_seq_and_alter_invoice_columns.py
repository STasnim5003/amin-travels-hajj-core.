"""create seq and alter invoice columns

Revision ID: aef096f89d52
Revises: 6c66cb4a72a3
Create Date: 2026-04-08 13:41:23.364489

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'aef096f89d52'
down_revision: Union[str, Sequence[str], None] = '6c66cb4a72a3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE SEQUENCE core.invoice_number_seq START WITH 100 INCREMENT BY 1")
    op.execute("""
        ALTER TABLE core.umrah_customer_billing
        ALTER COLUMN invoice_no
        SET DEFAULT 'INV-' || nextval('core.invoice_number_seq')
    """)

    op.execute("""
            ALTER TABLE core.umrah_vendor_billing
            ALTER COLUMN invoice_no
            SET DEFAULT 'INV-' || nextval('core.invoice_number_seq')
        """)

    op.execute("""
            ALTER TABLE core.umrah_b2b_payements
            ALTER COLUMN invoice_no
            SET DEFAULT 'INV-' || nextval('core.invoice_number_seq')
        """)

    op.execute("""
            ALTER TABLE core.umrah_requisition
            ALTER COLUMN discount SET DEFAULT 0
        """)

def downgrade() -> None:

    op.execute("""
        ALTER TABLE core.umrah_customer_billing
        ALTER COLUMN invoice_no DROP DEFAULT
    """)

    op.execute("""
        ALTER TABLE core.umrah_vendor_billing
        ALTER COLUMN invoice_no DROP DEFAULT
    """)

    op.execute("""
        ALTER TABLE core.umrah_b2b_payements
        ALTER COLUMN invoice_no DROP DEFAULT
    """)


    op.execute("DROP SEQUENCE IF EXISTS core.invoice_number_seq")
