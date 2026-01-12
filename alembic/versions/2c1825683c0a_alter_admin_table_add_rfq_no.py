"""alter admin table add rfq no

Revision ID: 2c1825683c0a
Revises: 7016c45b60c4
Create Date: 2026-01-12 15:55:31.534714

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2c1825683c0a'
down_revision: Union[str, Sequence[str], None] = '7016c45b60c4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('admin', sa.Column('rfq_no', sa.Integer(), nullable=True), schema='core')


def downgrade() -> None:
    op.drop_column('admin', 'rfq_no', schema='core')
