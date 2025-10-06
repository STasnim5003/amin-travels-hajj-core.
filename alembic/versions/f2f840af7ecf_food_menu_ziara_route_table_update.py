"""food menu ziara route table update

Revision ID: f2f840af7ecf
Revises: 7ea563dd24f1
Create Date: 2025-10-06 21:39:06.552320

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f2f840af7ecf'
down_revision: Union[str, Sequence[str], None] = '7ea563dd24f1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("route", sa.Column("route_name", sa.String(), nullable=True),schema="core")
    op.add_column("food_menu", sa.Column("area", sa.String(), nullable=True),schema="core")
    op.drop_column("ziara", "pic", schema="core")
    op.drop_column("ziara", "name", schema="core")
    op.drop_column("ziara", "location", schema="core")
    op.drop_column("ziara", "google_map_location", schema="core")
    op.drop_column("ziara", "area", schema="core")


def downgrade() -> None:
    op.drop_column("route", "route_name", schema="core")
    op.drop_column("food_menu", "area", schema="core")

