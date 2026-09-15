"""admin user latest assign time

Revision ID: 6aa3dfe8fea0
Revises: f2d8a4c17b35
Create Date: 2026-09-15 14:58:41.948876

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6aa3dfe8fea0'
down_revision: Union[str, Sequence[str], None] = 'f2d8a4c17b35'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('umrah_requisition', sa.Column('assign_to', sa.String, nullable=True), schema='core')
    op.add_column('admin_user', sa.Column('latest_assign_time', sa.DateTime(), nullable=True), schema='core')

def downgrade() -> None:
    op.drop_column('admin_user', 'latest_assign_time', schema='core')
    op.drop_column('umrah_requisition', 'assign_to', schema='core')
