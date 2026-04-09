"""alter vendor price table

Revision ID: 56ce53c3b3b6
Revises: 7cb5624c2b63
Create Date: 2026-04-09 13:26:46.899481

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '56ce53c3b3b6'
down_revision: Union[str, Sequence[str], None] = '7cb5624c2b63'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_unique_constraint(
        'uq_umrah_vendors_price_umrah_requisition_id',
        'umrah_vendor_prices',
        ['umrah_requisition_id'],
        schema='core',
    )


def downgrade() -> None:
    """Downgrade schema."""
    pass
