"""alter payment table add column

Revision ID: 4fefe854a304
Revises: 272e42e90b76
Create Date: 2026-03-10 15:35:44.525496

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4fefe854a304'
down_revision: Union[str, Sequence[str], None] = '272e42e90b76'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('payment', sa.Column('agency_name', sa.String(), nullable=True), schema='core')


def downgrade() -> None:
    op.drop_column('payment', 'agency_name', schema='core')
