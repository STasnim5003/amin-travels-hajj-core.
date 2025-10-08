"""alter payment table add column

Revision ID: 6777c892da5f
Revises: 1bb274a41973
Create Date: 2025-10-08 15:51:50.263044

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '6777c892da5f'
down_revision: Union[str, Sequence[str], None] = '1bb274a41973'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('payment', sa.Column('pilgrims_id', postgresql.JSON(astext_type=sa.Text()),nullable=True), schema="core")
    op.add_column('payment', sa.Column('group_leader', sa.String(), nullable=True), schema="core")
    op.add_column('payment', sa.Column('category', sa.String(), nullable=True), schema="core")
    op.add_column('payment', sa.Column('transaction_id', sa.String(), nullable=True), schema="core")
    op.add_column('payment', sa.Column('parent_transaction_id', sa.String(), nullable=True), schema="core")


def downgrade() -> None:
    op.drop_column('payment', 'pilgrims_id', schema="core")
    op.drop_column('payment', 'group_leader', schema="core")
    op.drop_column('payment', 'category', schema="core")

    op.drop_column('payment', 'transaction_id', schema="core")
    op.drop_column('payment', 'parent_transaction_id', schema="core")

