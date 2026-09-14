"""create food purchase table

Revision ID: f2d8a4c17b35
Revises: a1c6f3d9b210
Create Date: 2026-09-14 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'f2d8a4c17b35'
down_revision: Union[str, Sequence[str], None] = 'a1c6f3d9b210'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "food_purchase",
        sa.Column("id", sa.Integer(), autoincrement=True, primary_key=True),
        sa.Column("agency_name", sa.String(), nullable=False),
        sa.Column("food_name", sa.String(), nullable=False),
        sa.Column("items", postgresql.JSONB(), nullable=True),
        sa.Column("vendor_name", sa.String(), nullable=True),
        sa.Column("meals_purchased", sa.Integer(), nullable=False),
        sa.Column("cost", sa.Float(), nullable=False),
        sa.Column("currency", sa.String(), nullable=False, server_default="BDT"),
        sa.Column("purchase_date", sa.String(), nullable=True),
        sa.Column("booking_file", postgresql.JSONB(), nullable=True),
        sa.Column("remarks", sa.String(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(),
            server_default=sa.text("(NOW() AT TIME ZONE 'UTC') + interval '6 hours'"),
            nullable=False,
        ),
        sa.Column(
            "updated_at", sa.DateTime(),
            server_default=sa.text("(NOW() AT TIME ZONE 'UTC') + interval '6 hours'"),
            nullable=False,
        ),
        sa.Column("created_by", sa.String(), nullable=True),
        sa.Column("updated_by", sa.String(), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        schema="core",
    )
    op.create_index(
        op.f("ix_core_food_purchase_id"), "food_purchase", ["id"], unique=False, schema="core"
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_core_food_purchase_id"), table_name="food_purchase", schema="core")
    op.drop_table("food_purchase", schema="core")
