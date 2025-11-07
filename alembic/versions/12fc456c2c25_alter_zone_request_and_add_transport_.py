"""alter zone_request and add transport data

Revision ID: 12fc456c2c25
Revises: 8316b73296a4
Create Date: 2025-11-07 15:41:29.610692

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '12fc456c2c25'
down_revision: Union[str, Sequence[str], None] = '8316b73296a4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('zone_request', sa.Column('total_pilgrims', sa.Integer, nullable=True), schema='core')


def downgrade() -> None:
    op.drop_column('zone_request', 'total_pilgrims', schema='core')
