"""alter umrah b2b and vendor billing

Revision ID: cbc276a0fdfc
Revises: 62d191ed1c91
Create Date: 2026-06-13 15:28:29.645565

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cbc276a0fdfc'
down_revision: Union[str, Sequence[str], None] = '62d191ed1c91'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column("umrah_b2b_payements", "amin_office_code", schema="core")
    op.drop_column("umrah_vendor_billing", "amin_office_code", schema="core")


def downgrade() -> None:
    """Downgrade schema."""
    pass
