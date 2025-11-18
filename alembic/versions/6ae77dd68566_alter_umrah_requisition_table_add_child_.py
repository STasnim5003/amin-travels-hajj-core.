"""alter umrah requisition table add child infant info

Revision ID: 6ae77dd68566
Revises: f3cdeb71feb5
Create Date: 2025-11-18 14:52:28.281342

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '6ae77dd68566'
down_revision: Union[str, Sequence[str], None] = 'f3cdeb71feb5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('umrah_requisition', sa.Column('child_service', postgresql.JSONB(astext_type=sa.Text()), nullable=True),schema='core')
    op.add_column('umrah_requisition', sa.Column('infant_service', postgresql.JSONB(astext_type=sa.Text()), nullable=True),schema='core')


def downgrade() -> None:
    op.drop_column('umrah_requisition', 'child_service',schema='core')
    op.drop_column('umrah_requisition', 'infant_service',schema='core')
