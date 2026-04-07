"""alter umrah requisition add column

Revision ID: 6c66cb4a72a3
Revises: 21f86c675c0b
Create Date: 2026-04-07 22:33:56.700321

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '6c66cb4a72a3'
down_revision: Union[str, Sequence[str], None] = '21f86c675c0b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('umrah_requisition', sa.Column('service_confirmation_status', postgresql.JSONB(astext_type=sa.Text()), nullable=True),schema='core')


def downgrade() -> None:
    op.drop_column('umrah_requisition', 'service_confirmation_status', schema='core')
