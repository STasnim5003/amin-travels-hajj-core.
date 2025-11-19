"""alter table hotel request add column

Revision ID: c928ec80f98e
Revises: 85177ddf0249
Create Date: 2025-11-19 14:02:46.285604

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'c928ec80f98e'
down_revision: Union[str, Sequence[str], None] = '85177ddf0249'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('hotel_request', sa.Column('document', postgresql.JSONB(astext_type=sa.Text()), nullable=True), schema='core')
    op.add_column('hotel_request', sa.Column('pricing', postgresql.JSONB(astext_type=sa.Text()), nullable=True), schema='core')


def downgrade() -> None:
    op.drop_column('hotel_request', 'document', schema='core')
    op.drop_column('hotel_request', 'pricing', schema='core')
