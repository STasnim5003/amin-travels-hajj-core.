"""alter pilgrim table add package assign columns

Revision ID: 3c4724da5d89
Revises: b3d46f6d2ed1
Create Date: 2025-10-09 01:03:30.246010

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '3c4724da5d89'
down_revision: Union[str, Sequence[str], None] = 'b3d46f6d2ed1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("pilgrim_data", sa.Column("package_name", sa.String(), nullable=True), schema='core')
    op.add_column("pilgrim_data", sa.Column("package_duration", sa.Integer(), nullable=True), schema='core')
    op.add_column("pilgrim_data", sa.Column("package_bed_types", sa.String(), nullable=True), schema='core')
    op.add_column("pilgrim_data", sa.Column("add_ons_services", postgresql.JSONB(), nullable=True), schema='core')


def downgrade() -> None:
    op.drop_column("pilgrim_data", "package_name", schema='core')
    op.drop_column("pilgrim_data", "package_duration", schema='core')
    op.drop_column("pilgrim_data", "package_bed_types", schema='core')
    op.drop_column("pilgrim_data", "add_ons_services", schema='core')