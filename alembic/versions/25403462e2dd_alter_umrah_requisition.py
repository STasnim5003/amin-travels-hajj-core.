"""alter umrah requisition

Revision ID: 25403462e2dd
Revises: 64f4e09932c1
Create Date: 2026-07-02 14:24:19.882749

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '25403462e2dd'
down_revision: Union[str, Sequence[str], None] = '64f4e09932c1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('umrah_requisition', sa.Column('b2b_type', sa.String(), nullable=True), schema='core')
    op.add_column('umrah_requisition', sa.Column('b2b_partial_guests', postgresql.JSONB(astext_type=sa.Text()), nullable=True), schema='core')
    op.add_column('umrah_requisition', sa.Column('b2b_partial_description', postgresql.JSONB(astext_type=sa.Text()), nullable=True), schema='core')


def downgrade() -> None:
    op.drop_column('umrah_requisition', 'b2b_partial_description', schema='core')
    op.drop_column('umrah_requisition', 'b2b_partial_guests', schema='core')
    op.drop_column('umrah_requisition', 'b2b_type', schema='core')
