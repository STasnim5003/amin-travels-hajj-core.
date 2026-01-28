"""create table dashboard

Revision ID: 9fb2aa8167a0
Revises: 28635eef73b9
Create Date: 2026-01-27 14:21:01.757341

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9fb2aa8167a0'
down_revision: Union[str, Sequence[str], None] = '28635eef73b9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('admin', sa.Column('flight_requested', sa.Integer(), server_default=sa.text('0'), nullable=True), schema='core')
    op.add_column('admin', sa.Column('hotel_requested', sa.Integer(), server_default=sa.text('0'),nullable=True), schema='core')
    op.add_column('admin', sa.Column('route_requested', sa.Integer(), server_default=sa.text('0'),nullable=True), schema='core')


def downgrade() -> None:
    op.drop_column('admin', 'route_requested', schema='core')
    op.drop_column('admin', 'flight_requested', schema='core')
    op.drop_column('admin', 'hotel_requested', schema='core')
