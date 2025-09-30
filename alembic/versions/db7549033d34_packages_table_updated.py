"""packages table updated

Revision ID: db7549033d34
Revises: fa719f172387
Create Date: 2025-09-29 23:38:50.623242

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'db7549033d34'
down_revision: Union[str, Sequence[str], None] = 'fa719f172387'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("packages", sa.Column("duration_range", postgresql.JSONB(astext_type=sa.TEXT())), schema="core")
    op.add_column("packages", sa.Column("flight_date", postgresql.JSONB(astext_type=sa.TEXT())), schema="core")
    op.add_column("packages", sa.Column("bed_type", postgresql.JSONB(astext_type=sa.TEXT())), schema="core")
    op.add_column("packages", sa.Column("return_ticket", sa.String(), nullable=True), schema="core")
    op.add_column("packages", sa.Column("fixed_or_shifting", sa.String(), nullable=True), schema="core")
    op.add_column("packages", sa.Column("food_menu_id", sa.Integer(), nullable=True), schema="core")
    op.add_column("packages", sa.Column("ziara_id", postgresql.JSONB(astext_type=sa.TEXT())), schema="core")
    op.add_column("packages", sa.Column("special_services", postgresql.JSONB(astext_type=sa.TEXT())), schema="core")
    op.add_column("packages", sa.Column("other_services", postgresql.JSONB(astext_type=sa.TEXT())), schema="core")


def downgrade() -> None:
    op.drop_column("packages", "duration_range", schema="core")
    op.drop_column("packages", "flight_date", schema="core")
    op.drop_column("packages", "bed_type", schema="core")
    op.drop_column("packages", "return_ticket", schema="core")
    op.drop_column("packages", "fixed_or_shifting", schema="core")
    op.drop_column("packages", "food_menu_id", schema="core")
    op.drop_column("packages", "ziara_id", schema="core")
    op.drop_column("packages", "special_services", schema="core")
    op.drop_column("packages", "other_services", schema="core")