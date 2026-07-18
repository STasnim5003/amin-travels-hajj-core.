"""alter payment table

Revision ID: d97a0e356590
Revises: 1780fe29a48a
Create Date: 2026-07-16 15:42:07.108256

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd97a0e356590'
down_revision: Union[str, Sequence[str], None] = '1780fe29a48a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('payment', column=sa.Column('nid', sa.String(), nullable=True), schema='core')
    op.add_column('payment', column=sa.Column('passport_no', sa.String(), nullable=True), schema='core')
    op.add_column('payment', column=sa.Column('pilgrim_name', sa.String(), nullable=True), schema='core')
    op.add_column('payment', column=sa.Column('hajj_year', sa.Integer(), nullable=True), schema='core')


def downgrade() -> None:
    op.drop_column('payment', 'nid', schema='core')
    op.drop_column('payment', 'passport_no', schema='core')
    op.drop_column('payment', 'pilgrim_name', schema='core')
    op.drop_column('payment', 'hajj_year', schema='core')
